from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import tempfile
from typing import Any

from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem

from subsystems.foundation.engines.errors import CoreError
from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.module_runtime import LIFECYCLE_TRANSITIONS
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
from subsystems.insight.engines.projections import analytics_projection, dashboard_projection, review_projection
from subsystems.operations.engines.reports import ReportsService


def _tags(raw: str) -> list[str]:
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def render_dashboard(hub: LivingHub) -> None:
    import streamlit as st

    data = dashboard_projection(hub)
    st.title("Living OS")
    st.caption("v1.2 · Subsystem Architecture · compatible canonical state")
    st.success("System Status: NORMAL")
    cols = st.columns(5)
    cols[0].metric("Journal", data["journal_count"])
    cols[1].metric("Decisions", data["decision_count"])
    cols[2].metric("Needs Review", data["review_count"])
    cols[3].metric("Knowledge", data["knowledge_count"])
    cols[4].metric("Reports", data["report_count"])
    left, right = st.columns(2)
    with left:
        st.subheader("Recent Journal")
        for item in data["recent_journals"]:
            st.markdown(f"**{item.get('date', '-')} — {item.get('title', 'Untitled')}**")
        if not data["recent_journals"]:
            st.info("No journal entries yet.")
    with right:
        st.subheader("Recent Decisions")
        for item in data["recent_decisions"]:
            st.markdown(f"**{item.get('decision', 'Untitled')}**")
            st.caption(f"Status: {item.get('status', 'draft')}")
        if not data["recent_decisions"]:
            st.info("No decisions yet.")


def render_journal(hub: LivingHub) -> None:
    import streamlit as st

    service = JournalService(hub)
    st.title("Journal")
    st.caption("Daily operating records saved through explicit audited commands.")
    with st.form("v2_journal_form", clear_on_submit=True):
        entry_date = st.date_input("Date").isoformat()
        title = st.text_input("Title")
        mood = st.text_input("Status", placeholder="NORMAL / FOCUSED / TIRED")
        tags = st.text_input("Tags", placeholder="work, learning, health")
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
    import streamlit as st

    service = DecisionService(hub)
    st.title("Decision")
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
    import streamlit as st

    service = KnowledgeService(hub)
    st.title("Knowledge")
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


def render_reports(hub: LivingHub) -> None:
    import streamlit as st

    service = ReportsService(hub)
    st.title("Reports")
    report_type = st.selectbox("Report Type", ["daily", "weekly", "monthly"])
    preview = service.build(report_type)
    edited = st.text_area("Deterministic Report", value=preview, height=400)
    if st.button("Save Report"):
        try:
            record = service.save(report_type, edited)
        except (CoreError, OSError, ValueError):
            st.error("The report could not be saved.")
        else:
            st.success(f"Saved {record['id']}")
    st.divider()
    st.subheader("Optional AI Report Draft")
    st.caption("Draft-only. AI cannot write canonical data; saving requires a separate explicit command.")
    _ensure_ai_model(st)
    source = preview
    st.code(source, language="text")
    if st.button("Generate AI Report Draft"):
        api_key, _ = resolve_api_key(str(st.session_state.get("ai_session_api_key", "")))
        if not api_key:
            st.error("Configure an OpenAI API key in Settings first.")
        else:
            try:
                briefing = AIBriefingService(hub, OpenAITextProvider(api_key))
                st.session_state.v2_ai_report_draft = briefing.analyze("report", st.session_state.ai_model, source)
            except AIServiceError as exc:
                st.error(str(exc))
    draft = str(st.session_state.get("v2_ai_report_draft", ""))
    if draft:
        edited_draft = st.text_area("Unsaved AI Draft", value=draft, height=350)
        if st.button("Save AI Draft (Explicit Approval)"):
            try:
                service.save(report_type, edited_draft, generated_by="ai-approved-draft")
            except (CoreError, OSError, ValueError):
                st.error("The AI draft could not be saved.")
            else:
                st.success("AI draft saved as a canonical report artifact.")
    st.divider()
    for item in service.list()[:20]:
        st.write(f"{item.get('report_type', 'report')} · {item.get('id')} · {item.get('generated_by')}")


def _render_counter(title: str, counter: Counter[str]) -> None:
    import streamlit as st

    st.subheader(title)
    if counter:
        st.dataframe([{"Name": key, "Count": value} for key, value in counter.most_common()], hide_index=True, width="stretch")
    else:
        st.info("No data yet.")


