from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.maintenance import MaintenanceEngine
from subsystems.vehicle.engines.odometer import OdometerEngine
from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_date,
    optional_non_negative_integer,
    require_choice,
    require_date,
    require_text,
    utc_now_iso,
)
from subsystems.vehicle.engines.vehicle import VehicleEngine


class ScheduleEngine:
    def __init__(self, store: VehicleStorageEngine, vehicles: VehicleEngine,
                 odometer: OdometerEngine, maintenance: MaintenanceEngine) -> None:
        self.store = store
        self.vehicles = vehicles
        self.odometer = odometer
        self.maintenance = maintenance

    def create(self, vehicle_id: Any, service_type: Any, due_on: Any = None,
               due_odometer_km: Any = None) -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        clean_due_on = optional_date(due_on, "due_on")
        clean_due_km = optional_non_negative_integer(due_odometer_km, "due_odometer_km")
        if clean_due_on is None and clean_due_km is None:
            raise ValueError("due_on or due_odometer_km is required.")
        now = utc_now_iso()
        row = {
            "schedule_id": str(uuid4()), "vehicle_id": vehicle["vehicle_id"],
            "service_type": require_text(service_type, "service_type", 200),
            "due_on": clean_due_on, "due_odometer_km": clean_due_km,
            "status": "active", "completed_maintenance_id": None,
            "created_at": now, "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO vehicle_maintenance_schedules(
                schedule_id,vehicle_id,service_type,due_on,due_odometer_km,status,
                completed_maintenance_id,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)""",
                tuple(row.values()),
            )
        return row

    def get(self, schedule_id: Any) -> dict[str, Any]:
        key = require_text(schedule_id, "schedule_id", 200)
        row = self.store.query_one(
            "SELECT * FROM vehicle_maintenance_schedules WHERE schedule_id=?", (key,)
        )
        if row is None:
            raise KeyError("Vehicle maintenance schedule not found.")
        return row

    def list(self, vehicle_id: Any, status: Any | None = None) -> list[dict[str, Any]]:
        vehicle = self.vehicles.get(vehicle_id)
        if status is None:
            return self.store.query(
                """SELECT * FROM vehicle_maintenance_schedules WHERE vehicle_id=?
                ORDER BY status,due_on,due_odometer_km,schedule_id""",
                (vehicle["vehicle_id"],),
            )
        clean = require_choice(status, "status", {"active", "completed", "dismissed"})
        return self.store.query(
            """SELECT * FROM vehicle_maintenance_schedules WHERE vehicle_id=? AND status=?
            ORDER BY due_on,due_odometer_km,schedule_id""",
            (vehicle["vehicle_id"], clean),
        )

    def complete(self, schedule_id: Any, maintenance_id: Any) -> dict[str, Any]:
        schedule = self.get(schedule_id)
        if schedule["status"] != "active":
            raise ValueError("Only an active maintenance schedule can be completed.")
        maintenance = self.maintenance.get(maintenance_id)
        if maintenance["vehicle_id"] != schedule["vehicle_id"]:
            raise ValueError("Maintenance record and schedule must belong to the same vehicle.")
        updated_at = utc_now_iso()
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE vehicle_maintenance_schedules
                SET status='completed',completed_maintenance_id=?,updated_at=?
                WHERE schedule_id=? AND status='active'""",
                (maintenance["maintenance_id"], updated_at, schedule["schedule_id"]),
            )
        return {**schedule, "status": "completed",
                "completed_maintenance_id": maintenance["maintenance_id"], "updated_at": updated_at}

    def due(self, vehicle_id: Any, as_of: Any = None) -> list[dict[str, Any]]:
        on = require_date(as_of or date.today().isoformat(), "as_of")
        current = self.odometer.current(vehicle_id)
        current_km = int(current["odometer_km"]) if current else None
        due_rows: list[dict[str, Any]] = []
        for row in self.list(vehicle_id, "active"):
            due_by_date = row["due_on"] is not None and row["due_on"] <= on
            due_by_odometer = (
                current_km is not None and row["due_odometer_km"] is not None
                and current_km >= int(row["due_odometer_km"])
            )
            if due_by_date or due_by_odometer:
                due_rows.append({**row, "due_by_date": due_by_date,
                                 "due_by_odometer": due_by_odometer,
                                 "current_odometer_km": current_km})
        return due_rows
