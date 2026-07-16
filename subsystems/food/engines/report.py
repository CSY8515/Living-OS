from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any

from subsystems.food.engines.cooking import CookingEngine
from subsystems.food.engines.meal import MealEngine
from subsystems.food.engines.nutrition import NutritionEngine, _format
from subsystems.food.engines.recipe import RecipeEngine
from subsystems.food.engines.validation import NUTRIENTS


class FoodReportEngine:
    def __init__(self, recipes: RecipeEngine, cooking: CookingEngine,
                 meals: MealEngine, nutrition: NutritionEngine) -> None:
        self.recipes = recipes
        self.cooking = cooking
        self.meals = meals
        self.nutrition = nutrition

    def report(self, start_on: Any = None, end_on: Any = None) -> dict[str, Any]:
        meals = self.meals.list(start_on, end_on)
        cooking = self.cooking.list(start_on, end_on)
        recipe_names = {row["recipe_id"]: row["name"] for row in self.recipes.list()}
        frequency = Counter(
            row["recipe_id"] for row in meals if row["recipe_id"] is not None
        )
        nutrition_totals = {name: Decimal("0") for name in NUTRIENTS}
        sources = Counter()
        complete_count = 0
        for meal in meals:
            result = self.nutrition.meal(meal["meal_id"])
            sources[result["source"]] += 1
            if result["complete"]:
                complete_count += 1
                for name in NUTRIENTS:
                    nutrition_totals[name] += Decimal(result["totals"][name])
        return {
            "start_on": start_on,
            "end_on": end_on,
            "meal_count": len(meals),
            "cooking_count": len(cooking),
            "recipe_frequency": [
                {"recipe_id": key, "recipe_name": recipe_names.get(key, "Unknown"), "meal_count": count}
                for key, count in sorted(
                    frequency.items(), key=lambda item: (-item[1], recipe_names.get(item[0], ""), item[0])
                )
            ],
            "nutrition": {
                "complete_meal_count": complete_count,
                "incomplete_meal_count": len(meals) - complete_count,
                "source_counts": dict(sorted(sources.items())),
                "totals": {name: _format(value) for name, value in nutrition_totals.items()},
                "owner_entered_only": True,
            },
            "meals": meals,
            "cooking_records": cooking,
        }
