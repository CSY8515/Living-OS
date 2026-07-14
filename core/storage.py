from __future__ import annotations

import json
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any, Iterator

from core.contracts import DomainEvent, RecordRef, Relationship
from core.errors import ConcurrencyError
from shared.time import utc_now_iso


SCHEMA_VERSION = 1


class HubStore:
    """Transactional canonical storage adapter for the single-owner Hub."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS system_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS records (
                    module_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    privacy_class TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (module_id, entity_type, record_id)
                );

                CREATE TABLE IF NOT EXISTS domain_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    module_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    published_at TEXT
                );

                CREATE TABLE IF NOT EXISTS audit_entries (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT NOT NULL UNIQUE,
                    command_id TEXT NOT NULL,
                    module_id TEXT NOT NULL,
                    command_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    source TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_module TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    target_module TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (
                        source_module, source_type, source_id, relation_type,
                        target_module, target_type, target_id
                    )
                );

                CREATE TABLE IF NOT EXISTS module_states (
                    module_id TEXT PRIMARY KEY,
                    manifest_json TEXT NOT NULL,
                    lifecycle_state TEXT NOT NULL,
                    health_state TEXT NOT NULL,
                    installed_at TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    content_hash TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    privacy_class TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (document_id, version)
                );

                CREATE TABLE IF NOT EXISTS migration_runs (
                    migration_id TEXT PRIMARY KEY,
                    source_version TEXT NOT NULL,
                    target_version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS projection_checkpoints (
                    projection_id TEXT PRIMARY KEY,
                    last_event_sequence INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS paired_devices (
                    device_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    paired_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    revoked_at TEXT
                );
                """
            )
            self._set_meta(connection, "schema_version", str(SCHEMA_VERSION))
            self._set_meta(connection, "product_version", "v2.0")

    def _set_meta(self, connection: sqlite3.Connection, key: str, value: str) -> None:
        connection.execute(
            """
            INSERT INTO system_meta (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (key, value, utc_now_iso()),
        )

    def set_meta(self, key: str, value: str) -> None:
        with self.transaction() as connection:
            self._set_meta(connection, key, value)

    def get_meta(self, key: str, default: str = "") -> str:
        self.initialize()
        with closing(self.connect()) as connection:
            row = connection.execute("SELECT value FROM system_meta WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row else default

    def put_record(
        self,
        ref: RecordRef,
        payload: dict[str, Any],
        *,
        expected_version: int | None = None,
        privacy_class: str = "personal",
        connection: sqlite3.Connection | None = None,
    ) -> int:
        if connection is None:
            with self.transaction() as owned:
                return self.put_record(
                    ref,
                    payload,
                    expected_version=expected_version,
                    privacy_class=privacy_class,
                    connection=owned,
                )

        row = connection.execute(
            """SELECT version, created_at FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (ref.module_id, ref.entity_type, ref.record_id),
        ).fetchone()
        current_version = int(row["version"]) if row else 0
        if expected_version is not None and current_version != expected_version:
            raise ConcurrencyError(
                f"Expected {ref.record_id} version {expected_version}, found {current_version}."
            )
        next_version = current_version + 1
        now = utc_now_iso()
        created_at = str(row["created_at"]) if row else now
        connection.execute(
            """
            INSERT INTO records (
                module_id, entity_type, record_id, version, payload_json,
                privacy_class, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(module_id, entity_type, record_id) DO UPDATE SET
                version=excluded.version,
                payload_json=excluded.payload_json,
                privacy_class=excluded.privacy_class,
                updated_at=excluded.updated_at
            """,
            (
                ref.module_id,
                ref.entity_type,
                ref.record_id,
                next_version,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                privacy_class,
                created_at,
                now,
            ),
        )
        return next_version

    def get_record(self, ref: RecordRef) -> dict[str, Any] | None:
        self.initialize()
        with closing(self.connect()) as connection:
            row = connection.execute(
                """SELECT version, payload_json, privacy_class, created_at, updated_at
                   FROM records WHERE module_id=? AND entity_type=? AND record_id=?""",
                (ref.module_id, ref.entity_type, ref.record_id),
            ).fetchone()
        if row is None:
            return None
        return {
            **json.loads(row["payload_json"]),
            "_version": int(row["version"]),
            "_privacy_class": str(row["privacy_class"]),
        }

    def list_records(self, module_id: str, entity_type: str) -> list[dict[str, Any]]:
        self.initialize()
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """SELECT record_id, version, payload_json, privacy_class
                   FROM records WHERE module_id=? AND entity_type=? ORDER BY updated_at DESC""",
                (module_id, entity_type),
            ).fetchall()
        return [
            {
                **json.loads(row["payload_json"]),
                "_version": int(row["version"]),
                "_privacy_class": str(row["privacy_class"]),
            }
            for row in rows
        ]

    def append_event(self, event: DomainEvent, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            INSERT INTO domain_events (
                event_id, module_id, event_type, entity_type, record_id, payload_json, occurred_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.module_id,
                event.event_type,
                event.record.entity_type,
                event.record.record_id,
                json.dumps(dict(event.payload), ensure_ascii=False, sort_keys=True),
                event.occurred_at,
            ),
        )

    def add_relationship(self, relationship: Relationship) -> None:
        self.initialize()
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO relationships (
                    relationship_id, source_module, source_type, source_id, relation_type,
                    target_module, target_type, target_id, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relationship.relationship_id,
                    relationship.source.module_id,
                    relationship.source.entity_type,
                    relationship.source.record_id,
                    relationship.relation_type,
                    relationship.target.module_id,
                    relationship.target.entity_type,
                    relationship.target.record_id,
                    relationship.created_by,
                    relationship.created_at,
                ),
            )

    def count(self, table: str) -> int:
        allowed = {
            "records",
            "domain_events",
            "audit_entries",
            "relationships",
            "module_states",
            "documents",
            "migration_runs",
            "paired_devices",
        }
        if table not in allowed:
            raise ValueError("Unknown Core table.")
        self.initialize()
        with closing(self.connect()) as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])
