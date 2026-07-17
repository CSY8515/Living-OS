from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso
from subsystems.knowledge.models import KnowledgeRecord
from subsystems.knowledge.repository import KnowledgeRepository


class KnowledgeSubsystem:
    subsystem_id = "SUB-KNOWLEDGE"
    VERSION = "1.0.0"

    def __init__(self, root: Path, database_path: Path | None = None, database_foundation: Any = None) -> None:
        path = Path(database_path) if database_path else Path(root) / "data" / "knowledge" / "knowledge.sqlite3"
        self.repository = KnowledgeRepository(path, database_foundation)
        self.repository.register_contract(schema_version=1, migration_id="knowledge-schema-v1")
        self.database_foundation = database_foundation

    def create(self, title: str, content: str, **fields: Any) -> dict[str, Any]:
        now = utc_now_iso(); record_id = str(fields.pop("record_id", "") or uuid4())
        record = KnowledgeRecord(record_id=record_id, title=title, content=content, created_at=now, updated_at=now, **fields)
        result = self.repository.create(record.to_dict())
        self._execution("create", record_id, "COMPLETED")
        return result

    def get(self, record_id: str) -> dict[str, Any] | None:
        result = self.repository.get(record_id); self._execution("read", record_id, "COMPLETED")
        return result

    def update(self, record_id: str, **changes: Any) -> dict[str, Any]:
        current = self.repository.get(record_id)
        if current is None: raise KeyError(record_id)
        payload = {**current, **changes, "record_id": record_id, "updated_at": utc_now_iso()}
        KnowledgeRecord(**payload).validate()
        result = self.repository.update(record_id, payload); self._execution("update", record_id, "COMPLETED")
        return result

    def archive(self, record_id: str) -> dict[str, Any]:
        result = self.update(record_id, status="ARCHIVED", archived_at=utc_now_iso()); self._execution("archive", record_id, "COMPLETED")
        return result

    def list(self, **filters: Any) -> list[dict[str, Any]]: return self.repository.list(**filters)
    def search(self, query: str, **filters: Any) -> list[dict[str, Any]]:
        result = self.repository.search(query, **filters); self._execution("search", query, "COMPLETED")
        return result
    def health(self) -> dict[str, Any]: return self.repository.health()

    def management_summary(self) -> dict[str, Any]:
        records = self.list(include_archived=True, limit=1000)
        executions = self._executions()
        return {"total": len(records), "by_status": dict(Counter(r["status"] for r in records)), "by_category": dict(Counter(r["category"] for r in records)), "recent_created": sorted(records, key=lambda r: r["created_at"], reverse=True)[:5], "recent_updated": sorted(records, key=lambda r: r["updated_at"], reverse=True)[:5], "archived": sum(r["status"] == "ARCHIVED" for r in records), "health": self.health(), "execution_success": sum(e["status"] == "COMPLETED" for e in executions), "execution_failure": sum(e["status"] == "FAILED" for e in executions), "registry_registered": any(e.get("component_id") == self.subsystem_id for e in (self.database_foundation.registered_components() if self.database_foundation else []))}

    def _execution(self, action: str, target: str, status: str) -> None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version() >= self.database_foundation.expected_schema_version:
                self.database_foundation.executions.record(self.subsystem_id, action, target, status, actor="knowledge", result={"target_id": target, "version": "v1.8"})
        except Exception:
            # Observability must never invalidate an already committed domain write.
            return
    def _executions(self) -> list[dict[str, Any]]:
        return [e for e in (self.database_foundation.execution_records(500) if self.database_foundation else []) if e.get("subsystem") == self.subsystem_id]
