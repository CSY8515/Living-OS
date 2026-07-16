from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.food.engines.storage import FoodStorageEngine
from subsystems.food.engines.validation import (
    UNITS,
    decimal_string,
    nutrition_values,
    optional_text,
    require_choice,
    require_text,
    utc_now_iso,
)


class IngredientEngine:
    def __init__(self, store: FoodStorageEngine) -> None:
        self.store = store

    def create(self, name: Any, category: Any, base_quantity: Any, unit: Any,
               nutrition: Any = None) -> dict[str, Any]:
        now = utc_now_iso()
        nutrients = nutrition_values(nutrition)
        row = {
            "ingredient_id": str(uuid4()),
            "name": require_text(name, "name", 200),
            "category": optional_text(category, "category", 100),
            "base_quantity": decimal_string(base_quantity, "base_quantity", positive=True),
            "unit": require_choice(unit, "unit", UNITS),
            **nutrients,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        columns = tuple(row)
        with self.store.transaction() as connection:
            connection.execute(
                f"INSERT INTO food_ingredients({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
                tuple(row[column] for column in columns),
            )
        return row

    def get(self, ingredient_id: Any) -> dict[str, Any]:
        key = require_text(ingredient_id, "ingredient_id", 200)
        row = self.store.query_one("SELECT * FROM food_ingredients WHERE ingredient_id=?", (key,))
        if row is None:
            raise KeyError("Ingredient not found.")
        return row

    def list(self, status: Any | None = None, category: Any | None = None) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[Any] = []
        if status is not None:
            clauses.append("status=?")
            parameters.append(require_choice(status, "status", {"active", "archived"}))
        if category is not None:
            clauses.append("category=?")
            parameters.append(optional_text(category, "category", 100))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self.store.query(
            "SELECT * FROM food_ingredients" + where + " ORDER BY status,name,ingredient_id",
            tuple(parameters),
        )

    def update(self, ingredient_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(ingredient_id)
        allowed = {"name", "category", "base_quantity", "unit", "nutrition", "status"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Ingredient fields: {sorted(unexpected)}")
        nutrients = (
            nutrition_values(changes["nutrition"])
            if "nutrition" in changes
            else {name: current[name] for name in ("calories", "protein", "carbohydrate", "fat")}
        )
        row = {
            **current,
            "name": require_text(changes.get("name", current["name"]), "name", 200),
            "category": optional_text(changes.get("category", current["category"]), "category", 100),
            "base_quantity": decimal_string(
                changes.get("base_quantity", current["base_quantity"]), "base_quantity", positive=True
            ),
            "unit": require_choice(changes.get("unit", current["unit"]), "unit", UNITS),
            **nutrients,
            "status": require_choice(
                changes.get("status", current["status"]), "status", {"active", "archived"}
            ),
            "updated_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE food_ingredients SET name=?,category=?,base_quantity=?,unit=?,
                calories=?,protein=?,carbohydrate=?,fat=?,status=?,updated_at=? WHERE ingredient_id=?""",
                (row["name"], row["category"], row["base_quantity"], row["unit"],
                 row["calories"], row["protein"], row["carbohydrate"], row["fat"],
                 row["status"], row["updated_at"], row["ingredient_id"]),
            )
        return row

    def archive(self, ingredient_id: Any) -> dict[str, Any]:
        return self.update(ingredient_id, status="archived")
