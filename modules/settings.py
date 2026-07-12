from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from modules.ai_credentials import (
    CredentialError,
    credential_status,
    remove_saved_api_key,
    resolve_api_key,
    save_api_key,
)
from modules.ai_service import AI_MODELS, DEFAULT_AI_MODEL, test_connection
from modules.storage import (
    ARCHIVE_FILE,
    BACKUPS_DIR,
    DAILY_LOG_FILE,
    DECISION_LOG_FILE,
    MODULE_REGISTRY_FILE,
    REPORT_INDEX_FILE,
    SETTINGS_FILE,
    read_json,
    write_json,
)


BACKUP_TARGETS = [
    DAILY_LOG_FILE,
    ARCHIVE_FILE,
    REPORT_INDEX_FILE,
    SETTINGS_FILE,
    MODULE_REGISTRY_FILE,
    DECISION_LOG_FILE,
]


def load_settings() -> dict[str, Any]:
    value = read_json(SETTINGS_FILE, {})
    return value if isinstance(value, dict) else {}


def save_settings(settings: dict[str, Any]) -> None:
    write_json(SETTINGS_FILE, settings)


def create_backup() -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    backup: dict[str, Any] = {"created_at": datetime.now().astimezone().isoformat(), "files": {}}
    for path in BACKUP_TARGETS:
        if not path.exists():
            continue
        try:
            backup["files"][str(path.relative_to(path.parent.parent))] = path.read_text(encoding="utf-8")
        except OSError:
            continue
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / f"living_os_backup_{timestamp}.json"
    backup_path.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding="utf-8")
    return backup_path


def restore_backup(raw_json: str) -> int:
    data = json.loads(raw_json)
    files = data.get("files", {}) if isinstance(data, dict) else {}
    if not isinstance(files, dict):
        return 0

    restored = 0
    allowed = {str(path.relative_to(path.parent.parent)): path for path in BACKUP_TARGETS}
    for relative_path, content in files.items():
        target = allowed.get(str(relative_path))
        if target is None or not isinstance(content, str):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        restored += 1
    return restored


def render_settings() -> None:
    import streamlit as st

    st.title("Settings")
    st.caption("Basic settings, data backup, and restore.")

    settings = load_settings()
    with st.form("settings_form"):
        settings["app_name"] = st.text_input("App Name", value=str(settings.get("app_name", "Living OS")))
        settings["default_report_range"] = st.selectbox(
            "Default Report Range",
            ["daily", "weekly", "monthly"],
            index=["daily", "weekly", "monthly"].index(str(settings.get("default_report_range", "daily")))
            if str(settings.get("default_report_range", "daily")) in {"daily", "weekly", "monthly"}
            else 0,
        )
        submitted = st.form_submit_button("Save Settings")

    if submitted:
        save_settings(settings)
        st.success("Settings saved.")

    st.divider()
    st.subheader("OpenAI Configuration")
    st.caption("The API key is never stored in Living OS JSON/JSONL files. AI requests run only when you press an AI action button.")
    if "ai_model" not in st.session_state or st.session_state.ai_model not in AI_MODELS:
        st.session_state.ai_model = DEFAULT_AI_MODEL
    st.selectbox("OpenAI Model", AI_MODELS, key="ai_model")
    session_key = st.text_input(
        "OpenAI API Key",
        value=str(st.session_state.get("ai_session_api_key", "")),
        type="password",
        placeholder="Session-only unless explicitly saved below",
    )
    st.session_state.ai_session_api_key = session_key.strip()
    status = credential_status(st.session_state.ai_session_api_key)
    if status.configured:
        st.success(f"Configured from {status.source}: {status.masked}")
    else:
        st.info("No API key configured. You may also set OPENAI_API_KEY in the local environment.")

    credential_col, remove_col, test_col = st.columns(3)
    if credential_col.button("Save Key to OS Credential Store"):
        try:
            save_api_key(st.session_state.ai_session_api_key)
        except CredentialError as exc:
            st.error(str(exc))
        else:
            st.success("API key saved to the operating-system credential store.")
    if remove_col.button("Remove Saved Key"):
        try:
            remove_saved_api_key()
        except CredentialError as exc:
            st.error(str(exc))
        else:
            st.success("Saved API key removed. Session and environment keys were not changed.")
    if test_col.button("Test OpenAI Connection"):
        api_key, _ = resolve_api_key(st.session_state.ai_session_api_key)
        result = test_connection(api_key, st.session_state.ai_model)
        if result.ok:
            st.success(result.message)
        else:
            st.error(result.message)

    st.divider()
    st.subheader("Data Management")
    if st.button("Create Backup"):
        path = create_backup()
        st.success(f"Backup created: {path.name}")

    st.subheader("Restore")
    raw_json = st.text_area("Paste backup JSON", height=180)
    if st.button("Restore Backup"):
        if not raw_json.strip():
            st.error("Backup JSON is required.")
        else:
            try:
                restored = restore_backup(raw_json)
            except json.JSONDecodeError:
                st.error("Invalid backup JSON.")
            else:
                st.success(f"Restored {restored} file(s).")

    st.divider()
    st.subheader("Storage Files")
    for path in BACKUP_TARGETS:
        st.write(f"{path.relative_to(path.parent.parent)} · {'OK' if path.exists() else 'Missing'}")
