from __future__ import annotations

from datetime import date
from typing import Any, Mapping
from uuid import uuid4

from core.commands import CommandResult
from core.contracts import CommandEnvelope, DomainEvent, RecordRef
from core.hub import LivingHub
from core.schemas import SchemaDefinition
from shared.time import utc_now_iso


def _validate_journal(payload: Mapping[str, Any]) -> None:
    if not str(payload.get("id", "")).strip():
        raise ValueError("Journal ID is required.")
    if not str(payload.get("title", "")).strip() and not str(payload.get("content", "")).strip():
        raise ValueError("Journal title or content is required.")
    if not isinstance(payload.get("tags", []), list):
        raise ValueError("Journal tags must be a list.")


class JournalService:
    module_id = "journal"
    entity_type = "journal_entry"

    def __init__(self, hub: LivingHub) -> None:
        self.hub = hub
        try:
            hub.schemas.register(SchemaDefinition(self.module_id, self.entity_type, 1, _validate_journal))
        except ValueError:
            pass
        try:
            hub.commands.register(self.module_id, "create", self._handle_create)
        except ValueError:
            pass

    def _handle_create(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        payload = dict(command.payload)
        self.hub.schemas.validate(self.module_id, self.entity_type, 1, payload)
        ref = RecordRef(self.module_id, self.entity_type, str(payload["id"]))
        version = self.hub.store.put_record(
            ref,
            payload,
            expected_version=0,
            connection=connection,
        )
        event = DomainEvent(self.module_id, "JournalEntryCreated", ref, {"version": version})
        return CommandResult({**payload, "_version": version}, (event,))

    def create(
        self,
        entry_date: str,
        title: str,
        content: str,
        tags: list[str],
        mood: str,
    ) -> dict[str, Any]:
        timestamp = utc_now_iso()
        payload = {
            "id": f"JRN-{uuid4()}",
            "date": entry_date or date.today().isoformat(),
            "title": title.strip() or "Untitled Journal Entry",
            "content": content.strip(),
            "tags": [str(tag).strip() for tag in tags if str(tag).strip()],
            "mood": mood.strip(),
            "created_at": timestamp,
            "updated_at": timestamp,
            "schema_version": 1,
        }
        result = self.hub.commands.execute(
            CommandEnvelope(self.module_id, "create", payload, reason="create-journal-entry")
        )
        return dict(result.value)

    def list(self) -> list[dict[str, Any]]:
        return self.hub.store.list_records(self.module_id, self.entity_type)
