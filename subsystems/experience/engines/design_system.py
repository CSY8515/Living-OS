from __future__ import annotations

import base64
from functools import lru_cache
from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence

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


def _tone(status: str) -> str:
    return STATUS_TONES.get(str(status).upper(), "info")


def navigation_identity(*, version: str, page: str, enabled: int) -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<section class="los-nav-identity">
          <div class="los-nav-sigil" aria-hidden="true"><i></i><span></span><b></b></div>
          <div class="los-nav-copy"><small>OFFICIAL LIFE SYSTEM</small><strong>리빙 OS</strong>
          <p>{escape(version)} · {enabled}개 모듈 연결</p></div>
        </section>
        <div class="los-nav-current"><span>현재 공간</span><b>{escape(str(ui_text(page)))}</b><i></i></div>''',
        unsafe_allow_html=True,
    )


def system_banner(*, version: str, status: str, detail: str) -> None:
    st = localized_streamlit()
    tone = _tone(status)
    st.markdown(
        f'''<header class="los-app-chrome">
          <div class="los-app-brand"><span class="los-mini-sigil" aria-hidden="true"><i></i></span>
          <div><small>LIVING INTELLIGENCE</small><b>리빙 OS</b></div></div>
          <div class="los-app-compass" aria-hidden="true"><i></i><i></i><b></b></div>
          <div class="los-app-state"><span class="los-dot {tone}"></span><div><b>{escape(str(ui_text(status)))}</b>
          <small>{escape(str(ui_text(detail, context="caption")))}</small></div><em>{escape(version)}</em></div>
        </header>''', unsafe_allow_html=True,
    )


def page_header(title: str, eyebrow: str, description: str = "", status: str | None = None) -> None:
    st = localized_streamlit()
    badge = ""
    if status:
        badge = f'<span class="los-badge {_tone(status)}"><i></i>{escape(str(ui_text(status)))}</span>'
    st.markdown(
        f'''<section class="los-page-hero">
          <div class="los-page-glyph" aria-hidden="true"><span></span><i></i></div>
          <div class="los-page-copy"><div class="los-eyebrow">{escape(str(ui_text(eyebrow)))}</div>
          <h1>{escape(str(ui_text(title)))}</h1><p>{escape(str(ui_text(description, context="caption")))}</p></div>
          <div class="los-page-orbit" aria-hidden="true"><i></i><i></i><b></b></div>{badge}
        </section>''',
        unsafe_allow_html=True,
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
    """Render the immersive official Living OS world while preserving all route behavior."""
    st = localized_streamlit()
    image = _world_asset_uri()
    style = f"--los-world-image:url('{image}')" if image else ""
    st.markdown(
        f'''<section class="los-world-stage" aria-label="리빙 OS 공식 세계" style="{style}">
          <div class="los-cosmos-depth" aria-hidden="true"><i></i><i></i><i></i></div>
          <div class="los-world-orbits" aria-hidden="true"><i></i><i></i><i></i><i></i><b></b></div>
          <header class="los-world-brand"><span class="los-world-emblem"><i></i><b></b></span>
            <div><small>PERSONAL LIFE UNIVERSE</small><strong>리빙 OS</strong></div>
          </header>
          <div class="los-world-home"><span aria-hidden="true">⌂</span><b>홈</b></div>
          <aside class="los-world-card los-world-card-left">
            <small>TODAY'S SIGNAL</small><b>{escape(str(ui_text(schedule)))}</b>
            <p>{escape(str(ui_text(summary, context="caption")))}</p><span>오늘의 흐름</span>
          </aside>
          <aside class="los-world-card los-world-card-right">
            <small>GUIDED FOCUS</small><b>{escape(str(ui_text(priority)))}</b>
            <p>{escape(str(ui_text(ai_brief, context="caption")))}</p><span>기록 기반 안내</span>
          </aside>
          <article class="los-world-core">
            <div class="los-life-dome" aria-hidden="true"><span></span><i></i><b></b></div>
            <span class="los-world-kicker">LIVING INTELLIGENCE CORE</span>
            <h1>리빙 OS</h1><p>{escape(str(ui_text(greeting)))}</p><time>{escape(date_label)}</time>
            <div class="los-world-enter"><span>시스템 상태</span><b>{escape(str(ui_text(status)))}</b><i></i></div>
          </article>
          <footer class="los-world-dock-label"><span>운영 허브</span><i></i><b>생활의 모든 흐름이 하나의 세계로 연결됩니다</b><i></i><span>11 SYSTEMS</span></footer>
        </section>''',
        unsafe_allow_html=True,
    )


def home_core(
    *, greeting: str, date_label: str, summary: str, ai_brief: str,
    schedule: str, priority: str, status: str,
) -> None:
    home_world(
        greeting=greeting, date_label=date_label, summary=summary, ai_brief=ai_brief,
        schedule=schedule, priority=priority, status=status,
    )


def metric_deck(cards: Sequence[dict[str, Any]], *, label: str = "LIVE SIGNALS") -> None:
    st = localized_streamlit()
    items = []
    glyphs = ("◈", "◇", "⌁", "✦", "◎", "△")
    for index, card in enumerate(cards):
        tone = _tone(str(card.get("status", "INFO")))
        items.append(
            f'''<article class="los-signal-card {tone}"><div class="los-signal-top"><span>{glyphs[index % len(glyphs)]}</span>
            <small>{escape(str(ui_text(card.get("label", "상태"))))}</small><i></i></div>
            <strong>{escape(str(card.get("value", "-")))}</strong>
            <p>{escape(str(ui_text(card.get("detail", "실시간 운영 상태"), context="caption")))}</p></article>'''
        )
    st.markdown(
        f'<section class="los-metric-section"><header><span>{escape(label)}</span><i></i><b>현재 생활 신호</b></header>'
        f'<div class="los-signal-grid">{"".join(items)}</div></section>', unsafe_allow_html=True,
    )


def workspace_rail(title: str, description: str, *, icon: str = "◇", meta: str = "LIVE WORKSPACE") -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<div class="los-workspace-rail"><span class="los-rail-icon">{escape(icon)}</span><div>
        <small>{escape(meta)}</small><b>{escape(str(ui_text(title)))}</b><p>{escape(str(ui_text(description, context="caption")))}</p>
        </div><i></i></div>''', unsafe_allow_html=True,
    )


