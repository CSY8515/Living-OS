from __future__ import annotations

from pathlib import Path
from typing import Callable

from subsystems.experience.engines.pages import (
    render_ai_briefing,
    render_analytics,
    render_dashboard,
    render_decisions,
    render_documents,
    render_finance,
    render_food,
    render_health,
    render_housing,
    render_vehicle,
    render_journal,
    render_knowledge,
    render_module_manager,
    render_reports,
    render_timeline,
    render_global_search,
    render_review,
    render_settings,
    render_knowledge_subsystem,
    render_knowledge_management,
    render_routine_subsystem,
    render_routine_management,
    render_investment_subsystem,
    render_investment_management,
    render_job_subsystem,
    render_job_management,
    render_personal_growth,
    render_personal_growth_management,
    render_collaboration,
    render_collaboration_management,
    render_database,
    render_database_management,
    render_owner_data_control,
)
from subsystems.experience.engines.design_system import (
    navigation_identity,
    official_user_navigation,
)
from subsystems.experience.engines.responsive import apply_responsive_layout
from subsystems.experience.engines.ui_interface import LIVING_OS_UI, ui_scope_marker
from subsystems.experience.engines.ultra_brain_world import (
    inherited_world_css,
    sync_inherited_world,
)
from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem
from subsystems.knowledge import KnowledgeSubsystem
from subsystems.routine import RoutineSubsystem
from subsystems.investment import InvestmentSubsystem
from subsystems.job import JobSubsystem
from subsystems.personal_growth import PersonalGrowthSubsystem
from subsystems.collaboration import CollaborationSubsystem
from subsystems.foundation.engines.hub import LivingHub
from subsystems.operations.engines.catalog import V206_STABLE_MANIFESTS
from subsystems.foundation.engines.runtime_config import RuntimeConfigurationError
from subsystems.foundation.engines.version import PRODUCT_VERSION
from subsystems.experience.engines.localization import ui_text


VERSION = PRODUCT_VERSION
ROOT = Path(__file__).resolve().parents[3]

USER_PAGE_ORDER = (
    "Command Center", "Daily Log", "Decision Log", "Reports", "Analytics",
    "Timeline", "Search", "AI Analysis", "Finance", "Investment", "Job",
    "Health", "Vehicle", "Housing", "Food", "Knowledge", "Routine",
    "Personal Growth",
)

FEATURE_PAGES = {
    "Finance", "Investment", "Job", "Health", "Vehicle", "Housing", "Food",
    "Knowledge", "Routine", "Personal Growth",
}

NAV_ICONS = {
    "Command Center": "◈", "Daily Log": "✦", "Decision Log": "◇", "Reports": "▤",
    "Archive": "▣", "Analytics": "⌁", "Timeline": "↕", "Search": "⌕", "Review": "◎", "AI Analysis": "✧",
    "Documents": "▧", "Finance": "◐", "Food": "◒", "Health": "♡",
    "Housing": "⌂", "Vehicle": "▷", "Knowledge": "◫", "Routine": "↻",
    "Investment": "↗", "Job": "▱", "Personal Growth": "△", "Collaboration": "◉",
    "Knowledge Management": "◫", "Routine Management": "↻",
    "Investment Management": "↗", "Job Management": "▱",
    "Personal Growth Management": "△", "Collaboration Management": "◉",
    "Database": "▦", "Database Management": "▦", "Module Manager": "⬡", "Settings": "⚙",
}


def _hub() -> LivingHub:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_hub() -> LivingHub:
        hub = LivingHub(ROOT)
        hub.bootstrap(V206_STABLE_MANIFESTS)
        return hub

    return build_hub()


def _finance() -> FinanceSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_finance() -> FinanceSubsystem:
        hub = _hub()
        return FinanceSubsystem(
            ROOT,
            database_path=hub.component_database_path("finance"),
            database_foundation=hub.database,
        )

    return build_finance()


def _food() -> FoodSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_food() -> FoodSubsystem:
        hub = _hub()
        return FoodSubsystem(
            ROOT,
            database_path=hub.component_database_path("food"),
            database_foundation=hub.database,
        )

    return build_food()


def _health() -> HealthSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_health() -> HealthSubsystem:
        hub = _hub()
        return HealthSubsystem(
            ROOT,
            database_path=hub.component_database_path("health"),
            database_foundation=hub.database,
        )

    return build_health()


