from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.foundation.engines.time import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1


class KnowledgeRepository(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(database_path, component_id="SUB-KNOWLEDGE", display_name="Knowledge Subsystem", foundation=foundation)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connections.transaction() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS knowledge_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS knowledge_records (
                    record_id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
                    summary TEXT NOT NULL, category TEXT NOT NULL, tags_json TEXT NOT NULL,
                    source_type TEXT NOT NULL, source_reference TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('NEW','REVIEW','ORGANIZED','ACTIVE','ARCHIVED')),
                    importance INTEGER NOT NULL CHECK(importance BETWEEN 1 AND 5),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, archived_at TEXT,
                    metadata_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_knowledge_status ON knowledge_records(status, updated_at);
                CREATE INDEX IF NOT EXISTS ix_knowledge_category ON knowledge_records(category, updated_at);
                CREATE TABLE IF NOT EXISTS knowledge_migrations (
                    migration_id TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, status TEXT NOT NULL,
                    started_at TEXT NOT NULL, completed_at TEXT NOT NULL, error TEXT NOT NULL DEFAULT ''
                );
            """)
            now = utc_now_iso()
            connection.execute("INSERT INTO knowledge_meta(key,value,updated_at) VALUES('schema_version',?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at", (str(SCHEMA_VERSION), now))
            connection.execute("INSERT OR IGNORE INTO knowledge_migrations VALUES(?,?,?,?,?,?)", ("knowledge-schema-v1", SCHEMA_VERSION, "APPLIED", now, now, ""))
        self.register_contract(schema_version=SCHEMA_VERSION, migration_id="knowledge-schema-v1")

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            connection.execute("""INSERT INTO knowledge_records(record_id,title,content,summary,category,tags_json,source_type,source_reference,status,importance,created_at,updated_at,archived_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", self._values(payload))
        return self.get(str(payload["record_id"])) or {}

    def get(self, record_id: str) -> dict[str, Any] | None:
        rows = self.query_rows("SELECT * FROM knowledge_records WHERE record_id=?", (record_id,))
        return self._decode(rows[0]) if rows else None

    def update(self, record_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            cursor = connection.execute("""UPDATE knowledge_records SET title=?,content=?,summary=?,category=?,tags_json=?,source_type=?,source_reference=?,status=?,importance=?,updated_at=?,archived_at=?,metadata_json=? WHERE record_id=?""", (*self._values(payload)[1:10], payload["updated_at"], payload.get("archived_at"), json.dumps(payload.get("metadata", {}), ensure_ascii=False, sort_keys=True), record_id))
            if cursor.rowcount != 1:
                raise KeyError(record_id)
        return self.get(record_id) or {}

    def list(self, *, status: str | None = None, category: str | None = None, include_archived: bool = False, limit: int = 200) -> list[dict[str, Any]]:
        clauses, params = [], []
        if not include_archived: clauses.append("status!='ARCHIVED'")
        if status: clauses.append("status=?"); params.append(status)
        if category: clauses.append("category=?"); params.append(category)
        sql = "SELECT * FROM knowledge_records" + (" WHERE " + " AND ".join(clauses) if clauses else "") + " ORDER BY updated_at DESC LIMIT ?"
        params.append(max(1, min(int(limit), 1000)))
        return [self._decode(row) for row in self.query_rows(sql, tuple(params))]

    def search(self, query: str, *, include_archived: bool = False) -> list[dict[str, Any]]:
        value = f"%{query.strip().lower()}%"
        if value == "%%": return self.list(include_archived=include_archived)
        sql = "SELECT * FROM knowledge_records WHERE (lower(title) LIKE ? OR lower(content) LIKE ? OR lower(summary) LIKE ? OR lower(tags_json) LIKE ?)"
        params: list[Any] = [value] * 4
        if not include_archived: sql += " AND status!='ARCHIVED'"
        sql += " ORDER BY importance DESC, updated_at DESC"
        return [self._decode(row) for row in self.query_rows(sql, tuple(params))]

    def health(self) -> dict[str, Any]:
        if not self.initialized: return {"status": "READY", "initialized": False, "schema_version": SCHEMA_VERSION}
        row = self.query_rows("PRAGMA integrity_check")
        ok = bool(row) and next(iter(row[0].values())) == "ok"
        return {"status": "HEALTHY" if ok else "DEGRADED", "initialized": True, "schema_version": SCHEMA_VERSION, "integrity": "ok" if ok else "failed"}

    @staticmethod
    def _values(payload: dict[str, Any]) -> tuple[Any, ...]:
        return (payload["record_id"], payload["title"], payload["content"], payload.get("summary", ""), payload.get("category", "General"), json.dumps(payload.get("tags", []), ensure_ascii=False), payload.get("source_type", "manual"), payload.get("source_reference", ""), payload.get("status", "NEW"), int(payload.get("importance", 3)), payload["created_at"], payload["updated_at"], payload.get("archived_at"), json.dumps(payload.get("metadata", {}), ensure_ascii=False, sort_keys=True))

    @staticmethod
    def _decode(row: dict[str, Any]) -> dict[str, Any]:
        payload = dict(row)
        payload["tags"] = json.loads(payload.pop("tags_json"))
        payload["metadata"] = json.loads(payload.pop("metadata_json"))
        return payload
