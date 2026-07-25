from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
import json
from typing import Any, Callable, Mapping
from uuid import uuid4

from subsystems.foundation.engines.commands import CommandResult
from subsystems.foundation.engines.contracts import CommandEnvelope, DomainEvent, RecordRef
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.schemas import SchemaDefinition
from subsystems.foundation.engines.time import utc_now_iso
from subsystems.foundation.engines.version import PRODUCT_VERSION


REPORT_TYPES = ("daily", "weekly", "monthly", "yearly")
REPORT_STATUSES = ("ACTIVE", "ARCHIVED")
REPORT_SOURCE_SUBSYSTEMS = (
    "journal",
    "decision",
    "finance",
    "health",
    "vehicle",
    "housing",
    "food",
    "investment",
    "job",
    "knowledge",
    "routine",
    "personal-growth",
    "collaboration",
)


@dataclass(frozen=True)
class ReportContract:
    report_id: str
    report_type: str
    title: str
    summary: str
    content: str
    period_start: str
    period_end: str
    source_subsystems: tuple[str, ...]
    status: str = "ACTIVE"
    generated_by: str = "deterministic"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    archived_at: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = 2

    def validate(self) -> None:
        if not self.report_id.strip() or not self.title.strip() or not self.content.strip():
            raise ValueError("Report ID, title, and content are required.")
        if self.report_type not in REPORT_TYPES:
            raise ValueError("Unknown report type.")
        if self.status not in REPORT_STATUSES:
            raise ValueError("Unknown report status.")
        start = date.fromisoformat(self.period_start)
        end = date.fromisoformat(self.period_end)
        if start > end:
            raise ValueError("Report period_start cannot be after period_end.")
        unknown = set(self.source_subsystems) - set(REPORT_SOURCE_SUBSYSTEMS)
        if unknown:
            raise ValueError(f"Unknown report sources: {', '.join(sorted(unknown))}")
        if not isinstance(self.metadata, Mapping):
            raise ValueError("Report metadata must be an object.")

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["id"] = payload.pop("report_id")
        payload["source_subsystems"] = list(self.source_subsystems)
        return payload


def _validate_report(payload: Mapping[str, Any]) -> None:
    contract = ReportContract(
        report_id=str(payload.get("id", "")),
        report_type=str(payload.get("report_type", "")),
        title=str(payload.get("title", "")),
        summary=str(payload.get("summary", "")),
        content=str(payload.get("content", "")),
        period_start=str(payload.get("period_start", "")),
        period_end=str(payload.get("period_end", "")),
        source_subsystems=tuple(payload.get("source_subsystems", ())),
        status=str(payload.get("status", "ACTIVE")),
        generated_by=str(payload.get("generated_by", "deterministic")),
        created_at=str(payload.get("created_at", "")),
        updated_at=str(payload.get("updated_at", "")),
        archived_at=payload.get("archived_at"),
        metadata=dict(payload.get("metadata", {})),
        schema_version=int(payload.get("schema_version", 2)),
    )
    contract.validate()


ReportSource = Callable[[str, date, date], Any]