def record_gallery(items: Iterable[dict[str, Any]], *, empty: str, limit: int = 6) -> None:
    st = localized_streamlit()
    rows = list(items)[:limit]
    if not rows:
        state_panel("기록이 아직 없습니다", empty)
        return
    cards = []
    for item in rows:
        title = item.get("title") or item.get("제목") or item.get("name") or "기록"
        subsystem = item.get("subsystem") or item.get("하위 시스템") or item.get("category") or "Living OS"
        status = item.get("status") or item.get("상태") or "READY"
        moment = item.get("event_time") or item.get("시간") or item.get("updated_at") or ""
        cards.append(
            f'''<article class="los-record-card"><div><span>{escape(str(ui_text(subsystem)))}</span>
            <em class="{_tone(str(status))}">{escape(str(ui_text(status)))}</em></div>
            <b>{escape(str(title))}</b><p>{escape(str(moment))}</p><i></i></article>'''
        )
    st.markdown(f'<div class="los-record-gallery">{"".join(cards)}</div>', unsafe_allow_html=True)


def status_card(label: str, value: Any, detail: str = "", status: str = "INFO") -> None:
    metric_deck(({"label": label, "value": value, "detail": detail, "status": status},))


def panel_header(title: str, caption: str = "", action: str = "") -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<div class="los-panel-header"><div><small>OPERATING PANEL</small><h3>{escape(str(ui_text(title)))}</h3>
        <p>{escape(str(ui_text(caption, context="caption")))}</p></div><span>{escape(str(ui_text(action)))}</span></div>''',
        unsafe_allow_html=True,
    )


def activity_feed(items: Iterable[dict[str, Any]], *, empty: str = "아직 기록된 활동이 없습니다.") -> None:
    st = localized_streamlit()
    rows = list(items)
    if not rows:
        state_panel("고요한 흐름", empty)
        return
    html = []
    for item in rows:
        html.append(
            '<div class="los-activity"><span class="los-activity-node"></span><div>'
            f'<b>{escape(str(item.get("title", "활동")))}</b><p>{escape(str(item.get("detail", "")))}</p></div>'
            f'<time>{escape(str(item.get("time", "")))}</time></div>'
        )
    st.markdown('<div class="los-feed">' + ''.join(html) + '</div>', unsafe_allow_html=True)


def health_row(label: str, status: str, detail: str = "") -> None:
    st = localized_streamlit()
    st.markdown(
        f'<div class="los-health-row"><span class="los-dot {_tone(status)}"></span><b>{escape(str(ui_text(label)))}</b>'
        f'<span>{escape(str(ui_text(detail, context="caption")))}</span><em>{escape(str(ui_text(status)))}</em></div>',
        unsafe_allow_html=True,
    )


def state_panel(title: str, detail: str, *, state: str = "empty") -> None:
    st = localized_streamlit()
    labels = {"empty": "고요한 흐름", "loading": "정보를 불러오는 중", "error": "확인이 필요합니다"}
    tone = " danger" if state == "error" else ""
    st.markdown(
        f'<div class="los-empty{tone}"><div class="los-empty-orbit"><i></i><span></span></div>'
        f'<b>{escape(labels.get(state, str(ui_text(state))))}</b><strong>{escape(str(ui_text(title)))}</strong>'
        f'<p>{escape(str(ui_text(detail, context="caption")))}</p></div>', unsafe_allow_html=True,
    )