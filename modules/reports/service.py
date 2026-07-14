from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Mapping
from uuid import uuid4

from core.commands import CommandResult
from core.contracts import CommandEnvelope, DomainEvent, RecordRef
from core.hub import LivingHub
from core.schemas import SchemaDefinition
from shared.time import utc_now_iso


REPORT_TYPES = ("daily", "weekly", "monthly")


def _validate_report(payload: Mapping[str, Any]) -> None:
    if not str(payload.get("id", "")).strip():
        raise ValueError("Report ID is required.")
    if str(payload.get("report_type", "")) not in REPORT_TYPES:
        raise ValueError("Unknown report type.")
    if not str(payload.get("content", "")).strip():
        raise ValueError("Report content is required.")


class ReportsService:
    module_id = "reports"
    entity_type = "report"

    def __init__(self, hub: LivingHub) -> None:
        self.hub = hub
        try:
            hub.schemas.register(SchemaDefinition(self.module_id, self.entity_type, 1, _validate_report))
        except ValueError:
            pass
        try:
            hub.commands.register(self.module_id, "save", self._handle_save)
        except ValueError:
            pass

    def _handle_save(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        payload = dict(command.payload)
        self.hub.schemas.validate(self.module_id, self.entity_type, 1, payload)
        ref = RecordRef(self.module_id, self.entity_type, str(payload["id"]))
        version = self.hub.store.put_record(ref, payload, expected_version=0, connection=connection)
        return CommandResult(
            {**payload, "_version": version},
            (DomainEvent(self.module_id, "ReportSaved", ref, {"version": version}),),
        )

    def _range(self, report_type: str) -> tuple[date, date]:
        today = date.today()
        if report_type == "weekly":
            return today - timedelta(days=6), today
        if report_type == "monthly":
            return today.replace(day=1), today
        return today, today

    def build(self, report_type: str) -> str:
        selected = report_type if report_type in REPORT_TYPES else "daily"
        start, end = self._range(selected)
        journals = []
        for item in self.hub.store.list_records("journal", "journal_entry"):
            try:
                entry_date = date.fromisoformat(str(item.get("date", ""))[:10])
            except ValueError:
                continue
            if start <= entry_date <= end:
                journals.append(item)
        decisions = self.hub.store.list_records("decision", "decision")[:10]
        lines = [
            f"# Living OS {selected.title()} Report",
            "",
            f"- Generated At: {utc_now_iso()}",
            f"- Range: {start.isoformat()} to {end.isoformat()}",
            "- Version: Living OS v2.0",
            "",
            "## Summary",
            "",
            f"- Journal Entries: {len(journals)}",
            f"- Decisions: {len(decisions)}",
            "",
            "## Journal",
            "",
        ]
        if journals:
            for item in sorted(journals, key=lambda value: str(value.get("date", ""))):
                lines.extend(
                    [
                        f"### {item.get('date', '-')} — {item.get('title', 'Untitled')}",
                        str(item.get("content", "")).strip() or "-",
                        "",
                    ]
                )
        else:
            lines.extend(["No journal entries for this period.", ""])
        lines.extend(["## Decision Review", ""])
        if decisions:
            for item in decisions:
                lines.append(
                    f"- {item.get('id', '-')} — {item.get('decision', 'Untitled')} — {item.get('status', 'draft')}"
                )
        else:
            lines.append("No decisions yet.")
        lines.extend(["", "## Next Review", "", "- Review open decisions.", "- Promote reviewed evidence into Knowledge when appropriate.", ""])
        return "\n".join(lines)

    def save(self, report_type: str, content: str, *, generated_by: str = "deterministic") -> dict[str, Any]:
        payload = {
            "id": f"RPT-{uuid4()}",
            "report_type": report_type if report_type in REPORT_TYPES else "daily",
            "content": content,
            "generated_by": generated_by,
            "source_modules": ["journal", "decision"],
            "created_at": utc_now_iso(),
            "schema_version": 1,
        }
        result = self.hub.commands.execute(
            CommandEnvelope(self.module_id, "save", payload, reason="save-report-artifact")
        )
        return dict(result.value)

    def list(self) -> list[dict[str, Any]]:
        return self.hub.store.list_records(self.module_id, self.entity_type)