def _housing() -> HousingSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_housing() -> HousingSubsystem:
        hub = _hub()
        return HousingSubsystem(
            ROOT,
            database_path=hub.component_database_path("housing"),
            database_foundation=hub.database,
        )

    return build_housing()


def _vehicle() -> VehicleSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build_vehicle() -> VehicleSubsystem:
        hub = _hub()
        return VehicleSubsystem(
            ROOT,
            database_path=hub.component_database_path("vehicle"),
            database_foundation=hub.database,
        )

    return build_vehicle()


def _knowledge_subsystem() -> KnowledgeSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> KnowledgeSubsystem:
        hub = _hub()
        return KnowledgeSubsystem(
            ROOT,
            database_path=hub.component_database_path("knowledge"),
            database_foundation=hub.database,
        )
    return build()


def _routine_subsystem() -> RoutineSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> RoutineSubsystem:
        hub = _hub()
        return RoutineSubsystem(
            ROOT,
            database_path=hub.component_database_path("routine"),
            database_foundation=hub.database,
        )
    return build()


def _investment_subsystem() -> InvestmentSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> InvestmentSubsystem:
        hub = _hub()
        return InvestmentSubsystem(
            ROOT,
            database_path=hub.component_database_path("investment"),
            database_foundation=hub.database,
        )
    return build()


def _job_subsystem() -> JobSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> JobSubsystem:
        hub = _hub()
        return JobSubsystem(
            ROOT,
            database_path=hub.component_database_path("job"),
            database_foundation=hub.database,
        )
    return build()


def _personal_growth_subsystem() -> PersonalGrowthSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> PersonalGrowthSubsystem:
        hub = _hub()
        return PersonalGrowthSubsystem(
            ROOT,
            database_path=hub.component_database_path("personal-growth"),
            database_foundation=hub.database,
        )
    return build()


def _collaboration_subsystem() -> CollaborationSubsystem:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    @st.cache_resource
    def build() -> CollaborationSubsystem:
        hub = _hub()
        return CollaborationSubsystem(
            ROOT,
            database_path=hub.component_database_path("collaboration"),
            database_foundation=hub.database,
        )
    return build()


def _configure_timeline_sources(
    hub: LivingHub,
    finance: FinanceSubsystem,
    food: FoodSubsystem,
    health: HealthSubsystem,
    housing: HousingSubsystem,
    vehicle: VehicleSubsystem,
    knowledge: KnowledgeSubsystem,
    routine: RoutineSubsystem,
    investment: InvestmentSubsystem,
    job: JobSubsystem,
    growth: PersonalGrowthSubsystem,
    collaboration: CollaborationSubsystem,
) -> None:
    sources = (
        ("finance", finance.list_transactions, "transaction", {}),
        ("investment", lambda: investment.list(include_archived=True, limit=1000), "investment", {}),
        ("job", lambda: job.list(include_archived=True, limit=1000), "job", {}),
        ("health", health.list_weights, "weight", {"event_time_field": "measured_on"}),
        (
            "health",
            health.list_health_checkups,
            "health-checkup",
            {"event_time_field": "checked_on"},
        ),
        (
            "health",
            health.list_exercise,
            "exercise",
            {"title_field": "activity", "event_time_field": "exercised_on"},
        ),
        ("vehicle", vehicle.list_vehicles, "vehicle", {}),
        ("vehicle", lambda: [item for v in vehicle.list_vehicles() for item in vehicle.list_trips(v["vehicle_id"])],
         "trip", {"id_field": "trip_id", "title_field": "purpose", "event_time_field": "driven_on"}),
        ("vehicle", lambda: [item for v in vehicle.list_vehicles() for item in vehicle.list_maintenance_records(v["vehicle_id"])],
         "maintenance", {"id_field": "maintenance_id", "title_field": "service_type", "event_time_field": "serviced_on"}),
        ("vehicle", lambda: [item for v in vehicle.list_vehicles() for item in vehicle.list_energy_logs(v["vehicle_id"])],
         "energy", {"id_field": "energy_id", "title_field": "energy_type", "event_time_field": "recorded_on"}),
        ("housing", housing.list_candidates, "housing-candidate", {}),
        ("housing", lambda: housing.list_contracts(), "housing-contract",
         {"id_field": "contract_id", "title_field": "name", "summary_field": "address", "event_time_field": "start_on"}),
        ("food", food.list_ingredients, "ingredient", {}),
        ("food", food.list_recipes, "recipe", {"id_field": "recipe_id"}),
        ("food", food.list_meals, "meal",
         {"id_field": "meal_id", "title_field": "meal_type", "event_time_field": "eaten_on"}),
        ("food", food.list_cooking_records, "cooking",
         {"id_field": "cooking_id", "title_field": "note", "event_time_field": "cooked_on"}),
        (
            "knowledge",
            lambda: knowledge.list(include_archived=True, limit=1000),
            "knowledge-record",
            {},
        ),
        (
            "routine",
            lambda: routine.list(include_archived=True, limit=1000),
            "routine",
            {},
        ),
        (
            "personal-growth",
            lambda: growth.list(include_archived=True, limit=1000),
            "growth-goal",
            {},
        ),
        (
            "collaboration",
            lambda: collaboration.list(include_archived=True, limit=1000),
            "collaboration",
            {},
        ),
    )
    for subsystem, loader, record_type, overrides in sources:
        hub.timeline.register_subsystem_source(
            subsystem,
            loader,
            record_type=record_type,
            replace=True,
            **overrides,
        )


