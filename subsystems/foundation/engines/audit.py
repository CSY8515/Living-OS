from __future__ import annotations

import json
import sqlite3
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.contracts import CommandEnvelope
from subsystems.foundation.engines.time import utc_now_iso


def append_audit(
    connection: sqlite3.Connection,
    command: CommandEnvelope,
    outcome: str,
    details: dict[str, Any] | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_entries (
            audit_id, command_id, module_id, command_type, actor, source,
            reason, outcome, details_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid4()),
            command.command_id,
            command.module_id,
            command.command_type,
            command.actor,
            command.source,
            command.reason,
            outcome,
            json.dumps(details or {}, ensure_ascii=False, sort_keys=True),
            utc_now_iso(),
        ),
    )
