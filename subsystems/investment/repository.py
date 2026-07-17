from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.database.engines.repository import RecordRepository
from subsystems.foundation.engines.time import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1
ENTITY_TYPE = "investment"


class InvestmentRepository(ComponentDatabaseAdapter):
    """Investment data owner backed by the common versioned RecordRepository."""

    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(database_path, component_id="SUB-INVESTMENT", display_name="Investment Subsystem", foundation=foundation)
        self.records = RecordRepository(self.connections)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connections.transaction() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS investment_meta (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS records (
                    module_id TEXT NOT NULL, entity_type TEXT NOT NULL, record_id TEXT NOT NULL,
                    version INTEGER NOT NULL, payload_json TEXT NOT NULL, privacy_class TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'ACTIVE',
                    owner TEXT NOT NULL DEFAULT 'owner', source TEXT NOT NULL DEFAULT 'living-os',
                    archived_at TEXT, correlation_id TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(module_id, entity_type, record_id)
                );
                CREATE INDEX IF NOT EXISTS ix_records_status ON records(module_id,entity_type,status,updated_at);
                CREATE TABLE IF NOT EXISTS investment_migrations (
                    migration_id TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, status TEXT NOT NULL,
                    started_at TEXT NOT NULL, completed_at TEXT NOT NULL, error TEXT NOT NULL DEFAULT ''
                );
            """)
            now = utc_now_iso()
            connection.execute(
                "INSERT INTO investment_meta(key,value,updated_at) VALUES('schema_version',?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at",
                (str(SCHEMA_VERSION), now),
            )
            connection.execute(
                "INSERT OR IGNORE INTO investment_migrations VALUES(?,?,?,?,?,?)",
                ("investment-schema-v1", SCHEMA_VERSION, "APPLIED", now, now, ""),
            )
        self.register_contract(
            schema_version=SCHEMA_VERSION, migration_id="investment-schema-v1", integration_mode="record-repository"
        )

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            record = self.records.create(
                self.component_id, ENTITY_TYPE, str(payload["investment_id"]), payload,
                owner="investment", source="investment-subsystem", privacy_class="sensitive",
                connection=connection,
            )
        return self._domain(record)

    def get(self, investment_id: str) -> dict[str, Any] | None:
        if not self.initialized:
            return None
        record = self.records.read(self.component_id, ENTITY_TYPE, investment_id)
        return self._domain(record) if record else None

    def update(self, investment_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.initialized:
            raise KeyError(investment_id)
        current = self.records.read(self.component_id, ENTITY_TYPE, investment_id)
        if current is None:
            raise KeyError(investment_id)
        with self.transaction() as connection:
            record = self.records.update(
                self.component_id, ENTITY_TYPE, investment_id, payload,
                expected_version=int(current["_version"]), source="investment-subsystem", connection=connection,
            )
        return self._domain(record)

    def list(self, *, status: str | None = None, asset_type: str | None = None,
             include_archived: bool = False, limit: int = 200) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        items = [self._domain(item) for item in self.records.list(
            self.component_id, ENTITY_TYPE, include_archived=include_archived, limit=limit
        )]
        if not include_archived:
            items = [item for item in items if item["status"] != "ARCHIVED"]
        if status:
            items = [item for item in items if item["status"] == status]
        if asset_type:
            items = [item for item in items if item["asset_type"] == asset_type]
        return items

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "READY", "initialized": False, "schema_version": SCHEMA_VERSION}
        rows = self.query_rows("PRAGMA integrity_check")
        ok = bool(rows) and next(iter(rows[0].values())) == "ok"
        return {"status": "HEALTHY" if ok else "DEGRADED", "initialized": True,
                "schema_version": SCHEMA_VERSION, "integrity": "ok" if ok else "failed"}

    @staticmethod
    def _domain(record: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key != "id" and not key.startswith("_")}
