from __future__ import annotations

from pathlib import Path
from typing import Any

from subsystems.food.engines.cooking import CookingEngine
from subsystems.food.engines.ingredient import IngredientEngine
from subsystems.food.engines.meal import MealEngine
from subsystems.food.engines.nutrition import NutritionEngine
from subsystems.food.engines.recipe import RecipeEngine
from subsystems.food.engines.report import FoodReportEngine
from subsystems.food.engines.storage import FoodStorageEngine


class FoodSubsystem:
    """The only supported Living OS boundary for Food Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.6,<2.0"
    PRIVACY_CLASS = "sensitive"

    def __init__(self, root: Path, database_path: Path | None = None) -> None:
        self.root = Path(root)
        path = (Path(database_path) if database_path is not None
                else self.root / "data" / "food" / "food.sqlite3")
        store = FoodStorageEngine(path)
        ingredients = IngredientEngine(store)
        recipes = RecipeEngine(store, ingredients)
        cooking = CookingEngine(store, recipes)
        meals = MealEngine(store, recipes, cooking)
        nutrition = NutritionEngine(recipes, meals)
        report = FoodReportEngine(recipes, cooking, meals, nutrition)
        self._store, self._ingredients, self._recipes = store, ingredients, recipes
        self._cooking, self._meals, self._nutrition, self._report = cooking, meals, nutrition, report

    @property
    def database_path(self) -> Path:
        return self._store.database_path

    def health(self) -> dict[str, Any]:
        return {**self._store.health(), "subsystem": "food", "version": self.VERSION,
                "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
                "privacy_class": self.PRIVACY_CLASS}

    def interface_manifest(self) -> dict[str, Any]:
        return {
            "subsystem": "food", "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
            "privacy_class": self.PRIVACY_CLASS,
            "capabilities": ("ingredient-catalog", "recipe", "cooking-record",
                             "meal-record", "nutrition-summary", "food-report"),
        }

    def create_ingredient(self, name: Any, category: Any, base_quantity: Any,
                          unit: Any, nutrition: Any = None) -> dict[str, Any]:
        return self._ingredients.create(name, category, base_quantity, unit, nutrition)

    def get_ingredient(self, ingredient_id: Any) -> dict[str, Any]:
        return self._ingredients.get(ingredient_id)

    def list_ingredients(self, status: Any = None, category: Any = None) -> list[dict[str, Any]]:
        return self._ingredients.list(status, category)

    def update_ingredient(self, ingredient_id: Any, **changes: Any) -> dict[str, Any]:
        return self._ingredients.update(ingredient_id, **changes)

    def archive_ingredient(self, ingredient_id: Any) -> dict[str, Any]:
        return self._ingredients.archive(ingredient_id)

    def create_recipe(self, name: Any, servings: Any, instructions: Any = ()) -> dict[str, Any]:
        return self._recipes.create(name, servings, instructions)

    def get_recipe(self, recipe_id: Any) -> dict[str, Any]:
        return self._recipes.get(recipe_id)

    def list_recipes(self, status: Any = None) -> list[dict[str, Any]]:
        return self._recipes.list(status)

    def update_recipe(self, recipe_id: Any, **changes: Any) -> dict[str, Any]:
        return self._recipes.update(recipe_id, **changes)

    def archive_recipe(self, recipe_id: Any) -> dict[str, Any]:
        return self._recipes.archive(recipe_id)

    def set_recipe_ingredients(self, recipe_id: Any, ingredients: Any) -> list[dict[str, Any]]:
        return self._recipes.set_ingredients(recipe_id, ingredients)

    def record_cooking(self, recipe_id: Any, cooked_on: Any, servings_produced: Any,
                       note: Any = "") -> dict[str, Any]:
        return self._cooking.record(recipe_id, cooked_on, servings_produced, note)

    def list_cooking_records(self, start_on: Any = None, end_on: Any = None,
                             recipe_id: Any = None) -> list[dict[str, Any]]:
        return self._cooking.list(start_on, end_on, recipe_id)

    def record_meal(self, eaten_on: Any, meal_type: Any, servings_consumed: Any,
                    recipe_id: Any = None, cooking_id: Any = None,
                    nutrition_override: Any = None, note: Any = "") -> dict[str, Any]:
        return self._meals.record(
            eaten_on, meal_type, servings_consumed, recipe_id, cooking_id,
            nutrition_override, note,
        )

    def list_meals(self, start_on: Any = None, end_on: Any = None,
                   meal_type: Any = None, recipe_id: Any = None) -> list[dict[str, Any]]:
        return self._meals.list(start_on, end_on, meal_type, recipe_id)

    def recipe_nutrition(self, recipe_id: Any) -> dict[str, Any]:
        return self._nutrition.recipe(recipe_id)

    def meal_nutrition(self, meal_id: Any) -> dict[str, Any]:
        return self._nutrition.meal(meal_id)

    def food_report(self, start_on: Any = None, end_on: Any = None) -> dict[str, Any]:
        return self._report.report(start_on, end_on)

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
