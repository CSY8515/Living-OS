from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.validation import (
    optional_text,
    require_date,
    require_non_negative_integer,
    require_text,
    utc_now_iso,
)
from subsystems.vehicle.engines.vehicle import VehicleEngine


class TripEngine:
    def __init__(self, store: VehicleStorageEngine, vehicles: VehicleEngine) -> None:
        self.store = store
        self.vehicles = vehicles

    def _available(self) -> bool:
        return bool(self.store.query_one(
            "SELECT 1 AS present FROM sqlite_master WHERE type='table' AND name='vehicle_trips'"
        ))

    def _ensure_schema(self) -> None:
        if self._available():
            return
        with self.store.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS vehicle_trips (
                    trip_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL,
                    driven_on TEXT NOT NULL, start_odometer_km INTEGER NOT NULL,
                    end_odometer_km INTEGER NOT NULL, distance_km INTEGER NOT NULL,
                    purpose TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL,
                    CHECK(start_odometer_km >= 0 AND end_odometer_km >= start_odometer_km),
                    FOREIGN KEY(vehicle_id) REFERENCES vehicle_vehicles(vehicle_id)
                );
                CREATE INDEX IF NOT EXISTS ix_vehicle_trip_date
                    ON vehicle_trips(vehicle_id,driven_on);
                """
            )

    def record(
        self,
        vehicle_id: Any,
        driven_on: Any,
        start_odometer_km: Any,
        end_odometer_km: Any,
        purpose: Any = "",
        note: Any = "",
    ) -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        self._ensure_schema()
        start = require_non_negative_integer(start_odometer_km, "start_odometer_km")
        end = require_non_negative_integer(end_odometer_km, "end_odometer_km")
        if end < start:
            raise ValueError("end_odometer_km cannot be lower than start_odometer_km.")
        row = {
            "trip_id": str(uuid4()),
            "vehicle_id": vehicle["vehicle_id"],
            "driven_on": require_date(driven_on, "driven_on"),
            "start_odometer_km": start,
            "end_odometer_km": end,
            "distance_km": end - start,
            "purpose": optional_text(purpose, "purpose", 500),
            "note": optional_text(note, "note"),
            "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO vehicle_trips VALUES(?,?,?,?,?,?,?,?,?)", tuple(row.values())
            )
        return row

    def get(self, trip_id: Any) -> dict[str, Any]:
        if not self._available():
            raise KeyError("Vehicle trip not found.")
        key = require_text(trip_id, "trip_id", 100)
        row = self.store.query_one("SELECT * FROM vehicle_trips WHERE trip_id=?", (key,))
        if row is None:
            raise KeyError("Vehicle trip not found.")
        return row

    def list(
        self, vehicle_id: Any, start_on: Any = None, end_on: Any = None
    ) -> list[dict[str, Any]]:
        vehicle = self.vehicles.get(vehicle_id)
        if not self._available():
            return []
        sql, params = "SELECT * FROM vehicle_trips WHERE vehicle_id=?", [vehicle["vehicle_id"]]
        if start_on is not None:
            sql += " AND driven_on>=?"
            params.append(require_date(start_on, "start_on"))
        if end_on is not None:
            sql += " AND driven_on<=?"
            params.append(require_date(end_on, "end_on"))
        if len(params) >= 3 and params[-2] > params[-1]:
            raise ValueError("start_on cannot be after end_on.")
        return self.store.query(sql + " ORDER BY driven_on DESC,created_at DESC", tuple(params))

    def delete(self, trip_id: Any) -> bool:
        row = self.get(trip_id)
        with self.store.transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM vehicle_trips WHERE trip_id=?", (row["trip_id"],)
            )
        return cursor.rowcount == 1
