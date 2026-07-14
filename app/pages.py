from __future__ import annotations

from collections import Counter
from pathlib import Path
import tempfile
from typing import Any

from core.errors import CoreError
from core.hub import LivingHub
from core.module_runtime import LIFECYCLE_TRANSITIONS
from modules.ai_credentials import resolve_api_key
from modules.ai_service import (
    AI_MODELS,
    DEFAULT_AI_MODEL,
    AIServiceError,
    record_source,
)
from modules.ai_briefing import AIBriefingService, OpenAITextProvider
from modules.decision import DecisionService
from modules.journal import JournalService
from modules.knowledge import KnowledgeService
from modules.hub_settings import HubSettingsService
from modules.projections import analytics_projection, dashboard_projection, review_projection
from modules.reports import ReportsService


def _tags(raw: str) -> list[str]:
    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def render_dashboard(hub: LivingHub) -> None:
    import streamlit as st

    data = dashboard_projection(hub)
    st.title("Living OS")
    st.caption("v2.0 Hub · One Core, one canonical state, explicit commands")
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
        from modules.settings import load_settings, save_settings

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
        st.success("v1 compatibility migration is complete. The v2 Hub store is canonical.")
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
    if st.button("Create Verified v2 Backup"):
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
    restore_file = st.file_uploader("Select a Living OS v2 backup", type=["zip"], key="v2_restore_file")
    restore_approval = st.checkbox("I approve a safety backup followed by restoring this verified archive.")
    if st.button("Restore Verified v2 Backup"):
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
