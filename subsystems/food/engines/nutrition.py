from __future__ import annotations

from decimal import Decimal
from typing import Any

from subsystems.food.engines.meal import MealEngine
from subsystems.food.engines.recipe import RecipeEngine
from subsystems.food.engines.validation import NUTRIENTS


def _format(number: Decimal) -> str:
    text = format(number.quantize(Decimal("0.001")).normalize(), "f")
    return "0" if text in {"-0", ""} else text


class NutritionEngine:
    def __init__(self, recipes: RecipeEngine, meals: MealEngine) -> None:
        self.recipes = recipes
        self.meals = meals

    def recipe(self, recipe_id: Any) -> dict[str, Any]:
        recipe = self.recipes.get(recipe_id)
        lines = recipe["ingredients"]
        totals = {name: Decimal("0") for name in NUTRIENTS}
        missing: list[dict[str, Any]] = []
        for line in lines:
            reasons: list[str] = []
            if line["unit"] != line["base_unit"]:
                reasons.append("unit-mismatch")
            absent = [name for name in NUTRIENTS if line[name] is None]
            if absent:
                reasons.append("missing-nutrition:" + ",".join(absent))
            if reasons:
                missing.append({
                    "line_order": line["line_order"],
                    "ingredient_id": line["ingredient_id"],
                    "reasons": tuple(reasons),
                })
                continue
            ratio = Decimal(line["quantity"]) / Decimal(line["base_quantity"])
            for name in NUTRIENTS:
                totals[name] += Decimal(line[name]) * ratio
        complete = bool(lines) and not missing
        servings = Decimal(str(recipe["servings"]))
        return {
            "recipe_id": recipe["recipe_id"],
            "recipe_name": recipe["name"],
            "servings": recipe["servings"],
            "complete": complete,
            "owner_entered_only": True,
            "missing_lines": missing,
            "totals": {name: _format(value) for name, value in totals.items()} if complete else None,
            "per_serving": {
                name: _format(value / servings) for name, value in totals.items()
            } if complete else None,
        }

    def meal(self, meal_id: Any) -> dict[str, Any]:
        meal = self.meals.get(meal_id)
        explicit = self.meals.explicit_nutrition(meal)
        if any(value is not None for value in explicit.values()):
            complete = all(value is not None for value in explicit.values())
            return {
                "meal_id": meal["meal_id"],
                "source": "explicit-override",
                "complete": complete,
                "owner_entered_only": True,
                "totals": explicit if complete else None,
                "missing_fields": [name for name, value in explicit.items() if value is None],
            }
        if meal["recipe_id"] is None:
            return {
                "meal_id": meal["meal_id"], "source": "unavailable", "complete": False,
                "owner_entered_only": True, "totals": None,
                "missing_fields": list(NUTRIENTS),
            }
        recipe = self.recipe(meal["recipe_id"])
        if not recipe["complete"]:
            return {
                "meal_id": meal["meal_id"], "source": "recipe", "complete": False,
                "owner_entered_only": True, "totals": None,
                "missing_fields": list(NUTRIENTS), "recipe_nutrition": recipe,
            }
        servings = Decimal(meal["servings_consumed"])
        totals = {
            name: _format(Decimal(recipe["per_serving"][name]) * servings)
            for name in NUTRIENTS
        }
        return {
            "meal_id": meal["meal_id"], "source": "recipe", "complete": True,
            "owner_entered_only": True, "totals": totals, "missing_fields": [],
            "recipe_id": meal["recipe_id"],
        }
