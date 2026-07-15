from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso


@dataclass(frozen=True)
class RecordRef:
    module_id: str
    entity_type: str
    record_id: str


@dataclass(frozen=True)
class CommandEnvelope:
    module_id: str
    command_type: str
    payload: Mapping[str, Any]
    actor: str = "owner"
    source: str = "living-os-ui"
    reason: str = "explicit-user-action"
    expected_version: int | None = None
    command_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class DomainEvent:
    module_id: str
    event_type: str
    record: RecordRef
    payload: Mapping[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class Relationship:
    source: RecordRef
    relation_type: str
    target: RecordRef
    created_by: str = "owner"
    relationship_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class DocumentRef:
    document_id: str
    content_hash: str
    filename: str
    media_type: str
    size_bytes: int
    version: int
    privacy_class: str


@dataclass(frozen=True)
class ModuleManifest:
    module_id: str
    name: str
    version: str
    core_compatibility: str
    description: str
    status: str = "registered"
    permissions: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    privacy_class: str = "personal"

    def validate(self) -> None:
        if not self.module_id or not self.module_id.replace("_", "").isalnum():
            raise ValueError("Module ID must contain letters, numbers, or underscores.")
        if self.status not in {
            "registered",
            "installed",
            "enabled",
            "degraded",
            "disabled",
            "removed",
        }:
            raise ValueError("Unknown module lifecycle state.")
