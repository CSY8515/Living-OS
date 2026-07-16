from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from subsystems.food.engines.ingredient import IngredientEngine
from subsystems.food.engines.storage import FoodStorageEngine
from subsystems.food.engines.validation import (
    UNITS,
    decimal_string,
    instructions_json,
    require_choice,
    require_positive_integer,
    require_text,
    utc_now_iso,
)


class RecipeEngine:
    def __init__(self, store: FoodStorageEngine, ingredients: IngredientEngine) -> None:
        self.store = store
        self.ingredients = ingredients

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        result = dict(row)
        result["instructions"] = json.loads(result.pop("instructions_json"))
        return result

    def create(self, name: Any, servings: Any, instructions: Any = ()) -> dict[str, Any]:
        now = utc_now_iso()
        row = {
            "recipe_id": str(uuid4()),
            "name": require_text(name, "name", 200),
            "servings": require_positive_integer(servings, "servings"),
            "instructions_json": json.dumps(instructions_json(instructions), ensure_ascii=False),
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO food_recipes VALUES(?,?,?,?,?,?,?)",
                tuple(row.values()),
            )
        return self._public(row)

    def get(self, recipe_id: Any) -> dict[str, Any]:
        key = require_text(recipe_id, "recipe_id", 200)
        row = self.store.query_one("SELECT * FROM food_recipes WHERE recipe_id=?", (key,))
        if row is None:
            raise KeyError("Recipe not found.")
        result = self._public(row)
        result["ingredients"] = self.lines(key)
        return result

    def list(self, status: Any | None = None) -> list[dict[str, Any]]:
        if status is None:
            rows = self.store.query("SELECT * FROM food_recipes ORDER BY status,name,recipe_id")
        else:
            clean = require_choice(status, "status", {"active", "archived"})
            rows = self.store.query(
                "SELECT * FROM food_recipes WHERE status=? ORDER BY name,recipe_id", (clean,)
            )
        return [self._public(row) for row in rows]

    def update(self, recipe_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(recipe_id)
        allowed = {"name", "servings", "instructions", "status"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Recipe fields: {sorted(unexpected)}")
        instructions = instructions_json(changes.get("instructions", current["instructions"]))
        row = {
            "recipe_id": current["recipe_id"],
            "name": require_text(changes.get("name", current["name"]), "name", 200),
            "servings": require_positive_integer(changes.get("servings", current["servings"]), "servings"),
            "instructions_json": json.dumps(instructions, ensure_ascii=False),
            "status": require_choice(
                changes.get("status", current["status"]), "status", {"active", "archived"}
            ),
            "created_at": current["created_at"],
            "updated_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE food_recipes SET name=?,servings=?,instructions_json=?,status=?,updated_at=?
                WHERE recipe_id=?""",
                (row["name"], row["servings"], row["instructions_json"], row["status"],
                 row["updated_at"], row["recipe_id"]),
            )
        return self.get(recipe_id)

    def archive(self, recipe_id: Any) -> dict[str, Any]:
        return self.update(recipe_id, status="archived")

    def lines(self, recipe_id: Any) -> list[dict[str, Any]]:
        key = require_text(recipe_id, "recipe_id", 200)
        return self.store.query(
            """SELECT ri.recipe_id,ri.line_order,ri.ingredient_id,ri.quantity,ri.unit,
            i.name AS ingredient_name,i.base_quantity,i.unit AS base_unit,
            i.calories,i.protein,i.carbohydrate,i.fat,i.status AS ingredient_status
            FROM food_recipe_ingredients ri JOIN food_ingredients i ON i.ingredient_id=ri.ingredient_id
            WHERE ri.recipe_id=? ORDER BY ri.line_order""",
            (key,),
        )

    def set_ingredients(self, recipe_id: Any, lines: Any) -> list[dict[str, Any]]:
        recipe_key = require_text(recipe_id, "recipe_id", 200)
        self.get(recipe_key)
        if not isinstance(lines, (list, tuple)):
            raise ValueError("ingredients must be a list of recipe lines.")
        if len(lines) > 500:
            raise ValueError("ingredients must contain at most 500 lines.")
        validated: list[tuple[str, int, str, str, str]] = []
        for index, line in enumerate(lines):
            if not isinstance(line, dict):
                raise ValueError("Each recipe ingredient must be a mapping.")
            unexpected = set(line) - {"ingredient_id", "quantity", "unit"}
            if unexpected:
                raise ValueError(f"Unsupported recipe ingredient fields: {sorted(unexpected)}")
            ingredient_id = require_text(line.get("ingredient_id"), "ingredient_id", 200)
            self.ingredients.get(ingredient_id)
            validated.append((
                recipe_key,
                index,
                ingredient_id,
                decimal_string(line.get("quantity"), "quantity", positive=True),
                require_choice(line.get("unit"), "unit", UNITS),
            ))
        with self.store.transaction() as connection:
            connection.execute("DELETE FROM food_recipe_ingredients WHERE recipe_id=?", (recipe_key,))
            connection.executemany(
                """INSERT INTO food_recipe_ingredients(
                recipe_id,line_order,ingredient_id,quantity,unit) VALUES(?,?,?,?,?)""",
                validated,
            )
        return self.lines(recipe_key)
