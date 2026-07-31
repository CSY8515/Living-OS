from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Any, Collection, Iterable

from subsystems.foundation.engines.timeline import TimelineRecord, TimelineService


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")
    start = date(year, month, 1)
    end = date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
    return start, end


def _percent_change(current: int, previous: int) -> float | None:
    if previous == 0:
        return 100.0 if current else 0.0
    return round(((current - previous) / previous) * 100, 1)


class AnalyticsEngine:
    """Read-only analytics derived from the common Timeline contract."""

    def __init__(
        self,
        timeline: TimelineService,
        *,
        visible_subsystems: Collection[str] | None = None,
    ) -> None:
        self.timeline = timeline
        self.visible_subsystems = (
            frozenset(visible_subsystems) if visible_subsystems is not None else None
        )

    def _visible(self, records: Iterable[TimelineRecord]) -> list[TimelineRecord]:
        return [
            item
            for item in records
            if "execution_id" not in item.metadata
            and (
                self.visible_subsystems is None
                or item.subsystem in self.visible_subsystems
            )
        ]

    def summary(
        self,
        start: date,
        end: date,
        *,
        subsystem: str | None = None,
        include_archived: bool = True,
    ) -> dict[str, Any]:
        if start > end:
            raise ValueError("start cannot be after end")
        records = self._visible(
            self.timeline.query(
                start=start,
                end=end,
                subsystem=subsystem,
                include_archived=include_archived,
                limit=1000,
            )
        )
        by_subsystem = Counter(item.subsystem for item in records)
        by_status = Counter(item.status for item in records)
        by_category = Counter(item.category for item in records)
        return {
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
            "total_activity": len(records),
            "active_activity": sum(not item.archived for item in records),
            "archived_activity": sum(item.archived for item in records),
            "subsystem_count": len(by_subsystem),
            "by_subsystem": dict(sorted(by_subsystem.items())),
            "by_status": dict(sorted(by_status.items())),
            "by_category": dict(sorted(by_category.items())),
        }

    def monthly_summary(
        self, year: int, month: int, *, subsystem: str | None = None
    ) -> dict[str, Any]:
        start, end = _month_bounds(year, month)
        return {
            "summary_type": "monthly",
            **self.summary(start, end, subsystem=subsystem),
        }

    def yearly_summary(
        self, year: int, *, subsystem: str | None = None
    ) -> dict[str, Any]:
        return {
            "summary_type": "yearly",
            **self.summary(
                date(year, 1, 1),
                date(year, 12, 31),
                subsystem=subsystem,
            ),
        }

    def trend(
        self,
        start: date,
        end: date,
        *,
        subsystem: str | None = None,
        granularity: str = "month",
    ) -> list[dict[str, Any]]:
        if granularity not in {"day", "month", "year"}:
            raise ValueError("granularity must be day, month, or year")
        records = self._visible(
            self.timeline.query(
                start=start, end=end, subsystem=subsystem, limit=1000
            )
        )
        grouped: dict[str, list[TimelineRecord]] = defaultdict(list)
        sizes = {"day": 10, "month": 7, "year": 4}
        for item in records:
            grouped[item.event_time[: sizes[granularity]]].append(item)
        return [
            {
                "period": period,
                "activity": len(items),
                "active": sum(not item.archived for item in items),
                "archived": sum(item.archived for item in items),
                "subsystems": len({item.subsystem for item in items}),
            }
            for period, items in sorted(grouped.items())
        ]

    def comparison(
        self,
        start: date,
        end: date,
        *,
        subsystem: str | None = None,
    ) -> dict[str, Any]:
        if start > end:
            raise ValueError("start cannot be after end")
        duration = end - start
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - duration
        current = self.summary(start, end, subsystem=subsystem)
        previous = self.summary(previous_start, previous_end, subsystem=subsystem)
        current_by = Counter(current["by_subsystem"])
        previous_by = Counter(previous["by_subsystem"])
        names = sorted(set(current_by) | set(previous_by))
        return {
            "current": current,
            "previous": previous,
            "activity_change": current["total_activity"] - previous["total_activity"],
            "growth_percent": _percent_change(
                current["total_activity"], previous["total_activity"]
            ),
            "by_subsystem": [
                {
                    "subsystem": name,
                    "current": current_by[name],
                    "previous": previous_by[name],
                    "change": current_by[name] - previous_by[name],
                    "growth_percent": _percent_change(
                        current_by[name], previous_by[name]
                    ),
                }
                for name in names
            ],
        }

    def growth_analysis(
        self,
        *,
        as_of: date | None = None,
        months: int = 12,
        subsystem: str | None = None,
    ) -> dict[str, Any]:
        if months < 2 or months > 36:
            raise ValueError("months must be between 2 and 36")
        selected = as_of or date.today()
        first_month_index = selected.year * 12 + selected.month - months
        start = date(first_month_index // 12, first_month_index % 12 + 1, 1)
        trend = self.trend(start, selected, subsystem=subsystem, granularity="month")
        first = trend[0]["activity"] if trend else 0
        last = trend[-1]["activity"] if trend else 0
        return {
            "months": months,
            "start": start.isoformat(),
            "end": selected.isoformat(),
            "trend": trend,
            "net_growth": last - first,
            "growth_percent": _percent_change(last, first),
        }

    def dashboard(
        self, *, as_of: date | None = None, recent_limit: int = 8
    ) -> dict[str, Any]:
        selected = as_of or date.today()
        start = selected - timedelta(days=29)
        summary = self.summary(start, selected)
        recent = self._visible(
            self.timeline.query(limit=max(1, min(recent_limit, 20)))
        )
        busiest = max(
            summary["by_subsystem"],
            key=summary["by_subsystem"].get,
            default="-",
        )
        return {
            "summary": summary,
            "recent_activity": [item.to_dict() for item in recent],
            "state_cards": [
                {"label": "30-day activity", "value": summary["total_activity"], "state": "NORMAL"},
                {"label": "Active records", "value": summary["active_activity"], "state": "NORMAL"},
                {"label": "Archived", "value": summary["archived_activity"], "state": "INFO"},
                {"label": "Busiest subsystem", "value": busiest, "state": "NORMAL"},
            ],
            "quick_actions": [
                {"label": "Open Timeline", "target": "Timeline"},
                {"label": "Search records", "target": "Search"},
                {"label": "Create report", "target": "Reports"},
                {"label": "Review analytics", "target": "Analytics"},
            ],
        }
