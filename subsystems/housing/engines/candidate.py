from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from subsystems.housing.engines.scoring import HousingScoringEngine
from subsystems.housing.engines.storage import HousingStorageEngine
from subsystems.housing.engines.validation import require_status, require_text, utc_now_iso


_COLUMNS = """candidate_id,name,deposit,monthly_rent,maintenance_fee,
maintenance_fee_provided,total_monthly_cost,commute_minutes,parking_available,
options_memo,special_notes,score,grade,deductions_json,status,created_at,updated_at"""


class HousingCandidateEngine:
    def __init__(self, store: HousingStorageEngine, scoring: HousingScoringEngine) -> None:
        self.store = store
        self.scoring = scoring

    def create(self, *, status: Any = "active", **values: Any) -> dict[str, Any]:
        calculated = self.scoring.calculate(**values)
        now = utc_now_iso()
        row = {
            "candidate_id": str(uuid4()),
            **calculated,
            "status": require_status(status),
            "created_at": now,
            "updated_at": now,
        }
        with self.store.transaction() as connection:
            self._insert(connection, row)
        return row

    def get(self, candidate_id: Any) -> dict[str, Any]:
        key = require_text(candidate_id, "candidate_id", 200)
        row = self.store.query_one("SELECT * FROM housing_candidates WHERE candidate_id=?", (key,))
        if row is None:
            raise KeyError("Housing candidate not found.")
        return row

    def list(self, status: Any | None = None) -> list[dict[str, Any]]:
        if status is None:
            return self.store.query(
                "SELECT * FROM housing_candidates ORDER BY score DESC,total_monthly_cost,commute_minutes,name"
            )
        clean_status = require_status(status)
        return self.store.query(
            """SELECT * FROM housing_candidates WHERE status=?
            ORDER BY score DESC,total_monthly_cost,commute_minutes,name""",
            (clean_status,),
        )

    def update(self, candidate_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(candidate_id)
        allowed = {
            "name", "deposit", "monthly_rent", "maintenance_fee", "maintenance_fee_provided",
            "commute_minutes", "parking_available", "options_memo", "special_notes", "status",
        }
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Housing candidate fields: {sorted(unexpected)}")
        score_values = {
            key: changes.get(key, current[key])
            for key in (
                "name", "deposit", "monthly_rent", "maintenance_fee", "maintenance_fee_provided",
                "commute_minutes", "parking_available", "options_memo", "special_notes",
            )
        }
        calculated = self.scoring.calculate(**score_values)
        row = {
            "candidate_id": current["candidate_id"],
            **calculated,
            "status": require_status(changes.get("status", current["status"])),
            "created_at": current["created_at"],
            "updated_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("DELETE FROM housing_candidates WHERE candidate_id=?", (row["candidate_id"],))
            self._insert(connection, row)
        return row

    def delete(self, candidate_id: Any) -> bool:
        current = self.get(candidate_id)
        with self.store.transaction() as connection:
            connection.execute("DELETE FROM housing_candidates WHERE candidate_id=?", (current["candidate_id"],))
        return True

    @staticmethod
    def _insert(connection: Any, row: dict[str, Any]) -> None:
        connection.execute(
            f"INSERT INTO housing_candidates({_COLUMNS}) VALUES({','.join('?' for _ in range(17))})",
            (
                row["candidate_id"], row["name"], row["deposit"], row["monthly_rent"],
                row["maintenance_fee"], int(row["maintenance_fee_provided"]), row["total_monthly_cost"],
                row["commute_minutes"], int(row["parking_available"]), row["options_memo"],
                row["special_notes"], row["score"], row["grade"],
                json.dumps(row["deductions"], sort_keys=True), row["status"], row["created_at"], row["updated_at"],
            ),
        )
