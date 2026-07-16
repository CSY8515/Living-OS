from __future__ import annotations

from typing import Any

from subsystems.housing.engines.candidate import HousingCandidateEngine


class HousingComparisonEngine:
    def __init__(self, candidates: HousingCandidateEngine) -> None:
        self.candidates = candidates

    def rank(self, status: Any | None = None) -> list[dict[str, Any]]:
        rows = self.candidates.list(status)
        return [
            {
                "rank": index,
                "candidate_id": row["candidate_id"],
                "name": row["name"],
                "score": row["score"],
                "grade": row["grade"],
                "deposit": row["deposit"],
                "total_monthly_cost": row["total_monthly_cost"],
                "commute_minutes": row["commute_minutes"],
                "status": row["status"],
                "deductions": row["deductions"],
            }
            for index, row in enumerate(rows, start=1)
        ]
