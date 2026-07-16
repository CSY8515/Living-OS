from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.food.engines.cooking import CookingEngine
from subsystems.food.engines.recipe import RecipeEngine
from subsystems.food.engines.storage import FoodStorageEngine
from subsystems.food.engines.validation import (
    MEAL_TYPES,
    NUTRIENTS,
    decimal_string,
    nutrition_values,
    optional_identifier,
    optional_text,
    require_choice,
    require_date,
    require_text,
    utc_now_iso,
)


class MealEngine:
    def __init__(self, store: FoodStorageEngine, recipes: RecipeEngine,
                 cooking: CookingEngine) -> None:
        self.store = store
        self.recipes = recipes
        self.cooking = cooking

    def record(self, eaten_on: Any, meal_type: Any, servings_consumed: Any,
               recipe_id: Any = None, cooking_id: Any = None,
               nutrition_override: Any = None, note: Any = "") -> dict[str, Any]:
        recipe_key = optional_identifier(recipe_id, "recipe_id")
        cooking_key = optional_identifier(cooking_id, "cooking_id")
        if recipe_key is not None:
            self.recipes.get(recipe_key)
        if cooking_key is not None:
            cooking_record = self.cooking.get(cooking_key)
            if recipe_key is not None and cooking_record["recipe_id"] != recipe_key:
                raise ValueError("cooking_id does not belong to recipe_id.")
            recipe_key = cooking_record["recipe_id"]
        nutrients = nutrition_values(nutrition_override)
        row = {
            "meal_id": str(uuid4()),
            "eaten_on": require_date(eaten_on, "eaten_on"),
            "meal_type": require_choice(meal_type, "meal_type", MEAL_TYPES),
            "recipe_id": recipe_key,
            "cooking_id": cooking_key,
            "servings_consumed": decimal_string(
                servings_consumed, "servings_consumed", positive=True
            ),
            **nutrients,
            "note": optional_text(note, "note"),
            "created_at": utc_now_iso(),
        }
        columns = tuple(row)
        with self.store.transaction() as connection:
            connection.execute(
                f"INSERT INTO food_meals({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
                tuple(row[column] for column in columns),
            )
        return row

    def get(self, meal_id: Any) -> dict[str, Any]:
        key = require_text(meal_id, "meal_id", 200)
        row = self.store.query_one("SELECT * FROM food_meals WHERE meal_id=?", (key,))
        if row is None:
            raise KeyError("Meal not found.")
        return row

    def list(self, start_on: Any = None, end_on: Any = None,
             meal_type: Any = None, recipe_id: Any = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[Any] = []
        if start_on is not None:
            clauses.append("eaten_on>=?")
            parameters.append(require_date(start_on, "start_on"))
        if end_on is not None:
            clauses.append("eaten_on<=?")
            parameters.append(require_date(end_on, "end_on"))
        if meal_type is not None:
            clauses.append("meal_type=?")
            parameters.append(require_choice(meal_type, "meal_type", MEAL_TYPES))
        if recipe_id is not None:
            clauses.append("recipe_id=?")
            parameters.append(require_text(recipe_id, "recipe_id", 200))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self.store.query(
            "SELECT * FROM food_meals" + where + " ORDER BY eaten_on,created_at,meal_id",
            tuple(parameters),
        )

    @staticmethod
    def explicit_nutrition(row: dict[str, Any]) -> dict[str, str | None]:
        return {name: row[name] for name in NUTRIENTS}
