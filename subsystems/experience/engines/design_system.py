from __future__ import annotations

from base64 import b64encode
from functools import lru_cache

from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence

from subsystems.experience.engines.localization import localized_streamlit, ui_text
from subsystems.experience.engines.living_world import (
    FEATURE_WORLD_IDENTITY,
    LivingWorldDefinition,
    build_living_world_definition,
)
from subsystems.experience.engines.ui_interface import (
    LIVING_OS_UI,
    resolve_ui_asset,
    resolve_ui_icon,
)
from subsystems.experience.engines.ultra_brain_world import active_inherited_world


ROOT = Path(__file__).resolve().parents[3]
WORLD_ASSET = ROOT / "assets" / "living-os-v2092-official-style-clean.png"
SUBSYSTEM_WORLD_ASSETS = {
    "finance": ROOT / "assets" / "subsystem-worlds" / "finance-world.png",
    "investment": ROOT / "assets" / "subsystem-worlds" / "investment-world.png",
    "job": ROOT / "assets" / "subsystem-worlds" / "job-world.png",
    "health": ROOT / "assets" / "subsystem-worlds" / "health-world.png",
    "vehicle": ROOT / "assets" / "subsystem-worlds" / "vehicle-world.png",
    "housing": ROOT / "assets" / "subsystem-worlds" / "housing-world.png",
    "food": ROOT / "assets" / "subsystem-worlds" / "food-world.png",
    "knowledge": ROOT / "assets" / "subsystem-worlds" / "knowledge-world.png",
    "routine": ROOT / "assets" / "subsystem-worlds" / "routine-world.png",
    "growth": ROOT / "assets" / "subsystem-worlds" / "growth-world.png",
}

STATUS_TONES = {
    "HEALTHY": "good", "NORMAL": "good", "ACTIVE": "good", "COMPLETED": "good",
    "READY": "info", "REGISTERED": "info", "PLANNED": "info", "PENDING": "warn",
    "DEGRADED": "warn", "WARNING": "warn", "FAILED": "danger", "ERROR": "danger",
    "MISSING": "danger", "ARCHIVED": "muted", "PAUSED": "muted", "ONLINE": "good",
}


def _living_world_definition() -> LivingWorldDefinition:
    inherited = active_inherited_world()
    contract = LIVING_OS_UI.resolve()
    theme_id = inherited.requested_theme if inherited else contract.theme_id
    world_id = inherited.world if inherited else f"{theme_id}-living-world"
    home_asset = resolve_ui_asset("background.home", str(WORLD_ASSET))
    overrides: dict[str, str] = {}
    for scene in FEATURE_WORLD_IDENTITY:
        default = str(SUBSYSTEM_WORLD_ASSETS.get(scene, ""))
        resolved = resolve_ui_asset(f"background.module.{scene}", default)
        if resolved and resolved != default:
            overrides[scene] = resolved
    return build_living_world_definition(
        theme_id=theme_id,
        world_id=world_id,
        home_asset=home_asset,
        feature_assets=SUBSYSTEM_WORLD_ASSETS,
        feature_overrides=overrides,
    )



@lru_cache(maxsize=16)
def _asset_data_uri(path_value: str) -> str:
    """Return a stable inline image URL so Streamlit cannot reflow World artwork."""
    if path_value.startswith(("data:image/", "https://", "http://")):
        return path_value
    path = Path(path_value)
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime};base64,{b64encode(path.read_bytes()).decode('ascii')}"

def _tone(status: str) -> str:
    return STATUS_TONES.get(str(status).upper(), "info")


