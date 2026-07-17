from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.food.engines.validation import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1


class FoodStorageEngine(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(
            database_path,
            component_id="SUB-FOOD",
            display_name="Food Subsystem",
            foundation=foundation,
        )

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            statements = (
                "CREATE TABLE IF NOT EXISTS food_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)",
                """CREATE TABLE IF NOT EXISTS food_ingredients (
                    ingredient_id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
                    base_quantity TEXT NOT NULL, unit TEXT NOT NULL,
                    calories TEXT, protein TEXT, carbohydrate TEXT, fat TEXT,
                    status TEXT NOT NULL CHECK(status IN ('active','archived')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""",
                """CREATE TABLE IF NOT EXISTS food_recipes (
                    recipe_id TEXT PRIMARY KEY, name TEXT NOT NULL, servings INTEGER NOT NULL CHECK(servings > 0),
                    instructions_json TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('active','archived')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""",
                """CREATE TABLE IF NOT EXISTS food_recipe_ingredients (
                    recipe_id TEXT NOT NULL, line_order INTEGER NOT NULL CHECK(line_order >= 0),
                    ingredient_id TEXT NOT NULL, quantity TEXT NOT NULL, unit TEXT NOT NULL,
                    PRIMARY KEY(recipe_id,line_order),
                    FOREIGN KEY(recipe_id) REFERENCES food_recipes(recipe_id),
                    FOREIGN KEY(ingredient_id) REFERENCES food_ingredients(ingredient_id))""",
                """CREATE TABLE IF NOT EXISTS food_cooking_records (
                    cooking_id TEXT PRIMARY KEY, recipe_id TEXT NOT NULL, cooked_on TEXT NOT NULL,
                    servings_produced INTEGER NOT NULL CHECK(servings_produced > 0),
                    note TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(recipe_id) REFERENCES food_recipes(recipe_id))""",
                """CREATE TABLE IF NOT EXISTS food_meals (
                    meal_id TEXT PRIMARY KEY, eaten_on TEXT NOT NULL,
                    meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast','lunch','dinner','snack','other')),
                    recipe_id TEXT, cooking_id TEXT, servings_consumed TEXT NOT NULL,
                    calories TEXT, protein TEXT, carbohydrate TEXT, fat TEXT,
                    note TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(recipe_id) REFERENCES food_recipes(recipe_id),
                    FOREIGN KEY(cooking_id) REFERENCES food_cooking_records(cooking_id))""",
                "CREATE INDEX IF NOT EXISTS ix_food_ingredient_status ON food_ingredients(status,name)",
                "CREATE INDEX IF NOT EXISTS ix_food_recipe_status ON food_recipes(status,name)",
                "CREATE INDEX IF NOT EXISTS ix_food_cooking_date ON food_cooking_records(cooked_on,recipe_id)",
                "CREATE INDEX IF NOT EXISTS ix_food_meal_date ON food_meals(eaten_on,meal_type)",
            )
            for statement in statements:
                connection.execute(statement)
            now = utc_now_iso()
            for key, value in (("schema_version", str(SCHEMA_VERSION)), ("subsystem_version", "1.0.0")):
                connection.execute(
                    """INSERT INTO food_meta(key,value,updated_at) VALUES(?,?,?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                    (key, value, now),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        self.register_contract(schema_version=SCHEMA_VERSION, migration_id="food-schema-v1")

    def query(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        connection = self._connect()
        try:
            return [dict(row) for row in connection.execute(sql, parameters).fetchall()]
        finally:
            connection.close()

    def query_one(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        if not self.initialized:
            return None
        connection = self._connect()
        try:
            row = connection.execute(sql, parameters).fetchone()
            return dict(row) if row is not None else None
        finally:
            connection.close()

    def export_snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "ingredients": self.query("SELECT * FROM food_ingredients ORDER BY name,ingredient_id"),
            "recipes": self.query("SELECT * FROM food_recipes ORDER BY name,recipe_id"),
            "recipe_ingredients": self.query(
                "SELECT * FROM food_recipe_ingredients ORDER BY recipe_id,line_order"
            ),
            "cooking_records": self.query(
                "SELECT * FROM food_cooking_records ORDER BY cooked_on,cooking_id"
            ),
            "meals": self.query("SELECT * FROM food_meals ORDER BY eaten_on,meal_id"),
        }

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "ready", "initialized": False, "schema_version": SCHEMA_VERSION}
        row = self.query_one("PRAGMA integrity_check")
        healthy = bool(row) and next(iter(row.values())) == "ok"
        return {
            "status": "healthy" if healthy else "degraded",
            "initialized": True,
            "schema_version": SCHEMA_VERSION,
            "database_path": str(self.database_path),
        }
