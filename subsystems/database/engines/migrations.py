from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable
from uuid import uuid4

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.foundation.engines.time import utc_now_iso


@dataclass(frozen=True)
class DatabaseMigration:
    version: int
    name: str
    statements: tuple[str, ...]


V17_MIGRATIONS = (
    DatabaseMigration(
        2,
        "v1_7_database_foundation",
        (
            "ALTER TABLE records ADD COLUMN status TEXT NOT NULL DEFAULT 'ACTIVE'",
            "ALTER TABLE records ADD COLUMN owner TEXT NOT NULL DEFAULT 'owner'",
            "ALTER TABLE records ADD COLUMN source TEXT NOT NULL DEFAULT 'living-os'",
            "ALTER TABLE records ADD COLUMN archived_at TEXT",
            "ALTER TABLE records ADD COLUMN correlation_id TEXT NOT NULL DEFAULT ''",
            "CREATE INDEX IF NOT EXISTS ix_records_status ON records(module_id, entity_type, status, updated_at)",
            "CREATE INDEX IF NOT EXISTS ix_records_updated ON records(updated_at)",
            """CREATE TABLE IF NOT EXISTS database_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT NOT NULL DEFAULT '',
                execution_id TEXT NOT NULL DEFAULT ''
            )""",
            """CREATE TABLE IF NOT EXISTS execution_records (
                execution_id TEXT PRIMARY KEY,
                subsystem TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,
                result_json TEXT NOT NULL DEFAULT '{}',
                error_code TEXT NOT NULL DEFAULT '',
                error_message TEXT NOT NULL DEFAULT '',
                actor TEXT NOT NULL,
                source TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                trace_id TEXT NOT NULL
            )""",
            "CREATE INDEX IF NOT EXISTS ix_execution_status ON execution_records(status, started_at)",
            "CREATE INDEX IF NOT EXISTS ix_execution_action ON execution_records(subsystem, action, started_at)",
            """CREATE TABLE IF NOT EXISTS backup_history (
                backup_id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                schema_version INTEGER NOT NULL,
                size_bytes INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                verified_at TEXT,
                execution_id TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS restore_history (
                restore_id TEXT PRIMARY KEY,
                backup_path TEXT NOT NULL,
                safety_backup_path TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL,
                schema_version INTEGER,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT NOT NULL DEFAULT '',
                execution_id TEXT NOT NULL
            )""",
        ),
    ),
)


class MigrationRegistry:
    def __init__(
        self,
        connections: SQLiteConnectionLayer,
        migrations: Iterable[DatabaseMigration] = V17_MIGRATIONS,
    ) -> None:
        self.connections = connections
        ordered = tuple(sorted(migrations, key=lambda item: item.version))
        if len({item.version for item in ordered}) != len(ordered):
            raise ValueError("Migration versions must be unique.")
        self.migrations = ordered

    def current_version(self) -> int:
        if not self.connections.database_path.is_file():
            return 0
        with self.connections.connection(read_only=True) as connection:
            if not self._table_exists(connection, "system_meta"):
                return 0
            row = connection.execute(
                "SELECT value FROM system_meta WHERE key='schema_version'"
            ).fetchone()
        return int(row["value"]) if row else 0

    def pending(self) -> list[DatabaseMigration]:
        current = self.current_version()
        return [migration for migration in self.migrations if migration.version > current]

    def apply_pending(self, *, execution_id: str = "") -> list[dict[str, object]]:
        applied: list[dict[str, object]] = []
        for migration in self.pending():
            started_at = utc_now_iso()
            try:
                with self.connections.transaction() as connection:
                    for statement in migration.statements:
                        connection.execute(statement)
                    connection.execute(
                        """INSERT INTO database_migrations(
                               version,name,status,started_at,completed_at,error,execution_id
                           ) VALUES(?,?,?,?,?,?,?)""",
                        (
                            migration.version,
                            migration.name,
                            "APPLIED",
                            started_at,
                            utc_now_iso(),
                            "",
                            execution_id,
                        ),
                    )
                    connection.execute(
                        """INSERT INTO system_meta(key,value,updated_at) VALUES('schema_version',?,?)
                           ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                        (str(migration.version), utc_now_iso()),
                    )
                    connection.execute(
                        """INSERT INTO system_meta(key,value,updated_at) VALUES('product_version','v1.7',?)
                           ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                        (utc_now_iso(),),
                    )
                applied.append({"version": migration.version, "name": migration.name, "status": "APPLIED"})
            except Exception as exc:
                self._record_failure(migration, started_at, execution_id, exc)
                raise
        return applied

    def history(self, status: str | None = None) -> list[dict[str, object]]:
        if not self.connections.database_path.is_file():
            return []
        with self.connections.connection(read_only=True) as connection:
            if not self._table_exists(connection, "database_migrations"):
                return []
            sql = "SELECT * FROM database_migrations"
            parameters: tuple[object, ...] = ()
            if status:
                sql += " WHERE status=?"
                parameters = (status,)
            rows = connection.execute(sql + " ORDER BY version", parameters).fetchall()
        return [dict(row) for row in rows]

    def _record_failure(
        self,
        migration: DatabaseMigration,
        started_at: str,
        execution_id: str,
        error: Exception,
    ) -> None:
        source_version = self.current_version()
        try:
            with self.connections.transaction() as connection:
                connection.execute(
                    """INSERT INTO migration_runs(
                           migration_id,source_version,target_version,status,report_json,
                           started_at,completed_at
                       ) VALUES(?,?,?,?,?,?,?)""",
                    (
                        f"database-v{migration.version}-{uuid4()}",
                        str(source_version),
                        str(migration.version),
                        "failed",
                        json.dumps(
                            {
                                "error_type": type(error).__name__,
                                "execution_id": execution_id,
                                "name": migration.name,
                            },
                            sort_keys=True,
                        ),
                        started_at,
                        utc_now_iso(),
                    ),
                )
        except sqlite3.Error:
            pass

    def failures(self) -> list[dict[str, object]]:
        if not self.connections.database_path.is_file():
            return []
        with self.connections.connection(read_only=True) as connection:
            if not self._table_exists(connection, "migration_runs"):
                return []
            rows = connection.execute(
                """SELECT migration_id,target_version,report_json,started_at,completed_at
                   FROM migration_runs
                   WHERE status='failed' AND migration_id LIKE 'database-v%'
                   ORDER BY started_at DESC"""
            ).fetchall()
        failures: list[dict[str, object]] = []
        for row in rows:
            report = json.loads(row["report_json"])
            failures.append(
                {
                    "migration_id": row["migration_id"],
                    "version": int(row["target_version"]),
                    "name": report.get("name", ""),
                    "error_type": report.get("error_type", ""),
                    "execution_id": report.get("execution_id", ""),
                    "started_at": row["started_at"],
                    "failed_at": row["completed_at"],
                }
            )
        return failures

    @staticmethod
    def _table_exists(connection: sqlite3.Connection, name: str) -> bool:
        row = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        return row is not None
