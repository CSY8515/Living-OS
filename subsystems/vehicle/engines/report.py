from __future__ import annotations

from datetime import date
from typing import Any

from subsystems.vehicle.engines.energy import EnergyEngine
from subsystems.vehicle.engines.maintenance import MaintenanceEngine
from subsystems.vehicle.engines.odometer import OdometerEngine
from subsystems.vehicle.engines.schedule import ScheduleEngine
from subsystems.vehicle.engines.vehicle import VehicleEngine


class VehicleReportEngine:
    def __init__(self, vehicles: VehicleEngine, odometer: OdometerEngine,
                 maintenance: MaintenanceEngine, schedules: ScheduleEngine,
                 energy: EnergyEngine) -> None:
        self.vehicles = vehicles
        self.odometer = odometer
        self.maintenance = maintenance
        self.schedules = schedules
        self.energy = energy

    def status(self, vehicle_id: Any, start_on: Any = None, end_on: Any = None,
               as_of: Any = None) -> dict[str, Any]:
        vehicle = self.vehicles.get(vehicle_id)
        readings = self.odometer.list(vehicle_id, start_on, end_on)
        maintenance = self.maintenance.list(vehicle_id, start_on, end_on)
        energy = self.energy.list(vehicle_id, start_on, end_on)
        due = self.schedules.due(vehicle_id, as_of or date.today().isoformat())
        current = self.odometer.current(vehicle_id)
        distance = 0
        if len(readings) > 1:
            distance = int(readings[-1]["odometer_km"]) - int(readings[0]["odometer_km"])
        maintenance_cost = sum(int(row["cost"]) for row in maintenance)
        energy_cost = sum(int(row["cost"]) for row in energy)
        quantities = {
            kind: sum(int(row["quantity_milliunits"]) for row in energy if row["energy_type"] == kind)
            for kind in ("fuel", "charge")
        }
        actions = [f"Review due maintenance: {row['service_type']}." for row in due]
        if current is None:
            actions.append("Record an odometer reading.")
        if not actions:
            actions.append("No maintenance is currently due.")
        return {
            "vehicle": vehicle,
            "current_odometer_km": int(current["odometer_km"]) if current else None,
            "distance_km": distance,
            "maintenance_count": len(maintenance),
            "maintenance_cost": maintenance_cost,
            "energy_count": len(energy),
            "energy_cost": energy_cost,
            "operating_cost": maintenance_cost + energy_cost,
            "fuel_milliunits": quantities["fuel"],
            "charge_milliunits": quantities["charge"],
            "due_maintenance": due,
            "maintenance_records": maintenance,
            "energy_logs": energy,
            "next_actions": actions,
        }
