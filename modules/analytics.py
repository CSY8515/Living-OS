from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from modules.archive import load_archive_items
from modules.daily_log import load_daily_logs
from modules.decision_log import read_decision_logs
from modules.storage import list_report_files


DATE_WINDOWS = {
    "All time": None,
    "Last 7 days": 6,
    "Last 30 days": 29,
    "This month": "month",
}


def parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def date_window_bounds(window: str) -> tuple[date | None, date | None]:
    today = date.today()
    selected = DATE_WINDOWS.get(window)
    if selected == "month":
        return today.replace(day=1), today
    if isinstance(selected, int):
        return today - timedelta(days=selected), today
    return None, None


def filter_logs_by_window(logs: list[dict[str, Any]], window: str) -> list[dict[str, Any]]:
    start, end = date_window_bounds(window)
    if start is None or end is None:
        return logs

    filtered: list[dict[str, Any]] = []
    for item in logs:
        parsed = parse_date(item.get("date"))
        if parsed is not None and start <= parsed <= end:
            filtered.append(item)
    return filtered


def count_tags(records: list[dict[str, Any]]) -> Counter[str]:
    tags: Counter[str] = Counter()
    for item in records:
        raw_tags = item.get("tags", [])
        if not isinstance(raw_tags, list):
            continue
        for tag in raw_tags:
            clean_tag = str(tag).strip()
            if clean_tag:
                tags[clean_tag] += 1
    return tags


def count_values(records: list[dict[str, Any]], field: str, fallback: str) -> Counter[str]:
    values: Counter[str] = Counter()
    for item in records:
        value = str(item.get(field) or fallback).strip() or fallback
        values[value] += 1
    return values


def counter_rows(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"Name": name, "Count": count}
        for name, count in counter.most_common()
    ]


def render_counter_table(title: str, counter: Counter[str], empty_message: str) -> None:
    import streamlit as st

    st.subheader(title)
    rows = counter_rows(counter)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info(empty_message)


def render_analytics() -> None:
    import streamlit as st

    st.title("Analytics")
    st.caption("Read-only summaries from existing Living OS records.")

    daily_logs = load_daily_logs()
    decisions = read_decision_logs()
    archive_items = load_archive_items()
    report_files = list_report_files()

    window = st.selectbox("Daily Log Range", list(DATE_WINDOWS.keys()))
    filtered_logs = filter_logs_by_window(daily_logs, window)

    reviewable_decisions = [
        item
        for item in decisions
        if str(item.get("status", "")).lower() in {"draft", "active", "review"}
    ]

    metric_cols = st.columns(5)
    metric_cols[0].metric("Daily Logs", len(filtered_logs))
    metric_cols[1].metric("All Daily Logs", len(daily_logs))
    metric_cols[2].metric("Decisions", len(decisions))
    metric_cols[3].metric("Reviewable", len(reviewable_decisions))
    metric_cols[4].metric("Reports", len(report_files))

    st.divider()

    log_left, log_right = st.columns(2)
    with log_left:
        render_counter_table(
            "Daily Log Tags",
            count_tags(filtered_logs),
            "No tags found for this range.",
        )
    with log_right:
        render_counter_table(
            "Daily Status",
            count_values(filtered_logs, "mood", "Unspecified"),
            "No daily status values found for this range.",
        )

    st.divider()

    decision_left, decision_right = st.columns(2)
    with decision_left:
        render_counter_table(
            "Decision Status",
            count_values(decisions, "status", "draft"),
            "No decisions found.",
        )
    with decision_right:
        render_counter_table(
            "Archive Tags",
            count_tags(archive_items),
            "No archive tags found.",
        )

    st.divider()

    archive_col, report_col = st.columns(2)
    with archive_col:
        render_counter_table(
            "Archive Sources",
            count_values(archive_items, "source", "Unspecified"),
            "No archive sources found.",
        )
    with report_col:
        st.subheader("Report Files")
        st.metric("Saved Reports", len(report_files))
        if report_files:
            for path in report_files[:10]:
                st.write(path.name)
        else:
            st.info("No report files found.")
