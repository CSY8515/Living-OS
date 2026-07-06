from __future__ import annotations

from typing import Any

from modules.storage import MODULE_REGISTRY_FILE, read_json, write_json


STATUSES = ["planned", "enabled", "disabled"]


def load_modules() -> list[dict[str, Any]]:
    data = read_json(MODULE_REGISTRY_FILE, {"modules": []})
    modules = data.get("modules", []) if isinstance(data, dict) else []
    if not isinstance(modules, list):
        return []
    return [item for item in modules if isinstance(item, dict)]


def save_modules(modules: list[dict[str, Any]]) -> None:
    write_json(MODULE_REGISTRY_FILE, {"modules": modules})


def render_module_manager() -> None:
    import streamlit as st

    st.title("Module Manager")
    st.caption("Prepare future OS modules without implementing them yet.")

    modules = load_modules()
    if not modules:
        st.info("No module registry found.")
        return

    changed = False
    for index, item in enumerate(modules):
        with st.expander(f"{item.get('name', item.get('id', 'Module'))} · {item.get('status', 'planned')}"):
            item["name"] = st.text_input("Name", value=str(item.get("name", "")), key=f"module_name_{index}")
            item["description"] = st.text_area(
                "Description",
                value=str(item.get("description", "")),
                height=90,
                key=f"module_description_{index}",
            )
            current_status = str(item.get("status", "planned"))
            status_index = STATUSES.index(current_status) if current_status in STATUSES else 0
            item["status"] = st.selectbox(
                "Status",
                STATUSES,
                index=status_index,
                key=f"module_status_{index}",
            )
            changed = True

    if st.button("Save Module Registry"):
        if changed:
            save_modules(modules)
        st.success("Module registry saved.")
