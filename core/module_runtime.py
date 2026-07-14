from __future__ import annotations

import json
from contextlib import closing
from dataclasses import asdict
from typing import Iterable

from core.audit import append_audit
from core.contracts import CommandEnvelope, ModuleManifest
from core.storage import HubStore
from shared.time import utc_now_iso


LIFECYCLE_TRANSITIONS = {
    "registered": {"installed", "removed"},
    "installed": {"enabled", "disabled", "removed"},
    "enabled": {"degraded", "disabled"},
    "degraded": {"enabled", "disabled"},
    "disabled": {"enabled", "removed"},
    "removed": {"registered"},
}


class ModuleRuntime:
    def __init__(self, store: HubStore) -> None:
        self.store = store

    def register(self, manifest: ModuleManifest) -> None:
        manifest.validate()
        self.store.initialize()
        with self.store.transaction() as connection:
            current = connection.execute(
                "SELECT lifecycle_state FROM module_states WHERE module_id = ?",
                (manifest.module_id,),
            ).fetchone()
            lifecycle = str(current["lifecycle_state"]) if current else manifest.status
            now = utc_now_iso()
            connection.execute(
                """
                INSERT INTO module_states (
                    module_id, manifest_json, lifecycle_state, health_state, installed_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(module_id) DO UPDATE SET
                    manifest_json=excluded.manifest_json,
                    updated_at=excluded.updated_at
                """,
                (
                    manifest.module_id,
                    json.dumps(asdict(manifest), ensure_ascii=False, sort_keys=True),
                    lifecycle,
                    "healthy",
                    now if lifecycle in {"installed", "enabled"} else None,
                    now,
                ),
            )

    def register_all(self, manifests: Iterable[ModuleManifest]) -> None:
        for manifest in manifests:
            self.register(manifest)

    def transition(self, module_id: str, target_state: str) -> None:
        if module_id in {"module_manager", "settings"} and target_state in {"disabled", "removed"}:
            raise ValueError("Core administration modules cannot be disabled or removed.")
        self.store.initialize()
        command = CommandEnvelope(
            "module_manager",
            "transition",
            {"module_id": module_id, "target_state": target_state},
            reason="change-module-lifecycle",
        )
        with self.store.transaction() as connection:
            row = connection.execute(
                "SELECT lifecycle_state FROM module_states WHERE module_id = ?", (module_id,)
            ).fetchone()
            if row is None:
                raise ValueError("Module is not registered.")
            current = str(row["lifecycle_state"])
            if target_state not in LIFECYCLE_TRANSITIONS.get(current, set()):
                raise ValueError(f"Invalid module transition: {current} -> {target_state}")
            now = utc_now_iso()
            connection.execute(
                """UPDATE module_states
                   SET lifecycle_state=?, installed_at=COALESCE(installed_at, ?), updated_at=?
                   WHERE module_id=?""",
                (target_state, now if target_state == "installed" else None, now, module_id),
            )
            append_audit(
                connection,
                command,
                "accepted",
                {"module_id": module_id, "from": current, "to": target_state},
            )

    def set_health(self, module_id: str, health_state: str) -> None:
        if health_state not in {"healthy", "degraded", "unavailable"}:
            raise ValueError("Unknown module health state.")
        self.store.initialize()
        with self.store.transaction() as connection:
            updated = connection.execute(
                "UPDATE module_states SET health_state=?, updated_at=? WHERE module_id=?",
                (health_state, utc_now_iso(), module_id),
            ).rowcount
        if not updated:
            raise ValueError("Module is not registered.")

    def list_modules(self) -> list[dict[str, object]]:
        self.store.initialize()
        with closing(self.store.connect()) as connection:
            rows = connection.execute(
                """SELECT manifest_json, lifecycle_state, health_state, installed_at, updated_at
                   FROM module_states ORDER BY module_id"""
            ).fetchall()
        modules: list[dict[str, object]] = []
        for row in rows:
            manifest = json.loads(row["manifest_json"])
            modules.append(
                {
                    **manifest,
                    "status": str(row["lifecycle_state"]),
                    "health": str(row["health_state"]),
                    "installed_at": row["installed_at"],
                    "updated_at": str(row["updated_at"]),
                }
            )
        return modules
