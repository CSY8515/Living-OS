from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


Validator = Callable[[Mapping[str, Any]], None]


@dataclass(frozen=True)
class SchemaDefinition:
    module_id: str
    entity_type: str
    version: int
    validator: Validator


class SchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, int], SchemaDefinition] = {}

    def register(self, definition: SchemaDefinition) -> None:
        key = (definition.module_id, definition.entity_type, definition.version)
        if key in self._schemas:
            raise ValueError("Schema version is already registered.")
        self._schemas[key] = definition

    def validate(
        self,
        module_id: str,
        entity_type: str,
        version: int,
        payload: Mapping[str, Any],
    ) -> None:
        definition = self._schemas.get((module_id, entity_type, version))
        if definition is None:
            raise ValueError(f"Unknown schema: {module_id}.{entity_type} v{version}")
        definition.validator(payload)
