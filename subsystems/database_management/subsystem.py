from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timedelta, timezone

from subsystems.database.engines.contracts import DatabaseControlInterface, RestoreCandidate
from subsystems.database_management.engines.health import DatabaseHealthEngine
from subsystems.database_management.engines.report import build_management_report


class DatabaseManagementSubsystem:
    """Control-plane facade; it never edits business records directly."""

    subsystem_id = "SUB-DATABASE-MANAGEMENT"
    version = "1.7.0"
    statuses = ("HEALTHY", "WARNING", "DEGRADED", "FAILED", "MAINTENANCE")

    def __init__(
        self,
        database: DatabaseControlInterface,
        *,
        capacity_warning_bytes: int = 512 * 1024 * 1024,
        degraded_check_ms: int = 1000,
        backup_retention_days: int = 30,
    ) -> None:
        self.database = database
        self.backup_retention_days = backup_retention_days
        self.health = DatabaseHealthEngine(
            database,
            capacity_warning_bytes=capacity_warning_bytes,
            degraded_check_ms=degraded_check_ms,
        )

    def health_check(self, *, record: bool = False, actor: str = "system") -> dict[str, Any]:
        return self.health.inspect(record=record, actor=actor)

    def schema_registry(self) -> dict[str, Any]:
        return self.database.schema_registry()

    def migration_status(self) -> dict[str, Any]:
        return {
            "current_version": self.database.current_schema_version(),
            "expected_version": self.database.expected_schema_version,
            "pending": self.database.pending_migrations(),
            "applied": self.database.applied_migrations(),
            "failed": self.database.failed_migrations(),
        }

    def request_migration(
        self, *, actor: str, correlation_id: str = ""
    ) -> list[dict[str, Any]]:
        return self.database.apply_migrations(actor=actor, correlation_id=correlation_id)

    def backup_status(self) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.backup_retention_days)
        result: list[dict[str, Any]] = []
        for item in self.database.list_backups():
            created_at = str(item.get("created_at", ""))
            try:
                created = datetime.fromisoformat(created_at)
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                stale = created < cutoff
            except ValueError:
                stale = True
            result.append({**item, "stale": stale})
        return result

    def request_backup(self, *, actor: str, correlation_id: str = "") -> Path:
        return self.database.create_backup(actor=actor, correlation_id=correlation_id)

    def restore_candidates(self) -> list[RestoreCandidate]:
        return [
            self.database.validate_restore(Path(item["path"]))
            for item in self.database.list_backups()
        ]

    def preflight_restore(self, archive_path: Path) -> RestoreCandidate:
        return self.database.validate_restore(archive_path)

    def request_restore(
        self, archive_path: Path, *, actor: str, correlation_id: str = ""
    ) -> dict[str, Any]:
        return self.database.restore(
            archive_path, actor=actor, correlation_id=correlation_id
        )

    def operational_report(self, *, record: bool = False, actor: str = "system") -> dict[str, Any]:
        health = self.health_check(record=record, actor=actor)
        schema = self.schema_registry()
        backups = self.backup_status()
        restores = self.database.restore_history()
        failures = self.database.failed_migrations()
        report = build_management_report(health, schema, backups, restores, failures)
        if record and self.database.current_schema_version() >= self.database.expected_schema_version:
            self.database.record_execution(
                self.subsystem_id,
                "management_report",
                actor=actor,
                result={
                    "database_status": report["database_status"],
                    "recommendations": len(report["recommendations"]),
                },
            )
        return report
