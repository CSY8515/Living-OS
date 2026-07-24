from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timezone
import json
from typing import Any, Callable, Iterable, Mapping

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.database.engines.execution import ExecutionRecorder


TIMELINE_SUBSYSTEMS = (
    "finance",
    "investment",
    "job",
    "health",
    "vehicle",
    "housing",
    "food",
    "knowledge",
    "routine",
    "personal-growth",
    "collaboration",
)

SUBSYSTEM_TIMELINE_PROFILES: dict[str, dict[str, str]] = {
    "finance": {
        "record_type": "transaction",
        "id_field": "transaction_id",
        "title_field": "description",
        "summary_field": "category",
        "event_time_field": "occurred_on",
    },
    "investment": {
        "record_type": "investment",
        "id_field": "investment_id",
        "title_field": "name",
        "summary_field": "notes",
    },
    "job": {
        "record_type": "job",
        "id_field": "job_id",
        "title_field": "title",
        "summary_field": "company",
    },
    "health": {
        "record_type": "health-record",
        "id_field": "record_id",
        "title_field": "title",
        "summary_field": "note",
        "event_time_field": "measured_on",
    },
    "vehicle": {
        "record_type": "vehicle",
        "id_field": "vehicle_id",
        "title_field": "display_name",
        "summary_field": "model",
    },
    "housing": {
        "record_type": "housing-candidate",
        "id_field": "candidate_id",
        "title_field": "title",
        "summary_field": "address",
    },
    "food": {
        "record_type": "food-record",
        "id_field": "ingredient_id",
        "title_field": "name",
        "summary_field": "category",
    },
    "knowledge": {
        "record_type": "knowledge-record",
        "id_field": "record_id",
        "title_field": "title",
        "summary_field": "summary",
    },
    "routine": {
        "record_type": "routine",
        "id_field": "routine_id",
        "title_field": "name",
        "summary_field": "description",
    },
    "personal-growth": {
        "record_type": "growth-goal",
        "id_field": "goal_id",
        "title_field": "title",
        "summary_field": "purpose",
    },
    "collaboration": {
        "record_type": "collaboration",
        "id_field": "collaboration_id",
        "title_field": "title",
        "summary_field": "objective",
    },
}

SUBSYSTEM_ALIASES = {
    "SUB-FINANCE": "finance",
    "SUB-INVESTMENT": "investment",
    "SUB-JOB": "job",
    "SUB-HEALTH": "health",
    "SUB-VEHICLE": "vehicle",
    "SUB-HOUSING": "housing",
    "SUB-FOOD": "food",
    "SUB-KNOWLEDGE": "knowledge",
    "SUB-ROUTINE": "routine",
    "SUB-PERSONAL-GROWTH": "personal-growth",
    "SUB-COLLABORATION": "collaboration",
}

ARCHIVE_VALUES = {"ARCHIVE", "ARCHIVED"}


def _timestamp(value: Any, fallback: str = "") -> str:
    text = str(value or fallback).strip()
    if not text:
        return datetime.now(timezone.utc).isoformat()
    if len(text) == 10:
        return datetime.combine(date.fromisoformat(text), time.min, timezone.utc).isoformat()
    datetime.fromisoformat(text.replace("Z", "+00:00"))
    return text


def _boundary(value: date | datetime | str | None, *, end: bool = False) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        selected = time.max if end else time.min
        return datetime.combine(value, selected, timezone.utc).isoformat()
    text = str(value)
    if len(text) == 10:
        selected = time.max if end else time.min
        return datetime.combine(date.fromisoformat(text), selected, timezone.utc).isoformat()
    datetime.fromisoformat(text.replace("Z", "+00:00"))
    return text


def _sort_value(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class TimelineRecord:
    record_id: str
    subsystem: str
    record_type: str
    event_type: str
    title: str
    summary: str
    event_time: str
    created_time: str
    updated_time: str
    status: str
    source: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "record_id": self.record_id,
            "subsystem": self.subsystem,
            "record_type": self.record_type,
            "event_type": self.event_type,
            "title": self.title,
            "event_time": self.event_time,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "status": self.status,
            "source": self.source,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"Timeline fields are required: {', '.join(missing)}")
        _timestamp(self.event_time)
        _timestamp(self.created_time)
        _timestamp(self.updated_time)
        if not isinstance(self.metadata, Mapping):
            raise ValueError("Timeline metadata must be an object.")

    @property
    def archived(self) -> bool:
        return self.status.upper() in ARCHIVE_VALUES or "ARCHIV" in self.event_type.upper()

    @property
    def record_ref(self) -> dict[str, str]:
        return {
            "subsystem": self.subsystem,
            "record_type": self.record_type,
            "record_id": self.record_id,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "archived": self.archived, "record_ref": self.record_ref}