def _canonical_pages(hub: LivingHub, finance: FinanceSubsystem, food: FoodSubsystem,
                     health: HealthSubsystem,
                     housing: HousingSubsystem,
                     vehicle: VehicleSubsystem, knowledge: KnowledgeSubsystem,
                     routine: RoutineSubsystem, investment: InvestmentSubsystem,
                     job: JobSubsystem, growth: PersonalGrowthSubsystem,
                     collaboration: CollaborationSubsystem) -> dict[str, Callable[[], None]]:
    _configure_timeline_sources(
        hub,
        finance,
        food,
        health,
        housing,
        vehicle,
        knowledge,
        routine,
        investment,
        job,
        growth,
        collaboration,
    )
    managed = {
        "Finance": finance,
        "Food": food,
        "Health": health,
        "Housing": housing,
        "Vehicle": vehicle,
        "Knowledge": knowledge,
        "Routine": routine,
        "Investment": investment,
        "Job": job,
        "Personal Growth": growth,
        "Collaboration": collaboration,
    }
    return {
        "Command Center": lambda: render_dashboard(hub, managed),
        "Daily Log": lambda: render_journal(hub),
        "Decision Log": lambda: render_decisions(hub),
        "Reports": lambda: render_reports(hub, managed),
        "Archive": lambda: render_knowledge(hub),
        "Analytics": lambda: render_analytics(hub),
        "Timeline": lambda: render_timeline(hub),
        "Search": lambda: render_global_search(hub),
        "Review": lambda: render_review(hub),
        "AI Analysis": lambda: render_ai_briefing(hub),
        "Documents": lambda: render_documents(hub),
        "Finance": lambda: render_finance(finance),
        "Food": lambda: render_food(food),
        "Health": lambda: render_health(health),
        "Housing": lambda: render_housing(housing),
        "Vehicle": lambda: render_vehicle(vehicle),
        "Knowledge": lambda: render_knowledge_subsystem(knowledge),
        "Routine": lambda: render_routine_subsystem(routine),
        "Investment": lambda: render_investment_subsystem(investment),
        "Job": lambda: render_job_subsystem(job),
        "Personal Growth": lambda: render_personal_growth(growth),
        "Collaboration": lambda: render_collaboration(collaboration),
        "Knowledge Management": lambda: render_knowledge_management(knowledge),
        "Routine Management": lambda: render_routine_management(routine),
        "Investment Management": lambda: render_investment_management(investment),
        "Job Management": lambda: render_job_management(job),
        "Personal Growth Management": lambda: render_personal_growth_management(growth),
        "Collaboration Management": lambda: render_collaboration_management(collaboration),
        "Database": lambda: render_database(hub),
        "Database Management": lambda: render_database_management(hub),
        "Module Manager": lambda: render_module_manager(hub),
        "Settings": lambda: render_settings(hub),
    }