SCENE_MATCHES = (
    (("finance", "재무"), "finance"),
    (("investment", "투자"), "investment"),
    (("job", "직업"), "job"),
    (("health", "건강"), "health"),
    (("vehicle", "차량"), "vehicle"),
    (("housing", "주거"), "housing"),
    (("food", "식사"), "food"),
    (("knowledge", "지식"), "knowledge"),
    (("routine", "루틴"), "routine"),
    (("growth", "자기계발"), "growth"),
    (("collaboration", "협업"), "collaboration"),
    (("timeline", "타임라인"), "timeline"),
    (("report", "리포트"), "reports"),
    (("analytics", "분석"), "analytics"),
    (("search", "검색"), "search"),
    (("journal", "일지"), "today"),
    (("decision", "의사결정"), "decision"),
    (("ai briefing", "ai 브리핑"), "assistant"),
)

SCENE_LABELS = {
    "finance": ("재무 금고", "장부 · 예산 · 월 결산"),
    "investment": ("투자 관측소", "자산 흐름 · 가치 · 추세"),
    "job": ("커리어 정거장", "기회 · 지원 · 다음 행동"),
    "health": ("건강 생체 정원", "몸의 신호 · 검사 · 목표"),
    "vehicle": ("모빌리티 베이", "운행 · 주유 · 정비"),
    "housing": ("생활 주거 공간", "계약 · 월세 · 관리비"),
    "food": ("식생활 아틀리에", "재료 · 레시피 · 식사"),
    "knowledge": ("지식 서고", "배움 · 기록 · 연결"),
    "routine": ("리듬 순환실", "반복 · 실행 · 연속성"),
    "growth": ("성장 온실", "목표 · 진행 · 성찰"),
    "collaboration": ("협업 연결망", "사람 · 약속 · 결과"),
    "timeline": ("생활 시간 궤도", "모든 활동의 흐름"),
    "reports": ("생활 기록 지도", "일간 · 주간 · 월간 · 연간"),
    "analytics": ("생활 관측소", "추세 · 비교 · 성장"),
    "search": ("생활 기록 탐색", "모든 공간을 한 번에"),
    "today": ("오늘의 기록", "지금의 흐름을 남기는 공간"),
    "decision": ("의사결정 기록", "선택 · 근거 · 결과"),
    "assistant": ("AI 브리핑", "내 기록을 읽는 보조 관측소"),
    "living": ("생활 중심 공간", "기록 · 실행 · 회고"),
}


def _scene_for(title: str, eyebrow: str = "") -> str:
    value = f"{title} {eyebrow}".lower()
    for needles, scene in SCENE_MATCHES:
        if any(needle in value for needle in needles):
            return scene
    return "living"


def official_user_navigation(*, page: str, feature: bool) -> None:
    st = localized_streamlit()
    kind = "생활 기능" if feature else "생활 허브"
    st.markdown(
        f'''<nav class="los-user-navigation" aria-label="리빙 OS 사용자 탐색">
          <div class="los-user-mark"><span aria-hidden="true"><i></i></span>
          <div><small>공식 생활 공간</small><b>리빙 OS</b></div></div>
          <div class="los-user-location"><small>{kind}</small><strong>{escape(str(ui_text(page)))}</strong></div>
          <div class="los-user-pulse" aria-hidden="true"><i></i><b></b><span></span></div>
        </nav>''', unsafe_allow_html=True,
    )


