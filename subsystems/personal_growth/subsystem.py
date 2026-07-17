from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso
from subsystems.personal_growth.models import GrowthGoal
from subsystems.personal_growth.repository import PersonalGrowthRepository


class PersonalGrowthSubsystem:
    subsystem_id = "SUB-PERSONAL-GROWTH"
    VERSION = "1.0.0"

    def __init__(self, root: Path, database_path: Path | None = None, database_foundation: Any = None) -> None:
        path = Path(database_path) if database_path else Path(root) / "data" / "personal_growth" / "personal_growth.sqlite3"
        self.repository = PersonalGrowthRepository(path, database_foundation)
        self.repository.register_contract(schema_version=1, migration_id="personal-growth-schema-v1", integration_mode="record-repository")
        self.database_foundation = database_foundation

    def create(self, title: str, **fields: Any) -> dict[str, Any]:
        now = utc_now_iso()
        record = GrowthGoal(goal_id=str(fields.pop("goal_id", "") or uuid4()), title=title, created_at=now, updated_at=now, **fields)
        result = self.repository.create(record.to_dict()); self._execution("create", result["goal_id"]); return result

    def get(self, goal_id: str) -> dict[str, Any] | None:
        return self.repository.get(goal_id)

    def update(self, goal_id: str, **changes: Any) -> dict[str, Any]:
        current = self.get(goal_id)
        if current is None: raise KeyError(goal_id)
        payload = {**current, **changes, "goal_id": goal_id, "updated_at": utc_now_iso()}
        GrowthGoal(**payload).validate()
        result = self.repository.update(goal_id, payload); self._execution("update", goal_id); return result

    def archive(self, goal_id: str) -> dict[str, Any]: return self.update(goal_id, status="ARCHIVED")
    def list(self, **filters: Any) -> list[dict[str, Any]]: return self.repository.list(**filters)
    def health(self) -> dict[str, Any]: return self.repository.health()

    def management_summary(self) -> dict[str, Any]:
        records = self.list(include_archived=True)
        today = date.today().isoformat()
        active = [r for r in records if r["status"] == "ACTIVE"]
        return {"total": len(records), "active": len(active), "completed": sum(r["status"] == "COMPLETED" for r in records),
                "overdue": sum(bool(r["status"] == "ACTIVE" and r["target_date"] and r["target_date"] < today) for r in records),
                "average_progress": round(sum(r["progress"] for r in active) / len(active)) if active else 0,
                "by_status": dict(Counter(r["status"] for r in records)), "by_area": dict(Counter(r["area"] for r in records)),
                "priorities": active[:8], "health": self.health(), "registry_registered": self._registered()}

    def _registered(self) -> bool:
        return any(item.get("component_id") == self.subsystem_id for item in (self.database_foundation.registered_components() if self.database_foundation else []))

    def _execution(self, action: str, target: str) -> None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version() >= self.database_foundation.expected_schema_version:
                self.database_foundation.executions.record(self.subsystem_id, action, target, "COMPLETED", actor="personal-growth", result={"target_id": target, "version": "v2.0"})
        except Exception:
            return
