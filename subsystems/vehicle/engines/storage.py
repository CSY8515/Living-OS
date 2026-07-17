from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.vehicle.engines.validation import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1


class VehicleStorageEngine(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(
            database_path,
            component_id="SUB-VEHICLE",
            display_name="Vehicle Subsystem",
            foundation=foundation,
        )

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            statements = (
                "CREATE TABLE IF NOT EXISTS vehicle_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)",
                """CREATE TABLE IF NOT EXISTS vehicle_vehicles (
                    vehicle_id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
                    manufacturer TEXT NOT NULL, model TEXT NOT NULL,
                    model_year INTEGER CHECK(model_year IS NULL OR model_year BETWEEN 1886 AND 9999),
                    powertrain TEXT NOT NULL CHECK(powertrain IN ('gasoline','diesel','hybrid','electric','other')),
                    status TEXT NOT NULL CHECK(status IN ('active','archived')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""",
                """CREATE TABLE IF NOT EXISTS vehicle_odometer_readings (
                    reading_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL,
                    recorded_on TEXT NOT NULL, odometer_km INTEGER NOT NULL CHECK(odometer_km >= 0),
                    note TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicle_vehicles(vehicle_id),
                    UNIQUE(vehicle_id,recorded_on,odometer_km))""",
                """CREATE TABLE IF NOT EXISTS vehicle_maintenance_records (
                    maintenance_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL,
                    service_type TEXT NOT NULL, serviced_on TEXT NOT NULL,
                    odometer_km INTEGER CHECK(odometer_km IS NULL OR odometer_km >= 0),
                    cost INTEGER NOT NULL CHECK(cost >= 0), provider TEXT NOT NULL,
                    note TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicle_vehicles(vehicle_id))""",
                """CREATE TABLE IF NOT EXISTS vehicle_maintenance_schedules (
                    schedule_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL,
                    service_type TEXT NOT NULL, due_on TEXT,
                    due_odometer_km INTEGER CHECK(due_odometer_km IS NULL OR due_odometer_km >= 0),
                    status TEXT NOT NULL CHECK(status IN ('active','completed','dismissed')),
                    completed_maintenance_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    CHECK(due_on IS NOT NULL OR due_odometer_km IS NOT NULL),
                    FOREIGN KEY(vehicle_id) REFERENCES vehicle_vehicles(vehicle_id),
                    FOREIGN KEY(completed_maintenance_id) REFERENCES vehicle_maintenance_records(maintenance_id))""",
                """CREATE TABLE IF NOT EXISTS vehicle_energy_logs (
                    energy_id TEXT PRIMARY KEY, vehicle_id TEXT NOT NULL,
                    energy_type TEXT NOT NULL CHECK(energy_type IN ('fuel','charge')),
                    recorded_on TEXT NOT NULL,
                    odometer_km INTEGER CHECK(odometer_km IS NULL OR odometer_km >= 0),
                    quantity_milliunits INTEGER NOT NULL CHECK(quantity_milliunits > 0),
                    cost INTEGER NOT NULL CHECK(cost >= 0), note TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(vehicle_id) REFERENCES vehicle_vehicles(vehicle_id))""",
                "CREATE INDEX IF NOT EXISTS ix_vehicle_odometer ON vehicle_odometer_readings(vehicle_id,recorded_on,odometer_km)",
                "CREATE INDEX IF NOT EXISTS ix_vehicle_maintenance ON vehicle_maintenance_records(vehicle_id,serviced_on)",
                "CREATE INDEX IF NOT EXISTS ix_vehicle_schedule ON vehicle_maintenance_schedules(vehicle_id,status,due_on,due_odometer_km)",
                "CREATE INDEX IF NOT EXISTS ix_vehicle_energy ON vehicle_energy_logs(vehicle_id,recorded_on)",
            )
            for statement in statements:
                connection.execute(statement)
            now = utc_now_iso()
            for key, value in (("schema_version", str(SCHEMA_VERSION)), ("subsystem_version", "1.0.0")):
                connection.execute(
                    """INSERT INTO vehicle_meta(key,value,updated_at) VALUES(?,?,?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                    (key, value, now),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self.register_contract(schema_version=SCHEMA_VERSION, migration_id="vehicle-schema-v1")

    def query(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        connection = self._connect()
        try:
            return [dict(row) for row in connection.execute(sql, parameters).fetchall()]
        finally:
            connection.close()

    def query_one(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        if not self.initialized:
            return None
        connection = self._connect()
        try:
            row = connection.execute(sql, parameters).fetchone()
            return dict(row) if row is not None else None
        finally:
            connection.close()

    def export_snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "vehicles": self.query("SELECT * FROM vehicle_vehicles ORDER BY display_name,vehicle_id"),
            "odometer_readings": self.query("SELECT * FROM vehicle_odometer_readings ORDER BY recorded_on,reading_id"),
            "maintenance_records": self.query("SELECT * FROM vehicle_maintenance_records ORDER BY serviced_on,maintenance_id"),
            "maintenance_schedules": self.query("SELECT * FROM vehicle_maintenance_schedules ORDER BY created_at,schedule_id"),
            "energy_logs": self.query("SELECT * FROM vehicle_energy_logs ORDER BY recorded_on,energy_id"),
        }

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "ready", "initialized": False, "schema_version": SCHEMA_VERSION}
        row = self.query_one("PRAGMA integrity_check")
        healthy = bool(row) and next(iter(row.values())) == "ok"
        return {
            "status": "healthy" if healthy else "degraded",
            "initialized": True,
            "schema_version": SCHEMA_VERSION,
            "database_path": str(self.database_path),
        }
