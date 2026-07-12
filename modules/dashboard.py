from __future__ import annotations

from typing import Any


def render_dashboard(data: dict[str, Any]) -> None:
    import streamlit as st

    st.title("Living OS")
    st.caption("v0.8 · Daily operating system for real use")

    status = data.get("system_status", "NORMAL")
    if status == "NORMAL":
        st.success("System Status: NORMAL")
    elif status == "WARNING":
        st.warning("System Status: WARNING")
    else:
        st.error("System Status: ERROR")

    today_col, log_col, decision_col, report_col = st.columns(4)
    today_col.metric("Today", data.get("today", "-"))
    log_col.metric("Today Logs", data.get("today_log_count", 0))
    decision_col.metric("Reviewable Decisions", data.get("reviewable_decision_count", 0))
    report_col.metric("Reports", data.get("report_count", 0))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Recent Logs")
        recent_logs = data.get("recent_logs", [])
        if not recent_logs:
            st.info("No daily logs yet.")
        else:
            for item in recent_logs:
                st.markdown(f"**{item.get('date', '-')} · {item.get('title', 'Untitled')}**")
                content = str(item.get("content", "")).strip()
                if content:
                    st.caption(content[:160] + ("..." if len(content) > 160 else ""))

    with right:
        st.subheader("Recent Decisions")
        recent_decisions = data.get("recent_decisions", [])
        if not recent_decisions:
            st.info("No decisions yet.")
        else:
            for item in recent_decisions:
                title = item.get("decision") or item.get("final_decision") or item.get("situation") or "Untitled"
                st.markdown(f"**{item.get('id', '-')} · {title}**")
                st.caption(f"Status: {item.get('status', 'draft')}")

    st.divider()
    st.subheader("Recent Report")
    if data.get("recent_report"):
        st.write(data["recent_report"])
    else:
        st.info("No report generated yet.")
