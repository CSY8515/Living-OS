from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.collaboration.models import CollaborationItem
from subsystems.collaboration.repository import CollaborationRepository
from subsystems.foundation.engines.time import utc_now_iso


class CollaborationSubsystem:
    subsystem_id = "SUB-COLLABORATION"; VERSION = "1.0.0"
    def __init__(self, root: Path, database_path: Path | None = None, database_foundation: Any = None) -> None:
        path = Path(database_path) if database_path else Path(root) / "data" / "collaboration" / "collaboration.sqlite3"
        self.repository = CollaborationRepository(path, database_foundation)
        self.repository.register_contract(schema_version=1, migration_id="collaboration-schema-v1", integration_mode="record-repository")
        self.database_foundation = database_foundation
    def create(self, title: str, partner: str, **fields: Any) -> dict[str, Any]:
        now = utc_now_iso(); record = CollaborationItem(collaboration_id=str(fields.pop("collaboration_id", "") or uuid4()), title=title, partner=partner, created_at=now, updated_at=now, **fields)
        result = self.repository.create(record.to_dict()); self._execution("create", result["collaboration_id"]); return result
    def get(self, item_id: str) -> dict[str, Any] | None: return self.repository.get(item_id)
    def update(self, item_id: str, **changes: Any) -> dict[str, Any]:
        current = self.get(item_id)
        if current is None: raise KeyError(item_id)
        payload = {**current, **changes, "collaboration_id": item_id, "updated_at": utc_now_iso()}; CollaborationItem(**payload).validate()
        result = self.repository.update(item_id, payload); self._execution("update", item_id); return result
    def archive(self, item_id: str) -> dict[str, Any]: return self.update(item_id, status="ARCHIVED")
    def list(self, **filters: Any) -> list[dict[str, Any]]: return self.repository.list(**filters)
    def health(self) -> dict[str, Any]: return self.repository.health()
    def management_summary(self) -> dict[str, Any]:
        records = self.list(include_archived=True); today = date.today().isoformat(); active = [r for r in records if r["status"] in {"PLANNED", "ACTIVE", "BLOCKED"}]
        return {"total": len(records), "active": sum(r["status"] == "ACTIVE" for r in records), "blocked": sum(r["status"] == "BLOCKED" for r in records), "completed": sum(r["status"] == "COMPLETED" for r in records), "due": sum(bool(r["status"] in {"PLANNED", "ACTIVE", "BLOCKED"} and r["due_date"] and r["due_date"] <= today) for r in records), "by_status": dict(Counter(r["status"] for r in records)), "by_partner": dict(Counter(r["partner"] for r in records)), "priorities": active[:8], "health": self.health(), "registry_registered": self._registered()}
    def _registered(self) -> bool: return any(i.get("component_id") == self.subsystem_id for i in (self.database_foundation.registered_components() if self.database_foundation else []))
    def _execution(self, action: str, target: str) -> None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version() >= self.database_foundation.expected_schema_version:
                self.database_foundation.executions.record(self.subsystem_id, action, target, "COMPLETED", actor="collaboration", result={"target_id": target, "version": "v2.0"})
        except Exception: return
