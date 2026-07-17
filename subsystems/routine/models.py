from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


ROUTINE_STATUSES = ("DRAFT", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED")
EXECUTION_STATUSES = ("PENDING", "COMPLETED", "FAILED", "SKIPPED")
FREQUENCIES = ("DAILY", "WEEKLY", "MONTHLY", "INTERVAL")


def validate_timestamp(value: str | None, field_name: str) -> None:
    if value:
        try: datetime.fromisoformat(value)
        except ValueError as exc: raise ValueError(f"{field_name} must be an ISO timestamp.") from exc


@dataclass
class RoutineRecord:
    routine_id: str
    name: str
    description: str = ""
    category: str = "General"
    frequency: str = "DAILY"
    schedule_rule: str = ""
    priority: int = 3
    status: str = "DRAFT"
    start_date: str = ""
    end_date: str = ""
    last_executed_at: str | None = None
    next_due_at: str | None = None
    completion_count: int = 0
    failure_count: int = 0
    streak: int = 0
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.routine_id.strip() or not self.name.strip(): raise ValueError("routine_id and name are required.")
        if self.status not in ROUTINE_STATUSES: raise ValueError(f"Unsupported Routine status: {self.status}")
        if self.frequency not in FREQUENCIES: raise ValueError(f"Unsupported frequency: {self.frequency}")
        if not 1 <= int(self.priority) <= 5: raise ValueError("priority must be between 1 and 5.")
        for field_name in ("last_executed_at", "next_due_at", "created_at", "updated_at"): validate_timestamp(getattr(self, field_name), field_name)
        if not isinstance(self.metadata, dict): raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]: self.validate(); return asdict(self)


@dataclass
class RoutineExecutionRecord:
    execution_id: str
    routine_id: str
    scheduled_at: str
    executed_at: str | None = None
    result: str = ""
    status: str = "PENDING"
    note: str = ""
    duration: int = 0
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.execution_id or not self.routine_id: raise ValueError("execution_id and routine_id are required.")
        if self.status not in EXECUTION_STATUSES: raise ValueError(f"Unsupported execution status: {self.status}")
        validate_timestamp(self.scheduled_at, "scheduled_at"); validate_timestamp(self.executed_at, "executed_at")
        if int(self.duration) < 0: raise ValueError("duration cannot be negative.")
        if not isinstance(self.metadata, dict): raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]: self.validate(); return asdict(self)
