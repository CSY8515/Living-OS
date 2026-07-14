from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.backup import BackupService
from core.commands import CommandBus
from core.contracts import ModuleManifest
from core.documents import DocumentService
from core.migration import V1MigrationService
from core.module_runtime import ModuleRuntime
from core.relationships import RelationshipService
from core.security import OwnerSecurityService
from core.schemas import SchemaRegistry
from core.storage import HubStore


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
