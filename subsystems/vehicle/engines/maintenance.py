from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_date,
    optional_non_negative_integer,
    optional_text,
    require_date,
    require_non_negative_integer,
    require_text,
    utc_now_iso,
)
from subsystems.vehicle.engines.vehicle import VehicleEngine


class MaintenanceEngine:
    def __init__(self, store: VehicleStorageEngine, vehicles: VehicleEngine) -> None:
        self.store = store
        self.vehicles = vehicles

    def record(self, vehicle_id: Any, service_type: Any, serviced_on: Any,
               odometer_km: Any = None, cost: Any = 0, provider: Any = "",
               note: Any = "") -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        row = {
            "maintenance_id": str(uuid4()), "vehicle_id": vehicle["vehicle_id"],
            "service_type": require_text(service_type, "service_type", 200),
            "serviced_on": require_date(serviced_on, "serviced_on"),
            "odometer_km": optional_non_negative_integer(odometer_km, "odometer_km"),
            "cost": require_non_negative_integer(cost, "cost"),
            "provider": optional_text(provider, "provider", 500),
            "note": optional_text(note, "note"), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO vehicle_maintenance_records(
                maintenance_id,vehicle_id,service_type,serviced_on,odometer_km,cost,provider,note,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                tuple(row.values()),
            )
        return row

    def get(self, maintenance_id: Any) -> dict[str, Any]:
        key = require_text(maintenance_id, "maintenance_id", 200)
        row = self.store.query_one(
            "SELECT * FROM vehicle_maintenance_records WHERE maintenance_id=?", (key,)
        )
        if row is None:
            raise KeyError("Vehicle maintenance record not found.")
        return row

    def list(self, vehicle_id: Any, start_on: Any = None, end_on: Any = None,
             service_type: Any = None) -> list[dict[str, Any]]:
        vehicle = self.vehicles.get(vehicle_id)
        start, end = optional_date(start_on, "start_on"), optional_date(end_on, "end_on")
        if start and end and start > end:
            raise ValueError("start_on cannot be after end_on.")
        sql = "SELECT * FROM vehicle_maintenance_records WHERE vehicle_id=?"
        parameters: list[Any] = [vehicle["vehicle_id"]]
        if start:
            sql += " AND serviced_on>=?"
            parameters.append(start)
        if end:
            sql += " AND serviced_on<=?"
            parameters.append(end)
        if service_type is not None:
            sql += " AND service_type=?"
            parameters.append(require_text(service_type, "service_type", 200))
        sql += " ORDER BY serviced_on DESC,maintenance_id DESC"
        return self.store.query(sql, tuple(parameters))
