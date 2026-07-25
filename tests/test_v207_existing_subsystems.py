from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from subsystems.finance import FinanceSubsystem
from subsystems.food import FoodSubsystem
from subsystems.health import HealthSubsystem
from subsystems.housing import HousingSubsystem
from subsystems.vehicle import VehicleSubsystem


class ExistingSubsystemCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_finance_crud_archive_search_budget_and_dashboard(self) -> None:
        finance = FinanceSubsystem(self.root)
        income = finance.record_income(3_000_000, "Salary", "2026-07-01", "July salary")
        expense = finance.record_expense(120_000, "Food", "2026-07-02", "Groceries")
        updated = finance.update_transaction(expense["transaction_id"], amount=110_000)
        self.assertEqual(updated["amount"], 110_000)
        self.assertEqual(
            finance.list_transactions(search="groceries")[0]["transaction_id"],
            expense["transaction_id"],
        )
        self.assertEqual(
            finance.archive_transaction(expense["transaction_id"])["status"], "archived"
        )
        self.assertEqual(len(finance.list_transactions(status="archived")), 1)
        finance.restore_transaction(expense["transaction_id"])
        finance.upsert_budget("2026-07", "Food", 300_000)
        finance.upsert_budget("2026-07", "Food", 250_000)
        self.assertEqual(finance.list_budgets("2026-07")[0]["amount"], 250_000)
        dashboard = finance.dashboard("2026-07")
        self.assertEqual(dashboard["cash_flow"]["income"], 3_000_000)
        self.assertEqual(dashboard["cash_flow"]["expense"], 110_000)
        self.assertTrue(finance.delete_transaction(income["transaction_id"]))

    def test_food_meal_and_cooking_crud_statistics_detail_and_archive(self) -> None:
        food = FoodSubsystem(self.root)
        rice = food.create_ingredient(
            "Rice", "grain", 100, "g",
            {"calories": 130, "protein": 2.7, "carbohydrate": 28, "fat": 0.3},
        )
        recipe = food.create_recipe("Rice bowl", 2, ["Cook rice"])
        food.set_recipe_ingredients(
            recipe["recipe_id"],
            [{"ingredient_id": rice["ingredient_id"], "quantity": 200, "unit": "g"}],
        )
        cooking = food.record_cooking(recipe["recipe_id"], "2026-07-01", 2, "batch")
        meal = food.record_meal(
            "2026-07-01", "dinner", 1, recipe_id=recipe["recipe_id"], note="home"
        )
        self.assertEqual(
            food.update_meal(meal["meal_id"], note="home dinner")["note"],
            "home dinner",
        )
        self.assertEqual(
            food.list_meals(search="dinner")[0]["meal_id"], meal["meal_id"]
        )
        self.assertEqual(food.record_detail(meal["meal_id"])["meal_id"], meal["meal_id"])
        self.assertEqual(food.dashboard()["meal_count"], 1)
        self.assertTrue(food.delete_meal(meal["meal_id"]))
        self.assertTrue(food.delete_cooking(cooking["cooking_id"]))
        self.assertEqual(food.archive_recipe(recipe["recipe_id"])["status"], "archived")

    def test_health_inbody_checkup_and_goal_lifecycle(self) -> None:
        health = HealthSubsystem(self.root)
        health.record_weight(80, "2026-07-01")
        body = health.record_body_composition("2026-07-01", 32, 25, 24)
        updated_body = health.update_body_composition(
            body["record_id"], body_fat_percent=24
        )
        self.assertEqual(updated_body["body_fat_percent"], 24)
        checkup = health.record_health_checkup(
            "2026-07-01", "Annual", "Review", "2026-08-01", {"glucose": 95}
        )
        updated_checkup = health.update_health_checkup(
            checkup["record_id"], metrics={"glucose": 92}
        )
        self.assertEqual(updated_checkup["metrics"]["glucose"], 92.0)
        goal = health.create_health_goal("Weight", "2026-07-01", 75, 20)
        self.assertIsNotNone(health.health_goal_progress(goal["goal_id"])["progress_percent"])
        self.assertEqual(
            health.update_health_goal_status(goal["goal_id"], "completed")["status"],
            "completed",
        )
        self.assertEqual(health.dashboard()["active_goal_count"], 0)
        self.assertTrue(health.delete_health_checkup(checkup["record_id"]))
        self.assertTrue(health.delete_body_composition(body["record_id"]))

    def test_housing_contract_rent_maintenance_archive_and_report(self) -> None:
        housing = HousingSubsystem(self.root)
        contract = housing.create_contract(
            "Home", "Seoul", "2026-01-01", "2026-12-31",
            10_000_000, 600_000, 100_000,
        )
        rent = housing.record_charge(
            contract["contract_id"], "2026-07-01", "rent", 600_000
        )
        housing.record_charge(
            contract["contract_id"], "2026-07-02", "maintenance", 100_000
        )
        report = housing.occupancy_report(contract["contract_id"])
        self.assertEqual(report["total_paid"], 700_000)
        self.assertEqual(housing.dashboard()["monthly_commitment"], 700_000)
        self.assertTrue(housing.delete_charge(rent["charge_id"]))
        self.assertEqual(
            housing.archive_contract(contract["contract_id"])["status"], "archived"
        )

    def test_vehicle_trip_fuel_maintenance_timeline_report_and_efficiency(self) -> None:
        vehicle = VehicleSubsystem(self.root)
        car = vehicle.create_vehicle("Daily", "Maker", "Model", 2024, "hybrid")
        vehicle.record_odometer(car["vehicle_id"], 10_000, "2026-07-01")
        trip = vehicle.record_trip(
            car["vehicle_id"], "2026-07-02", 10_000, 10_120, "Commute"
        )
        first = vehicle.record_energy(
            car["vehicle_id"], "fuel", "2026-07-01", 40, 70_000, 10_000
        )
        vehicle.record_energy(
            car["vehicle_id"], "fuel", "2026-07-10", 10, 18_000, 10_120
        )
        maintenance = vehicle.record_maintenance(
            car["vehicle_id"], "Oil", "2026-07-03", 10_050, 50_000
        )
        report = vehicle.vehicle_report(car["vehicle_id"])
        self.assertEqual(report["trip_distance_km"], 120)
        self.assertEqual(report["fuel_efficiency"]["km_per_liter"], 12.0)
        self.assertEqual(vehicle.dashboard(car["vehicle_id"])["operating_cost"], 138_000)
        self.assertTrue(vehicle.delete_trip(trip["trip_id"]))
        self.assertTrue(vehicle.delete_energy(first["energy_id"]))
        self.assertTrue(vehicle.delete_maintenance(maintenance["maintenance_id"]))

    def test_validation_and_not_found_errors_are_explicit(self) -> None:
        housing = HousingSubsystem(self.root)
        with self.assertRaisesRegex(ValueError, "start_on cannot be after end_on"):
            housing.create_contract(
                "Invalid", "Seoul", "2026-12-31", "2026-01-01", 0, 0
            )
        vehicle = VehicleSubsystem(self.root)
        car = vehicle.create_vehicle("Daily")
        with self.assertRaisesRegex(ValueError, "cannot be lower"):
            vehicle.record_trip(car["vehicle_id"], "2026-07-01", 100, 99)
        with self.assertRaisesRegex(KeyError, "not found"):
            vehicle.get_trip("missing")


if __name__ == "__main__":
    unittest.main()