@dataclass(frozen=True)
class TimelineSource:
    subsystem: str
    record_type: str
    loader: Callable[[], Iterable[Mapping[str, Any]]]
    id_field: str = "id"
    title_field: str = "title"
    summary_field: str = "summary"
    event_time_field: str = "updated_at"
    created_time_field: str = "created_at"
    updated_time_field: str = "updated_at"
    status_field: str = "status"
    source_field: str = "source"

    def snapshot(self) -> list[TimelineRecord]:
        subsystem = SUBSYSTEM_ALIASES.get(self.subsystem, self.subsystem).lower()
        if subsystem not in TIMELINE_SUBSYSTEMS:
            raise ValueError(f"Unsupported Timeline subsystem: {self.subsystem}")
        records: list[TimelineRecord] = []
        for item in self.loader():
            record_id = str(
                item.get(self.id_field)
                or next(
                    (
                        item.get(name)
                        for name in (
                            "id",
                            "record_id",
                            "transaction_id",
                            "investment_id",
                            "job_id",
                            "vehicle_id",
                            "candidate_id",
                            "ingredient_id",
                            "recipe_id",
                            "routine_id",
                            "goal_id",
                            "collaboration_id",
                        )
                        if item.get(name)
                    ),
                    "",
                )
            ).strip()
            if not record_id:
                continue
            created = _timestamp(
                item.get(self.created_time_field),
                str(item.get(self.event_time_field, "")),
            )
            updated = _timestamp(item.get(self.updated_time_field), created)
            status = str(item.get(self.status_field, "ACTIVE") or "ACTIVE").upper()
            event_type = "ARCHIVED" if status in ARCHIVE_VALUES else (
                "CREATED" if created == updated else "UPDATED"
            )
            title = str(
                item.get(self.title_field)
                or next(
                    (
                        item.get(name)
                        for name in (
                            "title",
                            "name",
                            "display_name",
                            "company",
                            "description",
                            "activity",
                            "category",
                        )
                        if item.get(name)
                    ),
                    record_id,
                )
            )
            summary = str(item.get(self.summary_field) or item.get("note") or "")
            source = str(item.get(self.source_field, "") or f"{subsystem}-snapshot")
            records.append(
                TimelineRecord(
                    record_id=record_id,
                    subsystem=subsystem,
                    record_type=self.record_type,
                    event_type=event_type,
                    title=title,
                    summary=summary,
                    event_time=updated,
                    created_time=created,
                    updated_time=updated,
                    status=status,
                    source=source,
                    metadata={"snapshot": True, "status": status},
                )
            )
        return records


