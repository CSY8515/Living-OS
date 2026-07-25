from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.housing.engines.candidate import HousingCandidateEngine
from subsystems.housing.engines.comparison import HousingComparisonEngine
from subsystems.housing.engines.migration import HousingMigrationEngine
from subsystems.housing.engines.occupancy import HousingOccupancyEngine
from subsystems.housing.engines.report import HousingReportEngine
from subsystems.housing.engines.scoring import HousingScoringEngine
from subsystems.housing.engines.storage import HousingStorageEngine
from subsystems.database.engines.observability import record_failures

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


class HousingSubsystem:
    """The only supported Living OS boundary for Housing Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.4,<2.0"
    PRIVACY_CLASS = "sensitive"

    def __init__(self, root: Path, database_path: Path | None = None,
                 database_foundation: DatabaseSubsystem | None = None) -> None:
        self.root = Path(root)
        path = Path(database_path) if database_path is not None else self.root / "data" / "housing" / "housing.sqlite3"
        store = HousingStorageEngine(path, database_foundation)
        store.register_contract(schema_version=1, migration_id="housing-schema-v1")
        scoring = HousingScoringEngine()
        candidates = HousingCandidateEngine(store, scoring)
        comparison = HousingComparisonEngine(candidates)
        report = HousingReportEngine(candidates, comparison)
        self._store = store
        self._scoring = scoring
        self._candidates = candidates
        self._comparison = comparison
        self._report = report
        self._occupancy = HousingOccupancyEngine(store)
        self._migration = HousingMigrationEngine(store, candidates, scoring)

    @property
    def database_path(self) -> Path:
        return self._store.database_path

    def health(self) -> dict[str, Any]:
        return {
            **self._store.health(),
            "subsystem": "housing",
            "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
            "privacy_class": self.PRIVACY_CLASS,
        }

    def interface_manifest(self) -> dict[str, Any]:
        return {
            "subsystem": "housing",
            "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
            "privacy_class": self.PRIVACY_CLASS,
            "capabilities": (
                "candidate-crud", "scoring", "comparison", "rental-contract",
                "rent-and-maintenance-charge", "housing-report", "migration",
            ),
        }

    def calculate_candidate(self, **values: Any) -> dict[str, Any]:
        return self._scoring.calculate(**values)

    @record_failures("create_candidate")
    def create_candidate(self, **values: Any) -> dict[str, Any]:
        return self._candidates.create(**values)

    def get_candidate(self, candidate_id: Any) -> dict[str, Any]:
        return self._candidates.get(candidate_id)

    def list_candidates(self, status: Any | None = None) -> list[dict[str, Any]]:
        return self._candidates.list(status)

    @record_failures("update_candidate")
    def update_candidate(self, candidate_id: Any, **changes: Any) -> dict[str, Any]:
        return self._candidates.update(candidate_id, **changes)

    @record_failures("delete_candidate")
    def delete_candidate(self, candidate_id: Any) -> bool:
        return self._candidates.delete(candidate_id)

    def rank_candidates(self, status: Any | None = None) -> list[dict[str, Any]]:
        return self._comparison.rank(status)

    def housing_report(self) -> dict[str, Any]:
        return self._report.status()

    @record_failures("create_housing_contract")
    def create_contract(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._occupancy.create_contract(*args, **kwargs)

    def get_contract(self, contract_id: Any) -> dict[str, Any]:
        return self._occupancy.get_contract(contract_id)

    def list_contracts(self, status: Any | None = None, search: str | None = None) -> list[dict[str, Any]]:
        return self._occupancy.list_contracts(status, search)

    @record_failures("update_housing_contract")
    def update_contract(self, contract_id: Any, **changes: Any) -> dict[str, Any]:
        return self._occupancy.update_contract(contract_id, **changes)

    @record_failures("archive_housing_contract")
    def archive_contract(self, contract_id: Any) -> dict[str, Any]:
        return self._occupancy.update_contract(contract_id, status="archived")

    @record_failures("record_housing_charge")
    def record_charge(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._occupancy.record_charge(*args, **kwargs)

    def list_charges(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return self._occupancy.list_charges(*args, **kwargs)

    @record_failures("delete_housing_charge")
    def delete_charge(self, charge_id: Any) -> bool:
        return self._occupancy.delete_charge(charge_id)

    def occupancy_report(self, contract_id: Any) -> dict[str, Any]:
        return self._occupancy.report(contract_id)

    def dashboard(self) -> dict[str, Any]:
        active = self.list_contracts("active")
        return {
            "candidate_count": len(self.list_candidates()),
            "active_contract_count": len(active),
            "monthly_commitment": sum(
                int(item["monthly_rent"]) + int(item["maintenance_fee"]) for item in active
            ),
        }

    def dry_run_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.dry_run_legacy_json(Path(source))

    @record_failures("migrate_legacy_json")
    def migrate_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.migrate_legacy_json(Path(source))

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
