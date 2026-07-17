from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.database.engines.repository import RecordRepository
from subsystems.foundation.engines.time import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


class PersonalGrowthRepository(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(database_path, component_id="SUB-PERSONAL-GROWTH", display_name="Personal Growth Subsystem", foundation=foundation)
        self.records = RecordRepository(self.connections)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connections.transaction() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS personal_growth_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS records(
                    module_id TEXT NOT NULL,entity_type TEXT NOT NULL,record_id TEXT NOT NULL,version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,privacy_class TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',owner TEXT NOT NULL DEFAULT 'owner',source TEXT NOT NULL DEFAULT 'living-os',
                    archived_at TEXT,correlation_id TEXT NOT NULL DEFAULT '',PRIMARY KEY(module_id,entity_type,record_id));
                CREATE INDEX IF NOT EXISTS ix_records_status ON records(module_id,entity_type,status,updated_at);
                CREATE TABLE IF NOT EXISTS personal_growth_migrations(migration_id TEXT PRIMARY KEY,schema_version INTEGER NOT NULL,status TEXT NOT NULL,started_at TEXT NOT NULL,completed_at TEXT NOT NULL,error TEXT NOT NULL DEFAULT '');
            """)
            now = utc_now_iso()
            connection.execute("INSERT INTO personal_growth_meta VALUES('schema_version','1',?) ON CONFLICT(key) DO UPDATE SET value='1',updated_at=excluded.updated_at", (now,))
            connection.execute("INSERT OR IGNORE INTO personal_growth_migrations VALUES(?,?,?,?,?,?)", ("personal-growth-schema-v1", 1, "APPLIED", now, now, ""))
        self.register_contract(schema_version=1, migration_id="personal-growth-schema-v1", integration_mode="record-repository")

    @staticmethod
    def _domain(record: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in record.items() if key != "id" and not key.startswith("_")}

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            record = self.records.create(self.component_id, "growth_goal", payload["goal_id"], payload, owner="personal-growth", source="personal-growth-subsystem", privacy_class="sensitive", connection=connection)
        return self._domain(record)

    def get(self, goal_id: str) -> dict[str, Any] | None:
        if not self.initialized:
            return None
        record = self.records.read(self.component_id, "growth_goal", goal_id)
        return self._domain(record) if record else None

    def update(self, goal_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.records.read(self.component_id, "growth_goal", goal_id) if self.initialized else None
        if current is None:
            raise KeyError(goal_id)
        with self.transaction() as connection:
            record = self.records.update(self.component_id, "growth_goal", goal_id, payload, expected_version=int(current["_version"]), source="personal-growth-subsystem", connection=connection)
        return self._domain(record)

    def list(self, *, include_archived: bool = False, status: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        items = [self._domain(item) for item in self.records.list(self.component_id, "growth_goal", include_archived=include_archived, limit=limit)]
        if not include_archived:
            items = [item for item in items if item["status"] != "ARCHIVED"]
        if status:
            items = [item for item in items if item["status"] == status]
        return sorted(items, key=lambda item: (-item["priority"], item["target_date"] or "9999"))

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "READY", "initialized": False, "schema_version": 1}
        rows = self.query_rows("PRAGMA integrity_check")
        ok = bool(rows) and next(iter(rows[0].values())) == "ok"
        return {"status": "HEALTHY" if ok else "DEGRADED", "initialized": True, "schema_version": 1, "integrity": "ok" if ok else "failed"}
