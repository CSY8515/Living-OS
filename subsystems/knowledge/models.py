from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


KNOWLEDGE_STATUSES = ("NEW", "REVIEW", "ORGANIZED", "ACTIVE", "ARCHIVED")


@dataclass
class KnowledgeRecord:
    record_id: str
    title: str
    content: str
    summary: str = ""
    category: str = "General"
    tags: list[str] = field(default_factory=list)
    source_type: str = "manual"
    source_reference: str = ""
    status: str = "NEW"
    importance: int = 3
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.record_id.strip():
            raise ValueError("record_id is required.")
        if not self.title.strip():
            raise ValueError("title is required.")
        if self.status not in KNOWLEDGE_STATUSES:
            raise ValueError(f"Unsupported Knowledge status: {self.status}")
        if not 1 <= int(self.importance) <= 5:
            raise ValueError("importance must be between 1 and 5.")
        if not isinstance(self.tags, list) or not all(isinstance(tag, str) for tag in self.tags):
            raise ValueError("tags must be a list of strings.")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object.")
        for field_name in ("created_at", "updated_at", "archived_at"):
            value = getattr(self, field_name)
            if value:
                try:
                    datetime.fromisoformat(value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO timestamp.") from exc

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
