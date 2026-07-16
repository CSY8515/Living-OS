from __future__ import annotations

import ast
import sqlite3
import tempfile
import unittest
from pathlib import Path

import subsystems.food as food_package
from subsystems.food import FoodSubsystem
from subsystems.operations.engines.catalog import V15_STABLE_MANIFESTS, V16_STABLE_MANIFESTS


class FoodSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "food.sqlite3"
        self.food = FoodSubsystem(self.root, self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def ingredient(self, name: str = "Rice", unit: str = "g") -> dict[str, object]:
        return self.food.create_ingredient(
            name, "grain", "100", unit,
            {"calories": "130", "protein": "2.7", "carbohydrate": "28", "fat": "0.3"},
        )

    def recipe(self, ingredient: dict[str, object] | None = None) -> dict[str, object]:
        item = ingredient or self.ingredient()
        recipe = self.food.create_recipe("Rice Bowl", 2, ["Cook rice", "Serve"])
        self.food.set_recipe_ingredients(recipe["recipe_id"], [{
            "ingredient_id": item["ingredient_id"], "quantity": "200", "unit": item["unit"],
        }])
        return recipe

    def test_public_interface_lazy_storage_and_manifest(self) -> None:
        self.assertEqual(food_package.__all__, ["FoodSubsystem"])
        self.assertFalse(self.database.exists())
        self.assertEqual(self.food.health()["status"], "ready")
        self.assertEqual(self.food.list_ingredients(), [])
        self.assertEqual(self.food.list_recipes(), [])
        self.assertEqual(self.food.food_report()["meal_count"], 0)
        self.assertEqual(self.food.export_snapshot()["ingredients"], [])
        self.assertFalse(self.database.exists())
        manifest = self.food.interface_manifest()
        self.assertEqual(manifest["living_os_compatibility"], ">=1.6,<2.0")
        self.assertEqual(manifest["capabilities"], (
            "ingredient-catalog", "recipe", "cooking-record",
            "meal-record", "nutrition-summary", "food-report",
        ))
        second = FoodSubsystem(self.root, self.root / "second.sqlite3")
        self.ingredient()
        self.assertEqual(second.list_ingredients(), [])

    def test_ingredient_lifecycle_validation_filtering_and_decimal_persistence(self) -> None:
        item = self.ingredient()
        self.assertEqual(item["base_quantity"], "100")
        self.assertEqual(item["protein"], "2.7")
        self.assertEqual(self.food.get_ingredient(item["ingredient_id"])["name"], "Rice")
        updated = self.food.update_ingredient(
            item["ingredient_id"], category="staple", base_quantity="100.000",
            nutrition={"calories": 131, "protein": 2.8, "carbohydrate": 28, "fat": 0.4},
        )
        self.assertEqual(updated["base_quantity"], "100")
        self.assertEqual(len(self.food.list_ingredients(category="staple")), 1)
        self.assertEqual(self.food.archive_ingredient(item["ingredient_id"])["status"], "archived")
        self.assertEqual(self.food.list_ingredients("active"), [])
        with self.assertRaises(ValueError):
            self.food.create_ingredient("", "", 1, "g")
        with self.assertRaises(ValueError):
            self.food.create_ingredient("Invalid", "", "1.0001", "g")
        with self.assertRaises(ValueError):
            self.food.create_ingredient("Invalid", "", 1, "cup")
        with self.assertRaises(ValueError):
            self.food.update_ingredient(item["ingredient_id"], unsupported=True)

    def test_recipe_lifecycle_ordered_lines_units_and_transaction_rollback(self) -> None:
        rice = self.ingredient()
        salt = self.food.create_ingredient("Salt", "seasoning", 1, "g")
        recipe = self.food.create_recipe("Rice Bowl", 2, ["Cook", "Season"])
        lines = self.food.set_recipe_ingredients(recipe["recipe_id"], [
            {"ingredient_id": rice["ingredient_id"], "quantity": 200, "unit": "g"},
            {"ingredient_id": salt["ingredient_id"], "quantity": 1, "unit": "g"},
        ])
        self.assertEqual([row["line_order"] for row in lines], [0, 1])
        self.assertEqual(self.food.get_recipe(recipe["recipe_id"])["instructions"], ["Cook", "Season"])
        with self.assertRaises(KeyError):
            self.food.set_recipe_ingredients(recipe["recipe_id"], [
                {"ingredient_id": rice["ingredient_id"], "quantity": 100, "unit": "g"},
                {"ingredient_id": "missing", "quantity": 1, "unit": "g"},
            ])
        self.assertEqual(len(self.food.get_recipe(recipe["recipe_id"])["ingredients"]), 2)
        updated = self.food.update_recipe(recipe["recipe_id"], servings=4, instructions=["Cook slowly"])
        self.assertEqual(updated["servings"], 4)
        self.assertEqual(self.food.archive_recipe(recipe["recipe_id"])["status"], "archived")
        with self.assertRaises(ValueError):
            self.food.create_recipe("Invalid", 0, [])

    def test_cooking_meals_linkage_filters_and_invalid_references(self) -> None:
        first = self.recipe()
        second = self.food.create_recipe("Second", 1, [])
        cooked = self.food.record_cooking(first["recipe_id"], "2026-07-10", 4, "Batch")
        linked = self.food.record_meal(
            "2026-07-11", "dinner", "1.5", cooking_id=cooked["cooking_id"]
        )
        self.assertEqual(linked["recipe_id"], first["recipe_id"])
        self.food.record_meal("2026-07-12", "snack", 1, note="Unlinked")
        self.assertEqual(len(self.food.list_cooking_records("2026-07-01", "2026-07-31")), 1)
        self.assertEqual(len(self.food.list_meals(meal_type="dinner")), 1)
        with self.assertRaises(ValueError):
            self.food.record_meal(
                "2026-07-12", "lunch", 1, recipe_id=second["recipe_id"],
                cooking_id=cooked["cooking_id"],
            )
        with self.assertRaises(KeyError):
            self.food.record_cooking("missing", "2026-07-12", 1)
        with self.assertRaises(ValueError):
            self.food.record_meal("2026-07-12", "invalid", 1)

    def test_deterministic_nutrition_incomplete_disclosure_and_no_conversion(self) -> None:
        rice = self.ingredient()
        recipe = self.recipe(rice)
        nutrition = self.food.recipe_nutrition(recipe["recipe_id"])
        self.assertTrue(nutrition["complete"])
        self.assertEqual(nutrition["totals"]["calories"], "260")
        self.assertEqual(nutrition["per_serving"]["protein"], "2.7")
        meal = self.food.record_meal("2026-07-16", "dinner", "1.5", recipe["recipe_id"])
        self.assertEqual(self.food.meal_nutrition(meal["meal_id"])["totals"]["calories"], "195")
        override = self.food.record_meal(
            "2026-07-16", "snack", 1,
            nutrition_override={"calories": 10, "protein": 1, "carbohydrate": 2, "fat": 0},
        )
        self.assertEqual(self.food.meal_nutrition(override["meal_id"])["source"], "explicit-override")
        self.food.set_recipe_ingredients(recipe["recipe_id"], [{
            "ingredient_id": rice["ingredient_id"], "quantity": 1, "unit": "kg",
        }])
        incomplete = self.food.recipe_nutrition(recipe["recipe_id"])
        self.assertFalse(incomplete["complete"])
        self.assertIn("unit-mismatch", incomplete["missing_lines"][0]["reasons"])
        self.assertIsNone(incomplete["totals"])

    def test_reports_export_integrity_health_and_transactional_failure(self) -> None:
        recipe = self.recipe()
        cooked = self.food.record_cooking(recipe["recipe_id"], "2026-07-10", 2)
        self.food.record_meal("2026-07-11", "dinner", 1, cooking_id=cooked["cooking_id"])
        self.food.record_meal("2026-07-12", "snack", 1)
        report = self.food.food_report("2026-07-01", "2026-07-31")
        self.assertEqual(report["meal_count"], 2)
        self.assertEqual(report["cooking_count"], 1)
        self.assertEqual(report["recipe_frequency"][0]["meal_count"], 1)
        self.assertEqual(report["nutrition"]["complete_meal_count"], 1)
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()
        self.assertEqual(self.food.health()["status"], "healthy")
        snapshot = self.food.export_snapshot()
        self.assertEqual(len(snapshot["ingredients"]), 1)
        self.assertEqual(len(snapshot["meals"]), 2)

    def test_privacy_manifest_separation_and_domain_boundaries(self) -> None:
        self.assertNotIn("food", {item.module_id for item in V15_STABLE_MANIFESTS})
        manifest = next(item for item in V16_STABLE_MANIFESTS if item.module_id == "food")
        self.assertEqual(manifest.privacy_class, "sensitive")
        self.assertEqual(V16_STABLE_MANIFESTS[:-1], V15_STABLE_MANIFESTS)
        repository = Path(__file__).resolve().parent.parent
        self.assertIn("data/food/", (repository / ".gitignore").read_text(encoding="utf-8"))
        forbidden = {"foundation", "operations", "insight", "compatibility", "finance",
                     "health", "housing", "vehicle"}
        violations: list[str] = []
        for path in (repository / "subsystems" / "food").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if module and module.startswith("subsystems.") and module.split(".")[1] in forbidden:
                    violations.append(str(path.relative_to(repository)))
        self.assertEqual(violations, [])
        engine_imports: list[str] = []
        for path in (repository / "subsystems").rglob("*.py"):
            if path.is_relative_to(repository / "subsystems" / "food"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (isinstance(node, ast.ImportFrom) and node.module
                        and node.module.startswith("subsystems.food.engines")):
                    engine_imports.append(str(path.relative_to(repository)))
        self.assertEqual(engine_imports, [])


if __name__ == "__main__":
    unittest.main()
