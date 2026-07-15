from __future__ import annotations

from typing import Any, Callable

from subsystems.insight.engines.ai_credentials import resolve_api_key
from subsystems.insight.engines.ai_service import (
    AI_MODELS,
    DEFAULT_AI_MODEL,
    AIServiceError,
    analyze_daily_log,
    analyze_decision,
    record_source,
)
from subsystems.compatibility.engines.daily_log import load_daily_logs
from subsystems.compatibility.engines.decision_log import decision_title, read_decision_logs


DAILY_FIELDS = ("id", "date", "title", "content", "tags", "mood", "created_at", "updated_at")
DECISION_FIELDS = (
    "id",
    "decision",
    "reason",
    "expected_result",
    "actual_result",
    "review_note",
    "status",
    "created_at",
    "updated_at",
)


def _selected(records: list[dict[str, Any]], selected_id: str) -> dict[str, Any] | None:
    return next((item for item in records if str(item.get("id", "")) == selected_id), None)


def _render_analysis(
    state_key: str,
    record: dict[str, Any],
    fields: tuple[str, ...],
    button_label: str,
    analyzer: Callable[[str, str, str], str],
) -> None:
    import streamlit as st

    source = record_source(record, fields)
    st.warning("Only the selected fields shown below will be sent to OpenAI after you press the analysis button.")
    st.code(source, language="text")
    if st.button(button_label, key=f"{state_key}_button"):
        api_key, _ = resolve_api_key(str(st.session_state.get("ai_session_api_key", "")))
        if not api_key:
            st.error("Configure an OpenAI API key in Settings first.")
        else:
            try:
                st.session_state[state_key] = analyzer(api_key, st.session_state.ai_model, source)
            except AIServiceError as exc:
                st.error(str(exc))

    result = str(st.session_state.get(state_key, ""))
    if result:
        st.subheader("Read-only AI output")
        st.caption("Not saved. Verify this untrusted AI output before using it manually.")
        st.markdown(result)


def render_ai_analysis() -> None:
    import streamlit as st

    st.title("AI Analysis")
    st.caption("User-triggered, read-only OpenAI analysis. AI never changes or saves Living OS records.")
    if "ai_model" not in st.session_state or st.session_state.ai_model not in AI_MODELS:
        st.session_state.ai_model = DEFAULT_AI_MODEL
    st.selectbox("Model", AI_MODELS, key="ai_model")

    api_key, source_name = resolve_api_key(str(st.session_state.get("ai_session_api_key", "")))
    if api_key:
        st.success(f"AI is configured from: {source_name}.")
    else:
        st.info("AI is not configured. Enter an API key in Settings before requesting analysis.")

    daily_tab, decision_tab = st.tabs(["Daily Log", "Decision"])
    with daily_tab:
        logs = load_daily_logs()
        if not logs:
            st.info("No Daily Logs are available.")
        else:
            options = [str(item.get("id", "")) for item in logs]
            selected_id = st.selectbox(
                "Select Daily Log",
                options,
                format_func=lambda value: next(
                    (f"{value} — {item.get('date', '-')} — {item.get('title', 'Untitled')}" for item in logs if str(item.get("id", "")) == value),
                    value,
                ),
            )
            record = _selected(logs, selected_id)
            if record:
                _render_analysis("ai_daily_result", record, DAILY_FIELDS, "Analyze selected Daily Log", analyze_daily_log)

    with decision_tab:
        decisions = read_decision_logs()
        if not decisions:
            st.info("No Decisions are available.")
        else:
            options = [str(item.get("id", "")) for item in decisions]
            selected_id = st.selectbox(
                "Select Decision",
                options,
                format_func=lambda value: next(
                    (f"{value} — {decision_title(item)}" for item in decisions if str(item.get("id", "")) == value),
                    value,
                ),
            )
            record = _selected(decisions, selected_id)
            if record:
                _render_analysis("ai_decision_result", record, DECISION_FIELDS, "Analyze selected Decision", analyze_decision)