def navigation_identity(*, version: str, page: str, enabled: int) -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<section class="los-nav-identity">
          <div class="los-nav-sigil" aria-hidden="true"><i></i><span></span><b></b></div>
          <div class="los-nav-copy"><small>공식 생활 시스템</small><strong>리빙 OS</strong>
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
          <div><small>생활 인텔리전스</small><b>리빙 OS</b></div></div>
          <div class="los-app-compass" aria-hidden="true"><i></i><i></i><b></b></div>
          <div class="los-app-state"><span class="los-dot {tone}"></span><div><b>{escape(str(ui_text(status)))}</b>
          <small>{escape(str(ui_text(detail, context="caption")))}</small></div><em>{escape(version)}</em></div>
        </header>''', unsafe_allow_html=True,
    )


def page_header(title: str, eyebrow: str, description: str = "", status: str | None = None) -> None:
    st = localized_streamlit()
    scene = _scene_for(title, eyebrow)
    world = _living_world_definition()
    feature = world.feature(scene)
    scene_title, scene_detail = SCENE_LABELS[scene]
    badge = ""
    if status:
        badge = f'<span class="los-badge {_tone(status)}"><i></i>{escape(str(ui_text(status)))}</span>'
    hero = f'''<section class="los-page-hero los-scene-{scene}">
          <div class="los-scene-atmosphere" aria-hidden="true"><i></i><i></i><i></i></div>
          <div class="los-feature-scene" aria-hidden="true"><span></span><i></i><b></b><em></em></div>
          <div class="los-page-glyph" aria-hidden="true"><span></span><i></i></div>
          <div class="los-page-copy"><div class="los-eyebrow">{escape(scene_title)}</div>
          <h1>{escape(str(ui_text(title)))}</h1><p>{escape(str(ui_text(description, context="caption")))}</p>
          <small>{escape(scene_detail)}</small></div>
          <div class="los-page-orbit" aria-hidden="true"><i></i><i></i><b></b></div>{badge}
        </section>'''
    image = ""
    backdrop = ""
    if feature.asset:
        asset_uri = _asset_data_uri(feature.asset)
        image = f'<img src="{asset_uri}" alt="">'
        backdrop = f'<div class="los-fixed-world-backdrop" aria-hidden="true"><img src="{asset_uri}" alt=""></div>'
    st.markdown(
        f'''<div class="los-world-scene-scope los-world-scene-{scene} los-world-theme-{escape(world.theme_id)} los-world-frame-{escape(world.language.frame)} los-feature-composition-{escape(feature.composition)}"
          data-living-world-context="feature" data-hierarchy-level="{escape(world.hierarchy_level)}"
          data-theme-world="{escape(world.world_id)}" data-theme-composition="{escape(world.language.composition)}"
          data-feature-id="{escape(feature.feature_id)}" data-main-object="{escape(feature.main_object)}"
          data-navigation-object="{escape(feature.navigation_object)}" data-feature-composition="{escape(feature.composition)}"
          data-feature-asset-state="{escape(feature.asset_state)}" data-theme-material="{escape(feature.material)}"
          data-theme-lighting="{escape(feature.lighting)}" data-theme-texture="{escape(feature.texture)}">
          {backdrop}
          <section class="los-subsystem-world-hero">{image}{hero}</section>
          <section class="los-world-threshold"><span>리빙 OS 월드</span><i></i>
            <strong>{escape(scene_title)}</strong><em>{escape(scene_detail)}</em>
          </section>
        </div>''',
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
    """Render the final-answer home with direct, non-reflowing interaction layers."""
    st = localized_streamlit()
    world = _living_world_definition()
    home_asset = world.home_asset
    world_uri = _asset_data_uri(home_asset)
    ornament_dir = ROOT / "assets" / "ornaments"
    roof_assets = {
        "bud": resolve_ui_asset("ornament.roof.bud", str(ornament_dir / "roof-bud.png")),
        "sprout": resolve_ui_asset("ornament.roof.sprout", str(ornament_dir / "roof-sprout.png")),
        "blossom": resolve_ui_asset("ornament.roof.blossom", str(ornament_dir / "roof-blossom.png")),
        "tree": resolve_ui_asset("ornament.roof.tree", str(ornament_dir / "roof-living-tree.png")),
    }
    roof_uris = {name: _asset_data_uri(path) for name, path in roof_assets.items()}
    roof_styles = "".join(
        f"--los-roof-{name}:url('{uri}');" for name, uri in roof_uris.items()
    )
    symbol_dir = ROOT / "assets" / "dome-symbols"
    symbol_assets = {
        name: resolve_ui_asset(
            f"icon.world.{name}", str(symbol_dir / f"{name}.png")
        )
        for name in (
            "finance",
            "job",
            "investment",
            "knowledge",
            "routine",
            "vehicle",
            "growth",
            "food",
            "housing",
            "health",
        )
    }
    symbol_uris = {
        name: _asset_data_uri(path) for name, path in symbol_assets.items()
    }
    symbol_styles = "".join(
        f"--los-symbol-{name}:url('{uri}');" for name, uri in symbol_uris.items()
    )
    symbol_layers = "".join(
        f'<span class="los-world-symbol los-world-symbol-{name}" aria-hidden="true"></span>'
        for name in symbol_assets
    )
    roof_layers = "".join(
        f'<span class="los-world-roof los-world-roof-{name}" aria-hidden="true"></span>'
        for name in ("finance", "job", "investment", "knowledge", "routine", "vehicle", "growth", "food", "housing", "health")
    )
    if home_asset == str(WORLD_ASSET):
        st.image(str(WORLD_ASSET), width="stretch")
    else:
        st.image(home_asset, width="stretch")
    st.markdown(
        f'''<section class="los-world-stage los-world-theme-{escape(world.theme_id)} los-world-frame-{escape(world.language.frame)}" aria-label="리빙 OS 공식 세계"
          data-living-world-context="home" data-hierarchy-level="{escape(world.hierarchy_level)}"
          data-theme-world="{escape(world.world_id)}" data-theme-composition="{escape(world.language.composition)}"
          data-theme-material="{escape(world.language.material)}" data-theme-lighting="{escape(world.language.lighting)}"
          data-theme-texture="{escape(world.language.texture)}"
          style="--los-home-image:url('{world_uri}');{roof_styles}{symbol_styles}">
          <div class="los-world-style-layer" aria-hidden="true"></div>
          <span class="los-world-central-roof" aria-hidden="true"></span>
          {roof_layers}
          {symbol_layers}
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


