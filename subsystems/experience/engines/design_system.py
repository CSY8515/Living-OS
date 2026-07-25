from __future__ import annotations

import base64
from functools import lru_cache
from html import escape
from pathlib import Path
from typing import Any, Iterable

from subsystems.experience.engines.localization import localized_streamlit, ui_text


ROOT = Path(__file__).resolve().parents[3]
WORLD_ASSET = ROOT / "assets" / "living-os-official-world.png"

STATUS_TONES = {
    "HEALTHY": "good", "NORMAL": "good", "ACTIVE": "good", "COMPLETED": "good",
    "READY": "info", "REGISTERED": "info", "PLANNED": "info", "PENDING": "warn",
    "DEGRADED": "warn", "WARNING": "warn", "FAILED": "danger", "ERROR": "danger",
    "MISSING": "danger", "ARCHIVED": "muted", "PAUSED": "muted", "ONLINE": "good",
}


@lru_cache(maxsize=1)
def _world_asset_uri() -> str:
    if not WORLD_ASSET.exists():
        return ""
    encoded = base64.b64encode(WORLD_ASSET.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def page_header(title: str, eyebrow: str, description: str = "", status: str | None = None) -> None:
    st = localized_streamlit()
    badge = ""
    if status:
        tone = STATUS_TONES.get(status.upper(), "info")
        badge = f'<span class="los-badge {tone}">{escape(str(ui_text(status)))}</span>'
    st.markdown(
        f'''<section class="los-page-header">
          <div><div class="los-eyebrow">{escape(str(ui_text(eyebrow)))}</div>
          <h1>{escape(str(ui_text(title)))}</h1><p>{escape(str(ui_text(description, context="caption")))}</p></div>{badge}
        </section>''',
        unsafe_allow_html=True,
    )


def system_banner(*, version: str, status: str, detail: str) -> None:
    st = localized_streamlit()
    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'''<div class="los-system-banner">
          <div class="los-orb" aria-hidden="true"><span></span><i></i></div>
          <div><div class="los-wordmark">리빙 <b>OS</b></div><small>{escape(version)} · 개인 생활 운영 시스템</small></div>
          <div class="los-system-state"><span class="los-dot {tone}"></span><div><b>{escape(str(ui_text(status)))}</b><small>{escape(str(ui_text(detail, context="caption")))}</small></div></div>
        </div>''', unsafe_allow_html=True,
    )


def home_world(
    *,
    greeting: str,
    date_label: str,
    summary: str,
    ai_brief: str,
    schedule: str,
    priority: str,
    status: str,
) -> None:
    """Render the concept-art-aligned Living OS world without changing navigation behavior."""
    st = localized_streamlit()
    image = _world_asset_uri()
    style = f"background-image:url('{image}')" if image else ""
    st.markdown(
        f'''<section class="los-world-stage" aria-label="리빙 OS 공식 세계" style="{style}">
          <div class="los-world-stars" aria-hidden="true"></div>
          <div class="los-world-orbits" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
          <div class="los-world-vignette" aria-hidden="true"></div>
          <header class="los-world-home"><span aria-hidden="true">⌂</span><b>홈</b></header>
          <article class="los-world-core">
            <span class="los-world-kicker">생활의 중심</span>
            <h1>리빙 OS</h1>
            <p>{escape(ui_text(greeting))}</p>
            <time>{escape(date_label)}</time>
            <div class="los-world-summary">{escape(ui_text(summary, context="caption"))}</div>
            <div class="los-world-enter"><span>오늘의 흐름</span><b>{escape(ui_text(status))}</b></div>
          </article>
          <aside class="los-world-brief">
            <span>오늘의 안내</span><p>{escape(ui_text(ai_brief, context="caption"))}</p>
            <dl><div><dt>일정</dt><dd>{escape(ui_text(schedule))}</dd></div>
            <div><dt>우선순위</dt><dd>{escape(ui_text(priority))}</dd></div></dl>
          </aside>
          <div class="los-world-axis" aria-hidden="true"><span></span></div>
        </section>''',
        unsafe_allow_html=True,
    )


def home_core(
    *, greeting: str, date_label: str, summary: str, ai_brief: str,
    schedule: str, priority: str, status: str,
) -> None:
    """Compatibility alias for the v2.0.9 official world renderer."""
    home_world(
        greeting=greeting, date_label=date_label, summary=summary, ai_brief=ai_brief,
        schedule=schedule, priority=priority, status=status,
    )


def status_card(label: str, value: Any, detail: str = "", status: str = "INFO") -> None:
    st = localized_streamlit()
    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'''<div class="los-card los-kpi {tone}"><div class="los-kpi-label">{escape(str(ui_text(label)))}</div>
        <div class="los-kpi-value">{escape(str(value))}</div><div class="los-kpi-detail">{escape(str(ui_text(detail, context="caption")))}</div></div>''',
        unsafe_allow_html=True,
    )


def panel_header(title: str, caption: str = "", action: str = "") -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<div class="los-panel-header"><div><h3>{escape(str(ui_text(title)))}</h3><p>{escape(str(ui_text(caption, context="caption")))}</p></div>
        <span>{escape(str(ui_text(action)))}</span></div>''', unsafe_allow_html=True,
    )


def activity_feed(items: Iterable[dict[str, Any]], *, empty: str = "아직 기록된 활동이 없습니다.") -> None:
    st = localized_streamlit()
    rows = list(items)
    if not rows:
        st.markdown(f'<div class="los-empty"><b>고요한 흐름</b><span>{escape(str(ui_text(empty, context="caption")))}</span></div>', unsafe_allow_html=True)
        return
    html = []
    for item in rows:
        html.append(
            '<div class="los-activity"><span class="los-activity-node"></span><div>'
            f'<b>{escape(str(item.get("title", "활동")))}</b>'
            f'<p>{escape(str(item.get("detail", "")))}</p></div>'
            f'<time>{escape(str(item.get("time", "")))}</time></div>'
        )
    st.markdown('<div class="los-feed">' + ''.join(html) + '</div>', unsafe_allow_html=True)


def health_row(label: str, status: str, detail: str = "") -> None:
    st = localized_streamlit()
    tone = STATUS_TONES.get(status.upper(), "info")
    st.markdown(
        f'<div class="los-health-row"><span class="los-dot {tone}"></span><b>{escape(str(ui_text(label)))}</b>'
        f'<span>{escape(str(ui_text(detail, context="caption")))}</span><em>{escape(str(ui_text(status)))}</em></div>', unsafe_allow_html=True,
    )


def state_panel(title: str, detail: str, *, state: str = "empty") -> None:
    st = localized_streamlit()
    labels = {"empty": "고요한 흐름", "loading": "정보를 불러오는 중", "error": "확인이 필요합니다"}
    tone = " danger" if state == "error" else ""
    st.markdown(
        f'<div class="los-empty{tone}"><b>{escape(labels.get(state, str(ui_text(state))))}</b>'
        f'<span>{escape(str(ui_text(title)))} · {escape(str(ui_text(detail, context="caption")))}</span></div>', unsafe_allow_html=True,
    )