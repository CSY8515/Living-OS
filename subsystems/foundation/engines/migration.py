from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.audit import append_audit
from subsystems.foundation.engines.backup import BackupService
from subsystems.foundation.engines.contracts import CommandEnvelope, RecordRef
from subsystems.foundation.engines.errors import MigrationError
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.time import utc_now_iso


@dataclass
class MigrationReport:
    source_version: str = "v1.0 Stable"
    target_version: str = "v1.2"
    source_checksums: dict[str, str] = field(default_factory=dict)
    accepted: dict[str, int] = field(default_factory=dict)
    quarantined: list[dict[str, str]] = field(default_factory=list)
    backup_path: str = ""
    applied: bool = False
    canonical_records: int = 0

    @property
    def accepted_total(self) -> int:
        return sum(self.accepted.values())

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "accepted_total": self.accepted_total}


class V1MigrationService:
    """Explicit, dry-run-first v1 compatibility importer."""

    JSON_SOURCES = {
        "data/daily_logs.json": ("logs", "journal", "journal_entry", "id"),
        "data/archive.json": ("items", "knowledge", "knowledge_item", "id"),
        "reports/report_index.json": ("reports", "reports", "report", "path"),
        "config/module_registry.json": ("modules", "module_manager", "legacy_module", "id"),
        "data/housing_candidates.json": (
            "candidates",
            "compatibility",
            "housing_candidate",
            "id",
        ),
    }

    def __init__(
        self,
        store: HubStore,
        repository_root: Path,
        backup_service: BackupService,
    ) -> None:
        self.store = store
        self.repository_root = repository_root
        self.backup_service = backup_service

    @property
    def legacy_paths(self) -> list[Path]:
        paths = [self.repository_root / relative for relative in self.JSON_SOURCES]
        paths.extend(
            [
                self.repository_root / "logs/decision_log.jsonl",
                self.repository_root / "state/settings.json",
                self.repository_root / "data/finance_budget.json",
            ]
        )
        paths.extend(sorted((self.repository_root / "reports").glob("*.md")))
        return paths

    def _checksum(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _load_json(self, path: Path, report: MigrationReport) -> Any | None:
        if not path.exists():
            return None
        relative = path.relative_to(self.repository_root).as_posix()
        report.source_checksums[relative] = self._checksum(path)
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            report.quarantined.append(
                {"source": relative, "record": "file", "reason": type(exc).__name__}
            )
            return None

    def inspect(self) -> tuple[MigrationReport, list[tuple[RecordRef, dict[str, Any]]]]:
        report = MigrationReport()
        accepted: list[tuple[RecordRef, dict[str, Any]]] = []

        for relative, (container, module_id, entity_type, id_field) in self.JSON_SOURCES.items():
            path = self.repository_root / relative
            value = self._load_json(path, report)
            if value is None:
                continue
            items = value.get(container) if isinstance(value, dict) else None
            if not isinstance(items, list):
                report.quarantined.append(
                    {"source": relative, "record": "container", "reason": "invalid-shape"}
                )
                continue
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    report.quarantined.append(
                        {"source": relative, "record": str(index), "reason": "not-an-object"}
                    )
                    continue
                record_id = str(item.get(id_field) or f"legacy-{index + 1}")
                accepted.append((RecordRef(module_id, entity_type, record_id), dict(item)))
                report.accepted[relative] = report.accepted.get(relative, 0) + 1

        reports_root = self.repository_root / "reports"
        if reports_root.exists():
            for path in sorted(reports_root.glob("*.md")):
                relative = path.relative_to(self.repository_root).as_posix()
                report.source_checksums[relative] = self._checksum(path)
                try:
                    content = path.read_text(encoding="utf-8-sig")
                except (OSError, UnicodeError) as exc:
                    report.quarantined.append(
                        {"source": relative, "record": "file", "reason": type(exc).__name__}
                    )
                    continue
                ref = RecordRef("reports", "report", relative)
                payload = {
                    "id": relative,
                    "path": relative,
                    "report_type": path.stem.split("_", 1)[0],
                    "content": content,
                    "generated_by": "v1-compatibility-import",
                    "created_at": utc_now_iso(),
                    "schema_version": 1,
                }
                matching_index = next(
                    (
                        index
                        for index, (existing_ref, _) in enumerate(accepted)
                        if existing_ref == ref
                    ),
                    None,
                )
                if matching_index is None:
                    accepted.append((ref, payload))
                else:
                    payload = {**accepted[matching_index][1], **payload}
                    accepted[matching_index] = (ref, payload)
                report.accepted[relative] = 1

        decision_path = self.repository_root / "logs/decision_log.jsonl"
        if decision_path.exists():
            relative = decision_path.relative_to(self.repository_root).as_posix()
            report.source_checksums[relative] = self._checksum(decision_path)
            for line_number, line in enumerate(
                decision_path.read_text(encoding="utf-8-sig").splitlines(), start=1
            ):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    report.quarantined.append(
                        {"source": relative, "record": str(line_number), "reason": "invalid-json"}
                    )
                    continue
                if not isinstance(item, dict):
                    report.quarantined.append(
                        {"source": relative, "record": str(line_number), "reason": "not-an-object"}
                    )
                    continue
                record_id = str(item.get("id") or f"legacy-{line_number}")
                accepted.append((RecordRef("decision", "decision", record_id), dict(item)))
                report.accepted[relative] = report.accepted.get(relative, 0) + 1

        for relative, entity_type in (
            ("state/settings.json", "configuration"),
            ("data/finance_budget.json", "finance_budget"),
        ):
            value = self._load_json(self.repository_root / relative, report)
            if value is None:
                continue
            if not isinstance(value, dict):
                report.quarantined.append(
                    {"source": relative, "record": "file", "reason": "not-an-object"}
                )
                continue
            module_id = "settings" if entity_type == "configuration" else "compatibility"
            accepted.append((RecordRef(module_id, entity_type, entity_type), dict(value)))
            report.accepted[relative] = 1

        report.canonical_records = len(accepted)
        return report, accepted

    def dry_run(self) -> MigrationReport:
        report, _ = self.inspect()
        return report

    def apply(self) -> MigrationReport:
        self.store.initialize()
        if self.store.get_meta("v1_migration_complete", "false") == "true":
            raise MigrationError("Living OS v1 data has already been migrated.")
        report, accepted = self.inspect()
        backup_path = self.backup_service.create(self.legacy_paths)
        if not self.backup_service.verify(backup_path):
            raise MigrationError("The pre-migration backup could not be verified.")
        report.backup_path = str(backup_path)
        migration_id = str(uuid4())
        started_at = utc_now_iso()
        command = CommandEnvelope(
            "settings",
            "migrate_v1",
            {"migration_id": migration_id, "canonical_records": report.canonical_records},
            reason="approved-v1-to-v2-migration",
        )
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO migration_runs (
                    migration_id, source_version, target_version, status, report_json, started_at
                ) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    migration_id,
                    report.source_version,
                    report.target_version,
                    "running",
                    json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True),
                    started_at,
                ),
            )
            for ref, payload in accepted:
                self.store.put_record(ref, payload, expected_version=0, connection=connection)
            report.applied = True
            completed_at = utc_now_iso()
            self.store._set_meta(connection, "v1_migration_complete", "true")
            connection.execute(
                """UPDATE migration_runs
                   SET status='complete', report_json=?, completed_at=? WHERE migration_id=?""",
                (
                    json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True),
                    completed_at,
                    migration_id,
                ),
            )
            append_audit(
                connection,
                command,
                "accepted",
                {
                    "migration_id": migration_id,
                    "canonical_records": report.canonical_records,
                    "quarantined": len(report.quarantined),
                },
            )
        return report
