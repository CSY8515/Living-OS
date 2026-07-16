from __future__ import annotations

from collections import Counter
from typing import Any

from subsystems.housing.engines.candidate import HousingCandidateEngine
from subsystems.housing.engines.comparison import HousingComparisonEngine


class HousingReportEngine:
    def __init__(self, candidates: HousingCandidateEngine, comparison: HousingComparisonEngine) -> None:
        self.candidates = candidates
        self.comparison = comparison

    def status(self) -> dict[str, Any]:
        rows = self.candidates.list()
        ranking = self.comparison.rank()
        if not rows:
            return {
                "candidate_count": 0,
                "best_candidate": None,
                "average_score": 0.0,
                "average_monthly_cost": 0,
                "grade_distribution": {},
                "status_distribution": {},
                "ranking": [],
                "next_actions": ["Add a Housing candidate before comparing options."],
            }
        selected = [row for row in rows if row["status"] == "selected"]
        shortlisted = [row for row in rows if row["status"] == "shortlisted"]
        actions: list[str] = []
        if not shortlisted and not selected:
            actions.append("Shortlist the candidates that merit detailed review.")
        if shortlisted and not selected:
            actions.append("Review the leading shortlisted candidate before selection.")
        if selected:
            actions.append("Verify costs and contract details for the selected candidate.")
        return {
            "candidate_count": len(rows),
            "best_candidate": ranking[0],
            "average_score": round(sum(row["score"] for row in rows) / len(rows), 1),
            "average_monthly_cost": round(sum(row["total_monthly_cost"] for row in rows) / len(rows)),
            "grade_distribution": dict(sorted(Counter(row["grade"] for row in rows).items())),
            "status_distribution": dict(sorted(Counter(row["status"] for row in rows).items())),
            "ranking": ranking,
            "next_actions": actions,
        }