def render_analytics(hub: LivingHub) -> None:
    import streamlit as st

    data = analytics_projection(hub)
    st.title("Analytics")
    st.caption("Read-only projections; never an alternate source of truth.")
    cols = st.columns(4)
    for column, (name, value) in zip(cols, data["counts"].items()):
        column.metric(name.title(), value)
    left, right = st.columns(2)
    with left:
        _render_counter("Journal Tags", data["journal_tags"])
        _render_counter("Decision Status", data["decision_statuses"])
    with right:
        _render_counter("Knowledge Tags", data["knowledge_tags"])


def render_review(hub: LivingHub) -> None:
    import streamlit as st

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
    import streamlit as st

    if not records:
        st.info("No canonical records are available.")
        return
    identifiers = [str(item.get("id", "")) for item in records]
    selected_id = st.selectbox("Select record", identifiers, key=f"select_{state_key}")
    record = next(item for item in records if str(item.get("id", "")) == selected_id)
    source = record_source(record, fields)
    st.warning("Only the visible selected fields will be sent after explicit approval.")
    st.code(source, language="text")
    if st.button("Request Read-only Analysis", key=f"request_{state_key}"):
        api_key, _ = resolve_api_key(str(st.session_state.get("ai_session_api_key", "")))
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
    import streamlit as st

    st.title("AI Briefing")
    st.caption("Source-attributed, explicit, read-only AI analysis.")
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
    import streamlit as st

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
    import streamlit as st

    st.title("Module Manager")
    st.caption("Validated lifecycle and health; no future roadmap modules are installed.")
    for module in hub.modules.list_modules():
        module_id = str(module["module_id"])
        with st.expander(f"{module.get('name', module_id)} · {module.get('status')} · {module.get('health')}"):
            st.write(module.get("description", ""))
            st.caption(f"Version {module.get('version')} · Core {module.get('core_compatibility')}")
            current = str(module.get("status"))
            targets = sorted(LIFECYCLE_TRANSITIONS.get(current, set()))
            if module_id in {"module_manager", "settings"}:
                st.info("Core administration modules cannot be disabled from their own control surface.")
            elif targets:
                target = st.selectbox("Lifecycle action", targets, key=f"lifecycle_{module_id}")
                if st.button("Apply Lifecycle Change", key=f"apply_lifecycle_{module_id}"):
                    try:
                        hub.modules.transition(module_id, target)
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.success(f"{module_id}: {current} → {target}")
                        st.rerun()


def render_settings(hub: LivingHub) -> None:
    import streamlit as st

    st.title("Settings / Hub Administration")
    st.caption("Explicit migration, backup, credentials, and storage status.")
    st.subheader("Application Preferences")
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
        with st.form("v1_compatibility_preferences"):
            app_name = st.text_input("App Name", value=str(legacy_settings.get("app_name", "Living OS")))
            ranges = ["daily", "weekly", "monthly"]
            current_range = str(legacy_settings.get("default_report_range", "daily"))
            report_range = st.selectbox(
                "Default Report Range",
                ranges,
                index=ranges.index(current_range) if current_range in ranges else 0,
            )
            save_preferences = st.form_submit_button("Save v1 Compatibility Preferences")
        if save_preferences:
            try:
                save_settings({"app_name": app_name, "default_report_range": report_range})
            except (OSError, ValueError):
                st.error("Compatibility preferences could not be saved.")
            else:
                st.success("Compatibility preferences saved without changing the v1 schema.")
    st.divider()
    st.subheader("OpenAI Configuration")
    session_key = st.text_input(
        "OpenAI API Key",
        value=str(st.session_state.get("ai_session_api_key", "")),
        type="password",
        placeholder="Session-only; never stored in canonical records",
    )
    st.session_state.ai_session_api_key = session_key.strip()
    _ensure_ai_model(st)
    st.divider()
    st.subheader("Owner Security and Paired Devices")
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
    st.subheader("Living OS v1 Compatibility Migration")
    if hub.v1_migration_complete:
        st.success("v1 compatibility migration is complete. The v1.2 Hub store is canonical.")
    else:
        st.warning("The application is operating in v1 compatibility mode. Migration requires review and explicit approval.")
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
    st.subheader("Hub Backup")
    if st.button("Create Verified v1.2 Backup"):
        try:
            path = hub.backups.create(hub.migration.legacy_paths)
            verified = hub.backups.verify(path)
        except (OSError, ValueError):
            st.error("The Hub backup could not be created.")
        else:
            if verified:
                st.success(f"Backup created and verified: {path.name}")
            else:
                st.error("Backup was created but verification failed. Do not use it for restore.")
    restore_file = st.file_uploader("Select a Living OS v1.2 backup", type=["zip"], key="v2_restore_file")
    restore_approval = st.checkbox("I approve a safety backup followed by restoring this verified archive.")
    if st.button("Restore Verified v1.2 Backup"):
        if restore_file is None or not restore_approval:
            st.error("Choose a backup and provide explicit restore approval.")
        else:
            try:
                with tempfile.TemporaryDirectory() as directory:
                    uploaded_path = Path(directory) / "uploaded_backup.zip"
                    uploaded_path.write_bytes(restore_file.getvalue())
                    safety = hub.backups.restore(uploaded_path)
            except (OSError, ValueError):
                st.error("Restore was rejected or failed. Existing data was preserved or rolled back.")
            else:
                st.success(f"Restore complete. Pre-restore safety backup: {safety.name}")
                st.rerun()
    st.divider()
    st.subheader("Core Status")
    st.write(f"Canonical store: {hub.store.database_path}")
    st.write(f"Records: {hub.store.count('records')}")
    st.write(f"Events: {hub.store.count('domain_events')}")
    st.write(f"Audit entries: {hub.store.count('audit_entries')}")



