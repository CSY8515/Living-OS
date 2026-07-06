from __future__ import annotations

from typing import Any

from modules.storage import DECISION_LOG_FILE, append_jsonl, now_iso, read_jsonl


STATUSES = ["draft", "active", "review", "done", "archive"]


def read_decision_logs() -> list[dict[str, Any]]:
    return read_jsonl(DECISION_LOG_FILE)


def next_decision_id(records: list[dict[str, Any]]) -> str:
    max_number = 0
    for item in records:
        raw_id = str(item.get("id", ""))
        if raw_id.startswith("DEC-"):
            try:
                max_number = max(max_number, int(raw_id.split("-", 1)[1]))
            except (IndexError, ValueError):
                continue
    return f"DEC-{max_number + 1:05d}"


def save_decision(
    decision: str,
    reason: str,
    expected_result: str,
    actual_result: str,
    review_note: str,
    status: str,
) -> dict[str, Any]:
    records = read_decision_logs()
    timestamp = now_iso()
    record = {
        "id": next_decision_id(records),
        "decision": decision.strip(),
        "reason": reason.strip(),
        "expected_result": expected_result.strip(),
        "actual_result": actual_result.strip(),
        "review_note": review_note.strip(),
        "status": status if status in STATUSES else "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    append_jsonl(DECISION_LOG_FILE, record)
    return record


def decision_title(record: dict[str, Any]) -> str:
    return (
        str(record.get("decision") or record.get("final_decision") or record.get("situation") or "Untitled Decision")
    )


def get_decision_summary() -> dict[str, Any]:
    records = read_decision_logs()
    recent = sorted(
        records,
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )[:5]
    reviewable = [
        item
        for item in records
        if str(item.get("status", "")).lower() in {"draft", "active", "review"}
    ]
    return {
        "total_count": len(records),
        "reviewable_count": len(reviewable),
        "recent": recent,
    }


def render_decision_log() -> None:
    import streamlit as st

    st.title("Decision Log")
    st.caption("Record decisions, reasons, results, and future review notes.")

    with st.form("decision_log_form", clear_on_submit=True):
        decision = st.text_input("Decision")
        reason = st.text_area("Reason", height=120)
        expected_result = st.text_area("Expected Result", height=90)
        actual_result = st.text_area("Actual Result", height=90)
        review_note = st.text_area("Review Note", height=90)
        status = st.selectbox("Status", STATUSES, index=1)
        submitted = st.form_submit_button("Save Decision")

    if submitted:
        if not decision.strip():
            st.error("Decision is required.")
        else:
            record = save_decision(
                decision,
                reason,
                expected_result,
                actual_result,
                review_note,
                status,
            )
            st.success(f"Saved {record['id']}")

    st.divider()
    records = sorted(
        read_decision_logs(),
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )

    status_filter = st.selectbox("Filter by status", ["all", *STATUSES])
    if status_filter != "all":
        records = [
            item
            for item in records
            if str(item.get("status", "")).lower() == status_filter
        ]

    if not records:
        st.info("No decision logs.")
        return

    for item in records[:50]:
        with st.expander(f"{item.get('id', '-')} · {decision_title(item)} · {item.get('status', 'draft')}"):
            if item.get("reason"):
                st.markdown("**Reason**")
                st.write(item["reason"])
            if item.get("expected_result"):
                st.markdown("**Expected Result**")
                st.write(item["expected_result"])
            if item.get("actual_result"):
                st.markdown("**Actual Result**")
                st.write(item["actual_result"])
            if item.get("review_note"):
                st.markdown("**Review Note**")
                st.write(item["review_note"])
            st.caption(f"Created: {item.get('created_at', '-')}")
