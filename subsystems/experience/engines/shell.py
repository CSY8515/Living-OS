from __future__ import annotations

from pathlib import Path
import os
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
)
from subsystems.experience.engines.design_system import system_banner
from subsystems.experience.engines.responsive import apply_responsive_layout
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
from subsystems.operations.engines.catalog import V20_STABLE_MANIFESTS


VERSION = "v2.0.3"
ROOT = Path(__file__).resolve().parents[3]

NAV_ICONS = {
    "Command Center": "◈", "Daily Log": "✦", "Decision Log": "◇", "Reports": "▤",
    "Archive": "▣", "Analytics": "⌁", "Review": "◎", "AI Analysis": "✧",
    "Documents": "▧", "Finance": "◐", "Food": "◒", "Health": "♡",
    "Housing": "⌂", "Vehicle": "▷", "Knowledge": "◫", "Routine": "↻",
    "Investment": "↗", "Job": "▱", "Personal Growth": "△", "Collaboration": "◉",
    "Knowledge Management": "◫", "Routine Management": "↻",
    "Investment Management": "↗", "Job Management": "▱",
    "Personal Growth Management": "△", "Collaboration Management": "◉",
    "Database": "▦", "Database Management": "▦", "Module Manager": "⬡", "Settings": "⚙",
}


def _hub() -> LivingHub:
    import streamlit as st

    @st.cache_resource
    def build_hub() -> LivingHub:
        hub = LivingHub(ROOT)
        hub.bootstrap(V20_STABLE_MANIFESTS)
        return hub

    return build_hub()


def _finance() -> FinanceSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_finance() -> FinanceSubsystem:
        return FinanceSubsystem(ROOT, database_foundation=_hub().database)

    return build_finance()


def _food() -> FoodSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_food() -> FoodSubsystem:
        return FoodSubsystem(ROOT, database_foundation=_hub().database)

    return build_food()


def _health() -> HealthSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_health() -> HealthSubsystem:
        return HealthSubsystem(ROOT, database_foundation=_hub().database)

    return build_health()


def _housing() -> HousingSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_housing() -> HousingSubsystem:
        return HousingSubsystem(ROOT, database_foundation=_hub().database)

    return build_housing()


def _vehicle() -> VehicleSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_vehicle() -> VehicleSubsystem:
        return VehicleSubsystem(ROOT, database_foundation=_hub().database)

    return build_vehicle()


def _knowledge_subsystem() -> KnowledgeSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> KnowledgeSubsystem: return KnowledgeSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _routine_subsystem() -> RoutineSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> RoutineSubsystem: return RoutineSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _investment_subsystem() -> InvestmentSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> InvestmentSubsystem: return InvestmentSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _job_subsystem() -> JobSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> JobSubsystem: return JobSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _personal_growth_subsystem() -> PersonalGrowthSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> PersonalGrowthSubsystem:
        return PersonalGrowthSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _collaboration_subsystem() -> CollaborationSubsystem:
    import streamlit as st
    @st.cache_resource
    def build() -> CollaborationSubsystem:
        return CollaborationSubsystem(ROOT, database_foundation=_hub().database)
    return build()


def _canonical_pages(hub: LivingHub, finance: FinanceSubsystem, food: FoodSubsystem,
                     health: HealthSubsystem,
                     housing: HousingSubsystem,
                     vehicle: VehicleSubsystem, knowledge: KnowledgeSubsystem,
                     routine: RoutineSubsystem, investment: InvestmentSubsystem,
                     job: JobSubsystem, growth: PersonalGrowthSubsystem,
                     collaboration: CollaborationSubsystem) -> dict[str, Callable[[], None]]:
    managed = {"Personal Growth": growth, "Collaboration": collaboration,
               "Knowledge": knowledge, "Routine": routine, "Investment": investment, "Job": job}
    return {
        "Command Center": lambda: render_dashboard(hub, managed),
        "Daily Log": lambda: render_journal(hub),
        "Decision Log": lambda: render_decisions(hub),
        "Reports": lambda: render_reports(hub),
        "Archive": lambda: render_knowledge(hub),
        "Analytics": lambda: render_analytics(hub),
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
    import streamlit as st

    remote_required = os.environ.get("LIVING_OS_REMOTE_ACCESS", "").strip().lower() in {
        "1", "true", "yes", "on"
    }
    if not hub.security.configured and not remote_required:
        return True
    if not hub.security.configured:
        st.title("Living OS Owner Setup")
        st.warning("Remote access requires owner authentication before the Hub can open.")
        with st.form("owner_setup"):
            first = st.text_input("New owner passphrase", type="password")
            second = st.text_input("Confirm passphrase", type="password")
            submitted = st.form_submit_button("Secure This Hub")
        if submitted:
            if first != second:
                st.error("Passphrases do not match.")
            else:
                try:
                    hub.security.configure(first)
                    device = hub.security.pair_device(first, "Initial Owner Device", "browser")
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.v2_device_id = device.device_id
                    st.rerun()
        return False

    device_id = str(st.session_state.get("v2_device_id", ""))
    if device_id and hub.security.validate_device(device_id):
        return True
    st.title("Living OS Owner Sign In")
    with st.form("owner_sign_in"):
        passphrase = st.text_input("Owner passphrase", type="password")
        device_name = st.text_input("Device name", value="Living OS Browser")
        submitted = st.form_submit_button("Pair and Open Hub")
    if submitted:
        try:
            device = hub.security.pair_device(passphrase, device_name, "browser")
        except ValueError:
            st.error("Owner authentication failed.")
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
    import streamlit as st

    st.set_page_config(page_title="Living OS v2.0.3", page_icon="◈", layout="wide", initial_sidebar_state="auto")
    apply_responsive_layout()
    hub = _hub()
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
    pages = _canonical_pages(hub, finance, food, health, housing, vehicle, knowledge, routine, investment, job, growth, collaboration)

    module_by_page = {
        "Command Center": "dashboard",
        "Daily Log": "journal",
        "Decision Log": "decision",
        "Reports": "reports",
        "Archive": "knowledge",
        "Analytics": "analytics",
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
        name
        for name in pages
        if module_by_page[name] in enabled or name in {"Module Manager", "Settings"}
    ]

    with st.sidebar:
        st.title("LIVING OS")
        st.caption(VERSION)
        st.caption("PERSONAL COMMAND SYSTEM")
        page = st.radio(
            "Menu", visible_pages, label_visibility="collapsed", key="nav_page",
            format_func=lambda name: f"{NAV_ICONS.get(name, '◇')}  {name}",
        )
    system_banner(version=VERSION, status="ONLINE", detail=f"{len(enabled)} modules active · {page}")
    pages[page]()
