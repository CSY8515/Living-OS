from __future__ import annotations

from pathlib import Path
from typing import Iterable

from subsystems.foundation.engines.backup import BackupService
from subsystems.foundation.engines.commands import CommandBus
from subsystems.foundation.engines.contracts import ModuleManifest
from subsystems.foundation.engines.documents import DocumentService
from subsystems.foundation.engines.migration import V1MigrationService
from subsystems.foundation.engines.module_runtime import ModuleRuntime
from subsystems.foundation.engines.relationships import RelationshipService
from subsystems.foundation.engines.security import OwnerSecurityService
from subsystems.foundation.engines.schemas import SchemaRegistry
from subsystems.foundation.engines.storage import HubStore


class LivingHub:
    """Composition root for the single-owner Living OS Hub."""

    def __init__(self, repository_root: Path) -> None:
        self.repository_root = repository_root.resolve()
        self.data_root = self.repository_root / "data" / "hub"
        self.store = HubStore(self.data_root / "living_os.sqlite3")
        self.schemas = SchemaRegistry()
        self.commands = CommandBus(self.store)
        self.relationships = RelationshipService(self.store)
        self.security = OwnerSecurityService(self.store)
        self.modules = ModuleRuntime(self.store)
        self.documents = DocumentService(self.store, self.data_root / "documents")
        self.backups = BackupService(
            self.store.database_path,
            self.repository_root / "backups" / "v2",
            self.repository_root,
        )
        self.migration = V1MigrationService(self.store, self.repository_root, self.backups)
        self._bootstrapped = False

    def bootstrap(self, manifests: Iterable[ModuleManifest] = ()) -> None:
        if self._bootstrapped:
            return
        self.store.initialize()
        self.modules.register_all(manifests)
        self._bootstrapped = True

    @property
    def v1_migration_complete(self) -> bool:
        return self.store.get_meta("v1_migration_complete", "false") == "true"