def _authorize(hub: LivingHub) -> bool:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    remote_required = hub.runtime_config.authentication_required
    if not hub.security.configured and not remote_required:
        return True
    if not hub.security.configured and hub.runtime_config.production:
        st.title("리빙 OS 접근 잠김")
        st.error(
            "운영 배포에 소유자 인증이 구성되지 않았습니다. "
            "접근을 허용하려면 먼저 릴리스 게이트를 완료해야 합니다."
        )
        return False
    if not hub.security.configured:
        st.title("리빙 OS 소유자 설정")
        st.warning("원격에서 허브를 열려면 소유자 인증이 필요합니다.")
        with st.form("owner_setup"):
            first = st.text_input("새 소유자 암호문", type="password")
            second = st.text_input("암호문 확인", type="password")
            submitted = st.form_submit_button("이 허브 보호")
        if submitted:
            if first != second:
                st.error("암호문이 일치하지 않습니다.")
            else:
                try:
                    hub.security.configure(first)
                    device = hub.security.pair_device(first, "최초 소유자 기기", "browser")
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.v2_device_id = device.device_id
                    st.rerun()
        return False

    device_id = str(st.session_state.get("v2_device_id", ""))
    if device_id and hub.security.validate_device(device_id):
        return True
    st.title("리빙 OS 소유자 로그인")
    with st.form("owner_sign_in"):
        passphrase = st.text_input("소유자 암호문", type="password")
        device_name = st.text_input("기기 이름", value="리빙 OS 브라우저")
        submitted = st.form_submit_button("기기 연결 후 허브 열기")
    if submitted:
        try:
            device = hub.security.pair_device(passphrase, device_name, "browser")
        except ValueError:
            st.error("소유자 인증에 실패했습니다.")
        else:
            st.session_state.v2_device_id = device.device_id
            st.rerun()
    return False


def _compatibility_pages(hub: LivingHub, finance: FinanceSubsystem, food: FoodSubsystem,
                         health: HealthSubsystem,
                         housing: HousingSubsystem,
                         vehicle: VehicleSubsystem, knowledge: KnowledgeSubsystem,
                         routine: RoutineSubsystem, investment: InvestmentSubsystem,
                         job: JobSubsystem) -> dict[str, Callable[[], None]]:
    from subsystems.compatibility.engines.ai_analysis import render_ai_analysis
    from subsystems.compatibility.engines.analytics import render_analytics as render_legacy_analytics
    from subsystems.compatibility.engines.archive import render_archive
    from subsystems.compatibility.engines.daily_log import render_daily_log
    from subsystems.compatibility.engines.dashboard import render_dashboard as render_legacy_dashboard
    from subsystems.compatibility.engines.decision_log import render_decision_log
    from subsystems.compatibility.engines.report_system import render_reports as render_legacy_reports
    from subsystems.compatibility.engines.review import render_review as render_legacy_review
    from subsystems.compatibility.engines.storage import load_dashboard_data

    return {
        "Dashboard": lambda: render_legacy_dashboard(load_dashboard_data()),
        "Daily Log": render_daily_log,
        "Decision Log": render_decision_log,
        "Reports": render_legacy_reports,
        "Archive": render_archive,
        "Analytics": render_legacy_analytics,
        "Review": render_legacy_review,
        "AI Analysis": render_ai_analysis,
        "Documents": lambda: render_documents(hub),
        "Finance": lambda: render_finance(finance),
        "Food": lambda: render_food(food),
        "Health": lambda: render_health(health),
        "Housing": lambda: render_housing(housing),
        "Vehicle": lambda: render_vehicle(vehicle),
        "Knowledge": lambda: render_knowledge_subsystem(knowledge),
        "Routine": lambda: render_routine_subsystem(routine),
        "Knowledge Management": lambda: render_knowledge_management(knowledge),
        "Routine Management": lambda: render_routine_management(routine),
        "Investment": lambda: render_investment_subsystem(investment),
        "Job": lambda: render_job_subsystem(job),
        "Investment Management": lambda: render_investment_management(investment),
        "Job Management": lambda: render_job_management(job),
        "Module Manager": lambda: render_module_manager(hub),
        "Settings": lambda: render_settings(hub),
    }