def render_finance(finance: FinanceSubsystem) -> None:
    import streamlit as st
    from calendar import monthrange
    from datetime import date

    st.title("Finance")
    st.caption("Finance Subsystem v1.0 · Ledger, Budget, Cash Flow, Savings, Reports")
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
        st.dataframe(transactions, width="stretch")

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
        st.dataframe(finance.list_budgets(month), width="stretch")

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
        st.dataframe(finance.list_savings(), width="stretch")

    with report_tab:
        st.code(finance.render_financial_status(month))
        if st.button("Close month", key="finance_monthly_close"):
            finance.monthly_close(month)
            st.success("Immutable monthly closing created.")
        legacy_path = finance.root / "data" / "finance_budget.json"
        with st.expander("Legacy Finance migration"):
            st.caption("Migration is explicit, checksum-guarded, and idempotent.")
            if st.button(
                "Migrate legacy Finance budget",
                disabled=not legacy_path.is_file(),
                key="finance_migrate_legacy",
            ):
                try:
                    result = finance.migrate_legacy_budget(legacy_path, month)
                except (OSError, ValueError) as exc:
                    st.error(str(exc))
                else:
                    st.json(result)


def render_health(health: HealthSubsystem) -> None:
    import streamlit as st
    from datetime import date

    st.title("Health")
    st.caption("Health Subsystem v1.0 · Sensitive owner data · Informational, not medical advice")
    today = date.today()
    weight_tab, inbody_tab, lifestyle_tab, goal_tab = st.tabs(
        ["Weight", "InBody / Checkup", "Sleep / Exercise / Nutrition", "Goals / Report"]
    )
    with weight_tab:
        with st.form("health_weight_form"):
            measured_on = st.date_input("Measured on", value=today, key="health_weight_date")
            weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=500.0, value=70.0)
            note = st.text_input("Weight note")
            submitted = st.form_submit_button("Record weight")
        if submitted:
            try:
                health.record_weight(weight_kg, measured_on, note)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("Weight recorded.")
                st.rerun()
        st.dataframe(health.list_weights(), width="stretch")
        st.json(health.weight_baseline_comparison())
    with inbody_tab:
        with st.form("health_inbody_form"):
            inbody_on = st.date_input("InBody date", value=today)
            muscle = st.number_input("Skeletal muscle (kg)", min_value=1.0, max_value=150.0, value=30.0)
            body_fat = st.number_input("Body fat (%)", min_value=1.0, max_value=75.0, value=20.0)
            bmi = st.number_input("BMI", min_value=5.0, max_value=100.0, value=22.0)
            inbody_submit = st.form_submit_button("Record InBody")
        if inbody_submit:
            try:
                health.record_body_composition(inbody_on, muscle, body_fat, bmi)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success("InBody recorded.")
                st.rerun()
        st.dataframe(health.body_composition_timeline(), width="stretch")
        st.subheader("Health checkups")
        st.dataframe(health.list_health_checkups(), width="stretch")
    with lifestyle_tab:
        st.subheader("Sleep")
        with st.form("health_sleep_form"):
            bedtime = st.text_input("Bedtime (ISO with timezone)", value=f"{today.isoformat()}T23:00:00+09:00")
            wake_time = st.text_input("Wake time (ISO with timezone)", value=f"{today.isoformat()}T23:30:00+09:00")
            fatigue = st.slider("Fatigue", 1, 5, 3)
            sleep_submit = st.form_submit_button("Record sleep")
        if sleep_submit:
            try:
                health.record_sleep(bedtime, wake_time, fatigue)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.rerun()
        st.dataframe(health.list_sleep(), width="stretch")
        st.subheader("Exercise")
        st.dataframe(health.list_exercise(), width="stretch")
        st.subheader("Nutrition")
        st.dataframe(health.list_nutrition(), width="stretch")
    with goal_tab:
        with st.form("health_goal_form"):
            goal_name = st.text_input("Goal name")
            target_weight = st.number_input("Target weight (kg)", min_value=20.0, max_value=500.0, value=70.0)
            target_fat = st.number_input("Target body fat (%)", min_value=1.0, max_value=75.0, value=20.0)
            goal_submit = st.form_submit_button("Create Health goal")
        if goal_submit:
            try:
                health.create_health_goal(goal_name, today, target_weight, target_fat)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.rerun()
        st.dataframe(health.list_health_goals(), width="stretch")
        report_month = st.text_input("Report month", value=today.strftime("%Y-%m"), key="health_report_month")
        try:
            st.json(health.monthly_report(report_month))
        except ValueError as exc:
            st.error(str(exc))


