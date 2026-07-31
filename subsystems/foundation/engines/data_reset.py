from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
from uuid import uuid4

from subsystems.foundation.engines.hub import LivingHub


class OwnerDataTarget(Protocol):
    subsystem_id: str
    database_path: Path

    def owner_data_count(self) -> int: ...
    def reset_owner_data(self) -> dict[str, int]: ...


class OwnerDataResetError(RuntimeError):
    """Raised when owner-data reset fails or cannot be rolled back safely."""


@dataclass(frozen=True)
class OwnerDataResetReport:
    backup_path: str
    removed_by_owner: dict[str, int]
    total_removed: int
    rollback_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "backup_path": self.backup_path,
            "removed_by_owner": dict(self.removed_by_owner),
            "total_removed": self.total_removed,
            "rollback_performed": self.rollback_performed,
        }


def development_legacy_empty_states(repository_root: Path) -> dict[Path, str]:
    """Return the canonical empty state for active legacy owner-data files."""
    root = Path(repository_root).resolve()
    return {
        root / "data" / "daily_logs.json": json.dumps(
            {"logs": []}, ensure_ascii=False, indent=2
        )
        + "\n",
        root / "data" / "archive.json": json.dumps(
            {"items": []}, ensure_ascii=False, indent=2
        )
        + "\n",
        root / "logs" / "decision_log.jsonl": "",
        root / "reports" / "report_index.json": json.dumps(
            {"reports": []}, ensure_ascii=False, indent=2
        )
        + "\n",
        root / "data" / "finance_budget.json": json.dumps(
            {
                "monthly_income": 0,
                "fixed_expenses": [],
                "savings_goals": [],
                "summary": {
                    "total_fixed_expenses": 0,
                    "total_savings_goals": 0,
                    "remaining_amount": 0,
                    "fixed_expense_ratio": 0.0,
                    "risk_level": "NORMAL",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        root / "data" / "housing_candidates.json": json.dumps(
            {"candidates": []}, ensure_ascii=False, indent=2
        )
        + "\n",
    }


class OwnerDataResetService:
    """Coordinate verified backup, reset, validation, and rollback."""

    def __init__(
        self,
        hub: LivingHub,
        targets: Sequence[OwnerDataTarget],
        *,
        legacy_empty_states: Mapping[Path, str] | None = None,
    ) -> None:
        self.hub = hub
        self.targets = tuple(targets)
        self.legacy_empty_states = {
            Path(path).resolve(): content
            for path, content in (legacy_empty_states or {}).items()
        }

    def preview(self) -> dict[str, int]:
        counts = {
            target.subsystem_id: int(target.owner_data_count())
            for target in self.targets
        }
        counts["HUB"] = self.hub.store.owner_data_count()
        counts["LEGACY"] = sum(
            self._legacy_record_count(path, content)
            for path, content in self.legacy_empty_states.items()
        )
        return counts

    def reset(self, *, actor: str = "owner") -> OwnerDataResetReport:
        correlation_id = f"owner-reset-{uuid4()}"
        legacy_paths = [
            path for path in self.legacy_empty_states if path.exists() and path.is_file()
        ]
        hub_backup = self.hub.backups.create(legacy_paths)
        if not self.hub.backups.verify(hub_backup):
            raise OwnerDataResetError("Verified backup creation failed; no data was reset.")

        component_backups: dict[str, Path] = {}
        for target in self.targets:
            if Path(target.database_path).is_file():
                component_backups[target.subsystem_id] = (
                    self.hub.database.create_component_backup(
                        target.subsystem_id, actor=actor
                    )
                )

        removed: dict[str, int] = {}
        try:
            for target in self.targets:
                result = target.reset_owner_data()
                removed[target.subsystem_id] = sum(int(value) for value in result.values())

            hub_result = self.hub.store.reset_owner_data(
                self.hub.documents.content_root
            )
            removed["HUB"] = sum(int(value) for value in hub_result.values())

            legacy_removed = 0
            for path, empty_content in self.legacy_empty_states.items():
                legacy_removed += self._legacy_record_count(path, empty_content)
                self._write_text_atomic(path, empty_content)
            removed["LEGACY"] = legacy_removed

            remaining = self.preview()
            if any(remaining.values()):
                raise OwnerDataResetError(
                    "Owner data remained after reset validation."
                )

            self.hub.database.record_execution(
                "SUB-FOUNDATION",
                "owner_data_reset",
                actor=actor,
                result={
                    "removed_total": sum(removed.values()),
                    "component_count": len(self.targets),
                    "correlation_id": correlation_id,
                },
            )
            return OwnerDataResetReport(
                str(hub_backup),
                removed,
                sum(removed.values()),
            )
        except Exception as exc:
            rollback_errors: list[str] = []
            try:
                self.hub.database.restore(
                    hub_backup,
                    actor=actor,
                    correlation_id=correlation_id,
                )
            except Exception as rollback_exc:
                rollback_errors.append(f"HUB:{type(rollback_exc).__name__}")
            for component_id, backup_path in component_backups.items():
                try:
                    self.hub.database.restore_component_backup(
                        component_id, backup_path, actor=actor
                    )
                except Exception as rollback_exc:
                    rollback_errors.append(
                        f"{component_id}:{type(rollback_exc).__name__}"
                    )
            if rollback_errors:
                raise OwnerDataResetError(
                    "Owner-data reset failed and rollback was incomplete: "
                    + ", ".join(rollback_errors)
                ) from exc
            raise OwnerDataResetError(
                "Owner-data reset failed; the verified backup was restored."
            ) from exc

    @staticmethod
    def _write_text_atomic(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.{uuid4().hex}.tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise

    @staticmethod
    def _legacy_record_count(path: Path, empty_content: str) -> int:
        if not path.exists() or not path.is_file():
            return 0
        try:
            text = path.read_text(encoding="utf-8-sig")
            if text == empty_content:
                return 0
            if path.suffix == ".jsonl":
                return sum(1 for line in text.splitlines() if line.strip())
            value = json.loads(text)
            if not isinstance(value, dict):
                return 1
            for key in ("logs", "items", "reports", "candidates"):
                records = value.get(key)
                if isinstance(records, list):
                    return len(records)
            if value == json.loads(empty_content):
                return 0
            return int(any(value.values()))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return 1
