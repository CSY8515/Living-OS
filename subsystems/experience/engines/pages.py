from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

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
from subsystems.experience.engines.design_system import (
    home_core,
    metric_deck,
    official_document,
    official_insight,
    official_records,
    page_header,
    panel_header,
    record_gallery,
    state_panel,
    workspace_rail,
)

from subsystems.foundation.engines.errors import CoreError
from subsystems.foundation.engines.data_reset import (
    OwnerDataResetError,
    OwnerDataResetService,
    development_legacy_empty_states,
)
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.module_runtime import LIFECYCLE_TRANSITIONS
from subsystems.foundation.engines.release_gate import evaluate_release_gate
from subsystems.foundation.engines.version import PRODUCT_VERSION
from subsystems.insight.engines.ai_credentials import resolve_api_key
from subsystems.insight.engines.ai_service import (
    AI_MODELS,
    DEFAULT_AI_MODEL,
    AIServiceError,
    record_source,
)
from subsystems.insight.engines.ai_briefing import AIBriefingService, OpenAITextProvider
from subsystems.operations.engines.decision import DecisionService
from subsystems.operations.engines.journal import JournalService
from subsystems.operations.engines.knowledge import KnowledgeService
from subsystems.operations.engines.settings import HubSettingsService
from subsystems.insight.engines.analytics import AnalyticsEngine
from subsystems.insight.engines.projections import review_projection
from subsystems.insight.engines.search import GlobalSearchEngine
from subsystems.operations.engines.reports import ReportsService


def _tags(raw: str) -> list[str]:
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def _render_record_browser(prefix: str, records: list[dict[str, Any]]) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    workspace_rail("기록 탐색", "검색·상태·정렬을 조합하고 선택한 기록의 상세를 확인합니다.", icon="◇", meta="생활 기록")
    if not records:
        st.caption("No records yet.")
        return
    search = st.text_input("Search", key=f"{prefix}_record_search")
    statuses = sorted({str(item.get("status")) for item in records if item.get("status")})
    status = st.selectbox(
        "Status", ["All", *statuses], key=f"{prefix}_record_status"
    )
    scalar_fields = sorted({
        key for item in records for key, value in item.items()
        if isinstance(value, (str, int, float)) or value is None
    })
    sort_by = st.selectbox(
        "Sort", scalar_fields, index=0, key=f"{prefix}_record_sort"
    )
    descending = st.toggle(
        "Descending", value=True, key=f"{prefix}_record_descending"
    )
    needle = search.strip().casefold()
    visible = [
        dict(item) for item in records
        if (status == "All" or str(item.get("status")) == status)
        and (not needle or needle in " ".join(str(value) for value in item.values()).casefold())
    ]
    visible.sort(
        key=lambda item: (item.get(sort_by) is None, str(item.get(sort_by, "")).casefold()),
        reverse=descending,
    )
    official_records(visible, title="기록 모음", empty="표시할 기록이 없습니다.")
    if visible:
        id_fields = (
            "record_id", "transaction_id", "ingredient_id", "recipe_id", "meal_id",
            "candidate_id", "contract_id", "charge_id", "vehicle_id", "trip_id",
            "maintenance_id", "energy_id", "goal_id",
        )
        options = [
            next((str(item[field]) for field in id_fields if item.get(field)), str(index))
            for index, item in enumerate(visible)
        ]
        selected = st.selectbox("Detail", options, key=f"{prefix}_record_detail")
        official_insight("선택한 기록", visible[options.index(selected)], caption="사용자가 선택한 생활 기록의 상세 정보")


