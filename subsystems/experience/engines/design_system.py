from __future__ import annotations

from html import escape
from typing import Any, Iterable


STATUS_TONES = {
    "HEALTHY": "good", "NORMAL": "good", "ACTIVE": "good", "COMPLETED": "good",
    "READY": "info", "REGISTERED": "info", "PLANNED": "info", "PENDING": "warn",
    "DEGRADED": "warn", "WARNING": "warn", "FAILED": "danger", "ERROR": "danger",
    "MISSING": "danger", "ARCHIVED": "muted", "PAUSED": "muted",
}


def page_header(title: str, eyebrow: str, description: str = "", status: str | None = None) -> None:
    import streamlit as st

    badge = ""
    if status:
        tone = STATUS_TONES.get(status.upper(), "info")
        badge = f'<span class="los-badge {tone}">{escape(status)}</span>'
    st.markdown(
        f'''<section class="los-page-header">
          <div><div class="los-eyebrow">{escape(eyebrow)}</div>
          <h1>{escape(title)}</h1><p>{escape(description)}</p></div>{badge}
        </section>''',
        unsafe_allow_html=True,
    )


def system_banner(*, version: str, status: str, detail: str) -> None:
    import streamlit as st

    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'''<div class="los-system-banner">
          <div class="los-orb"><span></span></div>
          <div><div class="los-wordmark">LIVING <b>OS</b></div><small>{escape(version)} · PERSONAL COMMAND SYSTEM</small></div>
          <div class="los-system-state"><span class="los-dot {tone}"></span><div><b>{escape(status)}</b><small>{escape(detail)}</small></div></div>
        </div>''', unsafe_allow_html=True,
    )


def home_welcome(*, greeting: str, date_label: str, message: str, status: str) -> None:
    """Welcome surface for the personal operating system home."""
    import streamlit as st

    st.markdown(
        f'''<section class="los-home-welcome">
          <div class="los-home-kicker">LIVING OS · PERSONAL OPERATING SYSTEM</div>
          <h1>{escape(greeting)}</h1>
          <p>{escape(message)}</p>
          <div class="los-home-date"><span>{escape(date_label)}</span><i></i><b>{escape(status)}</b></div>
        </section>''',
        unsafe_allow_html=True,
    )


def home_today_cards(items: Iterable[dict[str, Any]]) -> None:
    import streamlit as st

    cards = []
    for item in items:
        cards.append(
            '<article class="los-home-card">'
            f'<span>{escape(str(item.get("label", "Today")))}</span>'
            f'<b>{escape(str(item.get("value", "Ready")))}</b>'
            f'<p>{escape(str(item.get("detail", "")))}</p></article>'
        )
    st.markdown('<div class="los-home-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)


def home_ai_brief(*, status: str, detail: str) -> None:
    import streamlit as st

    st.markdown(
        f'''<article class="los-home-brief"><div class="los-home-brief-mark">AI</div>
          <div><span>AI BRIEF · {escape(status)}</span><h3>Your context is ready.</h3>
          <p>{escape(detail)}</p></div></article>''',
        unsafe_allow_html=True,
    )


def status_card(label: str, value: Any, detail: str = "", status: str = "INFO") -> None:
    import streamlit as st

    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'''<div class="los-card los-kpi {tone}"><div class="los-kpi-label">{escape(label)}</div>
        <div class="los-kpi-value">{escape(str(value))}</div><div class="los-kpi-detail">{escape(detail)}</div></div>''',
        unsafe_allow_html=True,
    )


def panel_header(title: str, caption: str = "", action: str = "") -> None:
    import streamlit as st

    st.markdown(
        f'''<div class="los-panel-header"><div><h3>{escape(title)}</h3><p>{escape(caption)}</p></div>
        <span>{escape(action)}</span></div>''', unsafe_allow_html=True,
    )


def activity_feed(items: Iterable[dict[str, Any]], *, empty: str = "No activity recorded yet.") -> None:
    import streamlit as st

    rows = list(items)
    if not rows:
        st.markdown(f'<div class="los-empty"><b>QUIET SIGNAL</b><span>{escape(empty)}</span></div>', unsafe_allow_html=True)
        return
    html = []
    for item in rows:
        html.append(
            '<div class="los-activity"><span class="los-activity-node"></span><div>'
            f'<b>{escape(str(item.get("title", "Activity")))}</b>'
            f'<p>{escape(str(item.get("detail", "")))}</p></div>'
            f'<time>{escape(str(item.get("time", "")))}</time></div>'
        )
    st.markdown('<div class="los-feed">' + ''.join(html) + '</div>', unsafe_allow_html=True)


def health_row(label: str, status: str, detail: str = "") -> None:
    import streamlit as st

    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'<div class="los-health-row"><span class="los-dot {tone}"></span><b>{escape(label)}</b>'
        f'<span>{escape(detail)}</span><em>{escape(status)}</em></div>', unsafe_allow_html=True,
    )


def state_panel(title: str, detail: str, *, state: str = "empty") -> None:
    """Shared empty, loading, and error state presentation."""
    import streamlit as st

    labels = {"empty": "QUIET SIGNAL", "loading": "SYNCHRONIZING", "error": "ACTION REQUIRED"}
    tone = " danger" if state == "error" else ""
    st.markdown(
        f'<div class="los-empty{tone}"><b>{escape(labels.get(state, state.upper()))}</b>'
        f'<span>{escape(title)} · {escape(detail)}</span></div>', unsafe_allow_html=True,
    )
