from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import uuid4

from subsystems.foundation.engines.commands import CommandResult
from subsystems.foundation.engines.contracts import CommandEnvelope, DomainEvent, RecordRef
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.schemas import SchemaDefinition
from subsystems.foundation.engines.time import utc_now_iso


KINDS = ("note", "archive", "case", "rule_candidate", "living_rule")
PROMOTIONS = {
    "note": "case",
    "archive": "case",
    "case": "rule_candidate",
    "rule_candidate": "living_rule",
}


def _validate_knowledge(payload: Mapping[str, Any]) -> None:
    if not str(payload.get("id", "")).strip():
        raise ValueError("Knowledge ID is required.")
    if not str(payload.get("title", "")).strip() and not str(payload.get("content", "")).strip():
        raise ValueError("Knowledge title or content is required.")
    if str(payload.get("kind", "")) not in KINDS:
        raise ValueError("Unknown knowledge kind.")
    if not isinstance(payload.get("tags", []), list):
        raise ValueError("Knowledge tags must be a list.")


class KnowledgeService:
    module_id = "knowledge"
    entity_type = "knowledge_item"

    def __init__(self, hub: LivingHub) -> None:
        self.hub = hub
        try:
            hub.schemas.register(SchemaDefinition(self.module_id, self.entity_type, 1, _validate_knowledge))
        except ValueError:
            pass
        for command_type, handler in (("create", self._handle_create), ("promote", self._handle_promote)):
            try:
                hub.commands.register(self.module_id, command_type, handler)
            except ValueError:
                pass

    def _handle_create(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        payload = dict(command.payload)
        self.hub.schemas.validate(self.module_id, self.entity_type, 1, payload)
        ref = RecordRef(self.module_id, self.entity_type, str(payload["id"]))
        version = self.hub.store.put_record(ref, payload, expected_version=0, connection=connection)
        return CommandResult(
            {**payload, "_version": version},
            (DomainEvent(self.module_id, "KnowledgeItemCreated", ref, {"version": version}),),
        )

    def _handle_promote(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        record_id = str(command.payload.get("id", ""))
        row = connection.execute(
            """SELECT version, payload_json FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (self.module_id, self.entity_type, record_id),
        ).fetchone()
        if row is None:
            raise ValueError("Knowledge item does not exist.")
        payload = json.loads(row["payload_json"])
        current_kind = str(payload.get("kind", "note"))
        target_kind = PROMOTIONS.get(current_kind)
        if target_kind is None:
            raise ValueError("This knowledge item cannot be promoted further.")
        payload["kind"] = target_kind
        payload["updated_at"] = utc_now_iso()
        payload.setdefault("promotion_history", []).append(
            {
                "from": current_kind,
                "to": target_kind,
                "reason": command.reason,
                "at": payload["updated_at"],
            }
        )
        self.hub.schemas.validate(self.module_id, self.entity_type, 1, payload)
        ref = RecordRef(self.module_id, self.entity_type, record_id)
        version = self.hub.store.put_record(
            ref,
            payload,
            expected_version=command.expected_version,
            connection=connection,
        )
        return CommandResult(
            {**payload, "_version": version},
            (
                DomainEvent(
                    self.module_id,
                    "KnowledgeItemPromoted",
                    ref,
                    {"from": current_kind, "to": target_kind, "version": version},
                ),
            ),
        )

    def create(
        self,
        title: str,
        content: str,
        source: str,
        tags: list[str],
        kind: str = "note",
    ) -> dict[str, Any]:
        timestamp = utc_now_iso()
        payload = {
            "id": f"KNW-{uuid4()}",
            "title": title.strip() or "Untitled Knowledge Item",
            "content": content.strip(),
            "source": source.strip(),
            "tags": [str(tag).strip() for tag in tags if str(tag).strip()],
            "kind": kind if kind in KINDS else "note",
            "promotion_history": [],
            "created_at": timestamp,
            "updated_at": timestamp,
            "schema_version": 1,
        }
        result = self.hub.commands.execute(
            CommandEnvelope(self.module_id, "create", payload, reason="create-knowledge-item")
        )
        return dict(result.value)

    def promote(self, record_id: str, expected_version: int, reason: str) -> dict[str, Any]:
        result = self.hub.commands.execute(
            CommandEnvelope(
                self.module_id,
                "promote",
                {"id": record_id},
                reason=reason.strip() or "promote-reviewed-knowledge",
                expected_version=expected_version,
            )
        )
        return dict(result.value)

    def list(self) -> list[dict[str, Any]]:
        return self.hub.store.list_records(self.module_id, self.entity_type)
