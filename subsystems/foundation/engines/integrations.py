from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from subsystems.foundation.engines.audit import append_audit
from subsystems.foundation.engines.contracts import CommandEnvelope, RecordRef
from subsystems.foundation.engines.errors import CommandRejected
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.time import utc_now_iso


@dataclass(frozen=True)
class AIContextPackage:
    request_type: str
    source: str
    source_refs: tuple[RecordRef, ...] = ()
    privacy_class: str = "personal"
    approved_by: str = "owner"
    created_at: str = field(default_factory=utc_now_iso)


class AIProvider(Protocol):
    def generate(self, model: str, instructions: str, source: str) -> str: ...


class AIGateway:
    """Provider-neutral, explicit-approval AI integration boundary."""

    def __init__(self, store: HubStore, provider: AIProvider) -> None:
        self.store = store
        self.provider = provider

    def request(
        self,
        package: AIContextPackage,
        *,
        model: str,
        instructions: str,
        explicitly_approved: bool,
    ) -> str:
        command = CommandEnvelope(
            "ai_briefing",
            package.request_type,
            {
                "source_refs": [
                    f"{ref.module_id}:{ref.entity_type}:{ref.record_id}"
                    for ref in package.source_refs
                ],
                "privacy_class": package.privacy_class,
            },
            actor=package.approved_by,
            source="ai-integration-gateway",
            reason="explicit-ai-request",
        )
        if not explicitly_approved:
            self._audit(command, "rejected", {"error_type": "ApprovalRequired"})
            raise CommandRejected("Explicit AI request approval is required.")
        if not package.source.strip():
            self._audit(command, "rejected", {"error_type": "EmptyContext"})
            raise CommandRejected("AI context is empty.")
        try:
            result = self.provider.generate(model, instructions, package.source)
        except Exception as exc:
            self._audit(command, "rejected", {"error_type": type(exc).__name__})
            raise
        self._audit(command, "accepted", {"result": "draft-only"})
        return result

    def _audit(self, command: CommandEnvelope, outcome: str, details: dict[str, str]) -> None:
        self.store.initialize()
        with self.store.transaction() as connection:
            append_audit(connection, command, outcome, details)
