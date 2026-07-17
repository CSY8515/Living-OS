from __future__ import annotations

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.database.engines.contracts import IntegrityResult


REQUIRED_TABLES = (
    "system_meta",
    "records",
    "domain_events",
    "audit_entries",
    "database_migrations",
    "execution_records",
    "backup_history",
    "restore_history",
)

REQUIRED_INDEXES = (
    "ix_records_status",
    "ix_records_updated",
    "ix_execution_status",
    "ix_execution_action",
)


class IntegrityEngine:
    def __init__(self, connections: SQLiteConnectionLayer) -> None:
        self.connections = connections

    def check(self, expected_schema_version: int) -> IntegrityResult:
        if not self.connections.database_path.is_file():
            return IntegrityResult(
                "FAILED",
                "missing-database",
                0,
                REQUIRED_TABLES,
                REQUIRED_INDEXES,
                0,
            )
        with self.connections.connection(read_only=True) as connection:
            integrity_row = connection.execute("PRAGMA integrity_check").fetchone()
            integrity = str(integrity_row[0]) if integrity_row else "unknown"
            foreign_key_violations = len(connection.execute("PRAGMA foreign_key_check").fetchall())
            tables = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            indexes = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='index'"
                ).fetchall()
            }
            version_row = connection.execute(
                "SELECT value FROM system_meta WHERE key='schema_version'"
            ).fetchone() if "system_meta" in tables else None
        schema_version = int(version_row[0]) if version_row else 0
        missing_tables = tuple(name for name in REQUIRED_TABLES if name not in tables)
        missing_indexes = tuple(name for name in REQUIRED_INDEXES if name not in indexes)
        if integrity != "ok" or foreign_key_violations:
            status = "FAILED"
        elif schema_version != expected_schema_version or missing_tables or missing_indexes:
            status = "DEGRADED"
        else:
            status = "HEALTHY"
        return IntegrityResult(
            status,
            integrity,
            foreign_key_violations,
            missing_tables,
            missing_indexes,
            schema_version,
        )