def metric_deck(cards: Sequence[dict[str, Any]], *, label: str = "현재 신호") -> None:
    st = localized_streamlit()
    items = []
    glyphs = ("◈", "◇", "⌁", "✦", "◎", "△")
    for index, card in enumerate(cards):
        tone = _tone(str(card.get("status", "INFO")))
        glyph = resolve_ui_icon(f"metric.{index}", glyphs[index % len(glyphs)])
        items.append(
            f'''<article class="los-signal-card {tone}"><div class="los-signal-top"><span>{escape(glyph)}</span>
            <small>{escape(str(ui_text(card.get("label", "상태"))))}</small><i></i></div>
            <strong>{escape(str(card.get("value", "-")))}</strong>
            <p>{escape(str(ui_text(card.get("detail", "실시간 운영 상태"), context="caption")))}</p></article>'''
        )
    st.markdown(
        f'<section class="los-metric-section"><header><span>{escape(str(ui_text(label)))}</span><i></i><b>현재 생활 신호</b></header>'
        f'<div class="los-signal-grid">{"".join(items)}</div></section>', unsafe_allow_html=True,
    )


def workspace_rail(title: str, description: str, *, icon: str = "◇", meta: str = "생활 공간") -> None:
    st = localized_streamlit()
    icon = resolve_ui_icon("component.workspace_rail", icon)
    st.markdown(
        f'''<div class="los-workspace-rail"><span class="los-rail-icon">{escape(icon)}</span><div>
        <small>{escape(str(ui_text(meta)))}</small><b>{escape(str(ui_text(title)))}</b><p>{escape(str(ui_text(description, context="caption")))}</p>
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


def _official_value(value: Any) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "예" if value else "아니요"
    if isinstance(value, dict):
        return " · ".join(f"{ui_text(key)} {item}" for key, item in list(value.items())[:4]) or "—"
    if isinstance(value, (list, tuple, set)):
        return f"{len(value)}개 항목"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def official_insight(title: str, payload: Any, *, caption: str = "생활 기록에서 정리한 현재 신호") -> None:
    """Render structured insight without exposing raw JSON or developer payloads."""
    st = localized_streamlit()
    if isinstance(payload, dict):
        entries = list(payload.items())
    elif isinstance(payload, (list, tuple)):
        entries = [("항목", f"{len(payload)}개")]
    else:
        entries = [("내용", payload)]
    if not entries:
        state_panel("표시할 요약이 없습니다", caption)
        return
    cells = []
    for key, value in entries[:12]:
        cells.append(
            f'''<article class="los-insight-cell"><small>{escape(str(ui_text(key)))}</small>
            <strong>{escape(_official_value(value))}</strong><i></i></article>'''
        )
    st.markdown(
        f'''<section class="los-insight-canvas"><header><div><small>생활 요약</small>
        <h3>{escape(str(ui_text(title)))}</h3><p>{escape(str(ui_text(caption, context="caption")))}</p></div><span>◇</span></header>
        <div class="los-insight-grid">{"".join(cells)}</div></section>''',
        unsafe_allow_html=True,
    )


def official_records(
    items: Iterable[dict[str, Any]], *, title: str, empty: str = "아직 기록이 없습니다.", limit: int = 16,
) -> None:
    """Render user records as Living OS cards instead of a raw data table."""
    st = localized_streamlit()
    rows = [dict(item) for item in items][:limit]
    if not rows:
        state_panel("기록이 아직 없습니다", empty)
        return
    identity_fields = (
        "title", "name", "company", "display_name", "category", "activity", "service_type",
        "meal_type", "transaction_type", "kind", "type", "status",
    )
    cards = []
    for index, row in enumerate(rows):
        heading = next((str(row[key]) for key in identity_fields if row.get(key) not in (None, "")), f"기록 {index + 1}")
        status = str(row.get("status", row.get("state", "READY")))
        details = []
        for key, value in row.items():
            if key in identity_fields or key.endswith("_id") or value in (None, "", [], {}):
                continue
            details.append(
                f'<span><small>{escape(str(ui_text(key.replace("_", " ").title())))}</small><b>{escape(_official_value(value))}</b></span>'
            )
            if len(details) == 4:
                break
        cards.append(
            f'''<article class="los-data-card"><header><em class="{_tone(status)}">{escape(str(ui_text(status)))}</em><i></i></header>
            <h4>{escape(heading)}</h4><div>{"".join(details) or '<span><small>상태</small><b>기록됨</b></span>'}</div></article>'''
        )
    st.markdown(
        f'''<section class="los-data-canvas"><header><div><small>생활 기록</small><h3>{escape(str(ui_text(title)))}</h3></div>
        <span>{len(rows)}개 기록</span></header><div class="los-data-grid">{"".join(cards)}</div></section>''',
        unsafe_allow_html=True,
    )

def official_document(title: str, content: Any, *, caption: str = "공식 기록") -> None:
    """Render long-form user content as an official Living OS document surface."""
    st = localized_streamlit()
    body = escape(str(content or "기록이 없습니다.")).replace("\n", "<br>")
    st.markdown(
        f'''<section class="los-document-canvas"><header><div><small>생활 문서</small>
        <h3>{escape(str(ui_text(title)))}</h3><p>{escape(str(ui_text(caption, context="caption")))}</p></div><span>문서</span></header>
        <article>{body}</article></section>''',
        unsafe_allow_html=True,
    )

def status_card(label: str, value: Any, detail: str = "", status: str = "INFO") -> None:
    metric_deck(({"label": label, "value": value, "detail": detail, "status": status},))


def panel_header(title: str, caption: str = "", action: str = "") -> None:
    st = localized_streamlit()
    st.markdown(
        f'''<div class="los-panel-header"><div><small>생활 운영</small><h3>{escape(str(ui_text(title)))}</h3>
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
