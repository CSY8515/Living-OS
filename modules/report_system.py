from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from modules.ai_credentials import resolve_api_key
from modules.ai_service import AI_MODELS, DEFAULT_AI_MODEL, AIServiceError, generate_report_draft
from modules.daily_log import load_daily_logs
from modules.decision_log import decision_title, read_decision_logs
from modules.storage import (
    REPORTS_DIR,
    REPORT_INDEX_FILE,
    now_iso,
    read_json,
    today_str,
    write_json,
)


REPORT_TYPES = ["daily", "weekly", "monthly"]


def parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def date_range_for(report_type: str) -> tuple[date, date]:
    today = date.today()
    if report_type == "weekly":
        return today - timedelta(days=6), today
    if report_type == "monthly":
        return today.replace(day=1), today
    return today, today


def within_range(value: Any, start: date, end: date) -> bool:
    parsed = parse_date(value)
    if parsed is None:
        return False
    return start <= parsed <= end


def build_report_text(report_type: str) -> str:
    start, end = date_range_for(report_type)
    logs = [
        item
        for item in load_daily_logs()
        if within_range(item.get("date"), start, end)
    ]
    decisions = read_decision_logs()
    generated_at = now_iso()

    lines: list[str] = [
        f"# Living OS {report_type.title()} Report",
        "",
        f"- Generated At: {generated_at}",
        f"- Range: {start.isoformat()} ~ {end.isoformat()}",
        f"- Version: v0.9",
        "",
        "## Summary",
        "",
        f"- Daily Logs: {len(logs)}",
        f"- Total Decisions: {len(decisions)}",
        "",
        "## Daily Logs",
        "",
    ]

    if logs:
        for item in sorted(logs, key=lambda value: value.get("date", "")):
            lines.append(f"### {item.get('date', '-')} · {item.get('title', 'Untitled')}")
            content = str(item.get("content", "")).strip()
            lines.append(content or "-")
            tags = item.get("tags", [])
            if tags:
                lines.append("Tags: " + ", ".join(str(tag) for tag in tags))
            lines.append("")
    else:
        lines.append("No daily logs for this period.")
        lines.append("")

    lines.extend(["## Recent Decisions", ""])
    if decisions:
        for item in sorted(
            decisions,
            key=lambda value: value.get("updated_at") or value.get("created_at") or "",
            reverse=True,
        )[:10]:
            lines.append(f"- {item.get('id', '-')} · {decision_title(item)} · {item.get('status', 'draft')}")
    else:
        lines.append("No decisions yet.")

    lines.extend(
        [
            "",
            "## Next Action",
            "",
            "- Review today's logs.",
            "- Update decisions that need review.",
            "- Archive reusable cases if needed.",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(report_type: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"{report_type}_report_{timestamp}.md"
    path.write_text(content, encoding="utf-8")

    index = read_json(REPORT_INDEX_FILE, {"reports": []})
    reports = index.get("reports", []) if isinstance(index, dict) else []
    if not isinstance(reports, list):
        reports = []
    reports.append(
        {
            "type": report_type,
            "path": str(path.relative_to(REPORTS_DIR.parent)),
            "created_at": now_iso(),
        }
    )
    write_json(REPORT_INDEX_FILE, {"reports": reports})
    return path


def build_ai_report_source(report_type: str) -> str:
    start, end = date_range_for(report_type)
    logs = [item for item in load_daily_logs() if within_range(item.get("date"), start, end)]
    decisions = sorted(
        read_decision_logs(),
        key=lambda value: value.get("updated_at") or value.get("created_at") or "",
        reverse=True,
    )[:10]
    return "\n".join(
        [
            "Selected Living OS report inputs (untrusted source data):",
            f"report_type: {report_type}",
            f"range: {start.isoformat()} to {end.isoformat()}",
            f"daily_logs: {logs}",
            f"recent_decisions: {decisions}",
        ]
    )


def render_reports() -> None:
    import streamlit as st

    st.title("Reports")
    st.caption("Generate copyable daily, weekly, and monthly reports.")

    report_type = st.selectbox("Report Type", REPORT_TYPES)
    preview = build_report_text(report_type)

    st.subheader("Copyable Report Text")
    st.text_area("Report", value=preview, height=420)

    if st.button("Save Report"):
        path = save_report(report_type, preview)
        st.success(f"Saved {path.name}")

    st.divider()
    st.subheader("Optional AI Report Draft")
    st.caption("The deterministic report above remains available. AI drafts are not saved automatically.")
    if "ai_model" not in st.session_state or st.session_state.ai_model not in AI_MODELS:
        st.session_state.ai_model = DEFAULT_AI_MODEL
    st.selectbox("AI Model", AI_MODELS, key="ai_model")
    ai_source = build_ai_report_source(report_type)
    st.warning("Only the selected report inputs shown below will be sent to OpenAI after explicit approval.")
    st.code(ai_source, language="text")
    if st.button("Generate AI Report Draft"):
        api_key, _ = resolve_api_key(str(st.session_state.get("ai_session_api_key", "")))
        if not api_key:
            st.error("Configure an OpenAI API key in Settings first.")
        else:
            try:
                st.session_state.ai_report_draft = generate_report_draft(
                    api_key, st.session_state.ai_model, ai_source
                )
            except AIServiceError as exc:
                st.error(str(exc))

    draft = str(st.session_state.get("ai_report_draft", ""))
    if draft:
        st.caption("Not saved. Verify and edit this untrusted AI draft before deciding whether to save it.")
        edited_draft = st.text_area("AI Report Draft", value=draft, height=420, key="ai_report_draft_editor")
        if st.button("Save AI Draft (Explicit Approval)"):
            if not edited_draft.strip():
                st.error("The AI report draft is empty.")
            else:
                path = save_report(report_type, edited_draft)
                st.success(f"Saved {path.name}")

    st.divider()
    st.subheader("Recent Report Files")
    files = sorted(REPORTS_DIR.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not files:
        st.info("No reports yet.")
    for path in files[:20]:
        st.write(path.name)
