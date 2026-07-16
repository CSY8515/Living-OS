from __future__ import annotations

from pathlib import Path
from typing import Any

from subsystems.housing.engines.candidate import HousingCandidateEngine
from subsystems.housing.engines.comparison import HousingComparisonEngine
from subsystems.housing.engines.migration import HousingMigrationEngine
from subsystems.housing.engines.report import HousingReportEngine
from subsystems.housing.engines.scoring import HousingScoringEngine
from subsystems.housing.engines.storage import HousingStorageEngine


class HousingSubsystem:
    """The only supported Living OS boundary for Housing Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.4,<2.0"
    PRIVACY_CLASS = "sensitive"

    def __init__(self, root: Path, database_path: Path | None = None) -> None:
        self.root = Path(root)
        path = Path(database_path) if database_path is not None else self.root / "data" / "housing" / "housing.sqlite3"
        store = HousingStorageEngine(path)
        scoring = HousingScoringEngine()
        candidates = HousingCandidateEngine(store, scoring)
        comparison = HousingComparisonEngine(candidates)
        report = HousingReportEngine(candidates, comparison)
        self._store = store
        self._scoring = scoring
        self._candidates = candidates
        self._comparison = comparison
        self._report = report
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
            "capabilities": ("candidate-crud", "scoring", "comparison", "housing-report", "migration"),
        }

    def calculate_candidate(self, **values: Any) -> dict[str, Any]:
        return self._scoring.calculate(**values)

    def create_candidate(self, **values: Any) -> dict[str, Any]:
        return self._candidates.create(**values)

    def get_candidate(self, candidate_id: Any) -> dict[str, Any]:
        return self._candidates.get(candidate_id)

    def list_candidates(self, status: Any | None = None) -> list[dict[str, Any]]:
        return self._candidates.list(status)

    def update_candidate(self, candidate_id: Any, **changes: Any) -> dict[str, Any]:
        return self._candidates.update(candidate_id, **changes)

    def delete_candidate(self, candidate_id: Any) -> bool:
        return self._candidates.delete(candidate_id)

    def rank_candidates(self, status: Any | None = None) -> list[dict[str, Any]]:
        return self._comparison.rank(status)

    def housing_report(self) -> dict[str, Any]:
        return self._report.status()

    def dry_run_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.dry_run_legacy_json(Path(source))

    def migrate_legacy_json(self, source: Path) -> dict[str, Any]:
        return self._migration.migrate_legacy_json(Path(source))

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