def main() -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.set_page_config(page_title=f"Living OS {VERSION}", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    inherited_world = sync_inherited_world(st.query_params)
    apply_responsive_layout()
    inherited_css = inherited_world_css(inherited_world)
    if inherited_css:
        st.markdown(inherited_css, unsafe_allow_html=True)
    ui_contract = LIVING_OS_UI.resolve()
    try:
        hub = _hub()
    except RuntimeConfigurationError:
        st.error(
            "리빙 OS 저장소 또는 인증 구성이 안전하지 않습니다. "
            "소유자 데이터를 열기 전에 앱을 잠갔습니다."
        )
        st.caption("운영 설정을 확인한 뒤 다시 접속해 주세요.")
        st.stop()
    finance = _finance()
    food = _food()
    health = _health()
    housing = _housing()
    vehicle = _vehicle()
    knowledge = _knowledge_subsystem()
    routine = _routine_subsystem()
    investment = _investment_subsystem()
    job = _job_subsystem()
    growth = _personal_growth_subsystem()
    collaboration = _collaboration_subsystem()
    if not _authorize(hub):
        return
    managed_systems = {
        "Finance": finance,
        "Food": food,
        "Health": health,
        "Housing": housing,
        "Vehicle": vehicle,
        "Knowledge": knowledge,
        "Routine": routine,
        "Investment": investment,
        "Job": job,
        "Personal Growth": growth,
        "Collaboration": collaboration,
    }
    pages = _canonical_pages(hub, finance, food, health, housing, vehicle, knowledge, routine, investment, job, growth, collaboration)

    with st.popover("내 데이터", use_container_width=False):
        render_owner_data_control(hub, managed_systems)

    module_by_page = {
        "Command Center": "dashboard",
        "Daily Log": "journal",
        "Decision Log": "decision",
        "Reports": "reports",
        "Archive": "knowledge",
        "Analytics": "analytics",
        "Timeline": "analytics",
        "Search": "analytics",
        "Review": "review",
        "AI Analysis": "ai_briefing",
        "Documents": "documents",
        "Finance": "finance",
        "Food": "food",
        "Health": "health",
        "Housing": "housing",
        "Vehicle": "vehicle",
        "Knowledge": "knowledge_subsystem",
        "Routine": "routine",
        "Knowledge Management": "knowledge_subsystem",
        "Routine Management": "routine",
        "Investment": "investment",
        "Job": "job",
        "Investment Management": "investment",
        "Job Management": "job",
        "Personal Growth": "personal_growth",
        "Personal Growth Management": "personal_growth",
        "Collaboration": "collaboration",
        "Collaboration Management": "collaboration",
        "Database": "database",
        "Database Management": "database_management",
        "Module Manager": "module_manager",
        "Settings": "settings",
    }
    enabled = {
        str(item["module_id"])
        for item in hub.modules.list_modules()
        if item.get("status") in {"enabled", "degraded"}
    }
    visible_pages = [
        name for name in USER_PAGE_ORDER
        if name in pages and module_by_page[name] in enabled
    ]

    with st.sidebar:
        current_page = str(st.session_state.get("nav_page", visible_pages[0]))
        navigation_identity(version=VERSION, page=current_page, enabled=len(enabled))
        st.title("리빙 OS")
        st.caption(VERSION)
        st.caption("개인 생활 운영 시스템")
        page = st.radio(
            "메뉴", visible_pages, label_visibility="collapsed", key="nav_page",
            format_func=lambda name: f"{ui_contract.icons.get(f'navigation.{name}', NAV_ICONS.get(name, '◇'))}  {ui_text(name)}",
        )
    st.markdown(ui_scope_marker(module_by_page[page]), unsafe_allow_html=True)
    if page != "Command Center":
        def navigate(target: str) -> None:
            st.session_state.nav_page = target

        with st.container(key="official_user_navigation"):
            official_user_navigation(page=page, feature=page in FEATURE_PAGES)
            nav = st.columns((1.35, 1, 1, 1, 1))
            nav[0].button("⌂  리빙 OS", key="official_nav_home", on_click=navigate, args=("Command Center",), width="stretch")
            nav[1].button("오늘", key="official_nav_today", on_click=navigate, args=("Daily Log",), width="stretch")
            nav[2].button("타임라인", key="official_nav_timeline", on_click=navigate, args=("Timeline",), width="stretch")
            nav[3].button("리포트", key="official_nav_reports", on_click=navigate, args=("Reports",), width="stretch")
            nav[4].button("검색", key="official_nav_search", on_click=navigate, args=("Search",), width="stretch")
    pages[page]()
