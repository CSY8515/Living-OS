from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


JOB_STATUSES = ("SAVED", "APPLIED", "INTERVIEW", "OFFER", "ACCEPTED", "REJECTED", "WITHDRAWN", "ARCHIVED")
EMPLOYMENT_TYPES = ("FULL_TIME", "PART_TIME", "CONTRACT", "FREELANCE", "INTERNSHIP", "OTHER")


@dataclass
class JobRecord:
    job_id: str
    company: str
    title: str
    status: str = "SAVED"
    employment_type: str = "FULL_TIME"
    location: str = ""
    source: str = ""
    source_url: str = ""
    applied_on: str = ""
    next_action_on: str = ""
    salary_min: float = 0.0
    salary_max: float = 0.0
    currency: str = "KRW"
    contact_name: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.job_id.strip() or not self.company.strip() or not self.title.strip():
            raise ValueError("job_id, company, and title are required.")
        if self.status not in JOB_STATUSES:
            raise ValueError(f"Unsupported Job status: {self.status}")
        if self.employment_type not in EMPLOYMENT_TYPES:
            raise ValueError(f"Unsupported employment type: {self.employment_type}")
        if float(self.salary_min) < 0 or float(self.salary_max) < 0:
            raise ValueError("salary values cannot be negative.")
        if self.salary_max and self.salary_min > self.salary_max:
            raise ValueError("salary_min cannot exceed salary_max.")
        if not self.currency.strip():
            raise ValueError("currency is required.")
        for field_name in ("applied_on", "next_action_on"):
            value = getattr(self, field_name)
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO date.") from exc
        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)
            if value:
                try:
                    datetime.fromisoformat(value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO timestamp.") from exc
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
