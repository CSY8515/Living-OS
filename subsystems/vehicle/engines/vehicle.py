from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_model_year,
    optional_text,
    require_choice,
    require_text,
    utc_now_iso,
)


class VehicleEngine:
    def __init__(self, store: VehicleStorageEngine) -> None:
        self.store = store

    def create(self, display_name: Any, manufacturer: Any = "", model: Any = "",
               model_year: Any = None, powertrain: Any = "other") -> dict[str, Any]:
        now = utc_now_iso()
        row = {
            "vehicle_id": str(uuid4()),
            "display_name": require_text(display_name, "display_name", 200),
            "manufacturer": optional_text(manufacturer, "manufacturer", 200),
            "model": optional_text(model, "model", 200),
            "model_year": optional_model_year(model_year),
            "powertrain": require_choice(
                powertrain, "powertrain", {"gasoline", "diesel", "hybrid", "electric", "other"}
            ),
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO vehicle_vehicles(
                vehicle_id,display_name,manufacturer,model,model_year,powertrain,status,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                tuple(row[key] for key in (
                    "vehicle_id", "display_name", "manufacturer", "model", "model_year",
                    "powertrain", "status", "created_at", "updated_at",
                )),
            )
        return row

    def get(self, vehicle_id: Any) -> dict[str, Any]:
        key = require_text(vehicle_id, "vehicle_id", 200)
        row = self.store.query_one("SELECT * FROM vehicle_vehicles WHERE vehicle_id=?", (key,))
        if row is None:
            raise KeyError("Vehicle not found.")
        return row

    def list(self, status: Any | None = None) -> list[dict[str, Any]]:
        if status is None:
            return self.store.query(
                "SELECT * FROM vehicle_vehicles ORDER BY status,display_name,vehicle_id"
            )
        clean = require_choice(status, "status", {"active", "archived"})
        return self.store.query(
            "SELECT * FROM vehicle_vehicles WHERE status=? ORDER BY display_name,vehicle_id",
            (clean,),
        )

    def update(self, vehicle_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(vehicle_id)
        allowed = {"display_name", "manufacturer", "model", "model_year", "powertrain", "status"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Vehicle fields: {sorted(unexpected)}")
        row = {
            **current,
            "display_name": require_text(changes.get("display_name", current["display_name"]), "display_name", 200),
            "manufacturer": optional_text(changes.get("manufacturer", current["manufacturer"]), "manufacturer", 200),
            "model": optional_text(changes.get("model", current["model"]), "model", 200),
            "model_year": optional_model_year(changes.get("model_year", current["model_year"])),
            "powertrain": require_choice(changes.get("powertrain", current["powertrain"]), "powertrain", {"gasoline", "diesel", "hybrid", "electric", "other"}),
            "status": require_choice(changes.get("status", current["status"]), "status", {"active", "archived"}),
            "updated_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE vehicle_vehicles SET display_name=?,manufacturer=?,model=?,model_year=?,
                powertrain=?,status=?,updated_at=? WHERE vehicle_id=?""",
                (row["display_name"], row["manufacturer"], row["model"], row["model_year"],
                 row["powertrain"], row["status"], row["updated_at"], row["vehicle_id"]),
            )
        return row

    def archive(self, vehicle_id: Any) -> dict[str, Any]:
        return self.update(vehicle_id, status="archived")
