from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.food.engines.recipe import RecipeEngine
from subsystems.food.engines.storage import FoodStorageEngine
from subsystems.food.engines.validation import (
    optional_text,
    require_date,
    require_positive_integer,
    require_text,
    utc_now_iso,
)


class CookingEngine:
    def __init__(self, store: FoodStorageEngine, recipes: RecipeEngine) -> None:
        self.store = store
        self.recipes = recipes

    def record(self, recipe_id: Any, cooked_on: Any, servings_produced: Any,
               note: Any = "") -> dict[str, Any]:
        key = require_text(recipe_id, "recipe_id", 200)
        self.recipes.get(key)
        row = {
            "cooking_id": str(uuid4()),
            "recipe_id": key,
            "cooked_on": require_date(cooked_on, "cooked_on"),
            "servings_produced": require_positive_integer(servings_produced, "servings_produced"),
            "note": optional_text(note, "note"),
            "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute("INSERT INTO food_cooking_records VALUES(?,?,?,?,?,?)", tuple(row.values()))
        return row

    def get(self, cooking_id: Any) -> dict[str, Any]:
        key = require_text(cooking_id, "cooking_id", 200)
        row = self.store.query_one("SELECT * FROM food_cooking_records WHERE cooking_id=?", (key,))
        if row is None:
            raise KeyError("Cooking record not found.")
        return row

    def list(self, start_on: Any = None, end_on: Any = None,
             recipe_id: Any = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[Any] = []
        if start_on is not None:
            clauses.append("cooked_on>=?")
            parameters.append(require_date(start_on, "start_on"))
        if end_on is not None:
            clauses.append("cooked_on<=?")
            parameters.append(require_date(end_on, "end_on"))
        if recipe_id is not None:
            clauses.append("recipe_id=?")
            parameters.append(require_text(recipe_id, "recipe_id", 200))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self.store.query(
            "SELECT * FROM food_cooking_records" + where + " ORDER BY cooked_on,created_at,cooking_id",
            tuple(parameters),
        )

    def update(self, cooking_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(cooking_id)
        allowed = {"recipe_id", "cooked_on", "servings_produced", "note"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported cooking fields: {sorted(unexpected)}")
        recipe_id = require_text(changes.get("recipe_id", current["recipe_id"]), "recipe_id", 200)
        self.recipes.get(recipe_id)
        with self.store.transaction() as connection:
            connection.execute(
                "UPDATE food_cooking_records SET recipe_id=?,cooked_on=?,servings_produced=?,note=? WHERE cooking_id=?",
                (
                    recipe_id,
                    require_date(changes.get("cooked_on", current["cooked_on"]), "cooked_on"),
                    require_positive_integer(changes.get("servings_produced", current["servings_produced"]), "servings_produced"),
                    optional_text(changes.get("note", current["note"]), "note"),
                    current["cooking_id"],
                ),
            )
        return self.get(current["cooking_id"])

    def delete(self, cooking_id: Any) -> bool:
        current = self.get(cooking_id)
        if self.store.query_one("SELECT meal_id FROM food_meals WHERE cooking_id=? LIMIT 1", (current["cooking_id"],)):
            raise ValueError("Cooking record is linked to a meal and cannot be deleted.")
        with self.store.transaction() as connection:
            cursor = connection.execute("DELETE FROM food_cooking_records WHERE cooking_id=?", (current["cooking_id"],))
        return cursor.rowcount == 1