def render_investment_subsystem(investment: InvestmentSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Investment", "투자 관측소", "보유 자산과 가치 변화를 한 공간에서 살펴봅니다.", investment.health().get("status", "READY"))
    st.caption("내가 보유한 자산과 평가 흐름을 통화별로 관리합니다.")
    with st.expander("Add Investment"):
        with st.form("investment_create"):
            name = st.text_input("Name")
            symbol = st.text_input("Symbol")
            asset_type = st.selectbox("Asset Type", ["STOCK", "ETF", "FUND", "BOND", "CRYPTO", "CASH", "OTHER"])
            quantity = st.number_input("Quantity", min_value=0.0, value=0.0)
            unit_cost = st.number_input("Unit Cost", min_value=0.0, value=0.0)
            current_price = st.number_input("Current Price", min_value=0.0, value=0.0)
            currency = st.text_input("Currency", value="KRW")
            active = st.checkbox("Active position", value=True)
            submitted = st.form_submit_button("Add")
        if submitted:
            try:
                investment.create(name, symbol=symbol, asset_type=asset_type, quantity=quantity,
                                  unit_cost=unit_cost, current_price=current_price, currency=currency.upper(),
                                  status="ACTIVE" if active else "WATCHLIST")
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Investment added.")
                st.rerun()
    records = investment.list(include_archived=True)
    official_records(records, title="투자 포트폴리오", empty="등록된 투자 자산이 없습니다.")
    for item in records:
        value = item["quantity"] * item["current_price"]
        with st.expander(f"{item['name']} · {item['status']} · {value:,.2f} {item['currency']}"):
            st.caption(f"{item['asset_type']} · {item['symbol'] or 'no symbol'}")
            price = st.number_input("Current Price", min_value=0.0, value=float(item["current_price"]),
                                    key=f"investment_price_{item['investment_id']}")
            actions = st.columns(2)
            if actions[0].button("Save Valuation", key=f"investment_value_{item['investment_id']}"):
                investment.update_valuation(item["investment_id"], price)
                st.rerun()
            lifecycle_label = "Restore" if item["status"] == "ARCHIVED" else "Archive"
            if actions[1].button(
                lifecycle_label, key=f"investment_lifecycle_{item['investment_id']}"
            ):
                if item["status"] == "ARCHIVED":
                    investment.restore(item["investment_id"])
                    st.success("Investment restored to Watchlist.")
                else:
                    investment.archive(item["investment_id"])
                    st.success("Investment archived.")
                st.rerun()
    if not records:
        st.info("No investment records yet.")


def render_investment_management(investment: InvestmentSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.title("Investment Management")
    summary = investment.management_summary()
    cols = st.columns(5)
    cols[0].metric("Total", summary["total"])
    cols[1].metric("Active", summary["active"])
    cols[2].metric("Archived", summary["archived"])
    cols[3].metric("Executions", summary["execution_success"])
    cols[4].metric("Registry", "REGISTERED" if summary["registry_registered"] else "MISSING")
    st.write("Portfolio valuation by currency")
    st.json(summary["valuation_by_currency"])
    st.write("Status and asset allocation")
    st.json({"status": summary["by_status"], "asset_type": summary["by_asset_type"]})
    st.write("Database Adapter")
    st.json(summary["health"])


def render_job_subsystem(job: JobSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Job", "커리어 정거장", "기회와 지원 과정, 다음 행동을 이어서 관리합니다.", job.health().get("status", "READY"))
    st.caption("기회, 지원, 면접과 다음 행동을 한 흐름으로 관리합니다.")
    query = st.text_input("Search Jobs", key="job_search")
    with st.expander("Add Job"):
        with st.form("job_create"):
            company = st.text_input("Company")
            title = st.text_input("Title")
            employment_type = st.selectbox("Employment Type", ["FULL_TIME", "PART_TIME", "CONTRACT", "FREELANCE", "INTERNSHIP", "OTHER"])
            location = st.text_input("Location")
            source = st.text_input("Source")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add")
        if submitted:
            try:
                job.create(company, title, employment_type=employment_type, location=location, source=source, notes=notes)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Job added.")
                st.rerun()
    records = job.search(query, include_archived=True) if query else job.list(include_archived=True)
    official_records(records, title="커리어 여정", empty="등록된 직업 기록이 없습니다.")
    statuses = ["SAVED", "APPLIED", "INTERVIEW", "OFFER", "ACCEPTED", "REJECTED", "WITHDRAWN", "ARCHIVED"]
    for item in records:
        with st.expander(f"{item['company']} · {item['title']} · {item['status']}"):
            st.caption(f"{item['employment_type']} · {item['location'] or 'location not set'}")
            new_status = st.selectbox("Status", statuses, index=statuses.index(item["status"]),
                                      key=f"job_status_{item['job_id']}")
            if st.button("Save Status", key=f"job_save_{item['job_id']}"):
                job.transition(item["job_id"], new_status)
                st.rerun()
            lifecycle_label = "Restore" if item["status"] == "ARCHIVED" else "Archive"
            if st.button(lifecycle_label, key=f"job_lifecycle_{item['job_id']}"):
                if item["status"] == "ARCHIVED":
                    job.restore(item["job_id"])
                    st.success("Job restored to Saved.")
                else:
                    job.archive(item["job_id"])
                    st.success("Job archived.")
                st.rerun()
            if item["notes"]:
                st.write(item["notes"])
    if not records:
        st.info("No job records match this view.")


def render_job_management(job: JobSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.title("Job Management")
    summary = job.management_summary()
    cols = st.columns(6)
    cols[0].metric("Total", summary["total"])
    cols[1].metric("Pipeline", summary["active_pipeline"])
    cols[2].metric("Due Actions", summary["due_actions"])
    cols[3].metric("Offers", summary["offers"])
    cols[4].metric("Accepted", summary["accepted"])
    cols[5].metric("Registry", "REGISTERED" if summary["registry_registered"] else "MISSING")
    st.write("Pipeline status")
    st.json(summary["by_status"])
    st.write("Upcoming actions")
    st.dataframe(summary["upcoming_actions"])
    st.write("Database Adapter")
    st.json(summary["health"])


def render_knowledge_subsystem(knowledge: KnowledgeSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Knowledge", "지식 서고", "배움과 자료를 기록하고 다시 연결합니다.", "READY")
    st.caption("배움, 메모, 자료와 아이디어를 연결해 나만의 지식으로 보존합니다.")
    search, status = st.columns([3, 1])
    query = search.text_input("Search Knowledge", key="knowledge_subsystem_search")
    selected_status = status.selectbox("Status", ["All", "NEW", "REVIEW", "ORGANIZED", "ACTIVE", "ARCHIVED"])
    with st.expander("Create Knowledge", expanded=False):
        with st.form("knowledge_subsystem_create"):
            title = st.text_input("Title")
            content = st.text_area("Content")
            summary = st.text_input("Summary")
            category = st.text_input("Category", value="General")
            tags = st.text_input("Tags")
            importance = st.slider("Importance", 1, 5, 3)
            submitted = st.form_submit_button("Create")
        if submitted:
            try: knowledge.create(title, content, summary=summary, category=category, tags=_tags(tags), importance=importance)
            except ValueError as exc: st.error(str(exc))
            else: st.success("Knowledge created."); st.rerun()
    records = knowledge.search(query, include_archived=True) if query else knowledge.list(include_archived=True)
    if selected_status != "All": records = [item for item in records if item["status"] == selected_status]
    official_records(records, title="지식 컬렉션", empty="연결된 지식 기록이 없습니다.")
    for item in records:
        with st.expander(f"{item['title']} · {item['status']} · importance {item['importance']}"):
            st.write(item["content"]); st.caption(f"{item['category']} · {', '.join(item['tags']) or 'no tags'}")
            new_status = st.selectbox("Update status", ["NEW", "REVIEW", "ORGANIZED", "ACTIVE", "ARCHIVED"], index=["NEW", "REVIEW", "ORGANIZED", "ACTIVE", "ARCHIVED"].index(item["status"]), key=f"knowledge_status_{item['record_id']}")
            if st.button("Save Status", key=f"knowledge_save_{item['record_id']}"):
                if new_status == "ARCHIVED": knowledge.archive(item["record_id"])
                else: knowledge.update(item["record_id"], status=new_status)
                st.rerun()
            if item["status"] == "ARCHIVED" and st.button(
                "Restore", key=f"knowledge_restore_{item['record_id']}"
            ):
                knowledge.restore(item["record_id"])
                st.success("Knowledge record restored to New.")
                st.rerun()
    if not records: st.info("No Knowledge records match this view.")


def render_knowledge_management(knowledge: KnowledgeSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.title("Knowledge Management")
    summary = knowledge.management_summary(); cols = st.columns(5)
    cols[0].metric("Total", summary["total"]); cols[1].metric("Archived", summary["archived"])
    cols[2].metric("Execution Success", summary["execution_success"]); cols[3].metric("Execution Failure", summary["execution_failure"])
    cols[4].metric("Registry", "REGISTERED" if summary["registry_registered"] else "MISSING")
    st.write("Status"); st.json(summary["by_status"]); st.write("Categories"); st.json(summary["by_category"])
    st.write("Database Adapter"); st.json(summary["health"])


def render_routine_subsystem(routine: RoutineSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Routine", "리듬 순환실", "반복 행동과 실행 흐름을 안정적으로 이어갑니다.", routine.health().get("status", "READY"))
    st.caption("반복되는 생활·업무·학습·건강 습관을 안정적으로 이어갑니다.")
    with st.expander("Create Routine"):
        with st.form("routine_subsystem_create"):
            name = st.text_input("Name"); description = st.text_area("Description"); category = st.text_input("Category", value="General")
            frequency = st.selectbox("Frequency", ["DAILY", "WEEKLY", "MONTHLY", "INTERVAL"]); schedule_rule = st.text_input("Interval days", value="1")
            priority = st.slider("Priority", 1, 5, 3); active = st.checkbox("Activate now", value=True); submitted = st.form_submit_button("Create")
        if submitted:
            try: routine.create(name, description=description, category=category, frequency=frequency, schedule_rule=schedule_rule if frequency == "INTERVAL" else "", priority=priority, status="ACTIVE" if active else "DRAFT")
            except ValueError as exc: st.error(str(exc))
            else: st.success("Routine created."); st.rerun()
    routines = routine.list(include_archived=True)
    official_records(routines, title="생활 리듬", empty="등록된 루틴이 없습니다.")
    for item in routines:
        with st.expander(f"{item['name']} · {item['status']} · streak {item['streak']}"):
            st.write(item["description"]); st.caption(f"{item['frequency']} · next due {item.get('next_due_at') or '-'}")
            if item["status"] == "ARCHIVED":
                if st.button("Restore", key=f"routine_restore_{item['routine_id']}"):
                    routine.restore(item["routine_id"])
                    st.success("Routine restored in Paused state.")
                    st.rerun()
                continue
            actions = st.columns(5)
            if actions[0].button("Schedule", key=f"routine_schedule_{item['routine_id']}"): routine.schedule(item["routine_id"]); st.rerun()
            if actions[1].button("Pause", key=f"routine_pause_{item['routine_id']}"): routine.pause(item["routine_id"]); st.rerun()
            if actions[2].button("Archive", key=f"routine_archive_{item['routine_id']}"): routine.archive(item["routine_id"]); st.rerun()
            pending = [entry for entry in routine.executions(routine_id=item["routine_id"]) if entry["status"] == "PENDING"]
            if pending:
                execution_id = pending[0]["execution_id"]
                if actions[3].button("Complete", key=f"routine_complete_{execution_id}"): routine.complete(execution_id); st.rerun()
                if actions[4].button("Skip", key=f"routine_skip_{execution_id}"): routine.skip(execution_id); st.rerun()
    if not routines: st.info("No routines yet.")


def render_routine_management(routine: RoutineSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.title("Routine Management")
    summary = routine.management_summary(); cols = st.columns(6)
    cols[0].metric("Total", summary["total"]); cols[1].metric("Due", summary["due"]); cols[2].metric("Completed", summary["completion_count"])
    cols[3].metric("Failed", summary["failure_count"]); cols[4].metric("Best Streak", summary["max_streak"]); cols[5].metric("Registry", "REGISTERED" if summary["registry_registered"] else "MISSING")
    st.json(summary["by_status"]); st.write("Database Adapter"); st.json(summary["health"]); st.write("Recent execution results"); st.dataframe(summary["recent_executions"])


def render_dashboard(hub: LivingHub, systems: dict[str, Any] | None = None) -> None:
    """Open the Living OS world without exposing a management dashboard beneath it."""
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()

    def navigate(target: str) -> None:
        st.session_state.nav_page = target

    with st.container(key="living_world"):
        home_core(
            greeting="리빙 OS에 오신 것을 환영합니다.",
            date_label="",
            summary="생활의 각 공간을 탐험합니다.",
            ai_brief="",
            schedule="",
            priority="",
            status="READY",
        )
        st.button("입장 →", key="world_enter", on_click=navigate, args=("Daily Log",))
        world_nodes = (
            ("◒  재무", "Finance", "finance"), ("▱  직업", "Job", "job"),
            ("↗  투자", "Investment", "investment"), ("◫  지식", "Knowledge", "knowledge"),
            ("↻  루틴", "Routine", "routine"), ("△  자기계발", "Personal Growth", "growth"),
            ("◒  식사", "Food", "food"), ("⌂  주거", "Housing", "housing"),
            ("♡  건강", "Health", "health"), ("◇  차량", "Vehicle", "vehicle"),
        )
        for label, target, key in world_nodes:
            st.button(label, key=f"world_node_{key}", on_click=navigate, args=(target,))
        world_navigation = (
            ("대시보드", "Command Center", "dashboard"), ("오늘", "Daily Log", "today"),
            ("의사결정 로그", "Decision Log", "decision"), ("리포트", "Reports", "reports"),
            ("AI 어시스턴트", "AI Analysis", "ai"),
        )
        for label, target, key in world_navigation:
            st.button(label, key=f"world_nav_{key}", on_click=navigate, args=(target,))

def render_personal_growth(growth: PersonalGrowthSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Personal Growth", "성장 온실", "의도를 측정 가능한 성장과 선명한 다음 행동으로 이어갑니다.", growth.health().get("status", "READY"))
    summary = growth.management_summary(); cols = st.columns(4)
    cols[0].metric("Active", summary["active"]); cols[1].metric("Average Progress", f"{summary['average_progress']}%")
    cols[2].metric("Completed", summary["completed"]); cols[3].metric("Overdue", summary["overdue"])
    create_tab, portfolio_tab = st.tabs(["Create goal", "Growth portfolio"])
    with create_tab:
        with st.form("growth_create", clear_on_submit=True):
            title = st.text_input("Goal title"); area = st.selectbox("Growth area", ["MIND", "BODY", "CAREER", "RELATIONSHIPS", "CREATIVITY", "FINANCE", "OTHER"])
            purpose = st.text_area("Purpose"); next_action = st.text_input("Next action"); priority = st.slider("Priority", 1, 5, 3); submitted = st.form_submit_button("Create goal")
        if submitted:
            try: growth.create(title, area=area, purpose=purpose, next_action=next_action, priority=priority)
            except ValueError as exc: st.error(str(exc))
            else: st.success("Growth goal created."); st.rerun()
    with portfolio_tab:
        records = growth.list(include_archived=True)
        official_records(records, title="성장 목표", empty="집중할 성장 목표를 만들어 보세요.")
        if not records: st.info("No growth goals yet. Create a focused goal to start.")
        for item in records:
            with st.expander(f"{item['title']} · {item['status']} · {item['progress']}%"):
                progress = st.slider("Progress", 0, 100, int(item["progress"]), key=f"growth_progress_{item['goal_id']}")
                status = st.selectbox("Status", ["PLANNED", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED"], index=["PLANNED", "ACTIVE", "PAUSED", "COMPLETED", "ARCHIVED"].index(item["status"]), key=f"growth_status_{item['goal_id']}")
                reflection = st.text_area("Reflection", value=item["last_reflection"], key=f"growth_reflection_{item['goal_id']}")
                if st.button("Save progress", key=f"growth_save_{item['goal_id']}"): growth.update(item["goal_id"], progress=progress, status=status, last_reflection=reflection); st.rerun()
                lifecycle_label = "Restore" if item["status"] == "ARCHIVED" else "Archive"
                if st.button(lifecycle_label, key=f"growth_lifecycle_{item['goal_id']}"):
                    if item["status"] == "ARCHIVED":
                        growth.restore(item["goal_id"])
                        st.success("Growth goal restored to Planned.")
                    else:
                        growth.archive(item["goal_id"])
                        st.success("Growth goal archived.")
                    st.rerun()


def render_personal_growth_management(growth: PersonalGrowthSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Growth Management", "Growth / Management", "Portfolio health, distribution, priorities, and data contract status.", growth.health().get("status", "READY"))
    summary = growth.management_summary(); cols = st.columns(5)
    for col, label, value in zip(cols, ["Total", "Active", "Completed", "Overdue", "Registry"], [summary["total"], summary["active"], summary["completed"], summary["overdue"], "REGISTERED" if summary["registry_registered"] else "MISSING"]): col.metric(label, value)
    left, right = st.columns(2); left.json({"Status": summary["by_status"], "Area": summary["by_area"]}); right.dataframe(summary["priorities"], width="stretch", hide_index=True)


def render_collaboration(collaboration: CollaborationSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Collaboration", "Collaboration / Workspace", "Coordinate partners, commitments, due dates, and blockers from one view.", collaboration.health().get("status", "READY"))
    summary = collaboration.management_summary(); cols = st.columns(4)
    cols[0].metric("Active", summary["active"]); cols[1].metric("Blocked", summary["blocked"]); cols[2].metric("Due", summary["due"]); cols[3].metric("Completed", summary["completed"])
    create_tab, work_tab = st.tabs(["New collaboration", "Active work"])
    with create_tab:
        with st.form("collaboration_create", clear_on_submit=True):
            title = st.text_input("Title"); partner = st.text_input("Partner / team"); objective = st.text_area("Shared objective"); next_action = st.text_input("Next action"); priority = st.slider("Priority", 1, 5, 3); submitted = st.form_submit_button("Create collaboration")
        if submitted:
            try: collaboration.create(title, partner, objective=objective, next_action=next_action, priority=priority)
            except ValueError as exc: st.error(str(exc))
            else: st.success("Collaboration created."); st.rerun()
    with work_tab:
        records = collaboration.list(include_archived=True)
        if not records: st.info("No collaboration records yet.")
        for item in records:
            with st.expander(f"{item['title']} · {item['partner']} · {item['status']}"):
                status = st.selectbox("Status", ["PLANNED", "ACTIVE", "BLOCKED", "COMPLETED", "ARCHIVED"], index=["PLANNED", "ACTIVE", "BLOCKED", "COMPLETED", "ARCHIVED"].index(item["status"]), key=f"collab_status_{item['collaboration_id']}")
                notes = st.text_area("Coordination notes", value=item["notes"], key=f"collab_notes_{item['collaboration_id']}")
                if st.button("Save collaboration", key=f"collab_save_{item['collaboration_id']}"): collaboration.update(item["collaboration_id"], status=status, notes=notes); st.rerun()
                lifecycle_label = "Restore" if item["status"] == "ARCHIVED" else "Archive"
                if st.button(lifecycle_label, key=f"collab_lifecycle_{item['collaboration_id']}"):
                    if item["status"] == "ARCHIVED":
                        collaboration.restore(item["collaboration_id"])
                        st.success("Collaboration restored to Planned.")
                    else:
                        collaboration.archive(item["collaboration_id"])
                        st.success("Collaboration archived.")
                    st.rerun()


def render_collaboration_management(collaboration: CollaborationSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Collaboration Management", "Collaboration / Management", "Pipeline health, blockers, partner distribution, and control status.", collaboration.health().get("status", "READY"))
    summary = collaboration.management_summary(); cols = st.columns(5)
    for col, label, value in zip(cols, ["Total", "Active", "Blocked", "Due", "Registry"], [summary["total"], summary["active"], summary["blocked"], summary["due"], "REGISTERED" if summary["registry_registered"] else "MISSING"]): col.metric(label, value)
    left, right = st.columns(2); left.json({"Status": summary["by_status"], "Partner": summary["by_partner"]}); right.dataframe(summary["priorities"], width="stretch", hide_index=True)


def render_database(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    management = hub.database_management; health = management.health_check(record=False); schema = management.schema_registry()
    page_header("Database Contract", "System / Database", "Execution Database, schema, registry, and integrity observability.", str(health.get("status", "UNKNOWN")))
    cols = st.columns(4); cols[0].metric("Schema", f"{schema.get('schema_version', 0)} / {schema.get('expected_schema_version', 0)}"); cols[1].metric("Integrity", health.get("integrity_status", "unknown")); cols[2].metric("Components", len(management.component_status())); cols[3].metric("Executions", len(hub.database.execution_records(500)))
    st.dataframe(management.component_status(), width="stretch", hide_index=True); st.dataframe(hub.database.execution_records(100), width="stretch", hide_index=True)


def render_database_management(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    management = hub.database_management; health = management.health_check(record=False); backups = management.backup_status()
    page_header("Database Management", "System / Control Plane", "Health checks, verified backup readiness, restore safety, and operational reporting.", str(health.get("status", "UNKNOWN")))
    cols = st.columns(4); cols[0].metric("Database", health.get("status", "UNKNOWN")); cols[1].metric("Integrity", health.get("integrity_status", "unknown")); cols[2].metric("Verified Backups", len(backups)); cols[3].metric("Size", f"{int(health.get('file_size', 0)):,} bytes")
    if st.button("Run health check", key="database_management_health"): st.session_state.v20_database_health = management.health_check(record=True, actor="owner")
    if st.button("Create verified backup", key="database_management_backup"):
        try: path = management.request_backup(actor="owner")
        except (OSError, ValueError): st.error("Backup failed verification; the source database was preserved.")
        else: st.success(f"Verified backup created: {path.name}"); st.rerun()
    if st.session_state.get("v20_database_health"): st.json(st.session_state.v20_database_health)
    st.dataframe(backups, width="stretch", hide_index=True)


def render_journal(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    service = JournalService(hub)
    page_header("Journal", "오늘의 기록", "오늘의 생각과 생활 흐름을 차분히 남깁니다.", "READY")
    st.caption("Daily operating records saved through explicit audited commands.")
    with st.form("v2_journal_form", clear_on_submit=True):
        entry_date = st.date_input("Date").isoformat()
        title = st.text_input("Title")
        mood = st.text_input("Status")
        tags = st.text_input("Tags")
        content = st.text_area("Journal Entry", height=220)
        submitted = st.form_submit_button("Save Journal Entry")
    if submitted:
        try:
            record = service.create(entry_date, title, content, _tags(tags), mood)
        except (CoreError, OSError, ValueError):
            st.error("The Journal entry could not be saved. Canonical data was not changed.")
        else:
            st.success(f"Saved {record['id']}")
    st.divider()
    for item in service.list()[:50]:
        with st.expander(f"{item.get('date', '-')} — {item.get('title', 'Untitled')}"):
            st.write(item.get("content", ""))
            st.caption(f"Version {item.get('_version', 1)} · Tags: {', '.join(item.get('tags', []))}")


def render_decisions(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    service = DecisionService(hub)
    page_header("Decision", "의사결정 기록", "선택의 근거와 결과를 함께 보존합니다.", "READY")
    st.caption("Versioned decisions with evidence, review, outcomes, and audit.")
    with st.form("v2_decision_form", clear_on_submit=True):
        decision = st.text_input("Decision")
        reason = st.text_area("Reason")
        expected = st.text_area("Expected Result")
        actual = st.text_area("Actual Result")
        review_note = st.text_area("Review Note")
        status = st.selectbox("Status", ["draft", "active", "review", "done", "archive"], index=1)
        submitted = st.form_submit_button("Save Decision")
    if submitted:
        try:
            record = service.create(decision, reason, expected, actual, review_note, status)
        except (CoreError, OSError, ValueError):
            st.error("The Decision could not be saved. Canonical data was not changed.")
        else:
            st.success(f"Saved {record['id']}")
    st.divider()
    for item in service.list()[:50]:
        with st.expander(f"{item.get('decision', 'Untitled')} — {item.get('status', 'draft')}"):
            st.write(item.get("reason", ""))
            st.caption(f"{item.get('id')} · Version {item.get('_version', 1)}")
            new_status = st.selectbox(
                "Review status",
                ["draft", "active", "review", "done", "archive"],
                index=["draft", "active", "review", "done", "archive"].index(str(item.get("status", "draft"))),
                key=f"decision_status_{item.get('id')}",
            )
            note = st.text_input("Review note", value=str(item.get("review_note", "")), key=f"decision_note_{item.get('id')}")
            if st.button("Save Decision Revision", key=f"revise_{item.get('id')}"):
                try:
                    service.revise(str(item["id"]), int(item.get("_version", 1)), status=new_status, review_note=note)
                except (CoreError, OSError, ValueError):
                    st.error("The Decision revision was rejected. Refresh and try again.")
                else:
                    st.success("Decision revision saved.")
                    st.rerun()


def render_knowledge(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    service = KnowledgeService(hub)
    page_header("Knowledge", "지식 서고", "배움과 자료를 기록하고 다시 연결합니다.", "READY")
    st.caption("Notes, archive material, cases, and governed Living Rule promotion.")
    with st.form("v2_knowledge_form", clear_on_submit=True):
        title = st.text_input("Title")
        source = st.text_input("Source")
        kind = st.selectbox("Kind", ["note", "archive"])
        tags = st.text_input("Tags")
        content = st.text_area("Content", height=180)
        submitted = st.form_submit_button("Save Knowledge Item")
    if submitted:
        try:
            record = service.create(title, content, source, _tags(tags), kind)
        except (CoreError, OSError, ValueError):
            st.error("The Knowledge item could not be saved.")
        else:
            st.success(f"Saved {record['id']}")
    query = st.text_input("Search Knowledge").strip().lower()
    items = service.list()
    if query:
        items = [item for item in items if query in " ".join((str(item.get("title", "")), str(item.get("content", "")), str(item.get("tags", [])))).lower()]
    for item in items[:100]:
        with st.expander(f"{item.get('kind', 'note')} — {item.get('title', 'Untitled')}"):
            st.write(item.get("content", ""))
            st.caption(f"{item.get('id')} · Version {item.get('_version', 1)}")
            if item.get("kind") != "living_rule":
                reason = st.text_input("Promotion reason", key=f"promote_reason_{item.get('id')}")
                if st.button("Promote Reviewed Knowledge", key=f"promote_{item.get('id')}"):
                    try:
                        service.promote(str(item["id"]), int(item.get("_version", 1)), reason)
                    except (CoreError, OSError, ValueError):
                        st.error("Promotion was rejected. A review reason and current version are required.")
                    else:
                        st.success("Knowledge item promoted.")
                        st.rerun()


def render_timeline(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Global Timeline", "MEMORY ORBIT / TIMELINE", "모든 하위 시스템의 생활 사건을 하나의 시간 궤도에서 탐색합니다.", "ACTIVE")
    workspace_rail("타임라인 필터", "기간·하위 시스템·분류·검색어를 조합해 생활의 흐름을 좁힙니다.", icon="↕", meta="ORBIT FILTER")
    dates = st.columns(2)
    start = dates[0].date_input("From", value=date.today().replace(day=1), key="timeline_start")
    end = dates[1].date_input("To", value=date.today(), key="timeline_end")
    filters = st.columns(4)
    subsystem = filters[0].selectbox("Subsystem", ["All", *hub.timeline.supported_subsystems()], key="timeline_subsystem")
    categories = hub.timeline.categories(subsystem=None if subsystem == "All" else subsystem)
    category = filters[1].selectbox("Category", ["All", *categories], key="timeline_category")
    query = filters[2].text_input("Search", key="timeline_search")
    order = filters[3].selectbox("Order", ["Newest", "Oldest"], key="timeline_sort")
    include_archived = st.toggle("Include archived", value=True, key="timeline_archived")
    if start > end:
        st.error("The start date cannot be after the end date."); return
    records = hub.timeline.query(start=start, end=end, subsystem=None if subsystem == "All" else subsystem,
        category=None if category == "All" else category, search=query, include_archived=include_archived,
        sort_order="desc" if order == "Newest" else "asc", limit=1000)
    metric_deck((
        {"label": "Results", "value": len(records), "detail": "선택한 조건의 사건", "status": "ACTIVE"},
        {"label": "Subsystems", "value": len({item.subsystem for item in records}), "detail": "연결된 생활 영역", "status": "READY"},
        {"label": "Archived", "value": sum(item.archived for item in records), "detail": "보관된 기록", "status": "ARCHIVED"},
    ), label="TIMELINE SIGNALS")
    workspace_rail("시간 궤도", "최신 사건과 상태 이동을 카드와 상세 기록으로 확인합니다.", icon="⌁", meta="EVENT STREAM")
    if not records:
        state_panel("일치하는 타임라인이 없습니다", "기간을 넓히거나 필터를 해제해 보세요."); return
    payload = [item.to_dict() for item in records]
    official_records(payload, title="전체 타임라인", empty="조건에 맞는 생활 기록이 없습니다.", limit=24)
    labels = [f"{item.subsystem} · {item.title} · {item.record_id}" for item in records]
    detail = records[labels.index(st.selectbox("Detail view", labels, key="timeline_detail"))]
    official_insight("선택한 타임라인", detail.to_dict(), caption="생활 기록의 현재 상태와 연결 정보")
    history = hub.timeline.status_history(detail.subsystem, detail.record_id)
    if history:
        panel_header("상태 이동 이력", "선택한 기록의 시간별 상태 변경", "HISTORY")
        official_records([item.to_dict() for item in history], title="상태 이동 이력", empty="상태 이동 이력이 없습니다.", limit=24)

def render_global_search(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Global Search", "LIVING INDEX / SEARCH", "생활 기록 전체를 한 번에 탐색하고 원래 공간으로 이동할 단서를 찾습니다.", "READY")
    workspace_rail("통합 검색", "제목·요약·식별자·분류를 기준으로 모든 연결 기록을 찾습니다.", icon="⌕", meta="UNIFIED DISCOVERY")
    query = st.text_input("Search all records", key="global_search")
    cols = st.columns(4)
    subsystem = cols[0].selectbox("Subsystem", ["All", *hub.timeline.supported_subsystems()], key="search_subsystem")
    category = cols[1].selectbox("Category", ["All", *hub.timeline.categories()], key="search_category")
    sort_by = cols[2].selectbox("Sort by", ["relevance", "event_time", "title", "subsystem"], key="search_sort")
    include_archived = cols[3].toggle("Archived", value=True, key="search_archived")
    results = GlobalSearchEngine(hub.timeline).search(query, subsystem=None if subsystem == "All" else subsystem,
        category=None if category == "All" else category, include_archived=include_archived, sort_by=sort_by, limit=200)
    metric_deck((
        {"label": "Results", "value": len(results), "detail": "검색된 생활 기록", "status": "ACTIVE" if results else "READY"},
        {"label": "Subsystems", "value": len({item.subsystem for item in results}), "detail": "결과가 있는 영역", "status": "READY"},
        {"label": "Archived", "value": sum(item.archived for item in results), "detail": "보관 결과 포함", "status": "ARCHIVED"},
    ), label="SEARCH SIGNALS")
    workspace_rail("검색 결과", "관련도와 시간 흐름을 함께 확인할 수 있습니다.", icon="◇", meta="RESULT CONSTELLATION")
    if not results:
        state_panel("검색 결과가 없습니다", "검색어를 줄이거나 필터를 제거해 보세요."); return
    official_records([item.to_dict() for item in results], title="전체 검색 결과", empty="검색 결과가 없습니다.", limit=24)
    labels = [f"{item.subsystem} · {item.title} · {item.record_id}" for item in results]
    selected_result = results[labels.index(st.selectbox("Result detail", labels, key="search_detail"))]
    official_insight("선택한 검색 결과", selected_result.to_dict(), caption="찾은 기록의 사용자용 상세 정보")

def render_reports(hub: LivingHub, systems: dict[str, Any] | None = None) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    sources = {name.casefold().replace(" ", "-"): provider for name, provider in (systems or {}).items()}
    service = ReportsService(hub, sources)
    page_header("Reports", "MEMORY ATLAS / REPORT", "기존 생활 기록을 일·주·월·연 단위의 결정 가능한 서사로 정리합니다.", "READY")
    workspace_rail("리포트 범위", "AI 없이도 재현 가능한 결정론적 요약을 생성합니다.", icon="▤", meta="REPORT COMPASS")
    report_type = st.selectbox("Report Type", ["daily", "weekly", "monthly", "yearly"])
    summary = service.report_summary(report_type)
    metric_deck((
        {"label": "Timeline events", "value": summary["timeline_events"], "detail": "기간 내 생활 사건", "status": "ACTIVE"},
        {"label": "Active", "value": summary["active_events"], "detail": "진행 중 기록", "status": "HEALTHY"},
        {"label": "Archived", "value": summary["archived_events"], "detail": "보관된 기록", "status": "ARCHIVED"},
        {"label": "Subsystems", "value": len(summary["by_subsystem"]), "detail": "요약에 연결된 영역", "status": "READY"},
    ), label="REPORT SIGNALS")
    cross = service.cross_subsystem_summary(report_type)
    workspace_rail("교차 하위 시스템 요약", "서로 다른 생활 영역의 사건을 하나의 보고 흐름으로 연결합니다.", icon="◉", meta="CROSS SYSTEM")
    if cross:
        official_records(cross, title="교차 영역 활동", empty="이 기간에는 교차 영역 활동이 없습니다.", limit=18)
    else:
        state_panel("요약할 활동이 없습니다", "이 리포트 기간에는 하위 시스템 활동이 없습니다.")
    preview = service.build(report_type)
    workspace_rail("결정론적 리포트", "편집 후 명시적으로 저장할 수 있는 공식 리포트 본문입니다.", icon="◇", meta="CANONICAL DRAFT")
    edited = st.text_area("Deterministic Report", value=preview, height=400)
    if st.button("Save Report"):
        try: record = service.save(report_type, edited)
        except (CoreError, OSError, ValueError): st.error("The report could not be saved.")
        else: st.success(f"Saved {record['id']}")
    workspace_rail("선택적 AI 초안", "AI는 정식 데이터를 직접 변경하지 않으며 별도의 승인이 필요합니다.", icon="✧", meta="OPTIONAL INTELLIGENCE")
    _ensure_ai_model(st)
    official_document("결정론적 리포트 원문", preview, caption="AI 초안 생성 전에 확인하는 공식 리포트 본문")
    if st.button("Generate AI Report Draft"):
        api_key, _ = resolve_api_key(
            str(st.session_state.get("ai_session_api_key", "")),
            allow_shared_sources=not hub.runtime_config.production,
        )
        if not api_key: st.error("Configure an OpenAI API key in Settings first.")
        else:
            try: st.session_state.v2_ai_report_draft = AIBriefingService(hub, OpenAITextProvider(api_key)).analyze("report", st.session_state.ai_model, preview)
            except AIServiceError as exc: st.error(str(exc))
    draft = str(st.session_state.get("v2_ai_report_draft", ""))
    if draft:
        edited_draft = st.text_area("Unsaved AI Draft", value=draft, height=350)
        if st.button("Save AI Draft (Explicit Approval)"):
            try: service.save(report_type, edited_draft, generated_by="ai-approved-draft")
            except (CoreError, OSError, ValueError): st.error("The AI draft could not be saved.")
            else: st.success("AI draft saved as a canonical report artifact.")
    saved = service.list(include_archived=True)[:50]
    workspace_rail("저장된 리포트", "명시적으로 저장된 공식 리포트 아카이브입니다.", icon="▣", meta="REPORT ARCHIVE")
    if not saved: state_panel("저장된 리포트가 없습니다", "리포트를 생성하고 저장하면 여기에 표시됩니다.")
    else: record_gallery(saved, empty="저장된 리포트가 없습니다.", limit=8)

def _render_counter(title: str, counter: Counter[str]) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.subheader(title)
    if counter:
        official_records([{"name": key, "count": value} for key, value in counter.most_common()], title=title, empty="아직 데이터가 없습니다.")
    else:
        st.info("No data yet.")


def render_analytics(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    engine = AnalyticsEngine(hub.timeline)
    page_header("Analytics", "LIFE OBSERVATORY / ANALYTICS", "생활 데이터의 추세·비교·성장 신호를 읽기 전용 관측소에서 확인합니다.", "ACTIVE")
    workspace_rail("관측 범위", "분석할 기간과 하위 시스템을 선택합니다.", icon="⌁", meta="OBSERVATION WINDOW")
    cols = st.columns(3)
    start = cols[0].date_input("From", value=date.today().replace(day=1), key="analytics_start")
    end = cols[1].date_input("To", value=date.today(), key="analytics_end")
    subsystem = cols[2].selectbox("Subsystem", ["All", *hub.timeline.supported_subsystems()], key="analytics_subsystem")
    if start > end: st.error("The start date cannot be after the end date."); return
    selected = None if subsystem == "All" else subsystem
    summary = engine.summary(start, end, subsystem=selected)
    metric_deck((
        {"label": "Activity", "value": summary["total_activity"], "detail": "선택 기간 전체 활동", "status": "ACTIVE"},
        {"label": "Active", "value": summary["active_activity"], "detail": "현재 진행 중인 흐름", "status": "HEALTHY"},
        {"label": "Archived", "value": summary["archived_activity"], "detail": "보관된 흐름", "status": "ARCHIVED"},
        {"label": "Subsystems", "value": summary["subsystem_count"], "detail": "관측된 생활 영역", "status": "READY"},
    ), label="OBSERVATORY SIGNALS")
    workspace_rail("인사이트 관측소", "추세·비교·월간/연간·성장 분석을 전환해 확인합니다.", icon="◎", meta="INSIGHT CHAMBERS")
    trend_tab, compare_tab, summary_tab, growth_tab = st.tabs(["Trend", "Comparison", "Monthly / Yearly", "Growth"])
    with trend_tab:
        panel_header("추세 궤도", "월 단위 활동 변화", "TREND")
        trend = engine.trend(start, end, subsystem=selected, granularity="month")
        if trend:
            official_records(trend, title="추세 기록", empty="추세 데이터가 없습니다.", limit=18)
        else: state_panel("추세 데이터가 없습니다", "선택한 기간에 기록이 쌓이면 변화가 나타납니다.")
    with compare_tab:
        comparison = engine.comparison(start, end, subsystem=selected)
        metric_deck((
            {"label": "Current", "value": comparison["current"]["total_activity"], "detail": "현재 기간", "status": "ACTIVE"},
            {"label": "Previous", "value": comparison["previous"]["total_activity"], "detail": "이전 기간", "status": "READY"},
            {"label": "Growth", "value": f"{comparison['growth_percent']}%", "detail": "기간 대비 변화", "status": "HEALTHY" if comparison["growth_percent"] >= 0 else "WARNING"},
        ), label="COMPARISON SIGNALS")
        official_records(comparison["by_subsystem"], title="영역별 비교", empty="비교할 영역 데이터가 없습니다.", limit=18)
    with summary_tab:
        left, right = st.columns(2)
        with left:
            panel_header("월간 요약", "선택 월의 생활 신호", "MONTH")
            official_insight("월간 생활 요약", engine.monthly_summary(end.year, end.month, subsystem=selected), caption="선택한 월의 영역별 생활 신호")
        with right:
            panel_header("연간 요약", "선택 연도의 생활 신호", "YEAR")
            official_insight("연간 생활 요약", engine.yearly_summary(end.year, subsystem=selected), caption="선택한 연도의 영역별 생활 신호")
    with growth_tab:
        growth = engine.growth_analysis(as_of=end, months=12, subsystem=selected)
        metric_deck(({"label": "12-month growth", "value": f"{growth['growth_percent']}%", "detail": f"순변화 {growth['net_growth']}", "status": "HEALTHY" if growth["growth_percent"] >= 0 else "WARNING"},), label="GROWTH SIGNAL")
        official_records(growth["trend"], title="성장 추세", empty="성장 추세 데이터가 없습니다.", limit=18)

def render_review(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    data = review_projection(hub)
    st.title("Review")
    st.caption("Human review queue derived from canonical records.")
    st.metric("Decisions Needing Review", len(data["queue"]))
    for item in data["queue"]:
        st.write(f"{item.get('decision', 'Untitled')} · {item.get('status', 'draft')}")
    st.divider()
    st.subheader("Recent Activity")
    for item in data["activity"]:
        st.write(f"{item['type']} · {item['title']}")
        st.caption(str(item.get("updated_at", "")))


def _ensure_ai_model(st: Any) -> None:
    if "ai_model" not in st.session_state or st.session_state.ai_model not in AI_MODELS:
        st.session_state.ai_model = DEFAULT_AI_MODEL
    st.selectbox("OpenAI Model", AI_MODELS, key="ai_model")


def _ai_panel(
    hub: LivingHub,
    records: list[dict[str, Any]],
    fields: tuple[str, ...],
    request_type: str,
    state_key: str,
) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    if not records:
        st.info("No canonical records are available.")
        return
    identifiers = [str(item.get("id", "")) for item in records]
    selected_id = st.selectbox("Select record", identifiers, key=f"select_{state_key}")
    record = next(item for item in records if str(item.get("id", "")) == selected_id)
    source = record_source(record, fields)
    st.warning("Only the visible selected fields will be sent after explicit approval.")
    official_document("전송 전 확인", source, caption="선택한 기록에서 AI 분석에 사용할 항목")
    if st.button("Request Read-only Analysis", key=f"request_{state_key}"):
        api_key, _ = resolve_api_key(
            str(st.session_state.get("ai_session_api_key", "")),
            allow_shared_sources=not hub.runtime_config.production,
        )
        if not api_key:
            st.error("Configure an OpenAI API key in Settings first.")
        else:
            try:
                briefing = AIBriefingService(hub, OpenAITextProvider(api_key))
                st.session_state[state_key] = briefing.analyze(request_type, st.session_state.ai_model, source)
            except AIServiceError as exc:
                st.error(str(exc))
    result = str(st.session_state.get(state_key, ""))
    if result:
        st.caption("Unsaved, untrusted draft. No canonical record was changed.")
        st.markdown(result)


def render_ai_briefing(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("AI Briefing", "AI 브리핑", "내가 선택한 생활 기록을 읽기 전용으로 분석합니다.", "READY")
    st.caption("Source-attributed, explicit, read-only AI analysis.")
    st.text_input(
        "OpenAI API Key",
        type="password",
        key="ai_session_api_key",
    )
    st.caption("키는 현재 브라우저 세션에서만 사용되며 저장되지 않습니다.")
    _ensure_ai_model(st)
    journal_tab, decision_tab = st.tabs(["Journal", "Decision"])
    with journal_tab:
        _ai_panel(
            hub,
            hub.store.list_records("journal", "journal_entry"),
            ("id", "date", "title", "content", "tags", "mood", "created_at", "updated_at"),
            "journal",
            "v2_ai_journal_result",
        )
    with decision_tab:
        _ai_panel(
            hub,
            hub.store.list_records("decision", "decision"),
            ("id", "decision", "reason", "expected_result", "actual_result", "review_note", "status"),
            "decision",
            "v2_ai_decision_result",
        )


def render_documents(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    st.title("Documents")
    st.caption("Content-integrity foundation with versioned references and privacy classification.")
    uploaded = st.file_uploader("Choose a document")
    privacy = st.selectbox("Privacy", ["personal", "sensitive", "restricted", "public"])
    if st.button("Add Document"):
        if uploaded is None:
            st.error("Choose a document first.")
        else:
            try:
                document = hub.documents.add(uploaded.name, uploaded.getvalue(), media_type=uploaded.type, privacy_class=privacy)
            except (OSError, ValueError):
                st.error("The document could not be added safely.")
            else:
                st.success(f"Added {document.filename} · {document.document_id}")
    st.divider()
    for document in hub.documents.list():
        st.write(f"{document.filename} · v{document.version} · {document.privacy_class}")
        st.caption(f"SHA-256 {document.content_hash} · {document.size_bytes} bytes")


def render_module_manager(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    modules = hub.modules.list_modules()
    page_header("Module Manager", "SYSTEM CONSTELLATION / MODULES", "설치된 생활 모듈의 상태·건강·수명주기를 하나의 시스템 성좌에서 관리합니다.", "READY")
    metric_deck((
        {"label": "Total", "value": len(modules), "detail": "등록된 전체 모듈", "status": "READY"},
        {"label": "Active", "value": sum(item.get("status") == "enabled" for item in modules), "detail": "활성 모듈", "status": "HEALTHY"},
        {"label": "Degraded", "value": sum(item.get("status") == "degraded" for item in modules), "detail": "확인이 필요한 모듈", "status": "WARNING"},
        {"label": "Disabled", "value": sum(item.get("status") == "disabled" for item in modules), "detail": "비활성 모듈", "status": "ARCHIVED"},
    ), label="MODULE SIGNALS")
    workspace_rail("모듈 성좌", "각 모듈의 설명·버전·호환성·수명주기 전환을 확인합니다.", icon="⬡", meta="LIFECYCLE CONTROL")
    for module in modules:
        module_id = str(module["module_id"])
        with st.expander(f"{module.get('name', module_id)} · {module.get('status')} · {module.get('health')}"):
            st.write(module.get("description", ""))
            st.caption(f"Version {module.get('version')} · Core {module.get('core_compatibility')}")
            current = str(module.get("status")); targets = sorted(LIFECYCLE_TRANSITIONS.get(current, set()))
            if module_id in {"module_manager", "settings"}:
                st.info("Core administration modules cannot be disabled from their own control surface.")
            elif targets:
                target = st.selectbox("Lifecycle action", targets, key=f"lifecycle_{module_id}")
                if st.button("Apply Lifecycle Change", key=f"apply_lifecycle_{module_id}"):
                    try: hub.modules.transition(module_id, target)
                    except ValueError as exc: st.error(str(exc))
                    else: st.success(f"{module_id}: {current} → {target}"); st.rerun()

def render_owner_data_control(
    hub: LivingHub, systems: dict[str, Any]
) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    legacy = (
        {}
        if hub.runtime_config.production
        else development_legacy_empty_states(hub.repository_root)
    )
    service = OwnerDataResetService(
        hub,
        tuple(systems.values()),
        legacy_empty_states=legacy,
    )
    preview = service.preview()
    total = sum(preview.values())
    st.subheader("내 데이터 관리")
    st.caption(
        "생활 기록을 초기 상태로 되돌립니다. 소유자 인증, 시스템 구조와 "
        "마이그레이션 정보는 보존됩니다."
    )
    st.write(f"초기화 대상: {total:,}개")
    if total == 0:
        st.info("초기화할 사용자 데이터가 없습니다.")
        return
    st.warning(
        "실행 전에 검증된 백업을 만듭니다. 이 작업은 모든 생활 영역의 "
        "사용자 기록을 삭제합니다."
    )
    confirmed = st.checkbox(
        "초기화 범위와 영향을 확인했습니다.",
        key="owner_data_reset_scope_confirmed",
    )
    phrase = st.text_input(
        "확인을 위해 초기화를 입력하세요.",
        key="owner_data_reset_phrase",
    )
    if st.button(
        "사용자 데이터 초기화",
        disabled=not confirmed or phrase.strip() != "초기화",
        key="owner_data_reset_execute",
    ):
        try:
            report = service.reset(actor="owner")
        except OwnerDataResetError as exc:
            st.error(str(exc))
        else:
            st.session_state.ai_session_api_key = ""
            st.session_state.owner_data_reset_result = report.to_dict()
            st.success(
                f"사용자 데이터 {report.total_removed:,}개를 초기화했습니다."
            )
            st.rerun()


def render_settings(hub: LivingHub) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Settings / Hub Administration", "SYSTEM SANCTUM / SETTINGS", "저장소·보안·자격 증명·백업·마이그레이션을 명시적 승인 경계 안에서 관리합니다.", "READY")
    workspace_rail("런타임 저장소와 릴리스 게이트", "데이터 지속성·백업 독립성·소유자 인증 상태를 확인합니다.", icon="⚙", meta="RUNTIME GUARD")
    runtime_status = hub.runtime_config.status()
    release_gate = evaluate_release_gate(
        hub.runtime_config,
        owner_security_configured=hub.security.configured,
    )
    runtime_columns = st.columns(4)
    runtime_columns[0].metric("Environment", str(runtime_status["environment"]).upper())
    runtime_columns[1].metric("Durability", str(runtime_status["durability"]).upper())
    runtime_columns[2].metric(
        "Backup",
        "INDEPENDENT" if runtime_status["backup_independent"] else "LOCAL",
    )
    runtime_columns[3].metric(
        "Authentication",
        "REQUIRED" if runtime_status["authentication_required"] else "OPTIONAL",
    )
    st.caption(f"Data root: {runtime_status['data_root']}")
    st.caption(f"Backup root: {runtime_status['backup_root']}")
    if hub.runtime_config.production:
        if release_gate.passed:
            st.success(f"Living OS {PRODUCT_VERSION} production release gate is ready.")
        else:
            st.error(
                "Production release gate is blocked: "
                + ", ".join(release_gate.failures)
            )
    else:
        st.info(
            "Development storage profile active. Production release requires "
            "durable data, independent backup, and Owner Authentication."
        )
    st.divider()
    workspace_rail("애플리케이션 환경설정", "표시 이름과 기본 리포트 범위를 관리합니다.", icon="◇", meta="PREFERENCES")
    if hub.v1_migration_complete:
        settings_service = HubSettingsService(hub)
        current_settings = settings_service.load()
        with st.form("v2_application_preferences"):
            app_name = st.text_input("App Name", value=str(current_settings.get("app_name", "Living OS")))
            ranges = ["daily", "weekly", "monthly"]
            current_range = str(current_settings.get("default_report_range", "daily"))
            report_range = st.selectbox(
                "Default Report Range",
                ranges,
                index=ranges.index(current_range) if current_range in ranges else 0,
            )
            save_preferences = st.form_submit_button("Save Preferences")
        if save_preferences:
            try:
                settings_service.update(app_name, report_range, int(current_settings.get("_version", 0)))
            except (CoreError, OSError, ValueError):
                st.error("Preferences could not be saved. Refresh and try again.")
            else:
                st.success("Preferences saved through the canonical command boundary.")
    else:
        from subsystems.compatibility.engines.settings import load_settings, save_settings

        legacy_settings = load_settings()
        with st.form("application_preferences_fallback"):
            app_name = st.text_input("App Name", value=str(legacy_settings.get("app_name", "Living OS")))
            ranges = ["daily", "weekly", "monthly"]
            current_range = str(legacy_settings.get("default_report_range", "daily"))
            report_range = st.selectbox(
                "Default Report Range",
                ranges,
                index=ranges.index(current_range) if current_range in ranges else 0,
            )
            save_preferences = st.form_submit_button("Save Preferences")
        if save_preferences:
            try:
                save_settings({"app_name": app_name, "default_report_range": report_range})
            except (OSError, ValueError):
                st.error("Preferences could not be saved.")
            else:
                st.success("Preferences saved.")
    st.divider()
    workspace_rail("OpenAI 구성", "세션 전용 자격 증명과 모델을 관리합니다.", icon="✧", meta="INTELLIGENCE GATE")
    session_key = st.text_input(
        "OpenAI API Key",
        value=str(st.session_state.get("ai_session_api_key", "")),
        type="password",
    )
    st.session_state.ai_session_api_key = session_key.strip()
    _ensure_ai_model(st)
    st.divider()
    workspace_rail("소유자 보안과 연결 기기", "소유자 인증과 신뢰 기기 수명주기를 관리합니다.", icon="◎", meta="OWNER SECURITY")
    if not hub.security.configured:
        with st.form("configure_owner_security"):
            first = st.text_input("New owner passphrase", type="password")
            second = st.text_input("Confirm owner passphrase", type="password")
            submitted = st.form_submit_button("Enable Owner Security")
        if submitted:
            if first != second:
                st.error("Passphrases do not match.")
            else:
                try:
                    hub.security.configure(first)
                    device = hub.security.pair_device(first, "Current Browser", "browser")
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.v2_device_id = device.device_id
                    st.success("Owner security enabled and this browser paired.")
    else:
        devices = hub.security.list_devices()
        for device in devices:
            state = "revoked" if device.revoked_at else "active"
            cols = st.columns([3, 2, 1])
            cols[0].write(device.name)
            cols[1].caption(f"{device.platform} · {state}")
            if not device.revoked_at and device.device_id != st.session_state.get("v2_device_id"):
                if cols[2].button("Revoke", key=f"revoke_{device.device_id}"):
                    hub.security.revoke(device.device_id)
                    st.rerun()
        st.caption("Encrypted transport must be provided by the selected deployment profile for remote access.")
    st.divider()
    workspace_rail("데이터 저장소 마이그레이션", "검토·백업·명시적 승인 후에만 이전합니다.", icon="↕", meta="MIGRATION GATE")
    if hub.v1_migration_complete:
        st.success("The canonical Hub store is current.")
    else:
        st.warning("A legacy data store is available. Migration requires review and explicit approval.")
        if st.button("Run Migration Dry Run"):
            report = hub.migration.dry_run()
            st.session_state.v2_migration_report = report.to_dict()
        report = st.session_state.get("v2_migration_report")
        if report:
            st.json(report)
            approval = st.checkbox("I reviewed the dry run and approve backup plus migration.")
            if st.button("Create Verified Backup and Migrate"):
                if not approval:
                    st.error("Explicit migration approval is required.")
                else:
                    try:
                        applied = hub.migration.apply()
                    except (CoreError, OSError, ValueError) as exc:
                        st.error(f"Migration did not complete: {exc}")
                    else:
                        st.success(f"Migrated {applied.accepted_total} records. Backup: {applied.backup_path}")
                        st.rerun()
    st.divider()
    workspace_rail("데이터베이스 관리", "스키마·무결성·백업·복원 제어면을 확인합니다.", icon="▦", meta="DATA CONTROL")
    management = hub.database_management
    health = management.health_check(record=False)
    schema = management.schema_registry()
    migration = management.migration_status()
    status_columns = st.columns(4)
    status_columns[0].metric("Database", str(health.get("status", "UNKNOWN")))
    status_columns[1].metric(
        "Schema",
        f"{schema.get('schema_version', 0)} / {schema.get('expected_schema_version', 0)}",
    )
    status_columns[2].metric("Integrity", str(health.get("integrity_status", "unknown")))
    status_columns[3].metric("Size", f"{int(health.get('file_size', 0)):,} bytes")

    if migration["pending"]:
        st.warning("A reviewed additive Database Foundation migration is pending.")
        st.json(migration["pending"])
        migration_approval = st.checkbox(
            "I reviewed the pending database migration and approve applying it.",
            key="v17_database_migration_approval",
        )
        if st.button("Apply Approved Database Migration"):
            if not migration_approval:
                st.error("Explicit migration approval is required.")
            else:
                try:
                    applied = management.request_migration(actor="owner")
                except (OSError, ValueError) as exc:
                    st.error(f"Database migration failed and was rolled back: {type(exc).__name__}")
                else:
                    st.success(f"Applied {len(applied)} database migration(s).")
                    st.rerun()
    else:
        st.success(f"Database schema is current for Living OS {PRODUCT_VERSION}.")

    st.markdown("#### Registered component databases")
    component_status = management.component_status()
    if component_status:
        st.dataframe(
            [
                {
                    "Component": item["display_name"],
                    "Layer": item["layer"],
                    "Owner": item["owner"],
                    "Mode": item["integration_mode"],
                    "Initialized": item["initialized"],
                    "Schema": f"{item['actual_schema_version']} / {item['schema_version']}",
                    "Migration": item["migration_status"],
                    "Integrity": item["integrity"],
                    "Executions": item["execution_count"],
                    "Status": item["status"],
                }
                for item in component_status
            ],
            width="stretch",
            hide_index=True,
        )
        by_name = {item["display_name"]: item for item in component_status}
        selected_component_name = st.selectbox(
            "Component database", list(by_name), key="database_component_selection"
        )
        selected_component = by_name[selected_component_name]
        if selected_component["initialized"]:
            if st.button("Create and Verify Component Backup"):
                try:
                    path = management.request_component_backup(
                        selected_component["component_id"], actor="owner"
                    )
                except (OSError, ValueError, RuntimeError):
                    st.error("The component backup failed integrity verification.")
                else:
                    st.success(f"Verified component backup created: {path.name}")
                    st.rerun()
            component_backups = management.component_backups(
                selected_component["component_id"]
            )
            if component_backups:
                backup_by_name = {
                    Path(str(item["path"])).name: item for item in component_backups
                }
                component_backup_name = st.selectbox(
                    "Verified component restore candidate",
                    list(backup_by_name),
                    key="component_restore_candidate",
                )
                component_restore_approval = st.checkbox(
                    "I approve a safety backup and restore for this component database.",
                    key="component_restore_approval",
                )
                if st.button("Restore Selected Component Backup"):
                    if not component_restore_approval:
                        st.error("Explicit component restore approval is required.")
                    else:
                        try:
                            result = management.request_component_restore(
                                selected_component["component_id"],
                                Path(str(backup_by_name[component_backup_name]["path"])),
                                actor="owner",
                            )
                        except (OSError, ValueError, RuntimeError):
                            st.error("Component restore failed; the safety copy was retained.")
                        else:
                            st.success(
                                "Component restore complete. Safety backup: "
                                f"{Path(result['safety_backup']).name}"
                            )
                            st.rerun()
        else:
            st.info("This registered component has no data file yet; it will be created on its first write.")
            if st.button("Initialize and Verify Component Schema"):
                try:
                    initialized = management.request_component_initialization(
                        selected_component["component_id"], actor="owner"
                    )
                except (OSError, ValueError, RuntimeError):
                    st.error("Component schema initialization failed and requires review.")
                else:
                    st.success(
                        f"{initialized['display_name']} schema initialized and verified."
                    )
                    st.rerun()
    else:
        st.info("No component database contracts are registered yet.")

    if st.button("Run and Record Database Health Check"):
        recorded_health = management.health_check(record=True, actor="owner")
        st.session_state.v17_database_health = recorded_health
    if st.session_state.get("v17_database_health"):
        st.json(st.session_state.v17_database_health)

    if not migration["pending"]:
        if st.button("Create and Verify Database Backup"):
            try:
                backup_path = management.request_backup(actor="owner")
            except (OSError, ValueError):
                st.error("The database backup failed or could not be verified.")
            else:
                st.success(f"Verified backup created: {backup_path.name}")
                st.rerun()

        backups = management.backup_status()
        if backups:
            st.caption(f"Last backup: {backups[0].get('created_at', '-')} · {backups[0].get('status', '-')}")
            valid_candidates = [
                candidate for candidate in management.restore_candidates() if candidate.valid
            ]
            if valid_candidates:
                candidate_by_name = {candidate.path.name: candidate for candidate in valid_candidates}
                selected_name = st.selectbox("Verified restore candidate", list(candidate_by_name))
                restore_approval = st.checkbox(
                    "I approve a safety backup followed by restoring this verified database archive.",
                    key="v17_restore_approval",
                )
                if st.button("Restore Selected Database Backup"):
                    if not restore_approval:
                        st.error("Explicit restore approval is required.")
                    else:
                        try:
                            result = management.request_restore(
                                candidate_by_name[selected_name].path, actor="owner"
                            )
                        except (OSError, ValueError):
                            st.error("Restore failed. The original database was preserved or rolled back.")
                        else:
                            st.success(
                                "Restore complete. Safety backup: "
                                f"{Path(result['safety_backup_path']).name}"
                            )
                            st.rerun()
        else:
            st.info("No registered database backup exists yet.")

        if st.button("Generate Database Management Report"):
            st.session_state.v17_database_report = management.operational_report(
                record=True, actor="owner"
            )
        if st.session_state.get("v17_database_report"):
            st.json(st.session_state.v17_database_report)

    st.divider()
    st.subheader("Core Status")
    st.write(f"Canonical store: {hub.store.database_path}")
    st.write(f"Records: {hub.store.count('records')}")
    st.write(f"Events: {hub.store.count('domain_events')}")
    st.write(f"Audit entries: {hub.store.count('audit_entries')}")
    st.write(f"Execution records: {len(hub.database.execution_records(500))}")



def render_finance(finance: FinanceSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    from calendar import monthrange
    from datetime import date

    page_header("Finance", "재무 금고", "장부, 예산, 저축과 월 결산을 한 공간에서 관리합니다.", finance.health().get("status", "READY"))
    st.caption("장부와 예산, 현금 흐름, 저축과 결산을 한곳에서 확인합니다.")
    month = st.text_input("Month", value=date.today().strftime("%Y-%m"), key="finance_month")
    try:
        summary = finance.summary_report(month)
    except ValueError as exc:
        st.error(str(exc))
        return

    flow = summary["cash_flow"]
    budget = summary["budget"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income", f"{flow['income']:,}")
    col2.metric("Expense", f"{flow['expense']:,}")
    col3.metric("Net Cash Flow", f"{flow['net_cash_flow']:,}")
    col4.metric("Budget Remaining", f"{budget['remaining']:,}")

    ledger_tab, budget_tab, savings_tab, report_tab = st.tabs(
        ["Ledger", "Budget", "Savings", "Report"]
    )
    with ledger_tab:
        with st.form("finance_ledger_form"):
            kind = st.selectbox("Transaction type", ["income", "expense"])
            amount = st.number_input("Amount", min_value=1, value=1, step=1000)
            category = st.text_input("Category")
            occurred_on = st.date_input("Date", value=date.today())
            description = st.text_input("Description")
            submitted = st.form_submit_button("Record transaction")
        if submitted:
            try:
                action = finance.record_income if kind == "income" else finance.record_expense
                action(amount, category, occurred_on, description)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Transaction recorded.")
                st.rerun()
        transactions = finance.list_transactions(
            start_on=f"{summary['month']}-01",
            end_on=date(int(summary["month"][:4]), int(summary["month"][5:]), monthrange(int(summary["month"][:4]), int(summary["month"][5:]))[1]),
        )
        official_records(transactions, title="장부 기록", empty="이 달의 장부 기록이 없습니다.")

    with budget_tab:
        with st.form("finance_budget_v10_form"):
            budget_category = st.text_input("Budget category")
            budget_amount = st.number_input(
                "Budget amount", min_value=0, value=0, step=1000
            )
            budget_submitted = st.form_submit_button("Create budget")
        if budget_submitted:
            try:
                finance.create_budget(month, budget_category, budget_amount)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Budget created.")
                st.rerun()
        official_records(finance.list_budgets(month), title="예산 계획", empty="이 달의 예산 계획이 없습니다.")

    with savings_tab:
        savings_kind = st.selectbox(
            "Savings type", ["installment", "deposit"], key="finance_savings_kind"
        )
        with st.form("finance_savings_form"):
            savings_name = st.text_input("Savings name")
            savings_amount = st.number_input(
                "Target or principal", min_value=1, value=1, step=1000
            )
            monthly_amount = st.number_input(
                "Monthly contribution", min_value=0, value=0, step=1000,
                disabled=savings_kind == "deposit",
            )
            interest_rate = st.number_input(
                "Annual interest rate (%)", min_value=0.0, max_value=100.0,
                value=0.0, step=0.1,
            )
            opened_on = st.date_input("Opened on", value=date.today())
            maturity_date = st.date_input(
                "Maturity date", value=date(date.today().year + 1, date.today().month, 1)
            )
            savings_submitted = st.form_submit_button("Create savings account")
        if savings_submitted:
            try:
                if savings_kind == "deposit":
                    finance.create_term_deposit(
                        savings_name, savings_amount, interest_rate,
                        opened_on, maturity_date,
                    )
                else:
                    finance.create_installment_savings(
                        savings_name, savings_amount, monthly_amount,
                        interest_rate, opened_on, maturity_date,
                    )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Savings account created.")
                st.rerun()
        official_records(finance.list_savings(), title="저축 포트폴리오", empty="등록된 저축 계좌가 없습니다.")

    with report_tab:
        official_insight("월 결산 요약", {"결산 내용": finance.render_financial_status(month)}, caption="장부와 예산을 바탕으로 정리한 월간 재무 흐름")
        if st.button("Close month", key="finance_monthly_close"):
            finance.monthly_close(month)
            st.success("Immutable monthly closing created.")
    snapshot = finance.export_snapshot()
    _render_record_browser(
        "finance",
        [item for key, value in snapshot.items() if isinstance(value, list) for item in value],
    )


def render_health(health: HealthSubsystem) -> None:
    import json
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    from datetime import date

    page_header("Health", "건강 생체 정원", "체중, 건강검진, 인바디와 목표 흐름을 살펴봅니다.", health.health().get("status", "READY"))
    st.caption("건강 기록은 사용자 본인만 관리하며 의료 진단을 대신하지 않습니다.")
    today = date.today()
    weight_tab, inbody_tab, lifestyle_tab, goal_tab = st.tabs(
        ["Weight", "InBody / Checkup", "Sleep / Exercise / Nutrition", "Goals / Report"]
    )
    with weight_tab:
        with st.form("health_weight_form"):
            measured_on = st.date_input(
                "Measured on", value=today, key="health_weight_date"
            )
            weight_kg = st.number_input(
                "Weight (kg)", min_value=20.0, max_value=500.0, value=70.0
            )
            note = st.text_input("Weight note")
            submitted = st.form_submit_button("Record weight")
        if submitted:
            try:
                health.record_weight(weight_kg, measured_on, note)
            except ValueError as exc:
                st.error(f"Weight record could not be saved: {exc}")
            else:
                st.success("Weight recorded.")
                st.rerun()
        weights = health.list_weights()
        official_records(weights, title="체중 기록", empty="기록된 체중이 없습니다.")
        official_insight("체중 변화", health.weight_baseline_comparison(), caption="기준 기록과 최근 체중의 변화")
        if weights:
            labels = {
                item["record_id"]: f"{item['measured_on']} · {item['weight_kg']} kg"
                for item in weights
            }
            selected_weight_id = st.selectbox(
                "Weight record to manage",
                list(labels),
                format_func=lambda value: labels[value],
                key="health_weight_manage",
            )
            selected_weight = next(
                item for item in weights if item["record_id"] == selected_weight_id
            )
            with st.form("health_weight_update_form"):
                corrected_date = st.date_input(
                    "Corrected date",
                    value=date.fromisoformat(selected_weight["measured_on"]),
                )
                corrected_weight = st.number_input(
                    "Corrected weight (kg)",
                    min_value=20.0,
                    max_value=500.0,
                    value=float(selected_weight["weight_kg"]),
                )
                corrected_note = st.text_input(
                    "Corrected note", value=str(selected_weight["note"])
                )
                update_weight = st.form_submit_button("Update weight record")
            if update_weight:
                try:
                    health.update_weight(
                        selected_weight_id,
                        measured_on=corrected_date,
                        weight_kg=corrected_weight,
                        note=corrected_note,
                    )
                except (KeyError, ValueError) as exc:
                    st.error(f"Weight record could not be updated: {exc}")
                else:
                    st.success("Weight record updated.")
                    st.rerun()
            with st.expander("Correction-only deletion"):
                st.caption(
                    "Health history is retained by default. Physical deletion is reserved "
                    "for an incorrectly entered weight record."
                )
                approve_delete = st.checkbox(
                    "I confirm this weight entry is incorrect.",
                    key="health_weight_delete_approval",
                )
                if st.button(
                    "Delete incorrect weight record",
                    disabled=not approve_delete,
                    key="health_weight_delete",
                ):
                    try:
                        health.delete_weight(selected_weight_id)
                    except (KeyError, ValueError) as exc:
                        st.error(f"Weight record could not be deleted: {exc}")
                    else:
                        st.success("Incorrect weight record deleted.")
                        st.rerun()

    with inbody_tab:
        with st.form("health_inbody_form"):
            inbody_on = st.date_input("InBody date", value=today)
            muscle = st.number_input(
                "Skeletal muscle (kg)", min_value=1.0, max_value=150.0, value=30.0
            )
            body_fat = st.number_input(
                "Body fat (%)", min_value=1.0, max_value=75.0, value=20.0
            )
            bmi = st.number_input("BMI", min_value=5.0, max_value=100.0, value=22.0)
            inbody_submit = st.form_submit_button("Record InBody")
        if inbody_submit:
            try:
                health.record_body_composition(inbody_on, muscle, body_fat, bmi)
            except ValueError as exc:
                st.error(f"InBody record could not be saved: {exc}")
            else:
                st.success("InBody recorded.")
                st.rerun()
        official_records(health.body_composition_timeline(), title="인바디 기록", empty="기록된 인바디 측정값이 없습니다.")
        official_insight("인바디 변화", health.body_composition_baseline_comparison(), caption="기준 측정과 최근 신체 구성의 변화")
        st.subheader("Health checkups")
        with st.form("health_checkup_form", clear_on_submit=True):
            checked_on = st.date_input("Checkup date", value=today)
            checkup_title = st.text_input("Checkup title")
            assessment = st.text_area("Assessment")
            has_follow_up = st.checkbox("Follow-up required")
            follow_up_on = st.date_input("Follow-up date", value=today)
            metrics_json = st.text_area(
                "Metrics (optional JSON object)",
                help='Example: {"fasting_glucose": 95, "blood_pressure": "120/80"}',
            )
            checkup_note = st.text_area("Checkup note")
            checkup_submit = st.form_submit_button("Record health checkup")
        if checkup_submit:
            try:
                metrics = json.loads(metrics_json) if metrics_json.strip() else {}
                if not isinstance(metrics, dict):
                    raise ValueError("Metrics must be a JSON object.")
                health.record_health_checkup(
                    checked_on,
                    checkup_title,
                    assessment,
                    follow_up_on if has_follow_up else None,
                    metrics,
                    checkup_note,
                )
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                st.error(f"Health checkup could not be recorded: {exc}")
            else:
                st.success("Health checkup recorded.")
                st.rerun()
        official_records(health.list_health_checkups(), title="건강검진 기록", empty="건강검진 기록이 없습니다.")
        st.write("Follow-up queue")
        official_records(health.health_checkup_follow_ups(), title="추적 확인", empty="추적 확인이 필요한 항목이 없습니다.")
        official_insight("검진 변화", health.health_checkup_baseline_comparison(), caption="기준 검진과 최근 검진의 변화")

    with lifestyle_tab:
        st.subheader("Sleep")
        with st.form("health_sleep_form"):
            bedtime = st.text_input(
                "Bedtime (ISO with timezone)",
                value=f"{today.isoformat()}T23:00:00+09:00",
            )
            wake_time = st.text_input(
                "Wake time (ISO with timezone)",
                value=f"{today.isoformat()}T23:30:00+09:00",
            )
            fatigue = st.slider("Fatigue", 1, 5, 3)
            sleep_submit = st.form_submit_button("Record sleep")
        if sleep_submit:
            try:
                health.record_sleep(bedtime, wake_time, fatigue)
            except ValueError as exc:
                st.error(f"Sleep record could not be saved: {exc}")
            else:
                st.success("Sleep record saved.")
                st.rerun()
        official_records(health.list_sleep(), title="수면 기록", empty="기록된 수면이 없습니다.")

        st.subheader("Exercise")
        with st.form("health_exercise_form", clear_on_submit=True):
            exercise_on = st.date_input("Exercise date", value=today)
            activity = st.text_input("Activity")
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=1440, value=30
            )
            repetitions = st.number_input(
                "Repetitions (optional)", min_value=0, value=0
            )
            exercise_note = st.text_input("Exercise note")
            exercise_submit = st.form_submit_button("Record exercise")
        if exercise_submit:
            try:
                health.record_exercise(
                    exercise_on,
                    activity,
                    duration,
                    repetitions if repetitions else None,
                    exercise_note,
                )
            except (KeyError, ValueError) as exc:
                st.error(f"Exercise could not be recorded: {exc}")
            else:
                st.success("Exercise recorded.")
                st.rerun()
        official_records(health.list_exercise(), title="운동 기록", empty="기록된 운동이 없습니다.")
        official_insight("운동 흐름", health.exercise_statistics(), caption="최근 운동 기록을 바탕으로 정리한 활동 신호")

        st.subheader("Nutrition")
        goals = health.list_health_goals()
        goal_labels = {
            item["goal_id"]: item["name"] for item in goals if item["status"] == "active"
        }
        with st.form("health_nutrition_form", clear_on_submit=True):
            nutrition_on = st.date_input("Meal date", value=today)
            meal_type = st.selectbox(
                "Health meal type",
                ["breakfast", "lunch", "dinner", "snack", "other"],
            )
            nutrition_note = st.text_area("Nutrition note")
            goal_options = [""] + list(goal_labels)
            nutrition_goal = st.selectbox(
                "Related Health goal (optional)",
                goal_options,
                format_func=lambda value: "No related goal"
                if not value
                else goal_labels[value],
            )
            nutrition_submit = st.form_submit_button("Record nutrition")
        if nutrition_submit:
            try:
                health.record_nutrition(
                    nutrition_on,
                    meal_type,
                    nutrition_note,
                    nutrition_goal or None,
                )
            except (KeyError, ValueError) as exc:
                st.error(f"Nutrition could not be recorded: {exc}")
            else:
                st.success("Nutrition recorded.")
                st.rerun()
        official_records(health.list_nutrition(), title="영양 기록", empty="기록된 식사와 영양 정보가 없습니다.")
        trend_columns = st.columns(2)
        with trend_columns[0]:
            official_insight(
                "신체 변화", {"체중": health.weight_trend(), "인바디": health.inbody_trend()},
                caption="체중과 신체 구성 기록을 연결한 변화 흐름",
            )
        with trend_columns[1]:
            official_insight(
                "생활 리듬", {"수면": health.sleep_trend(), "운동": health.exercise_trend()},
                caption="수면과 운동 기록을 연결한 생활 흐름",
            )

    with goal_tab:
        with st.form("health_goal_form"):
            goal_name = st.text_input("Goal name")
            target_weight = st.number_input(
                "Target weight (kg)", min_value=20.0, max_value=500.0, value=70.0
            )
            target_fat = st.number_input(
                "Target body fat (%)", min_value=1.0, max_value=75.0, value=20.0
            )
            goal_submit = st.form_submit_button("Create Health goal")
        if goal_submit:
            try:
                health.create_health_goal(goal_name, today, target_weight, target_fat)
            except ValueError as exc:
                st.error(f"Health goal could not be created: {exc}")
            else:
                st.success("Health goal created.")
                st.rerun()
        goals = health.list_health_goals()
        official_records(goals, title="건강 목표", empty="등록된 건강 목표가 없습니다.")
        for goal in goals:
            with st.expander(f"Goal progress · {goal['name']}"):
                try:
                    official_insight("목표 진행률", health.health_goal_progress(goal["goal_id"]), caption="현재 목표를 향한 진행 흐름")
                except (KeyError, ValueError) as exc:
                    st.error(f"Goal progress is unavailable: {exc}")
        st.subheader("Health reports")
        report_kind = st.selectbox(
            "Report range",
            ["daily", "weekly", "monthly"],
            key="health_report_kind",
        )
        report_date = st.date_input(
            "Report date / week ending",
            value=today,
            key="health_report_date",
        )
        report_month = st.text_input(
            "Report month",
            value=today.strftime("%Y-%m"),
            key="health_report_month",
            disabled=report_kind != "monthly",
        )
        try:
            if report_kind == "daily":
                report = health.daily_report(report_date)
            elif report_kind == "weekly":
                report = health.weekly_report(report_date)
            else:
                report = health.monthly_report(report_month)
            official_insight("건강 리포트", report, caption="선택한 기간의 건강 기록 요약")
        except (KeyError, ValueError) as exc:
            st.error(f"Health report could not be generated: {exc}")


    snapshot = health.export_snapshot()
    _render_record_browser(
        "health",
        [item for key, value in snapshot.items() if isinstance(value, list) for item in value],
    )


def render_housing(housing: HousingSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Housing", "생활 주거 공간", "계약, 월세와 관리비의 생활 흐름을 관리합니다.", housing.health().get("status", "READY"))
    st.caption("주거 후보를 비교하고 계약과 월별 비용을 함께 관리합니다.")
    candidate_tab, comparison_tab = st.tabs(["Candidates", "Comparison / Report"])

    with candidate_tab:
        with st.form("housing_candidate_v14_form", clear_on_submit=True):
            name = st.text_input("Candidate name")
            cost_col1, cost_col2, cost_col3 = st.columns(3)
            deposit = cost_col1.number_input("Deposit", min_value=0, step=1_000_000, format="%d")
            monthly_rent = cost_col2.number_input("Monthly rent", min_value=0, step=10_000, format="%d")
            maintenance_fee = cost_col3.number_input("Maintenance fee", min_value=0, step=10_000, format="%d")
            maintenance_fee_provided = st.checkbox("Maintenance fee is known", value=True)
            condition_col1, condition_col2 = st.columns(2)
            commute_minutes = condition_col1.number_input("Commute minutes", min_value=0, max_value=1440, step=5)
            parking_available = condition_col2.checkbox("Parking available")
            options_memo = st.text_area("Options memo")
            special_notes = st.text_area("Special notes")
            submitted = st.form_submit_button("Add candidate", type="primary")
        if submitted:
            try:
                housing.create_candidate(
                    name=name,
                    deposit=deposit,
                    monthly_rent=monthly_rent,
                    maintenance_fee=maintenance_fee,
                    maintenance_fee_provided=maintenance_fee_provided,
                    commute_minutes=commute_minutes,
                    parking_available=parking_available,
                    options_memo=options_memo,
                    special_notes=special_notes,
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Housing candidate added.")
                st.rerun()

        candidates = housing.list_candidates()
        official_records(candidates, title="주거 후보", empty="비교할 주거 후보가 없습니다.")
        if candidates:
            labels = {item["candidate_id"]: item["name"] for item in candidates}
            selected_id = st.selectbox(
                "Candidate to manage",
                list(labels),
                format_func=lambda value: labels[value],
            )
            status = st.selectbox("Status", ["active", "shortlisted", "rejected", "selected"])
            action_col1, action_col2 = st.columns(2)
            if action_col1.button("Update status", key="housing_update_status"):
                housing.update_candidate(selected_id, status=status)
                st.success("Candidate status updated.")
                st.rerun()
            confirm_delete = st.checkbox(
                "I understand this permanently deletes the selected candidate.",
                key="housing_confirm_delete",
            )
            if action_col2.button(
                "Delete candidate",
                key="housing_delete_candidate",
                disabled=not confirm_delete,
            ):
                try:
                    housing.delete_candidate(selected_id)
                except (KeyError, ValueError) as exc:
                    st.error(f"Candidate could not be deleted: {exc}")
                else:
                    st.success("Candidate deleted.")
                    st.rerun()

    with comparison_tab:
        official_records(housing.rank_candidates(), title="주거 비교", empty="비교할 주거 후보가 없습니다.")
        official_insight("주거 요약", housing.housing_report(), caption="후보와 계약을 바탕으로 정리한 주거 흐름")

    with st.expander("Rental contract and monthly charges"):
        with st.form("housing_contract_v207_form", clear_on_submit=True):
            contract_name = st.text_input("Contract name")
            contract_address = st.text_input("Contract address")
            start_on = st.date_input("Contract start", value=date.today())
            end_on = st.date_input("Contract end", value=date.today())
            contract_deposit = st.number_input("Contract deposit", min_value=0, step=1000000)
            contract_rent = st.number_input("Monthly rent", min_value=0, step=10000)
            contract_fee = st.number_input("Monthly maintenance", min_value=0, step=10000)
            contract_submit = st.form_submit_button("Create rental contract")
        if contract_submit:
            try:
                housing.create_contract(
                    contract_name, contract_address, start_on, end_on,
                    contract_deposit, contract_rent, contract_fee,
                )
            except (KeyError, ValueError) as exc:
                st.error(str(exc))
            else:
                st.success("Rental contract created.")
                st.rerun()
        contracts = housing.list_contracts()
        official_records(contracts, title="주거 계약", empty="등록된 주거 계약이 없습니다.")
        if contracts:
            labels = {item["contract_id"]: item["name"] for item in contracts}
            with st.form("housing_charge_v207_form", clear_on_submit=True):
                charge_contract = st.selectbox(
                    "Charge contract", list(labels), format_func=lambda value: labels[value]
                )
                charged_on = st.date_input("Charged on", value=date.today())
                charge_kind = st.selectbox(
                    "Charge type", ["rent", "maintenance", "utility", "other"]
                )
                charge_amount = st.number_input("Charge amount", min_value=0, step=10000)
                charge_submit = st.form_submit_button("Record housing charge")
            if charge_submit:
                try:
                    housing.record_charge(
                        charge_contract, charged_on, charge_kind, charge_amount
                    )
                except (KeyError, ValueError) as exc:
                    st.error(str(exc))
                else:
                    st.success("Housing charge recorded.")
                    st.rerun()
            official_insight("입주 비용", housing.occupancy_report(charge_contract), caption="선택한 계약의 월별 생활 비용")

    snapshot = housing.export_snapshot()
    _render_record_browser(
        "housing",
        [item for key, value in snapshot.items() if isinstance(value, list) for item in value],
    )


def render_vehicle(vehicle: VehicleSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Vehicle", "모빌리티 베이", "운행, 주유와 정비 기록을 안전하게 이어갑니다.", vehicle.health().get("status", "READY"))
    st.caption("차량별 운행, 주유와 정비 이력을 안전하게 기록합니다.")
    vehicles_tab, records_tab, report_tab = st.tabs(["Vehicles", "Records", "Status report"])

    with vehicles_tab:
        with st.form("vehicle_v15_profile_form", clear_on_submit=True):
            display_name = st.text_input("Vehicle name")
            manufacturer = st.text_input("Manufacturer")
            model = st.text_input("Model")
            model_year = st.number_input(
                "Model year", min_value=1886, max_value=date.today().year + 1,
                value=date.today().year, step=1,
            )
            powertrain = st.selectbox(
                "Powertrain", ["gasoline", "diesel", "hybrid", "electric", "other"]
            )
            create_submitted = st.form_submit_button("Add vehicle", type="primary")
        if create_submitted:
            try:
                vehicle.create_vehicle(display_name, manufacturer, model, model_year, powertrain)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Vehicle added.")
                st.rerun()

        vehicles = vehicle.list_vehicles("active")
        official_records(vehicles, title="내 차량", empty="등록된 차량이 없습니다.")
        if vehicles:
            labels = {item["vehicle_id"]: item["display_name"] for item in vehicles}
            archive_id = st.selectbox(
                "Vehicle to archive", list(labels), format_func=lambda value: labels[value],
                key="vehicle_archive_select",
            )
            if st.button("Archive vehicle", key="vehicle_archive_button"):
                vehicle.archive_vehicle(archive_id)
                st.success("Vehicle archived.")
                st.rerun()
        archived_vehicles = vehicle.list_vehicles("archived")
        if archived_vehicles:
            with st.expander("Archived vehicles"):
                archived_labels = {
                    item["vehicle_id"]: item["display_name"]
                    for item in archived_vehicles
                }
                restore_vehicle_id = st.selectbox(
                    "Vehicle to restore",
                    list(archived_labels),
                    format_func=lambda value: archived_labels[value],
                    key="vehicle_restore_select",
                )
                if st.button("Restore vehicle", key="vehicle_restore_button"):
                    try:
                        vehicle.restore_vehicle(restore_vehicle_id)
                    except (KeyError, ValueError) as exc:
                        st.error(f"Vehicle could not be restored: {exc}")
                    else:
                        st.success("Vehicle restored.")
                        st.rerun()

    with records_tab:
        vehicles = vehicle.list_vehicles("active")
        if not vehicles:
            st.info("Add an active vehicle before recording Vehicle data.")
        else:
            labels = {item["vehicle_id"]: item["display_name"] for item in vehicles}
            vehicle_id = st.selectbox(
                "Vehicle", list(labels), format_func=lambda value: labels[value],
                key="vehicle_records_select",
            )
            odometer_tab, maintenance_tab, schedule_tab, energy_tab = st.tabs(
                ["Odometer", "Maintenance", "Schedule", "Fuel / Charge"]
            )
            with odometer_tab:
                with st.form("vehicle_v15_odometer_form", clear_on_submit=True):
                    odometer_km = st.number_input("Odometer (km)", min_value=0, step=1)
                    recorded_on = st.date_input("Recorded on", value=date.today(), key="vehicle_odometer_date")
                    odometer_note = st.text_input("Note", key="vehicle_odometer_note")
                    odometer_submit = st.form_submit_button("Record odometer")
                if odometer_submit:
                    try:
                        vehicle.record_odometer(vehicle_id, odometer_km, recorded_on.isoformat(), odometer_note)
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.rerun()
                official_records(vehicle.list_odometer_readings(vehicle_id), title="주행거리 기록", empty="주행거리 기록이 없습니다.")

            with maintenance_tab:
                with st.form("vehicle_v15_maintenance_form", clear_on_submit=True):
                    service_type = st.text_input("Service type")
                    serviced_on = st.date_input("Serviced on", value=date.today(), key="vehicle_service_date")
                    service_km = st.number_input("Service odometer (km)", min_value=0, step=1)
                    service_cost = st.number_input("Service cost", min_value=0, step=1000)
                    provider = st.text_input("Provider")
                    service_note = st.text_area("Service note")
                    maintenance_submit = st.form_submit_button("Record maintenance")
                if maintenance_submit:
                    try:
                        vehicle.record_maintenance(
                            vehicle_id, service_type, serviced_on.isoformat(), service_km,
                            service_cost, provider, service_note,
                        )
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.rerun()
                official_records(vehicle.list_maintenance_records(vehicle_id), title="정비 기록", empty="정비 기록이 없습니다.")

            with schedule_tab:
                with st.form("vehicle_v15_schedule_form", clear_on_submit=True):
                    schedule_type = st.text_input("Scheduled service")
                    use_due_date = st.checkbox("Use due date", value=True)
                    due_on = st.date_input("Due on", value=date.today(), key="vehicle_due_date")
                    use_due_km = st.checkbox("Use due odometer")
                    due_km = st.number_input("Due odometer (km)", min_value=0, step=1)
                    schedule_submit = st.form_submit_button("Create schedule")
                if schedule_submit:
                    try:
                        vehicle.create_maintenance_schedule(
                            vehicle_id, schedule_type,
                            due_on.isoformat() if use_due_date else None,
                            due_km if use_due_km else None,
                        )
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.rerun()
                schedules = vehicle.list_maintenance_schedules(vehicle_id)
                official_records(schedules, title="정비 일정", empty="예정된 정비가 없습니다.")
                active = [item for item in schedules if item["status"] == "active"]
                maintenance = vehicle.list_maintenance_records(vehicle_id)
                if active and maintenance:
                    schedule_id = st.selectbox(
                        "Schedule to complete", [item["schedule_id"] for item in active],
                        format_func=lambda value: next(item["service_type"] for item in active if item["schedule_id"] == value),
                    )
                    maintenance_id = st.selectbox(
                        "Completion record", [item["maintenance_id"] for item in maintenance],
                        format_func=lambda value: next(item["service_type"] for item in maintenance if item["maintenance_id"] == value),
                    )
                    if st.button("Complete schedule", key="vehicle_complete_schedule"):
                        try:
                            vehicle.complete_maintenance_schedule(schedule_id, maintenance_id)
                        except ValueError as exc:
                            st.error(str(exc))
                        else:
                            st.rerun()

            with energy_tab:
                with st.form("vehicle_v15_energy_form", clear_on_submit=True):
                    energy_type = st.selectbox("Energy type", ["fuel", "charge"])
                    energy_on = st.date_input("Energy date", value=date.today(), key="vehicle_energy_date")
                    quantity = st.number_input("Quantity (L or kWh)", min_value=0.001, step=0.001, format="%.3f")
                    energy_cost = st.number_input("Energy cost", min_value=0, step=1000)
                    energy_km = st.number_input("Energy odometer (km)", min_value=0, step=1)
                    energy_note = st.text_input("Energy note")
                    energy_submit = st.form_submit_button("Record fuel / charge")
                if energy_submit:
                    try:
                        vehicle.record_energy(
                            vehicle_id, energy_type, energy_on.isoformat(), quantity,
                            energy_cost, energy_km, energy_note,
                        )
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.rerun()
                official_records(vehicle.list_energy_logs(vehicle_id), title="주유·충전 기록", empty="주유 또는 충전 기록이 없습니다.")

    with report_tab:
        vehicles = vehicle.list_vehicles("active")
        if not vehicles:
            st.info("Add an active vehicle before generating a status report.")
        else:
            labels = {item["vehicle_id"]: item["display_name"] for item in vehicles}
            report_id = st.selectbox(
                "Report vehicle", list(labels), format_func=lambda value: labels[value],
                key="vehicle_report_select",
            )
            official_insight("차량 상태 리포트", vehicle.vehicle_report(report_id), caption="주행과 정비 기록을 바탕으로 정리한 차량 상태")


    with st.expander("Trip log"):
        active = vehicle.list_vehicles("active")
        if not active:
            st.caption("Add an active vehicle first.")
        else:
            labels = {item["vehicle_id"]: item["display_name"] for item in active}
            with st.form("vehicle_trip_v207_form", clear_on_submit=True):
                trip_vehicle = st.selectbox(
                    "Trip vehicle", list(labels), format_func=lambda value: labels[value]
                )
                driven_on = st.date_input("Driven on", value=date.today())
                start_km = st.number_input("Start odometer", min_value=0, step=1)
                end_km = st.number_input("End odometer", min_value=0, step=1)
                purpose = st.text_input("Trip purpose")
                trip_submit = st.form_submit_button("Record trip")
            if trip_submit:
                try:
                    vehicle.record_trip(
                        trip_vehicle, driven_on, start_km, end_km, purpose
                    )
                except (KeyError, ValueError) as exc:
                    st.error(str(exc))
                else:
                    st.success("Trip recorded.")
                    st.rerun()
            official_records(vehicle.list_trips(trip_vehicle), title="운행 기록", empty="운행 기록이 없습니다.")
            official_insight("운행 요약", vehicle.dashboard(trip_vehicle), caption="선택한 차량의 주행과 유지 흐름")

    snapshot = vehicle.export_snapshot()
    _render_record_browser(
        "vehicle",
        [item for key, value in snapshot.items() if isinstance(value, list) for item in value],
    )


def render_food(food: FoodSubsystem) -> None:
    from subsystems.experience.engines.localization import localized_streamlit
    st = localized_streamlit()
    page_header("Food", "식생활 아틀리에", "재료, 레시피와 식사 기록을 하나로 연결합니다.", food.health().get("status", "READY"))
    st.caption("내가 입력한 재료, 레시피와 식사 기록을 바탕으로 정리합니다.")
    ingredients_tab, recipes_tab, records_tab, report_tab = st.tabs(
        ["Ingredients", "Recipes", "Cooking and meals", "Food report"]
    )

    with ingredients_tab:
        with st.form("food_v16_ingredient_form", clear_on_submit=True):
            name = st.text_input("Ingredient name")
            category = st.text_input("Category")
            base_quantity = st.number_input("Base quantity", min_value=0.001, step=0.001, format="%.3f")
            unit = st.selectbox("Base unit", ["g", "kg", "ml", "l", "item", "serving"])
            calories = st.number_input("Calories", min_value=0.0, step=0.1)
            protein = st.number_input("Protein", min_value=0.0, step=0.1)
            carbohydrate = st.number_input("Carbohydrate", min_value=0.0, step=0.1)
            fat = st.number_input("Fat", min_value=0.0, step=0.1)
            ingredient_submit = st.form_submit_button("Add ingredient", type="primary")
        if ingredient_submit:
            try:
                food.create_ingredient(
                    name, category, base_quantity, unit,
                    {"calories": calories, "protein": protein,
                     "carbohydrate": carbohydrate, "fat": fat},
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Ingredient added.")
                st.rerun()
        ingredients = food.list_ingredients("active")
        official_records(ingredients, title="식재료 보관함", empty="등록된 식재료가 없습니다.")
        if ingredients:
            ingredient_labels = {row["ingredient_id"]: row["name"] for row in ingredients}
            archive_id = st.selectbox(
                "Ingredient to archive", list(ingredient_labels),
                format_func=lambda value: ingredient_labels[value], key="food_ingredient_archive_select",
            )
            if st.button("Archive ingredient", key="food_ingredient_archive_button"):
                food.archive_ingredient(archive_id)
                st.success("Ingredient archived.")
                st.rerun()
        archived_ingredients = food.list_ingredients("archived")
        if archived_ingredients:
            with st.expander("Archived ingredients"):
                archived_ingredient_labels = {
                    row["ingredient_id"]: row["name"] for row in archived_ingredients
                }
                restore_ingredient_id = st.selectbox(
                    "Ingredient to restore",
                    list(archived_ingredient_labels),
                    format_func=lambda value: archived_ingredient_labels[value],
                    key="food_ingredient_restore_select",
                )
                if st.button(
                    "Restore ingredient", key="food_ingredient_restore_button"
                ):
                    try:
                        food.restore_ingredient(restore_ingredient_id)
                    except (KeyError, ValueError) as exc:
                        st.error(f"Ingredient could not be restored: {exc}")
                    else:
                        st.success("Ingredient restored.")
                        st.rerun()

    with recipes_tab:
        with st.form("food_v16_recipe_form", clear_on_submit=True):
            recipe_name = st.text_input("Recipe name")
            servings = st.number_input("Recipe servings", min_value=1, step=1)
            instructions = st.text_area("Instructions", help="Enter one step per line.")
            recipe_submit = st.form_submit_button("Add recipe", type="primary")
        if recipe_submit:
            try:
                food.create_recipe(
                    recipe_name, servings,
                    [line.strip() for line in instructions.splitlines() if line.strip()],
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Recipe added.")
                st.rerun()
        recipes = food.list_recipes("active")
        official_records(recipes, title="레시피 컬렉션", empty="등록된 레시피가 없습니다.")
        ingredients = food.list_ingredients("active")
        if recipes and ingredients:
            recipe_labels = {row["recipe_id"]: row["name"] for row in recipes}
            ingredient_labels = {row["ingredient_id"]: row["name"] for row in ingredients}
            with st.form("food_v16_recipe_ingredient_form", clear_on_submit=True):
                selected_recipe = st.selectbox(
                    "Recipe", list(recipe_labels), format_func=lambda value: recipe_labels[value]
                )
                selected_ingredient = st.selectbox(
                    "Ingredient", list(ingredient_labels),
                    format_func=lambda value: ingredient_labels[value],
                )
                line_quantity = st.number_input(
                    "Ingredient quantity", min_value=0.001, step=0.001, format="%.3f"
                )
                line_unit = st.selectbox("Ingredient unit", ["g", "kg", "ml", "l", "item", "serving"])
                line_submit = st.form_submit_button("Set as recipe ingredient")
            if line_submit:
                try:
                    food.set_recipe_ingredients(selected_recipe, [{
                        "ingredient_id": selected_ingredient,
                        "quantity": line_quantity,
                        "unit": line_unit,
                    }])
                except (KeyError, ValueError) as exc:
                    st.error(str(exc))
                else:
                    st.rerun()
        archived_recipes = food.list_recipes("archived")
        if archived_recipes:
            with st.expander("Archived recipes"):
                archived_recipe_labels = {
                    row["recipe_id"]: row["name"] for row in archived_recipes
                }
                restore_recipe_id = st.selectbox(
                    "Recipe to restore",
                    list(archived_recipe_labels),
                    format_func=lambda value: archived_recipe_labels[value],
                    key="food_recipe_restore_select",
                )
                if st.button("Restore recipe", key="food_recipe_restore_button"):
                    try:
                        food.restore_recipe(restore_recipe_id)
                    except (KeyError, ValueError) as exc:
                        st.error(f"Recipe could not be restored: {exc}")
                    else:
                        st.success("Recipe restored.")
                        st.rerun()

    with records_tab:
        recipes = food.list_recipes("active")
        if not recipes:
            st.info("Add an active recipe before recording cooking linked to a recipe.")
        else:
            recipe_labels = {row["recipe_id"]: row["name"] for row in recipes}
            with st.form("food_v16_cooking_form", clear_on_submit=True):
                cooking_recipe = st.selectbox(
                    "Cooked recipe", list(recipe_labels),
                    format_func=lambda value: recipe_labels[value],
                )
                cooked_on = st.date_input("Cooked on", value=date.today())
                produced = st.number_input("Servings produced", min_value=1, step=1)
                cooking_note = st.text_input("Cooking note")
                cooking_submit = st.form_submit_button("Record cooking")
            if cooking_submit:
                try:
                    food.record_cooking(cooking_recipe, cooked_on.isoformat(), produced, cooking_note)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.rerun()
        with st.form("food_v16_meal_form", clear_on_submit=True):
            eaten_on = st.date_input("Eaten on", value=date.today())
            meal_type = st.selectbox("Meal type", ["breakfast", "lunch", "dinner", "snack", "other"])
            meal_recipe_options = [""] + [row["recipe_id"] for row in recipes]
            meal_recipe = st.selectbox(
                "Meal recipe (optional)", meal_recipe_options,
                format_func=lambda value: "No linked recipe" if not value else recipe_labels[value],
            )
            consumed = st.number_input("Servings consumed", min_value=0.001, step=0.001, format="%.3f")
            meal_note = st.text_input("Meal note")
            meal_submit = st.form_submit_button("Record meal")
        if meal_submit:
            try:
                food.record_meal(
                    eaten_on.isoformat(), meal_type, consumed,
                    recipe_id=meal_recipe or None, note=meal_note,
                )
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.rerun()
        official_records(food.list_cooking_records(), title="조리 기록", empty="조리 기록이 없습니다.")
        official_records(food.list_meals(), title="식사 기록", empty="식사 기록이 없습니다.")

    with report_tab:
        st.info("Nutrition totals use owner-entered values only and are not medical guidance.")
        official_insight("식생활 리포트", food.food_report(), caption="재료, 레시피와 식사 기록을 바탕으로 정리한 영양 흐름")

    snapshot = food.export_snapshot()
    _render_record_browser(
        "food",
        [item for key, value in snapshot.items() if isinstance(value, list) for item in value],
    )


# v2.0.7 common Food record browser is rendered after the domain report.
