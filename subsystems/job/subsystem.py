from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso
from subsystems.job.models import JobRecord
from subsystems.job.repository import JobRepository


class JobSubsystem:
    subsystem_id = "SUB-JOB"
    VERSION = "1.0.0"

    def __init__(self, root: Path, database_path: Path | None = None, database_foundation: Any = None) -> None:
        path = Path(database_path) if database_path else Path(root) / "data" / "job" / "job.sqlite3"
        self.repository = JobRepository(path, database_foundation)
        self.repository.register_contract(
            schema_version=1, migration_id="job-schema-v1", integration_mode="record-repository"
        )
        self.database_foundation = database_foundation

    def create(self, company: str, title: str, **fields: Any) -> dict[str, Any]:
        now = utc_now_iso()
        record = JobRecord(
            job_id=str(fields.pop("job_id", "") or uuid4()), company=company, title=title,
            created_at=now, updated_at=now, **fields,
        )
        result = self.repository.create(record.to_dict())
        self._execution("create", result["job_id"])
        return result

    def get(self, job_id: str) -> dict[str, Any] | None:
        result = self.repository.get(job_id)
        self._execution("read", job_id)
        return result

    def update(self, job_id: str, **changes: Any) -> dict[str, Any]:
        current = self.repository.get(job_id)
        if current is None:
            raise KeyError(job_id)
        payload = {**current, **changes, "job_id": job_id, "updated_at": utc_now_iso()}
        JobRecord(**payload).validate()
        result = self.repository.update(job_id, payload)
        self._execution("update", job_id)
        return result

    def transition(self, job_id: str, status: str, **changes: Any) -> dict[str, Any]:
        result = self.update(job_id, status=status, **changes)
        self._execution("transition", job_id)
        return result

    def archive(self, job_id: str) -> dict[str, Any]:
        result = self.update(job_id, status="ARCHIVED")
        self._execution("archive", job_id)
        return result

    def list(self, **filters: Any) -> list[dict[str, Any]]:
        return self.repository.list(**filters)

    def search(self, query: str, **filters: Any) -> list[dict[str, Any]]:
        result = self.repository.search(query, **filters)
        self._execution("search", query)
        return result

    def health(self) -> dict[str, Any]:
        return self.repository.health()

    def management_summary(self) -> dict[str, Any]:
        records = self.list(include_archived=True, limit=1000)
        today = date.today().isoformat()
        actionable = {"SAVED", "APPLIED", "INTERVIEW", "OFFER"}
        due = [r for r in records if r["status"] in actionable and r["next_action_on"] and r["next_action_on"] <= today]
        executions = self._executions()
        return {
            "total": len(records), "active_pipeline": sum(r["status"] in actionable for r in records),
            "due_actions": len(due), "offers": sum(r["status"] == "OFFER" for r in records),
            "accepted": sum(r["status"] == "ACCEPTED" for r in records),
            "archived": sum(r["status"] == "ARCHIVED" for r in records),
            "by_status": dict(Counter(r["status"] for r in records)),
            "by_employment_type": dict(Counter(r["employment_type"] for r in records)),
            "upcoming_actions": sorted(
                [r for r in records if r["status"] in actionable and r["next_action_on"]],
                key=lambda r: r["next_action_on"],
            )[:10],
            "health": self.health(),
            "execution_success": sum(e["status"] == "COMPLETED" for e in executions),
            "execution_failure": sum(e["status"] == "FAILED" for e in executions),
            "registry_registered": any(e.get("component_id") == self.subsystem_id for e in
                                       (self.database_foundation.registered_components() if self.database_foundation else [])),
        }

    def _execution(self, action: str, target: str) -> None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version() >= self.database_foundation.expected_schema_version:
                self.database_foundation.executions.record(
                    self.subsystem_id, action, target, "COMPLETED", actor="job",
                    result={"target_id": target, "version": "v1.9"},
                )
        except Exception:
            return

    def _executions(self) -> list[dict[str, Any]]:
        records = self.database_foundation.execution_records(500) if self.database_foundation else []
        return [item for item in records if item.get("subsystem") == self.subsystem_id]
