from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_date,
    optional_non_negative_integer,
    optional_text,
    require_choice,
    require_date,
    require_non_negative_integer,
    require_positive_milliunits,
    utc_now_iso,
)
from subsystems.vehicle.engines.vehicle import VehicleEngine


class EnergyEngine:
    def __init__(self, store: VehicleStorageEngine, vehicles: VehicleEngine) -> None:
        self.store = store
        self.vehicles = vehicles

    def record(self, vehicle_id: Any, energy_type: Any, recorded_on: Any,
               quantity: Any, cost: Any = 0, odometer_km: Any = None,
               note: Any = "") -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        row = {
            "energy_id": str(uuid4()), "vehicle_id": vehicle["vehicle_id"],
            "energy_type": require_choice(energy_type, "energy_type", {"fuel", "charge"}),
            "recorded_on": require_date(recorded_on, "recorded_on"),
            "odometer_km": optional_non_negative_integer(odometer_km, "odometer_km"),
            "quantity_milliunits": require_positive_milliunits(quantity),
            "cost": require_non_negative_integer(cost, "cost"),
            "note": optional_text(note, "note"), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO vehicle_energy_logs(
                energy_id,vehicle_id,energy_type,recorded_on,odometer_km,
                quantity_milliunits,cost,note,created_at) VALUES(?,?,?,?,?,?,?,?,?)""",
                tuple(row.values()),
            )
        return row

    def list(self, vehicle_id: Any, start_on: Any = None, end_on: Any = None,
             energy_type: Any = None) -> list[dict[str, Any]]:
        vehicle = self.vehicles.get(vehicle_id)
        start, end = optional_date(start_on, "start_on"), optional_date(end_on, "end_on")
        if start and end and start > end:
            raise ValueError("start_on cannot be after end_on.")
        sql = "SELECT * FROM vehicle_energy_logs WHERE vehicle_id=?"
        parameters: list[Any] = [vehicle["vehicle_id"]]
        if start:
            sql += " AND recorded_on>=?"
            parameters.append(start)
        if end:
            sql += " AND recorded_on<=?"
            parameters.append(end)
        if energy_type is not None:
            sql += " AND energy_type=?"
            parameters.append(require_choice(energy_type, "energy_type", {"fuel", "charge"}))
        sql += " ORDER BY recorded_on DESC,energy_id DESC"
        return self.store.query(sql, tuple(parameters))

    def get(self, energy_id: Any) -> dict[str, Any]:
        key = str(energy_id or "").strip()
        row = self.store.query_one("SELECT * FROM vehicle_energy_logs WHERE energy_id=?", (key,))
        if row is None:
            raise KeyError("Vehicle energy record not found.")
        return row

    def delete(self, energy_id: Any) -> bool:
        row = self.get(energy_id)
        with self.store.transaction() as connection:
            cursor = connection.execute("DELETE FROM vehicle_energy_logs WHERE energy_id=?", (row["energy_id"],))
        return cursor.rowcount == 1

    def efficiency(self, vehicle_id: Any, start_on: Any = None, end_on: Any = None) -> dict[str, Any]:
        logs = [row for row in self.list(vehicle_id, start_on, end_on, "fuel") if row["odometer_km"] is not None]
        logs.sort(key=lambda row: (row["recorded_on"], row["odometer_km"]))
        distance = int(logs[-1]["odometer_km"]) - int(logs[0]["odometer_km"]) if len(logs) > 1 else 0
        quantity = sum(int(row["quantity_milliunits"]) for row in logs[1:])
        return {
            "distance_km": distance,
            "fuel_liters": round(quantity / 1000, 3),
            "km_per_liter": round(distance / (quantity / 1000), 2) if quantity else None,
            "source_count": len(logs),
        }
