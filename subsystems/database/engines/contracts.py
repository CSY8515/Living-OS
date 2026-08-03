from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Protocol


OPERATIONAL_DATA_REGISTRY: dict[str, dict[str, str]] = {
    "SUCCESS": {"severity": "INFO", "resolution_status": "RESOLVED"},
    "FAILURE": {"severity": "HIGH", "resolution_status": "OPEN"},
    "ERROR": {"severity": "HIGH", "resolution_status": "OPEN"},
    "WARNING": {"severity": "MEDIUM", "resolution_status": "OPEN"},
    "INCIDENT": {"severity": "CRITICAL", "resolution_status": "OPEN"},
    "RECOVERY": {"severity": "MEDIUM", "resolution_status": "RECOVERED"},
    "ROLLBACK": {"severity": "HIGH", "resolution_status": "ROLLED_BACK"},
    "VALIDATION_FAILURE": {"severity": "MEDIUM", "resolution_status": "OPEN"},
    "EXECUTION_FAILURE": {"severity": "HIGH", "resolution_status": "OPEN"},
    "INVALID_DATA": {"severity": "MEDIUM", "resolution_status": "OPEN"},
    "REJECTED_DECISION": {"severity": "MEDIUM", "resolution_status": "REJECTED"},
    "UNRESOLVED_ISSUE": {"severity": "HIGH", "resolution_status": "OPEN"},
}

OPERATIONAL_SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
OPERATIONAL_RESOLUTION_STATUSES = (
    "OPEN",
    "RESOLVED",
    "RECOVERED",
    "ROLLED_BACK",
    "REJECTED",
)


@dataclass(frozen=True)
class OperationalDataRecord:
    """Versioned, non-destructive operational data contract.

    The record contains safe operational context only. Source business payloads,
    secrets, and credentials do not belong in this contract.
    """

    operational_id: str
    data_type: str
    source_subsystem: str
    title: str
    summary: str
    occurred_at: str
    severity: str = ""
    resolution_status: str = ""
    related_execution_id: str = ""
    recovery_result: str = ""
    validation_result: str = ""
    recoverable: bool | None = None
    retryable: bool | None = None
    fingerprint: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.operational_id.strip():
            raise ValueError("operational_id is required.")
        if self.data_type not in OPERATIONAL_DATA_REGISTRY:
            raise ValueError("Unknown operational data type.")
        if not self.source_subsystem.strip():
            raise ValueError("source_subsystem is required.")
        if not self.title.strip() or not self.summary.strip():
            raise ValueError("Operational title and summary are required.")
        if not self.occurred_at.strip():
            raise ValueError("occurred_at is required.")
        severity = self.severity or OPERATIONAL_DATA_REGISTRY[self.data_type]["severity"]
        resolution = (
            self.resolution_status
            or OPERATIONAL_DATA_REGISTRY[self.data_type]["resolution_status"]
        )
        if severity not in OPERATIONAL_SEVERITIES:
            raise ValueError("Unknown operational severity.")
        if resolution not in OPERATIONAL_RESOLUTION_STATUSES:
            raise ValueError("Unknown operational resolution status.")
        if not isinstance(self.metadata, Mapping):
            raise ValueError("Operational metadata must be an object.")
        if self.recoverable is not None and not isinstance(self.recoverable, bool):
            raise ValueError("recoverable must be a boolean or null.")
        if self.retryable is not None and not isinstance(self.retryable, bool):
            raise ValueError("retryable must be a boolean or null.")

    def stable_fingerprint(self) -> str:
        if self.fingerprint.strip():
            return self.fingerprint.strip()
        payload = {
            "data_type": self.data_type,
            "source_subsystem": self.source_subsystem,
            "title": self.title,
            "summary": self.summary,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        defaults = OPERATIONAL_DATA_REGISTRY[self.data_type]
        return {
            "operational_id": self.operational_id,
            "data_type": self.data_type,
            "source_subsystem": self.source_subsystem,
            "title": self.title,
            "summary": self.summary,
            "occurred_at": self.occurred_at,
            "severity": self.severity or defaults["severity"],
            "resolution_status": (
                self.resolution_status or defaults["resolution_status"]
            ),
            "related_execution_id": self.related_execution_id,
            "recovery_result": self.recovery_result,
            "validation_result": self.validation_result,
            "recoverable": self.recoverable,
            "retryable": self.retryable,
            "fingerprint": self.stable_fingerprint(),
            "metadata": dict(self.metadata),
            "contract_version": 1,
            "retention_policy": "PRESERVE",
        }


@dataclass(frozen=True)
class IntegrityResult:
    status: str
    integrity: str
    foreign_key_violations: int
    missing_tables: tuple[str, ...]
    missing_indexes: tuple[str, ...]
    schema_version: int

    @property
    def healthy(self) -> bool:
        return (
            self.integrity == "ok"
            and self.foreign_key_violations == 0
            and not self.missing_tables
            and not self.missing_indexes
        )


@dataclass(frozen=True)
class RestoreCandidate:
    path: Path
    valid: bool
    schema_version: int | None
    created_at: str
    error: str = ""


class DatabaseControlInterface(Protocol):
    database_path: Path
    expected_schema_version: int

    def current_schema_version(self) -> int: ...
    def pending_migrations(self) -> list[dict[str, Any]]: ...
    def applied_migrations(self) -> list[dict[str, Any]]: ...
    def failed_migrations(self) -> list[dict[str, Any]]: ...
    def apply_migrations(self, *, actor: str, correlation_id: str = "") -> list[dict[str, Any]]: ...
    def integrity_check(self, *, record: bool = True, actor: str = "system") -> IntegrityResult: ...
    def schema_registry(self) -> dict[str, Any]: ...
    def create_backup(self, *, actor: str, correlation_id: str = "") -> Path: ...
    def list_backups(self) -> list[dict[str, Any]]: ...
    def validate_restore(self, archive_path: Path) -> RestoreCandidate: ...
    def restore(self, archive_path: Path, *, actor: str, correlation_id: str = "") -> dict[str, Any]: ...
    def restore_history(self) -> list[dict[str, Any]]: ...
    def execution_records(self, limit: int = 50) -> list[dict[str, Any]]: ...
    def record_operational_data(
        self, record: OperationalDataRecord, *, actor: str = "system"
    ) -> dict[str, Any]: ...
    def operational_data(
        self, *, include_archived: bool = True, limit: int = 1000
    ) -> list[dict[str, Any]]: ...
    def operational_data_registry(self) -> dict[str, Any]: ...
    def registered_components(self) -> list[dict[str, Any]]: ...
    def component_status(self) -> list[dict[str, Any]]: ...
    def initialize_component(self, component_id: str, *, actor: str) -> dict[str, Any]: ...
    def create_component_backup(self, component_id: str, *, actor: str) -> Path: ...
    def component_backups(self, component_id: str | None = None) -> list[dict[str, Any]]: ...
    def restore_component_backup(
        self, component_id: str, backup_path: Path, *, actor: str
    ) -> dict[str, Any]: ...
    def record_execution(
        self,
        subsystem: str,
        action: str,
        *,
        actor: str,
        result: dict[str, Any],
    ) -> str: ...
