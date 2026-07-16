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
    render_health,
    render_housing,
    render_vehicle,
    render_journal,
    render_knowledge,
    render_module_manager,
    render_reports,
    render_review,
    render_settings,
)
from subsystems.experience.engines.responsive import apply_responsive_layout
from subsystems.finance import FinanceSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem
from subsystems.foundation.engines.hub import LivingHub
from subsystems.operations.engines.catalog import V15_STABLE_MANIFESTS


VERSION = "v1.5 Stable"
ROOT = Path(__file__).resolve().parents[3]


def _hub() -> LivingHub:
    import streamlit as st

    @st.cache_resource
    def build_hub() -> LivingHub:
        hub = LivingHub(ROOT)
        hub.bootstrap(V15_STABLE_MANIFESTS)
        return hub

    return build_hub()


def _finance() -> FinanceSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_finance() -> FinanceSubsystem:
        return FinanceSubsystem(ROOT)

    return build_finance()


def _health() -> HealthSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_health() -> HealthSubsystem:
        return HealthSubsystem(ROOT)

    return build_health()


def _housing() -> HousingSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_housing() -> HousingSubsystem:
        return HousingSubsystem(ROOT)

    return build_housing()


def _vehicle() -> VehicleSubsystem:
    import streamlit as st

    @st.cache_resource
    def build_vehicle() -> VehicleSubsystem:
        return VehicleSubsystem(ROOT)

    return build_vehicle()


def _canonical_pages(hub: LivingHub, finance: FinanceSubsystem, health: HealthSubsystem,
                     housing: HousingSubsystem,
                     vehicle: VehicleSubsystem) -> dict[str, Callable[[], None]]:
    return {
        "Dashboard": lambda: render_dashboard(hub),
        "Daily Log": lambda: render_journal(hub),
        "Decision Log": lambda: render_decisions(hub),
        "Reports": lambda: render_reports(hub),
        "Archive": lambda: render_knowledge(hub),
        "Analytics": lambda: render_analytics(hub),
        "Review": lambda: render_review(hub),
        "AI Analysis": lambda: render_ai_briefing(hub),
        "Documents": lambda: render_documents(hub),
        "Finance": lambda: render_finance(finance),
        "Health": lambda: render_health(health),
        "Housing": lambda: render_housing(housing),
        "Vehicle": lambda: render_vehicle(vehicle),
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


def _compatibility_pages(hub: LivingHub, finance: FinanceSubsystem, health: HealthSubsystem,
                         housing: HousingSubsystem,
                         vehicle: VehicleSubsystem) -> dict[str, Callable[[], None]]:
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
        "Health": lambda: render_health(health),
        "Housing": lambda: render_housing(housing),
        "Vehicle": lambda: render_vehicle(vehicle),
        "Module Manager": lambda: render_module_manager(hub),
        "Settings": lambda: render_settings(hub),
    }


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Living OS", page_icon="◉", layout="wide")
    apply_responsive_layout()
    hub = _hub()
    finance = _finance()
    health = _health()
    housing = _housing()
    vehicle = _vehicle()
    if not _authorize(hub):
        return
    migrated = hub.v1_migration_complete
    pages = (_canonical_pages(hub, finance, health, housing, vehicle) if migrated
             else _compatibility_pages(hub, finance, health, housing, vehicle))

    module_by_page = {
        "Dashboard": "dashboard",
        "Daily Log": "journal",
        "Decision Log": "decision",
        "Reports": "reports",
        "Archive": "knowledge",
        "Analytics": "analytics",
        "Review": "review",
        "AI Analysis": "ai_briefing",
        "Documents": "documents",
        "Finance": "finance",
        "Health": "health",
        "Housing": "housing",
        "Vehicle": "vehicle",
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
        st.title("Living OS")
        st.caption(VERSION)
        st.caption("Canonical Hub" if migrated else "v1 Compatibility Mode")
        page = st.radio("Menu", visible_pages, label_visibility="collapsed")

    if not migrated and page != "Settings":
        st.info("Living OS v1.2 preserves existing v1 data in compatibility mode. Review and approve migration in Settings when ready.")
    pages[page]()
