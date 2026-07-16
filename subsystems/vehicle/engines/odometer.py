from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_date,
    optional_text,
    require_date,
    require_non_negative_integer,
    utc_now_iso,
)
from subsystems.vehicle.engines.vehicle import VehicleEngine


class OdometerEngine:
    def __init__(self, store: VehicleStorageEngine, vehicles: VehicleEngine) -> None:
        self.store = store
        self.vehicles = vehicles

    def record(self, vehicle_id: Any, odometer_km: Any, recorded_on: Any,
               note: Any = "") -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        on = require_date(recorded_on, "recorded_on")
        kilometers = require_non_negative_integer(odometer_km, "odometer_km")
        row = {
            "reading_id": str(uuid4()), "vehicle_id": vehicle["vehicle_id"],
            "recorded_on": on, "odometer_km": kilometers,
            "note": optional_text(note, "note"), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            earlier = connection.execute(
                """SELECT odometer_km FROM vehicle_odometer_readings
                WHERE vehicle_id=? AND recorded_on<?
                ORDER BY recorded_on DESC,odometer_km DESC LIMIT 1""",
                (vehicle["vehicle_id"], on),
            ).fetchone()
            later = connection.execute(
                """SELECT odometer_km FROM vehicle_odometer_readings
                WHERE vehicle_id=? AND recorded_on>?
                ORDER BY recorded_on,odometer_km LIMIT 1""",
                (vehicle["vehicle_id"], on),
            ).fetchone()
            if earlier is not None and kilometers < int(earlier[0]):
                raise ValueError("odometer_km cannot be lower than an earlier reading.")
            if later is not None and kilometers > int(later[0]):
                raise ValueError("odometer_km cannot be higher than a later reading.")
            connection.execute(
                """INSERT INTO vehicle_odometer_readings(
                reading_id,vehicle_id,recorded_on,odometer_km,note,created_at
                ) VALUES(?,?,?,?,?,?)""",
                tuple(row.values()),
            )
        return row

    def list(self, vehicle_id: Any, start_on: Any = None,
             end_on: Any = None) -> list[dict[str, Any]]:
        vehicle = self.vehicles.get(vehicle_id)
        start = optional_date(start_on, "start_on")
        end = optional_date(end_on, "end_on")
        if start and end and start > end:
            raise ValueError("start_on cannot be after end_on.")
        sql = "SELECT * FROM vehicle_odometer_readings WHERE vehicle_id=?"
        parameters: list[Any] = [vehicle["vehicle_id"]]
        if start:
            sql += " AND recorded_on>=?"
            parameters.append(start)
        if end:
            sql += " AND recorded_on<=?"
            parameters.append(end)
        sql += " ORDER BY recorded_on,odometer_km,reading_id"
        return self.store.query(sql, tuple(parameters))

    def current(self, vehicle_id: Any) -> dict[str, Any] | None:
        vehicle = self.vehicles.get(vehicle_id)
        return self.store.query_one(
            """SELECT * FROM vehicle_odometer_readings WHERE vehicle_id=?
            ORDER BY recorded_on DESC,odometer_km DESC,reading_id DESC LIMIT 1""",
            (vehicle["vehicle_id"],),
        )