def render_housing(housing: HousingSubsystem) -> None:
    import streamlit as st

    st.title("Housing")
    st.caption("Housing Subsystem v1.0 · Sensitive owner data · Deterministic candidate comparison")
    candidate_tab, comparison_tab, migration_tab = st.tabs(["Candidates", "Comparison / Report", "Migration"])

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
        st.dataframe(candidates, width="stretch", hide_index=True)
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
            if action_col2.button("Delete candidate", key="housing_delete_candidate"):
                housing.delete_candidate(selected_id)
                st.success("Candidate deleted.")
                st.rerun()

    with comparison_tab:
        st.dataframe(housing.rank_candidates(), width="stretch", hide_index=True)
        st.json(housing.housing_report())

    with migration_tab:
        legacy_path = housing.root / "data" / "housing_candidates.json"
        st.caption("Migration is dry-run-first, explicit, checksum-guarded, transactional, and idempotent.")
        dry_col, apply_col = st.columns(2)
        if dry_col.button("Dry run legacy Housing migration", disabled=not legacy_path.is_file()):
            try:
                result = housing.dry_run_legacy_json(legacy_path)
            except (OSError, ValueError) as exc:
                st.error(str(exc))
            else:
                st.session_state.housing_migration_dry_run = result
                st.json(result)
        dry_result = st.session_state.get("housing_migration_dry_run")
        if apply_col.button(
            "Apply reviewed Housing migration",
            disabled=not bool(dry_result),
            key="housing_apply_migration",
        ):
            try:
                result = housing.migrate_legacy_json(legacy_path)
            except (OSError, ValueError) as exc:
                st.error(str(exc))
            else:
                st.json(result)
                st.success("Reviewed Housing migration completed.")


def render_vehicle(vehicle: VehicleSubsystem) -> None:
    import streamlit as st

    st.title("Vehicle")
    st.caption("Vehicle Subsystem v1.0 · Sensitive owner data · Deterministic maintenance and cost records")
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
        st.dataframe(vehicles, width="stretch", hide_index=True)
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
                st.dataframe(vehicle.list_odometer_readings(vehicle_id), width="stretch", hide_index=True)

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
                st.dataframe(vehicle.list_maintenance_records(vehicle_id), width="stretch", hide_index=True)

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
                st.dataframe(schedules, width="stretch", hide_index=True)
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
                st.dataframe(vehicle.list_energy_logs(vehicle_id), width="stretch", hide_index=True)

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
            st.json(vehicle.vehicle_report(report_id))


def render_food(food: FoodSubsystem) -> None:
    import streamlit as st

    st.title("Food")
    st.caption("Food Subsystem v1.0 - Sensitive owner data - Owner-entered deterministic nutrition")
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
        st.dataframe(ingredients, width="stretch", hide_index=True)
        if ingredients:
            ingredient_labels = {row["ingredient_id"]: row["name"] for row in ingredients}
            archive_id = st.selectbox(
                "Ingredient to archive", list(ingredient_labels),
                format_func=lambda value: ingredient_labels[value], key="food_ingredient_archive_select",
            )
            if st.button("Archive ingredient", key="food_ingredient_archive_button"):
                food.archive_ingredient(archive_id)
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
        st.dataframe(recipes, width="stretch", hide_index=True)
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
        st.dataframe(food.list_cooking_records(), width="stretch", hide_index=True)
        st.dataframe(food.list_meals(), width="stretch", hide_index=True)

    with report_tab:
        st.info("Nutrition totals use owner-entered values only and are not medical guidance.")
        st.json(food.food_report())