class TimelineService:
    """Read-only common Timeline over domain events, execution history, and snapshots."""

    def __init__(
        self,
        connections: SQLiteConnectionLayer,
        executions: ExecutionRecorder,
    ) -> None:
        self.connections = connections
        self.executions = executions
        self._sources: dict[tuple[str, str], TimelineSource] = {}

    def register_source(self, source: TimelineSource, *, replace: bool = False) -> None:
        subsystem = SUBSYSTEM_ALIASES.get(source.subsystem, source.subsystem).lower()
        if subsystem not in TIMELINE_SUBSYSTEMS:
            raise ValueError(f"Unsupported Timeline subsystem: {source.subsystem}")
        key = (subsystem, source.record_type)
        if key in self._sources and not replace:
            raise ValueError(f"Timeline source already registered: {subsystem}.{source.record_type}")
        self._sources[key] = source

    def register_subsystem_source(
        self,
        subsystem: str,
        loader: Callable[[], Iterable[Mapping[str, Any]]],
        *,
        record_type: str | None = None,
        replace: bool = False,
        **overrides: str,
    ) -> TimelineSource:
        name = SUBSYSTEM_ALIASES.get(subsystem, subsystem).lower()
        if name not in SUBSYSTEM_TIMELINE_PROFILES:
            raise ValueError(f"Unsupported Timeline subsystem: {subsystem}")
        profile = {**SUBSYSTEM_TIMELINE_PROFILES[name], **overrides}
        default_type = profile.pop("record_type")
        selected_type = str(record_type or default_type)
        source = TimelineSource(
            subsystem=name,
            record_type=selected_type,
            loader=loader,
            **profile,
        )
        self.register_source(source, replace=replace)
        return source

    def supported_subsystems(self) -> tuple[str, ...]:
        return TIMELINE_SUBSYSTEMS

    def query(
        self,
        *,
        start: date | datetime | str | None = None,
        end: date | datetime | str | None = None,
        subsystem: str | None = None,
        record_id: str | None = None,
        include_archived: bool = True,
        limit: int = 500,
    ) -> list[TimelineRecord]:
        selected = SUBSYSTEM_ALIASES.get(str(subsystem or ""), str(subsystem or "")).lower()
        start_value = _boundary(start)
        end_value = _boundary(end, end=True)
        records = self._domain_events() + self._execution_events(limit)
        for source in self._sources.values():
            records.extend(source.snapshot())
        filtered: list[TimelineRecord] = []
        for item in records:
            if selected and item.subsystem.lower() != selected:
                continue
            if record_id and item.record_id != record_id:
                continue
            if not include_archived and item.archived:
                continue
            if start_value and _sort_value(item.event_time) < _sort_value(start_value):
                continue
            if end_value and _sort_value(item.event_time) > _sort_value(end_value):
                continue
            filtered.append(item)
        filtered.sort(key=lambda item: _sort_value(item.event_time), reverse=True)
        return filtered[: max(1, min(int(limit), 1000))]

    def status_history(self, subsystem: str, record_id: str) -> list[TimelineRecord]:
        return [
            item
            for item in reversed(
                self.query(subsystem=subsystem, record_id=record_id, include_archived=True)
            )
            if (
                "STATUS" in item.event_type.upper()
                or item.event_type.upper() in {"ARCHIVE", "ARCHIVED", "RESTORE", "TRANSITION"}
                or item.metadata.get("status")
            )
        ]

    def record_target(self, item: TimelineRecord) -> dict[str, str]:
        return item.record_ref

    def _domain_events(self) -> list[TimelineRecord]:
        if not self.connections.database_path.is_file():
            return []
        with self.connections.connection(read_only=True) as connection:
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='domain_events'"
            ).fetchone()
            if not exists:
                return []
            rows = connection.execute(
                """SELECT e.sequence,e.event_id,e.module_id,e.event_type,e.entity_type,e.record_id,
                          e.payload_json AS event_payload_json,e.occurred_at,
                          r.payload_json AS record_payload_json,r.created_at,r.updated_at,
                          r.status,r.source
                   FROM domain_events e
                   LEFT JOIN records r ON r.module_id=e.module_id
                     AND r.entity_type=e.entity_type AND r.record_id=e.record_id
                   ORDER BY e.occurred_at DESC,e.sequence DESC"""
            ).fetchall()
        result: list[TimelineRecord] = []
        for row in rows:
            payload = json.loads(row["record_payload_json"] or "{}")
            event_payload = json.loads(row["event_payload_json"] or "{}")
            created = _timestamp(row["created_at"], row["occurred_at"])
            updated = _timestamp(row["updated_at"], row["occurred_at"])
            title = str(
                payload.get("title")
                or payload.get("decision")
                or payload.get("name")
                or row["record_id"]
            )
            status = str(payload.get("status") or row["status"] or "ACTIVE").upper()
            result.append(
                TimelineRecord(
                    record_id=str(row["record_id"]),
                    subsystem=str(row["module_id"]).lower(),
                    record_type=str(row["entity_type"]),
                    event_type=str(row["event_type"]),
                    title=title,
                    summary=str(payload.get("summary") or payload.get("content") or "")[:500],
                    event_time=_timestamp(row["occurred_at"]),
                    created_time=created,
                    updated_time=updated,
                    status=status,
                    source=str(row["source"] or "living-os-domain-event"),
                    metadata={
                        "event_id": row["event_id"],
                        "event_sequence": int(row["sequence"]),
                        **event_payload,
                    },
                )
            )
        return result

    def _execution_events(self, limit: int) -> list[TimelineRecord]:
        result: list[TimelineRecord] = []
        for item in self.executions.list(max(1, min(int(limit), 500))):
            subsystem = SUBSYSTEM_ALIASES.get(
                str(item.get("subsystem", "")), str(item.get("subsystem", "")).lower()
            )
            if subsystem not in TIMELINE_SUBSYSTEMS:
                continue
            metadata = dict(item.get("result") or {})
            target = str(metadata.get("target_id") or item.get("target") or item["execution_id"])
            action = str(item.get("action", "event")).upper()
            status = str(metadata.get("status") or item.get("status") or "UNKNOWN").upper()
            result.append(
                TimelineRecord(
                    record_id=target,
                    subsystem=subsystem,
                    record_type=str(metadata.get("record_type") or "operation"),
                    event_type=action,
                    title=str(metadata.get("title") or f"{subsystem}: {item.get('action', 'event')}"),
                    summary=str(metadata.get("summary") or item.get("error_message") or ""),
                    event_time=_timestamp(item.get("started_at")),
                    created_time=_timestamp(item.get("started_at")),
                    updated_time=_timestamp(item.get("completed_at"), str(item.get("started_at", ""))),
                    status=status,
                    source=str(item.get("source") or "living-os-execution"),
                    metadata={
                        "execution_id": item["execution_id"],
                        "correlation_id": item.get("correlation_id", ""),
                        "status": status,
                        **metadata,
                    },
                )
            )
        return result
