from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


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
