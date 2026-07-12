import streamlit as st

from modules.analytics import render_analytics
from modules.archive import render_archive
from modules.dashboard import render_dashboard
from modules.daily_log import render_daily_log
from modules.decision_log import render_decision_log
from modules.module_manager import render_module_manager
from modules.report_system import render_reports
from modules.review import render_review
from modules.settings import render_settings
from modules.storage import ensure_data_files, load_dashboard_data


VERSION = "v0.7"


st.set_page_config(
    page_title="Living OS",
    page_icon="🏠",
    layout="wide",
)


def main() -> None:
    ensure_data_files()

    with st.sidebar:
        st.title("Living OS")
        st.caption(VERSION)
        page = st.radio(
            "Menu",
            [
                "Dashboard",
                "Daily Log",
                "Decision Log",
                "Reports",
                "Archive",
                "Analytics",
                "Review",
                "Module Manager",
                "Settings",
            ],
            label_visibility="collapsed",
        )

    if page == "Daily Log":
        render_daily_log()
    elif page == "Decision Log":
        render_decision_log()
    elif page == "Reports":
        render_reports()
    elif page == "Archive":
        render_archive()
    elif page == "Analytics":
        render_analytics()
    elif page == "Review":
        render_review()
    elif page == "Module Manager":
        render_module_manager()
    elif page == "Settings":
        render_settings()
    else:
        render_dashboard(load_dashboard_data())


if __name__ == "__main__":
    main()
