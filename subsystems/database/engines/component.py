from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator

from subsystems.database.engines.connection import SQLiteConnectionLayer

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


ALLOWED_COMPONENT_LAYERS = {
    "OS System",
    "Capability",
    "Module",
    "Subsystem",
    "Engine Group",
    "Engine",
    "Function",
}


@dataclass(frozen=True)
class DatabaseIntegrationContract:
    """Registration contract shared by every data-owning architecture component."""

    component_id: str
    display_name: str
    layer: str
    owner: str
    database_path: str
    schema_version: int
    migration_id: str
    integration_mode: str = "compatibility-adapter"
    execution_enabled: bool = True
    backup_enabled: bool = True
    restore_enabled: bool = True
    integrity_enabled: bool = True
    status: str = "ACTIVE"

    def validate(self) -> None:
        if not self.component_id.strip():
            raise ValueError("component_id is required.")
        if self.layer not in ALLOWED_COMPONENT_LAYERS:
            raise ValueError(f"Unsupported architecture layer: {self.layer}")
        if not self.owner.strip():
            raise ValueError("Data owner is required.")
        if self.schema_version < 1:
            raise ValueError("schema_version must be at least 1.")
        if self.integration_mode not in {"record-repository", "compatibility-adapter"}:
            raise ValueError("Unsupported database integration mode.")
        if not self.migration_id.strip():
            raise ValueError("migration_id is required.")

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


class ComponentDatabaseAdapter:
    """Common SQLite adapter for components that retain domain-owned schemas.

    The adapter owns connections and transaction boundaries. Domain engines own
    their tables and business rules. Registration is persisted through the
    canonical RecordRepository when a Database Foundation is supplied.
    """

    def __init__(
        self,
        database_path: Path,
        *,
        component_id: str,
        display_name: str,
        foundation: DatabaseSubsystem | None = None,
        layer: str = "Subsystem",
        owner: str | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self.component_id = component_id
        self.display_name = display_name
        self.layer = layer
        self.owner = owner or component_id
        self.foundation = foundation
        self.connections = SQLiteConnectionLayer(self.database_path)
        if foundation is not None:
            foundation.attach_component_adapter(self)

    @property
    def initialized(self) -> bool:
        return self.database_path.is_file()

    def _connect(self) -> sqlite3.Connection:
        """Compatibility hook; all SQLite access still goes through the common layer."""
        return self.connections.connect()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        if not self.initialized:
            self.initialize()  # type: ignore[attr-defined]
        try:
            with self.connections.transaction() as connection:
                yield connection
        except Exception as exc:
            self._record_execution("transaction", "FAILED", error=exc)
            raise
        else:
            self._record_execution("transaction", "COMPLETED", result={"committed": True})

    def query_rows(
        self, sql: str, parameters: tuple[Any, ...] = ()
    ) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        with self.connections.connection(read_only=True) as connection:
            return [dict(row) for row in connection.execute(sql, parameters).fetchall()]

    def register_contract(
        self,
        *,
        schema_version: int,
        migration_id: str,
        integration_mode: str = "compatibility-adapter",
    ) -> dict[str, Any] | None:
        contract = DatabaseIntegrationContract(
            component_id=self.component_id,
            display_name=self.display_name,
            layer=self.layer,
            owner=self.owner,
            database_path=str(self.database_path.resolve()),
            schema_version=schema_version,
            migration_id=migration_id,
            integration_mode=integration_mode,
        )
        if self.foundation is None:
            contract.validate()
            return None
        return self.foundation.register_component(contract, actor=self.component_id)

    def _record_execution(
        self,
        action: str,
        status: str,
        *,
        result: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        if self.foundation is None or self.foundation.current_schema_version() < 2:
            return
        self.foundation.executions.record(
            self.component_id,
            action,
            str(self.database_path),
            status,
            actor=self.component_id,
            result=result or {},
            error=error,
        )
