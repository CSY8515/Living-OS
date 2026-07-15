from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from subsystems.foundation.engines.audit import append_audit
from subsystems.foundation.engines.contracts import CommandEnvelope, DomainEvent
from subsystems.foundation.engines.errors import CommandRejected
from subsystems.foundation.engines.storage import HubStore


@dataclass(frozen=True)
class CommandResult:
    value: Any
    events: tuple[DomainEvent, ...] = ()


CommandHandler = Callable[[CommandEnvelope, Any], CommandResult]
PolicyCheck = Callable[[CommandEnvelope], None]


class CommandBus:
    """Policy-checked command boundary with idempotency and audit."""

    def __init__(self, store: HubStore) -> None:
        self.store = store
        self._handlers: dict[tuple[str, str], CommandHandler] = {}
        self._policies: list[PolicyCheck] = []

    def register(self, module_id: str, command_type: str, handler: CommandHandler) -> None:
        key = (module_id, command_type)
        if key in self._handlers:
            raise ValueError(f"Command handler already registered: {module_id}.{command_type}")
        self._handlers[key] = handler

    def add_policy(self, policy: PolicyCheck) -> None:
        self._policies.append(policy)

    def execute(self, command: CommandEnvelope) -> CommandResult:
        self.store.initialize()
        try:
            handler = self._handlers.get((command.module_id, command.command_type))
            if handler is None:
                raise CommandRejected(
                    f"No handler registered for {command.module_id}.{command.command_type}."
                )
            for policy in self._policies:
                policy(command)
            with self.store.transaction() as connection:
                existing = connection.execute(
                    "SELECT outcome, details_json FROM audit_entries WHERE command_id = ?",
                    (command.command_id,),
                ).fetchone()
                if existing:
                    raise CommandRejected("This command has already been processed.")
                result = handler(command, connection)
                for event in result.events:
                    self.store.append_event(event, connection)
                append_audit(
                    connection,
                    command,
                    "accepted",
                    {"event_ids": [event.event_id for event in result.events]},
                )
        except Exception as exc:
            if not isinstance(exc, CommandRejected) or "already been processed" not in str(exc):
                with self.store.transaction() as connection:
                    existing = connection.execute(
                        "SELECT 1 FROM audit_entries WHERE command_id = ?", (command.command_id,)
                    ).fetchone()
                    if not existing:
                        append_audit(
                            connection,
                            command,
                            "rejected",
                            {"error_type": type(exc).__name__},
                        )
            raise
        return result
