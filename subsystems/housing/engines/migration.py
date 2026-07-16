from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.housing.engines.candidate import HousingCandidateEngine
from subsystems.housing.engines.scoring import HousingScoringEngine
from subsystems.housing.engines.storage import HousingStorageEngine
from subsystems.housing.engines.validation import require_status, utc_now_iso


class HousingMigrationEngine:
    def __init__(
        self,
        store: HousingStorageEngine,
        candidates: HousingCandidateEngine,
        scoring: HousingScoringEngine,
    ) -> None:
        self.store = store
        self.candidates = candidates
        self.scoring = scoring
        self._reviewed_checksums: dict[str, str] = {}

    def dry_run_legacy_json(self, source: Path) -> dict[str, Any]:
        path, checksum, payload = self._read(source)
        rows = self._normalize(payload)
        self._reviewed_checksums[str(path.resolve())] = checksum
        return {
            "source": str(path.resolve()),
            "checksum": checksum,
            "dry_run": True,
            "accepted": {"candidates": len(rows)},
            "database_created": False,
        }

    def migrate_legacy_json(self, source: Path) -> dict[str, Any]:
        path, checksum, payload = self._read(source)
        source_key = str(path.resolve())
        existing = self.store.query_one(
            "SELECT checksum,result_json,imported_at FROM housing_migration_ledger WHERE source_key=?",
            (source_key,),
        )
        if existing:
            if existing["checksum"] != checksum:
                raise ValueError("Legacy Housing source changed after migration; review before importing again.")
            return {
                **json.loads(existing["result_json"]),
                "already_migrated": True,
                "imported_at": existing["imported_at"],
            }
        if self._reviewed_checksums.get(source_key) != checksum:
            raise ValueError("Run and review a Housing migration dry run for the current source before applying it.")
        rows = self._normalize(payload)
        imported_at = utc_now_iso()
        result = {
            "source": source_key,
            "checksum": checksum,
            "dry_run": False,
            "accepted": {"candidates": len(rows)},
            "already_migrated": False,
        }
        with self.store.transaction() as connection:
            for row in rows:
                self.candidates._insert(connection, row)
            connection.execute(
                "INSERT INTO housing_migration_ledger VALUES(?,?,?,?)",
                (source_key, checksum, json.dumps(result, sort_keys=True), imported_at),
            )
        return {**result, "imported_at": imported_at}

    @staticmethod
    def _read(source: Path) -> tuple[Path, str, dict[str, Any]]:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        checksum = hashlib.sha256(raw).hexdigest()
        try:
            payload = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Legacy Housing source must be valid UTF-8 JSON.") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("candidates"), list):
            raise ValueError("Legacy Housing source must contain a candidates array.")
        return path, checksum, payload

    def _normalize(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for index, raw in enumerate(payload["candidates"]):
            if not isinstance(raw, dict):
                raise ValueError(f"Housing candidate {index + 1} must be an object.")
            calculated = self.scoring.calculate(
                name=raw.get("name"),
                deposit=raw.get("deposit", 0),
                monthly_rent=raw.get("monthly_rent", 0),
                maintenance_fee=raw.get("maintenance_fee", 0),
                maintenance_fee_provided=bool(raw.get("maintenance_fee_provided", True)),
                commute_minutes=raw.get("commute_minutes", 0),
                parking_available=bool(raw.get("parking_available", False)),
                options_memo=raw.get("options_memo", ""),
                special_notes=raw.get("special_notes", ""),
            )
            created_at = str(raw.get("created_at") or utc_now_iso())
            normalized.append({
                "candidate_id": str(raw.get("id") or raw.get("candidate_id") or uuid4()),
                **calculated,
                "status": require_status(raw.get("status", "active")),
                "created_at": created_at,
                "updated_at": created_at,
            })
        return normalized
