from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from subsystems.foundation.engines.timeline import TimelineRecord, TimelineService


@dataclass(frozen=True)
class SearchResult:
    subsystem: str
    record_type: str
    record_id: str
    title: str
    summary: str
    category: str
    status: str
    event_time: str
    archived: bool
    score: int
    target: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsystem": self.subsystem,
            "record_type": self.record_type,
            "record_id": self.record_id,
            "title": self.title,
            "summary": self.summary,
            "category": self.category,
            "status": self.status,
            "event_time": self.event_time,
            "archived": self.archived,
            "score": self.score,
            "target": dict(self.target),
        }


class GlobalSearchEngine:
    """Unified read-only search over Timeline-backed subsystem records."""

    def __init__(self, timeline: TimelineService) -> None:
        self.timeline = timeline

    @staticmethod
    def _score(item: TimelineRecord, needle: str) -> int:
        if not needle:
            return 1
        fields = {
            "record_id": item.record_id.casefold(),
            "title": item.title.casefold(),
            "summary": item.summary.casefold(),
            "category": item.category.casefold(),
            "metadata": json.dumps(
                dict(item.metadata), ensure_ascii=False, default=str
            ).casefold(),
        }
        return (
            12 * (needle == fields["record_id"])
            + 10 * (needle == fields["title"])
            + 8 * (needle in fields["title"])
            + 5 * (needle in fields["summary"])
            + 4 * (needle in fields["category"])
            + 2 * (needle in fields["metadata"])
            + 1 * (needle in fields["record_id"])
        )

    def search(
        self,
        query: str = "",
        *,
        subsystem: str | None = None,
        category: str | None = None,
        status: str | None = None,
        include_archived: bool = True,
        sort_by: str = "relevance",
        descending: bool = True,
        limit: int = 100,
    ) -> list[SearchResult]:
        if sort_by not in {"relevance", "event_time", "title", "subsystem"}:
            raise ValueError("Unsupported search sort")
        needle = query.strip().casefold()
        records = self.timeline.query(
            subsystem=subsystem,
            category=category,
            search=query,
            include_archived=include_archived,
            limit=1000,
        )
        unique: dict[tuple[str, str, str], TimelineRecord] = {}
        for item in records:
            key = (item.subsystem, item.record_type, item.record_id)
            if key not in unique:
                unique[key] = item
        results = []
        for item in unique.values():
            if status and item.status.casefold() != status.casefold():
                continue
            score = self._score(item, needle)
            if needle and score == 0:
                continue
            results.append(
                SearchResult(
                    subsystem=item.subsystem,
                    record_type=item.record_type,
                    record_id=item.record_id,
                    title=item.title,
                    summary=item.summary,
                    category=item.category,
                    status=item.status,
                    event_time=item.event_time,
                    archived=item.archived,
                    score=score,
                    target=item.record_ref,
                )
            )
        key = {
            "relevance": lambda item: (item.score, item.event_time),
            "event_time": lambda item: item.event_time,
            "title": lambda item: item.title.casefold(),
            "subsystem": lambda item: (item.subsystem, item.title.casefold()),
        }[sort_by]
        results.sort(key=key, reverse=descending)
        return results[: max(1, min(int(limit), 500))]

    def subsystem_search(
        self, subsystem: str, query: str, **filters: Any
    ) -> list[SearchResult]:
        return self.search(query, subsystem=subsystem, **filters)
