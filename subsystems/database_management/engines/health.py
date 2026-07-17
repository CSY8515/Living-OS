from __future__ import annotations

from pathlib import Path
import time
from typing import Any

from subsystems.database.engines.contracts import DatabaseControlInterface
from subsystems.foundation.engines.time import utc_now_iso


class DatabaseHealthEngine:
    def __init__(
        self,
        database: DatabaseControlInterface,
        *,
        capacity_warning_bytes: int,
        degraded_check_ms: int,
    ) -> None:
        self.database = database
        self.capacity_warning_bytes = capacity_warning_bytes
        self.degraded_check_ms = degraded_check_ms

    def inspect(self, *, record: bool = False, actor: str = "system") -> dict[str, Any]:
        path = Path(self.database.database_path)
        if not path.is_file():
            return {
                "status": "FAILED",
                "checked_at": utc_now_iso(),
                "connection": "unavailable",
                "database_exists": False,
                "file_size": 0,
                "schema_version": 0,
                "expected_schema_version": self.database.expected_schema_version,
                "migration_status": "NOT_INITIALIZED",
                "integrity_status": "missing-database",
                "last_backup_at": "",
                "last_restore_at": "",
                "recent_error": "Database file does not exist.",
            }
        try:
            started = time.perf_counter()
            integrity = self.database.integrity_check(record=record, actor=actor)
            check_duration_ms = int((time.perf_counter() - started) * 1000)
            backups = self.database.list_backups()
            restores = self.database.restore_history()
            pending = self.database.pending_migrations()
            failures = self.database.failed_migrations()
            file_size = path.stat().st_size
            capacity_status = (
                "WARNING" if file_size >= self.capacity_warning_bytes else "NORMAL"
            )
            if failures:
                status = "FAILED"
            elif integrity.status == "FAILED":
                status = "FAILED"
            elif pending or integrity.status == "DEGRADED":
                status = "WARNING"
            elif check_duration_ms >= self.degraded_check_ms:
                status = "DEGRADED"
            elif capacity_status == "WARNING":
                status = "WARNING"
            else:
                status = "HEALTHY"
            return {
                "status": status,
                "checked_at": utc_now_iso(),
                "connection": "available",
                "database_exists": True,
                "file_size": file_size,
                "capacity_warning_bytes": self.capacity_warning_bytes,
                "capacity_status": capacity_status,
                "health_check_duration_ms": check_duration_ms,
                "degraded_check_ms": self.degraded_check_ms,
                "schema_version": integrity.schema_version,
                "expected_schema_version": self.database.expected_schema_version,
                "migration_status": "PENDING" if pending else "CURRENT",
                "integrity_status": integrity.integrity,
                "foreign_key_violations": integrity.foreign_key_violations,
                "missing_tables": list(integrity.missing_tables),
                "missing_indexes": list(integrity.missing_indexes),
                "last_backup_at": str(backups[0].get("created_at", "")) if backups else "",
                "last_restore_at": str(restores[0].get("completed_at", "")) if restores else "",
                "recent_error": str(failures[0].get("error_type", "")) if failures else "",
            }
        except Exception as exc:
            return {
                "status": "FAILED",
                "checked_at": utc_now_iso(),
                "connection": "failed",
                "database_exists": path.is_file(),
                "file_size": path.stat().st_size if path.is_file() else 0,
                "capacity_warning_bytes": self.capacity_warning_bytes,
                "capacity_status": "UNKNOWN",
                "health_check_duration_ms": 0,
                "degraded_check_ms": self.degraded_check_ms,
                "schema_version": 0,
                "expected_schema_version": self.database.expected_schema_version,
                "migration_status": "UNKNOWN",
                "integrity_status": "unknown",
                "last_backup_at": "",
                "last_restore_at": "",
                "recent_error": type(exc).__name__,
            }
