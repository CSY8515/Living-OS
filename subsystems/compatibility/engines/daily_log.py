from __future__ import annotations

from typing import Any

from subsystems.compatibility.engines.storage import DAILY_LOG_FILE, now_iso, read_json, read_json_for_update, today_str, write_json


def load_daily_logs() -> list[dict[str, Any]]:
    data = read_json(DAILY_LOG_FILE, {"logs": []})
    logs = data.get("logs", []) if isinstance(data, dict) else []
    if not isinstance(logs, list):
        return []
    return [item for item in logs if isinstance(item, dict)]


def save_daily_logs(logs: list[dict[str, Any]]) -> None:
    write_json(DAILY_LOG_FILE, {"logs": logs})


def load_daily_logs_for_update() -> list[dict[str, Any]]:
    data = read_json_for_update(DAILY_LOG_FILE, {"logs": []})
    if not isinstance(data, dict) or not isinstance(data.get("logs"), list):
        raise ValueError("Daily Log storage has an invalid shape.")
    if not all(isinstance(item, dict) for item in data["logs"]):
        raise ValueError("Daily Log storage contains an invalid record.")
    return data["logs"]


def next_log_id(logs: list[dict[str, Any]]) -> str:
    max_number = 0
    for item in logs:
        raw_id = str(item.get("id", ""))
        if raw_id.startswith("LOG-"):
            try:
                max_number = max(max_number, int(raw_id.split("-", 1)[1]))
            except (IndexError, ValueError):
                continue
    return f"LOG-{max_number + 1:05d}"


def parse_tags(raw_tags: str) -> list[str]:
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def add_daily_log(
    log_date: str,
    title: str,
    content: str,
    tags: list[str],
    mood: str,
) -> dict[str, Any]:
    logs = load_daily_logs_for_update()
    timestamp = now_iso()
    record = {
        "id": next_log_id(logs),
        "date": log_date,
        "title": title.strip() or "Untitled Daily Log",
        "content": content.strip(),
        "tags": tags,
        "mood": mood.strip(),
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    logs.append(record)
    save_daily_logs(logs)
    return record


def render_daily_log() -> None:
    import streamlit as st

    st.title("Daily Log")
    st.caption("Write the daily record that powers Living OS Core.")

    with st.form("daily_log_form", clear_on_submit=True):
        log_date = st.date_input("Date").isoformat()
        title = st.text_input("Title")
        mood = st.text_input("Today Status", placeholder="NORMAL / TIRED / FOCUSED")
        tags = st.text_input("Tags", placeholder="work, learning, health")
        content = st.text_area("Daily Log", height=220)
        submitted = st.form_submit_button("Save Daily Log")

    if submitted:
        if not content.strip() and not title.strip():
            st.error("Title or daily log content is required.")
        else:
            try:
                record = add_daily_log(log_date, title, content, parse_tags(tags), mood)
            except (OSError, UnicodeError, ValueError):
                st.error("The Daily Log could not be saved. Existing data was not changed.")
            else:
                st.success(f"Saved {record['id']}")

    st.divider()
    st.subheader("Recent Daily Logs")
    logs = sorted(
        load_daily_logs(),
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )

    if not logs:
        st.info("No daily logs yet.")
        return

    for item in logs[:20]:
        with st.expander(f"{item.get('date', '-')} · {item.get('title', 'Untitled')}"):
            st.write(item.get("content", ""))
            tags = item.get("tags", [])
            if tags:
                st.caption("Tags: " + ", ".join(str(tag) for tag in tags))
            if item.get("mood"):
                st.caption(f"Status: {item['mood']}")