class ReportsService:
    """Common deterministic Daily/Weekly/Monthly Report foundation."""

    module_id = "reports"
    entity_type = "report"

    def __init__(
        self,
        hub: LivingHub,
        sources: Mapping[str, ReportSource | Any] | None = None,
    ) -> None:
        self.hub = hub
        self._sources: dict[str, ReportSource | Any] = {}
        try:
            hub.schemas.register(SchemaDefinition(self.module_id, self.entity_type, 2, _validate_report))
        except ValueError:
            pass
        for command_type, handler in (
            ("save", self._handle_save),
            ("archive", self._handle_archive),
        ):
            try:
                hub.commands.register(self.module_id, command_type, handler)
            except ValueError:
                pass
        for name, provider in dict(sources or {}).items():
            self.connect_source(name, provider)

    def connect_source(self, subsystem: str, provider: ReportSource | Any) -> None:
        name = str(subsystem).strip().lower().replace("_", "-")
        if name not in REPORT_SOURCE_SUBSYSTEMS:
            raise ValueError(f"Unsupported report source: {subsystem}")
        self._sources[name] = provider

    def connected_sources(self) -> tuple[str, ...]:
        return tuple(name for name in REPORT_SOURCE_SUBSYSTEMS if name in self._sources)

    def _handle_save(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        payload = dict(command.payload)
        self.hub.schemas.validate(self.module_id, self.entity_type, 2, payload)
        ref = RecordRef(self.module_id, self.entity_type, str(payload["id"]))
        version = self.hub.store.put_record(ref, payload, expected_version=0, connection=connection)
        return CommandResult(
            {**payload, "_version": version, "_status": "ACTIVE"},
            (DomainEvent(self.module_id, "ReportCreated", ref, {"version": version}),),
        )

    def _handle_archive(self, command: CommandEnvelope, connection: Any) -> CommandResult:
        record_id = str(command.payload.get("id", ""))
        row = connection.execute(
            """SELECT version,payload_json,status FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (self.module_id, self.entity_type, record_id),
        ).fetchone()
        if row is None:
            raise ValueError("Report does not exist.")
        if int(row["version"]) != int(command.expected_version or 0):
            raise ValueError("Report has a newer version.")
        payload = json.loads(row["payload_json"])
        now = utc_now_iso()
        payload.update({"status": "ARCHIVED", "archived_at": now, "updated_at": now})
        self.hub.schemas.validate(self.module_id, self.entity_type, 2, payload)
        connection.execute(
            """UPDATE records SET payload_json=?,version=version+1,status='ARCHIVED',
                   archived_at=?,updated_at=?,source=?
               WHERE module_id=? AND entity_type=? AND record_id=? AND version=?""",
            (
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                now,
                now,
                command.source,
                self.module_id,
                self.entity_type,
                record_id,
                int(command.expected_version or 0),
            ),
        )
        ref = RecordRef(self.module_id, self.entity_type, record_id)
        return CommandResult(
            {**payload, "_version": int(row["version"]) + 1, "_status": "ARCHIVED"},
            (DomainEvent(self.module_id, "ReportArchived", ref, {"status": "ARCHIVED"}),),
        )

    def _range(self, report_type: str, as_of: date | None = None) -> tuple[date, date]:
        selected = as_of or date.today()
        if report_type == "weekly":
            return selected - timedelta(days=6), selected
        if report_type == "monthly":
            return selected.replace(day=1), selected
        if report_type == "yearly":
            return selected.replace(month=1, day=1), selected
        return selected, selected

    def report_summary(
        self,
        report_type: str,
        *,
        as_of: date | None = None,
    ) -> dict[str, Any]:
        selected = report_type if report_type in REPORT_TYPES else "daily"
        start, end = self._range(selected, as_of)
        timeline = self.hub.timeline.query(start=start, end=end, limit=1000)
        by_subsystem: dict[str, int] = {}
        by_category: dict[str, int] = {}
        for item in timeline:
            by_subsystem[item.subsystem] = by_subsystem.get(item.subsystem, 0) + 1
            by_category[item.category] = by_category.get(item.category, 0) + 1
        return {
            "report_type": selected,
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
            "timeline_events": len(timeline),
            "active_events": sum(not item.archived for item in timeline),
            "archived_events": sum(item.archived for item in timeline),
            "by_subsystem": dict(sorted(by_subsystem.items())),
            "by_category": dict(sorted(by_category.items())),
        }

    def cross_subsystem_summary(
        self,
        report_type: str,
        *,
        as_of: date | None = None,
    ) -> list[dict[str, Any]]:
        summary = self.report_summary(report_type, as_of=as_of)
        return [
            {"subsystem": name, "activity": count}
            for name, count in summary["by_subsystem"].items()
        ]

    def build(self, report_type: str, *, as_of: date | None = None) -> str:
        selected = report_type if report_type in REPORT_TYPES else "daily"
        start, end = self._range(selected, as_of)
        journals = []
        for item in self.hub.store.list_records("journal", "journal_entry"):
            try:
                entry_date = date.fromisoformat(str(item.get("date", ""))[:10])
            except ValueError:
                continue
            if start <= entry_date <= end:
                journals.append(item)
        decisions = self.hub.store.list_records("decision", "decision")[:10]
        timeline = self.hub.timeline.query(start=start, end=end, limit=500)
        lines = [
            f"# Living OS {selected.title()} Report",
            "",
            f"- Generated At: {utc_now_iso()}",
            f"- Range: {start.isoformat()} to {end.isoformat()}",
            f"- Version: Living OS {PRODUCT_VERSION}",
            "",
            "## Summary",
            "",
            f"- Journal Entries: {len(journals)}",
            f"- Decisions: {len(decisions)}",
            f"- Timeline Events: {len(timeline)}",
            f"- Active Events: {sum(not item.archived for item in timeline)}",
            f"- Archived Events: {sum(item.archived for item in timeline)}",
            "",
            "## Cross Subsystem Summary",
            "",
            *(f"- {item['subsystem']}: {item['activity']}" for item in self.cross_subsystem_summary(selected, as_of=as_of)),
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
                    f"- {item.get('id', '-')} — {item.get('decision', 'Untitled')} — "
                    f"{item.get('status', 'draft')}"
                )
        else:
            lines.append("No decisions yet.")
        lines.extend(["", "## Subsystem Reports", ""])
        for source in REPORT_SOURCE_SUBSYSTEMS[2:]:
            lines.extend([f"### {source.replace('-', ' ').title()}", ""])
            content = self._source_content(source, selected, start, end)
            lines.extend([content, ""])
        lines.extend(
            [
                "## Next Review",
                "",
                "- Review open decisions.",
                "- Review archived records separately from active work.",
                "- Promote reviewed evidence into Knowledge when appropriate.",
                "",
            ]
        )
        return "\n".join(lines)

    def create(
        self,
        report_type: str,
        *,
        as_of: date | None = None,
        save: bool = True,
    ) -> dict[str, Any]:
        selected = report_type if report_type in REPORT_TYPES else "daily"
        start, end = self._range(selected, as_of)
        content = self.build(selected, as_of=as_of)
        if not save:
            return self._contract(selected, content, start, end).to_payload()
        return self.save(selected, content, period_start=start, period_end=end)

    def save(
        self,
        report_type: str,
        content: str,
        *,
        generated_by: str = "deterministic",
        period_start: date | None = None,
        period_end: date | None = None,
    ) -> dict[str, Any]:
        selected = report_type if report_type in REPORT_TYPES else "daily"
        default_start, default_end = self._range(selected)
        contract = self._contract(
            selected,
            content,
            period_start or default_start,
            period_end or default_end,
            generated_by=generated_by,
        )
        result = self.hub.commands.execute(
            CommandEnvelope(
                self.module_id,
                "save",
                contract.to_payload(),
                reason="save-report-artifact",
            )
        )
        return dict(result.value)

    def get(self, report_id: str) -> dict[str, Any] | None:
        return self.hub.database.repository.read(self.module_id, self.entity_type, report_id)

    def list(self, *, include_archived: bool = False, limit: int = 100) -> list[dict[str, Any]]:
        return self.hub.database.repository.list(
            self.module_id,
            self.entity_type,
            include_archived=include_archived,
            limit=limit,
        )

    def archive(self, report_id: str, expected_version: int) -> dict[str, Any]:
        result = self.hub.commands.execute(
            CommandEnvelope(
                self.module_id,
                "archive",
                {"id": report_id},
                reason="archive-report-artifact",
                expected_version=expected_version,
            )
        )
        return dict(result.value)

    def _contract(
        self,
        report_type: str,
        content: str,
        start: date,
        end: date,
        *,
        generated_by: str = "deterministic",
    ) -> ReportContract:
        now = utc_now_iso()
        return ReportContract(
            report_id=f"RPT-{uuid4()}",
            report_type=report_type,
            title=f"Living OS {report_type.title()} Report",
            summary=f"Deterministic {report_type} report for {start} to {end}.",
            content=content,
            period_start=start.isoformat(),
            period_end=end.isoformat(),
            source_subsystems=REPORT_SOURCE_SUBSYSTEMS,
            generated_by=generated_by,
            created_at=now,
            updated_at=now,
            metadata={"product_version": PRODUCT_VERSION},
        )

    def _source_content(
        self,
        name: str,
        report_type: str,
        start: date,
        end: date,
    ) -> str:
        provider = self._sources.get(name)
        if provider is None:
            return "No source data connected."
        if callable(provider):
            value = provider(report_type, start, end)
        else:
            value = self._subsystem_report(provider, report_type, start, end)
        if isinstance(value, str):
            return value.strip() or "No source data."
        return "```json\n" + json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) + "\n```"

    @staticmethod
    def _subsystem_report(provider: Any, report_type: str, start: date, end: date) -> Any:
        if report_type == "daily" and callable(getattr(provider, "daily_report", None)):
            return provider.daily_report(end.isoformat())
        if report_type == "weekly" and callable(getattr(provider, "weekly_report", None)):
            return provider.weekly_report(end.isoformat())
        if report_type == "monthly" and callable(getattr(provider, "monthly_report", None)):
            return provider.monthly_report(end.strftime("%Y-%m"))
        if report_type == "yearly" and callable(getattr(provider, "yearly_report", None)):
            return provider.yearly_report(end.year)
        if callable(getattr(provider, "management_summary", None)):
            return provider.management_summary()
        if callable(getattr(provider, "housing_report", None)):
            return provider.housing_report()
        if callable(getattr(provider, "food_report", None)):
            return provider.food_report(start.isoformat(), end.isoformat())
        if (
            callable(getattr(provider, "list_vehicles", None))
            and callable(getattr(provider, "vehicle_report", None))
        ):
            return [
                provider.vehicle_report(item["vehicle_id"], start.isoformat(), end.isoformat())
                for item in provider.list_vehicles()
            ]
        if callable(getattr(provider, "summary_report", None)):
            return provider.summary_report(end.strftime("%Y-%m"))
        if callable(getattr(provider, "health", None)):
            return provider.health()
        return {"status": "CONNECTED", "detail": "Basic report source is available."}
