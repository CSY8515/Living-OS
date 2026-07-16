from __future__ import annotations

from typing import Any

from subsystems.housing.engines.validation import (
    optional_text,
    require_boolean,
    require_non_negative_integer,
    require_text,
)


def monthly_cost_deduction(total_monthly_cost: int) -> int:
    if total_monthly_cost <= 500_000:
        return 0
    if total_monthly_cost <= 700_000:
        return 5
    if total_monthly_cost <= 900_000:
        return 10
    if total_monthly_cost <= 1_100_000:
        return 15
    return min(30, 20 + ((total_monthly_cost - 1_100_000) // 200_000) * 5)


def commute_deduction(commute_minutes: int) -> int:
    if commute_minutes <= 20:
        return 0
    if commute_minutes <= 40:
        return 5
    if commute_minutes <= 60:
        return 10
    return 20


def housing_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "D"


class HousingScoringEngine:
    def calculate(
        self,
        name: Any,
        deposit: Any,
        monthly_rent: Any,
        maintenance_fee: Any,
        maintenance_fee_provided: Any,
        commute_minutes: Any,
        parking_available: Any,
        options_memo: Any = "",
        special_notes: Any = "",
    ) -> dict[str, Any]:
        clean_name = require_text(name, "name", 200)
        clean_deposit = require_non_negative_integer(deposit, "deposit")
        clean_rent = require_non_negative_integer(monthly_rent, "monthly_rent")
        fee_provided = require_boolean(maintenance_fee_provided, "maintenance_fee_provided")
        clean_maintenance = require_non_negative_integer(maintenance_fee, "maintenance_fee") if fee_provided else 0
        clean_commute = require_non_negative_integer(commute_minutes, "commute_minutes", 1440)
        parking = require_boolean(parking_available, "parking_available")
        total_monthly_cost = clean_rent + clean_maintenance
        deductions = {
            "monthly_cost": monthly_cost_deduction(total_monthly_cost),
            "commute": commute_deduction(clean_commute),
            "parking": 0 if parking else 10,
            "missing_maintenance_fee": 0 if fee_provided else 5,
        }
        score = max(0, 100 - sum(deductions.values()))
        return {
            "name": clean_name,
            "deposit": clean_deposit,
            "monthly_rent": clean_rent,
            "maintenance_fee": clean_maintenance,
            "maintenance_fee_provided": fee_provided,
            "total_monthly_cost": total_monthly_cost,
            "commute_minutes": clean_commute,
            "parking_available": parking,
            "options_memo": optional_text(options_memo, "options_memo"),
            "special_notes": optional_text(special_notes, "special_notes"),
            "score": score,
            "grade": housing_grade(score),
            "deductions": deductions,
        }
