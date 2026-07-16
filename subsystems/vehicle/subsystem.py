from __future__ import annotations

from pathlib import Path
from typing import Any

from subsystems.vehicle.engines.energy import EnergyEngine
from subsystems.vehicle.engines.maintenance import MaintenanceEngine
from subsystems.vehicle.engines.odometer import OdometerEngine
from subsystems.vehicle.engines.report import VehicleReportEngine
from subsystems.vehicle.engines.schedule import ScheduleEngine
from subsystems.vehicle.engines.storage import VehicleStorageEngine
from subsystems.vehicle.engines.vehicle import VehicleEngine


class VehicleSubsystem:
    """The only supported Living OS boundary for Vehicle Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.5,<2.0"
    PRIVACY_CLASS = "sensitive"

    def __init__(self, root: Path, database_path: Path | None = None) -> None:
        self.root = Path(root)
        path = (Path(database_path) if database_path is not None
                else self.root / "data" / "vehicle" / "vehicle.sqlite3")
        store = VehicleStorageEngine(path)
        vehicles = VehicleEngine(store)
        odometer = OdometerEngine(store, vehicles)
        maintenance = MaintenanceEngine(store, vehicles)
        schedules = ScheduleEngine(store, vehicles, odometer, maintenance)
        energy = EnergyEngine(store, vehicles)
        report = VehicleReportEngine(vehicles, odometer, maintenance, schedules, energy)
        self._store, self._vehicles, self._odometer = store, vehicles, odometer
        self._maintenance, self._schedules, self._energy = maintenance, schedules, energy
        self._report = report

    @property
    def database_path(self) -> Path:
        return self._store.database_path

    def health(self) -> dict[str, Any]:
        return {**self._store.health(), "subsystem": "vehicle", "version": self.VERSION,
                "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
                "privacy_class": self.PRIVACY_CLASS}

    def interface_manifest(self) -> dict[str, Any]:
        return {
            "subsystem": "vehicle", "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
            "privacy_class": self.PRIVACY_CLASS,
            "capabilities": ("vehicle-profile", "odometer", "maintenance",
                             "maintenance-schedule", "energy-cost", "vehicle-report"),
        }

    def create_vehicle(self, display_name: Any, manufacturer: Any = "", model: Any = "",
                       model_year: Any = None, powertrain: Any = "other") -> dict[str, Any]:
        return self._vehicles.create(display_name, manufacturer, model, model_year, powertrain)

    def get_vehicle(self, vehicle_id: Any) -> dict[str, Any]:
        return self._vehicles.get(vehicle_id)

    def list_vehicles(self, status: Any | None = None) -> list[dict[str, Any]]:
        return self._vehicles.list(status)

    def update_vehicle(self, vehicle_id: Any, **changes: Any) -> dict[str, Any]:
        return self._vehicles.update(vehicle_id, **changes)

    def archive_vehicle(self, vehicle_id: Any) -> dict[str, Any]:
        return self._vehicles.archive(vehicle_id)

    def record_odometer(self, vehicle_id: Any, odometer_km: Any, recorded_on: Any,
                        note: Any = "") -> dict[str, Any]:
        return self._odometer.record(vehicle_id, odometer_km, recorded_on, note)

    def list_odometer_readings(self, vehicle_id: Any, start_on: Any = None,
                               end_on: Any = None) -> list[dict[str, Any]]:
        return self._odometer.list(vehicle_id, start_on, end_on)

    def record_maintenance(self, vehicle_id: Any, service_type: Any, serviced_on: Any,
                           odometer_km: Any = None, cost: Any = 0, provider: Any = "",
                           note: Any = "") -> dict[str, Any]:
        return self._maintenance.record(
            vehicle_id, service_type, serviced_on, odometer_km, cost, provider, note
        )

    def list_maintenance_records(self, vehicle_id: Any, start_on: Any = None,
                                 end_on: Any = None, service_type: Any = None) -> list[dict[str, Any]]:
        return self._maintenance.list(vehicle_id, start_on, end_on, service_type)

    def create_maintenance_schedule(self, vehicle_id: Any, service_type: Any,
                                    due_on: Any = None, due_odometer_km: Any = None) -> dict[str, Any]:
        return self._schedules.create(vehicle_id, service_type, due_on, due_odometer_km)

    def list_maintenance_schedules(self, vehicle_id: Any,
                                   status: Any | None = None) -> list[dict[str, Any]]:
        return self._schedules.list(vehicle_id, status)

    def complete_maintenance_schedule(self, schedule_id: Any,
                                      maintenance_id: Any) -> dict[str, Any]:
        return self._schedules.complete(schedule_id, maintenance_id)

    def due_maintenance(self, vehicle_id: Any, as_of: Any = None) -> list[dict[str, Any]]:
        return self._schedules.due(vehicle_id, as_of)

    def record_energy(self, vehicle_id: Any, energy_type: Any, recorded_on: Any,
                      quantity: Any, cost: Any = 0, odometer_km: Any = None,
                      note: Any = "") -> dict[str, Any]:
        return self._energy.record(
            vehicle_id, energy_type, recorded_on, quantity, cost, odometer_km, note
        )

    def list_energy_logs(self, vehicle_id: Any, start_on: Any = None,
                         end_on: Any = None, energy_type: Any = None) -> list[dict[str, Any]]:
        return self._energy.list(vehicle_id, start_on, end_on, energy_type)

    def vehicle_report(self, vehicle_id: Any, start_on: Any = None,
                       end_on: Any = None, as_of: Any = None) -> dict[str, Any]:
        return self._report.status(vehicle_id, start_on, end_on, as_of)

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
