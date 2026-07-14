from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import uuid4

from core.commands import CommandResult
from core.contracts import CommandEnvelope, DomainEvent, RecordRef
from core.hub import LivingHub
from core.schemas import SchemaDefinition
from shared.time import utc_now_iso


STATUSES = ("draft", "active", "review", "done", "archive")


def _validate_decision(payload: Mapping[str, Any]) -> None:
    if not str(payload.get("id", "")).strip():
        raise ValueError("Decision ID is required.")
    if not str(payload.get("decision", "")).strip():
        raise ValueError("Decision text is required.")
    if str(payload.get("status", "")) not in STATUSES:
        raise ValueError("Unknown decision status.")


class DecisionService:
    module_id = "decision"
    entity_type = "decision"

    def __init__(self, hub: LivingHub) -> None:
        self.hub = hub
        try:
            hub.schemas.register(SchemaDefinition(self.module_id, self.entity_type, 1, _validate_decision))
        except ValueError:
            pass
        for command_type, handler in (("create", self._handle_create), ("revise", self._handle_revise)):
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
            (DomainEvent(self.module_id, "DecisionCreated", ref, {"version": version}),),
        )

    def _handle_revise(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        record_id = str(command.payload.get("id", ""))
        row = connection.execute(
            """SELECT version, payload_json FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (self.module_id, self.entity_type, record_id),
        ).fetchone()
        if row is None:
            raise ValueError("Decision does not exist.")
        payload = json.loads(row["payload_json"])
        for field in ("reason", "expected_result", "actual_result", "review_note", "status"):
            if field in command.payload:
                payload[field] = str(command.payload[field]).strip()
        payload["updated_at"] = utc_now_iso()
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
            (DomainEvent(self.module_id, "DecisionRevised", ref, {"version": version}),),
        )

    def create(
        self,
        decision: str,
        reason: str,
        expected_result: str,
        actual_result: str,
        review_note: str,
        status: str,
    ) -> dict[str, Any]:
        timestamp = utc_now_iso()
        payload = {
            "id": f"DEC-{uuid4()}",
            "decision": decision.strip(),
            "reason": reason.strip(),
            "expected_result": expected_result.strip(),
            "actual_result": actual_result.strip(),
            "review_note": review_note.strip(),
            "status": status if status in STATUSES else "draft",
            "created_at": timestamp,
            "updated_at": timestamp,
            "schema_version": 1,
        }
        result = self.hub.commands.execute(
            CommandEnvelope(self.module_id, "create", payload, reason="create-decision")
        )
        return dict(result.value)

    def revise(self, record_id: str, expected_version: int, **changes: str) -> dict[str, Any]:
        result = self.hub.commands.execute(
            CommandEnvelope(
                self.module_id,
                "revise",
                {"id": record_id, **changes},
                reason="revise-decision",
                expected_version=expected_version,
            )
        )
        return dict(result.value)

    def list(self) -> list[dict[str, Any]]:
        return self.hub.store.list_records(self.module_id, self.entity_type)
