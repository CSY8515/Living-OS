from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


GROWTH_STATUSES = ("PLANNED", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED")
GROWTH_AREAS = ("MIND", "BODY", "CAREER", "RELATIONSHIPS", "CREATIVITY", "FINANCE", "OTHER")


@dataclass
class GrowthGoal:
    goal_id: str
    title: str
    area: str = "OTHER"
    purpose: str = ""
    status: str = "PLANNED"
    priority: int = 3
    progress: int = 0
    target_date: str = ""
    next_action: str = ""
    last_reflection: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.goal_id.strip() or not self.title.strip():
            raise ValueError("goal_id and title are required.")
        if self.area not in GROWTH_AREAS or self.status not in GROWTH_STATUSES:
            raise ValueError("Unsupported growth area or status.")
        if not 1 <= int(self.priority) <= 5 or not 0 <= int(self.progress) <= 100:
            raise ValueError("priority must be 1-5 and progress must be 0-100.")
        if self.target_date:
            date.fromisoformat(self.target_date)
        for value in (self.created_at, self.updated_at):
            if value:
                datetime.fromisoformat(value)
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
