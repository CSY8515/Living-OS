from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


COLLABORATION_STATUSES = ("PLANNED", "ACTIVE", "BLOCKED", "COMPLETED", "ARCHIVED")


@dataclass
class CollaborationItem:
    collaboration_id: str
    title: str
    partner: str
    objective: str = ""
    status: str = "PLANNED"
    priority: int = 3
    due_date: str = ""
    next_action: str = ""
    owner_role: str = "OWNER"
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.collaboration_id.strip() or not self.title.strip() or not self.partner.strip():
            raise ValueError("collaboration_id, title, and partner are required.")
        if self.status not in COLLABORATION_STATUSES or not 1 <= int(self.priority) <= 5:
            raise ValueError("Unsupported status or priority.")
        if self.due_date: date.fromisoformat(self.due_date)
        for value in (self.created_at, self.updated_at):
            if value: datetime.fromisoformat(value)
        if not isinstance(self.metadata, dict): raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]: self.validate(); return asdict(self)
