from __future__ import annotations

from pathlib import Path
from typing import Iterable

from subsystems.foundation.engines.commands import CommandBus
from subsystems.foundation.engines.contracts import ModuleManifest
from subsystems.foundation.engines.documents import DocumentService
from subsystems.foundation.engines.migration import V1MigrationService
from subsystems.foundation.engines.module_runtime import ModuleRuntime
from subsystems.foundation.engines.relationships import RelationshipService
from subsystems.foundation.engines.runtime_config import RuntimeStorageConfig
from subsystems.foundation.engines.security import OwnerSecurityService
from subsystems.foundation.engines.schemas import SchemaRegistry
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.timeline import TimelineService
from subsystems.database import DatabaseSubsystem
from subsystems.database_management import DatabaseManagementSubsystem


class LivingHub:
    """Composition root for the single-owner Living OS Hub."""

    def __init__(
        self,
        repository_root: Path,
        runtime_config: RuntimeStorageConfig | None = None,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.runtime_config = runtime_config or RuntimeStorageConfig.from_environment(
            self.repository_root
        )
        self.data_root = self.runtime_config.data_root / "hub"
        self.store = HubStore(self.data_root / "living_os.sqlite3")
        self.database = DatabaseSubsystem(
            self.store.database_path,
            self.runtime_config.backup_root / "database",
            self.repository_root,
            store=self.store,
            allowed_storage_roots=(self.runtime_config.data_root,),
        )
        self.database_management = DatabaseManagementSubsystem(self.database)
        self.timeline = TimelineService(self.database.connections, self.database.executions)
        self.schemas = SchemaRegistry()
        self.commands = CommandBus(self.store)
        self.relationships = RelationshipService(self.store)
        self.security = OwnerSecurityService(self.store)
        self.modules = ModuleRuntime(self.store)
        self.documents = DocumentService(self.store, self.data_root / "documents")
        self.backups = self.database.backups
        self.migration = V1MigrationService(self.store, self.repository_root, self.backups)
        self._bootstrapped = False

    def bootstrap(self, manifests: Iterable[ModuleManifest] = ()) -> None:
        if self._bootstrapped:
            return
        self.runtime_config.prepare()
        # Foundation schema migrations are idempotent and activate the Execution
        # Database. Legacy business-data migration remains an explicit operation.
        self.database.initialize(apply_migrations=True, actor="living-os-bootstrap")
        self.modules.register_all(manifests)
        self._bootstrapped = True

    def component_database_path(self, component: str) -> Path:
        return self.runtime_config.component_database_path(component)

    @property
    def v1_migration_complete(self) -> bool:
        return self.store.get_meta("v1_migration_complete", "false") == "true"
