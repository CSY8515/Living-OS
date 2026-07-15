from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

import subsystems.finance as finance_package
from subsystems.finance import FinanceSubsystem
from subsystems.operations.engines.catalog import V12_STABLE_MANIFESTS


class FinanceSubsystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "finance.sqlite3"
        self.finance = FinanceSubsystem(self.root, self.database)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_public_surface_and_lazy_independent_storage(self) -> None:
        self.assertEqual(finance_package.__all__, ["FinanceSubsystem"])
        self.assertFalse(self.database.exists())
        self.assertEqual(self.finance.health()["status"], "ready")
        self.assertFalse(self.database.exists())
        self.assertEqual(self.finance.summary_report("2026-07")["transaction_count"], 0)
        self.assertFalse(self.database.exists())

        second = FinanceSubsystem(self.root, self.root / "second.sqlite3")
        self.finance.record_income(1000, "Salary", "2026-07-01")
        self.assertEqual(len(self.finance.list_transactions()), 1)
        self.assertEqual(second.list_transactions(), [])

    def test_ledger_records_income_expense_and_filters_transactions(self) -> None:
        income = self.finance.record_income(
            3_000_000, "Salary", "2026-07-01", metadata={"source": "employer"}
        )
        expense = self.finance.record_expense(120_000, "Food", "2026-07-02", "Groceries")
        self.assertEqual(income["kind"], "income")
        self.assertEqual(expense["kind"], "expense")
        self.assertEqual(
            [item["transaction_id"] for item in self.finance.list_transactions(kind="expense")],
            [expense["transaction_id"]],
        )
        self.assertEqual(
            self.finance.list_transactions(category="Salary")[0]["metadata"],
            {"source": "employer"},
        )
        with self.assertRaises(ValueError):
            self.finance.record_expense(0, "Food", "2026-07-02")
        with self.assertRaises(ValueError):
            self.finance.record_expense(1.5, "Food", "2026-07-02")
        with self.assertRaises(ValueError):
            self.finance.list_transactions(start_on="2026-08-01", end_on="2026-07-01")

    def test_budget_usage_and_remaining_are_driven_by_ledger(self) -> None:
        self.finance.create_budget("2026-07", "Food", 500_000)
        self.finance.record_expense(125_000, "Food", "2026-07-03")
        usage = self.finance.budget_usage("2026-07", "Food")
        self.assertEqual(usage["spent"], 125_000)
        self.assertEqual(usage["usage_percent"], 25.0)
        self.assertEqual(self.finance.remaining_budget("2026-07", "Food"), 375_000)
        with self.assertRaises(ValueError):
            self.finance.create_budget("2026-07", "Food", 100)

    def test_cash_flow_calculates_monthly_income_expense_and_net(self) -> None:
        self.finance.record_income(4_000_000, "Salary", "2026-07-01")
        self.finance.record_income(100_000, "Other", "2026-07-05")
        self.finance.record_expense(1_250_000, "Housing", "2026-07-10")
        self.finance.record_expense(50_000, "Food", "2026-08-01")
        self.assertEqual(
            self.finance.monthly_cash_flow("2026-07"),
            {"month": "2026-07", "income": 4_100_000, "expense": 1_250_000,
             "net_cash_flow": 2_850_000},
        )

    def test_installment_savings_progress_and_maturity(self) -> None:
        account = self.finance.create_installment_savings(
            "Emergency Fund", 1_000_000, 100_000, "3.5",
            "2026-01-01", "2027-01-01",
        )
        self.finance.record_savings_contribution(
            account["account_id"], 250_000, "2026-01-01", "Initial"
        )
        progress = self.finance.savings_goal_progress(account["account_id"])
        self.assertEqual(progress["current_amount"], 250_000)
        self.assertEqual(progress["progress_percent"], 25.0)
        maturity = self.finance.calculate_maturity(account["account_id"], "2026-07-01")
        self.assertEqual(maturity["principal_at_maturity"], 250_000)
        self.assertGreater(maturity["projected_interest"], 0)

    def test_term_deposit_maturity_is_deterministic(self) -> None:
        account = self.finance.create_term_deposit(
            "One Year Deposit", 1_000_000, "3.65", "2026-01-01", "2027-01-01"
        )
        maturity = self.finance.calculate_maturity(account["account_id"], "2026-01-01")
        self.assertEqual(maturity["projected_interest"], 36_500)
        self.assertEqual(maturity["projected_total"], 1_036_500)
        with self.assertRaises(ValueError):
            self.finance.record_savings_contribution(
                account["account_id"], 10_000, "2026-02-01"
            )

    def test_reports_summarize_and_monthly_closing_is_immutable(self) -> None:
        self.finance.create_budget("2026-07", "Food", 500_000)
        self.finance.record_income(2_000_000, "Salary", "2026-07-01")
        self.finance.record_expense(100_000, "Food", "2026-07-02")
        summary = self.finance.summary_report("2026-07")
        self.assertEqual(summary["cash_flow"]["net_cash_flow"], 1_900_000)
        self.assertIn("Net Cash Flow: 1,900,000", self.finance.render_financial_status("2026-07"))
        first = self.finance.monthly_close("2026-07")
        self.finance.record_expense(50_000, "Food", "2026-07-03")
        second = self.finance.monthly_close("2026-07")
        self.assertEqual(first["snapshot"], second["snapshot"])
        self.assertEqual(second["snapshot"]["cash_flow"]["expense"], 100_000)

    def test_legacy_migration_is_transactional_idempotent_and_checksum_guarded(self) -> None:
        source = self.root / "finance_budget.json"
        source.write_text(json.dumps({
            "monthly_income": 3_000_000,
            "fixed_expenses": [{"name": "Housing", "amount": 1_000_000}],
            "savings_goals": [{"name": "Emergency", "amount": 5_000_000}],
        }), encoding="utf-8")
        first = self.finance.migrate_legacy_budget(source, "2026-07")
        second = self.finance.migrate_legacy_budget(source, "2026-07")
        self.assertFalse(first["already_migrated"])
        self.assertTrue(second["already_migrated"])
        self.assertEqual(first["accepted"], {"income": 1, "budgets": 1, "savings": 1})
        self.assertEqual(len(self.finance.list_transactions()), 1)
        self.assertEqual(len(self.finance.list_savings()), 1)

        source.write_text('{"monthly_income": 1}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.finance.migrate_legacy_budget(source, "2026-07")

    def test_invalid_legacy_source_does_not_create_partial_state(self) -> None:
        source = self.root / "invalid.json"
        source.write_text(json.dumps({
            "monthly_income": 100,
            "fixed_expenses": "invalid",
            "savings_goals": [],
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.finance.migrate_legacy_budget(source, "2026-07")
        self.assertFalse(self.database.exists())

    def test_export_health_and_living_os_manifest_integration(self) -> None:
        self.finance.record_income(100, "Test", "2026-07-01")
        snapshot = self.finance.export_snapshot()
        self.assertEqual(snapshot["schema_version"], 1)
        self.assertEqual(len(snapshot["transactions"]), 1)
        self.assertEqual(self.finance.health()["status"], "healthy")
        manifest = next(item for item in V12_STABLE_MANIFESTS if item.module_id == "finance")
        self.assertEqual(manifest.version, "1.0.0")
        self.assertIn("ledger", manifest.capabilities)




    def test_other_subsystems_use_only_the_public_finance_facade(self) -> None:
        repository = Path(__file__).resolve().parent.parent
        violations: list[str] = []
        for path in (repository / "subsystems").rglob("*.py"):
            if path.is_relative_to(repository / "subsystems" / "finance"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.module
                    and node.module.startswith("subsystems.finance.engines")
                ):
                    violations.append(str(path.relative_to(repository)))
        self.assertEqual(violations, [])
if __name__ == "__main__":
    unittest.main()
