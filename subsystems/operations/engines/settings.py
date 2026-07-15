from __future__ import annotations

import json
from typing import Any

from subsystems.foundation.engines.commands import CommandResult
from subsystems.foundation.engines.contracts import CommandEnvelope, DomainEvent, RecordRef
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.time import utc_now_iso


class HubSettingsService:
    module_id = "settings"
    entity_type = "configuration"
    record_id = "configuration"

    def __init__(self, hub: LivingHub) -> None:
        self.hub = hub
        try:
            hub.commands.register(self.module_id, "update", self._handle_update)
        except ValueError:
            pass

    def _handle_update(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        row = connection.execute(
            """SELECT version, payload_json FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (self.module_id, self.entity_type, self.record_id),
        ).fetchone()
        current = json.loads(row["payload_json"]) if row else {}
        current.update(dict(command.payload))
        current["version"] = "v1.2"
        current["updated_at"] = utc_now_iso()
        if not str(current.get("app_name", "")).strip():
            raise ValueError("Application name is required.")
        if current.get("default_report_range") not in {"daily", "weekly", "monthly"}:
            raise ValueError("Unknown default report range.")
        ref = RecordRef(self.module_id, self.entity_type, self.record_id)
        version = self.hub.store.put_record(
            ref,
            current,
            expected_version=command.expected_version,
            connection=connection,
        )
        return CommandResult(
            {**current, "_version": version},
            (DomainEvent(self.module_id, "SettingsUpdated", ref, {"version": version}),),
        )

    def load(self) -> dict[str, Any]:
        record = self.hub.store.get_record(RecordRef(self.module_id, self.entity_type, self.record_id))
        return record or {
            "app_name": "Living OS",
            "version": "v1.2",
            "default_report_range": "daily",
            "date_format": "YYYY-MM-DD",
            "_version": 0,
        }

    def update(self, app_name: str, default_report_range: str, expected_version: int) -> dict[str, Any]:
        result = self.hub.commands.execute(
            CommandEnvelope(
                self.module_id,
                "update",
                {
                    "app_name": app_name.strip(),
                    "default_report_range": default_report_range,
                },
                reason="update-hub-settings",
                expected_version=expected_version,
            )
        )
        return dict(result.value)
