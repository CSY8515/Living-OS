from __future__ import annotations

from typing import Any

from modules.storage import ARCHIVE_FILE, now_iso, read_json, write_json


def load_archive_items() -> list[dict[str, Any]]:
    data = read_json(ARCHIVE_FILE, {"items": []})
    items = data.get("items", []) if isinstance(data, dict) else []
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def save_archive_items(items: list[dict[str, Any]]) -> None:
    write_json(ARCHIVE_FILE, {"items": items})


def next_archive_id(items: list[dict[str, Any]]) -> str:
    max_number = 0
    for item in items:
        raw_id = str(item.get("id", ""))
        if raw_id.startswith("ARC-"):
            try:
                max_number = max(max_number, int(raw_id.split("-", 1)[1]))
            except (IndexError, ValueError):
                continue
    return f"ARC-{max_number + 1:05d}"


def parse_tags(raw_tags: str) -> list[str]:
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def add_archive_item(title: str, content: str, source: str, tags: list[str]) -> dict[str, Any]:
    items = load_archive_items()
    timestamp = now_iso()
    record = {
        "id": next_archive_id(items),
        "title": title.strip() or "Untitled Archive Item",
        "content": content.strip(),
        "source": source.strip(),
        "tags": tags,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    items.append(record)
    save_archive_items(items)
    return record


def matches_query(item: dict[str, Any], query: str) -> bool:
    if not query:
        return True
    target = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("content", "")),
            str(item.get("source", "")),
            " ".join(str(tag) for tag in item.get("tags", [])),
        ]
    ).lower()
    return query.lower() in target


def render_archive() -> None:
    import streamlit as st

    st.title("Archive")
    st.caption("Store reusable records, references, and case material as JSON.")

    with st.form("archive_form", clear_on_submit=True):
        title = st.text_input("Title")
        source = st.text_input("Source", placeholder="daily log / decision / report / external")
        tags = st.text_input("Tags", placeholder="casebook, rule-candidate")
        content = st.text_area("Content", height=180)
        submitted = st.form_submit_button("Save Archive Item")

    if submitted:
        if not title.strip() and not content.strip():
            st.error("Title or content is required.")
        else:
            record = add_archive_item(title, content, source, parse_tags(tags))
            st.success(f"Saved {record['id']}")

    st.divider()
    query = st.text_input("Search Archive")
    items = sorted(
        load_archive_items(),
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )
    filtered = [item for item in items if matches_query(item, query)]

    st.caption(f"{len(filtered)} item(s)")
    if not filtered:
        st.info("No archive items found.")
        return

    for item in filtered[:100]:
        with st.expander(f"{item.get('id', '-')} · {item.get('title', 'Untitled')}"):
            st.write(item.get("content", ""))
            if item.get("source"):
                st.caption(f"Source: {item['source']}")
            tags = item.get("tags", [])
            if tags:
                st.caption("Tags: " + ", ".join(str(tag) for tag in tags))
