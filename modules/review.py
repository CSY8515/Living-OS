from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from modules.archive import load_archive_items
from modules.daily_log import load_daily_logs
from modules.decision_log import decision_title, read_decision_logs
from modules.storage import list_report_files


DATE_WINDOWS = {
    "All time": None,
    "Last 7 days": 6,
    "Last 30 days": 29,
    "This month": "month",
}
REVIEWABLE_STATUSES = ("draft", "active", "review")


def parse_record_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None


def window_bounds(window: str, today: date | None = None) -> tuple[date | None, date | None]:
    current = today or date.today()
    selected = DATE_WINDOWS.get(window)
    if selected == "month":
        return current.replace(day=1), current
    if isinstance(selected, int):
        return current - timedelta(days=selected), current
    return None, None


def record_date(record: dict[str, Any]) -> date | None:
    for field in ("updated_at", "created_at", "date"):
        parsed = parse_record_date(record.get(field))
        if parsed is not None:
            return parsed
    return None


def filter_records_by_window(
    records: list[dict[str, Any]],
    window: str,
    today: date | None = None,
) -> list[dict[str, Any]]:
    start, end = window_bounds(window, today)
    if start is None or end is None:
        return records
    return [
        record
        for record in records
        if (parsed := record_date(record)) is not None and start <= parsed <= end
    ]


def report_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        try:
            modified_at = datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat()
        except OSError:
            modified_at = ""
        records.append(
            {
                "type": "Report",
                "id": path.name,
                "title": path.name,
                "updated_at": modified_at,
            }
        )
    return records


def reviewable_decisions(
    decisions: list[dict[str, Any]], status: str = "all"
) -> list[dict[str, Any]]:
    selected = status.lower()
    records = [
        item
        for item in decisions
        if str(item.get("status", "")).lower() in REVIEWABLE_STATUSES
    ]
    if selected != "all":
        records = [
            item for item in records if str(item.get("status", "")).lower() == selected
        ]
    return sorted(records, key=activity_sort_value, reverse=True)


def activity_sort_value(record: dict[str, Any]) -> tuple[int, str]:
    value = record.get("updated_at") or record.get("created_at") or record.get("date") or ""
    if parse_record_date(value) is None:
        return 0, ""
    return 1, str(value)


def recent_activity(
    daily_logs: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    archive_items: list[dict[str, Any]],
    reports: list[dict[str, Any]],
    limit: int = 20,
) -> list[dict[str, Any]]:
    activity: list[dict[str, Any]] = []
    for item in daily_logs:
        activity.append(
            {
                **item,
                "type": "Daily Log",
                "title": str(item.get("title") or "Untitled Daily Log"),
            }
        )
    for item in decisions:
        activity.append({**item, "type": "Decision", "title": decision_title(item)})
    for item in archive_items:
        activity.append(
            {
                **item,
                "type": "Archive",
                "title": str(item.get("title") or "Untitled Archive Item"),
            }
        )
    activity.extend(reports)
    return sorted(activity, key=activity_sort_value, reverse=True)[:limit]


def render_review() -> None:
    import streamlit as st

    st.title("Review Workspace")
    st.caption("Read-only review of existing Living OS records.")

    daily_logs = load_daily_logs()
    decisions = read_decision_logs()
    archive_items = load_archive_items()
    reports = report_records(list_report_files())

    filter_col, status_col = st.columns(2)
    window = filter_col.selectbox("Review Range", list(DATE_WINDOWS.keys()))
    status = status_col.selectbox("Decision Status", ["all", *REVIEWABLE_STATUSES])

    filtered_logs = filter_records_by_window(daily_logs, window)
    filtered_decisions = filter_records_by_window(decisions, window)
    filtered_archive = filter_records_by_window(archive_items, window)
    filtered_reports = filter_records_by_window(reports, window)
    queue = reviewable_decisions(filtered_decisions, status)

    metric_cols = st.columns(5)
    metric_cols[0].metric("Daily Logs", len(filtered_logs))
    metric_cols[1].metric("Decisions", len(filtered_decisions))
    metric_cols[2].metric("Needs Review", len(queue))
    metric_cols[3].metric("Archive Items", len(filtered_archive))
    metric_cols[4].metric("Reports", len(filtered_reports))

    st.divider()
    st.subheader("Decision Review Queue")
    if queue:
        for item in queue:
            latest = item.get("updated_at") or item.get("created_at") or "-"
            st.markdown(
                f"**{item.get('id', '-')} · {decision_title(item)}**  \n"
                f"Status: {item.get('status', 'draft')} · Updated: {latest}"
            )
    else:
        st.info("No decisions need review for the selected filters.")

    st.divider()
    st.subheader("Recent Activity")
    activity = recent_activity(
        filtered_logs,
        filtered_decisions,
        filtered_archive,
        filtered_reports,
    )
    if not activity:
        st.info("No activity found for the selected range.")
        return

    for item in activity:
        latest = item.get("updated_at") or item.get("created_at") or item.get("date") or "-"
        st.markdown(f"**{item.get('type', 'Record')} · {item.get('title', 'Untitled')}**")
        st.caption(f"{item.get('id', '-')} · {latest}")
