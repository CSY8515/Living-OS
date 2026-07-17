from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.finance.engines.budget import BudgetEngine
from subsystems.finance.engines.cash_flow import CashFlowEngine
from subsystems.finance.engines.ledger import LedgerEngine
from subsystems.finance.engines.migration import FinanceMigrationEngine
from subsystems.finance.engines.report import ReportEngine
from subsystems.finance.engines.savings import SavingsEngine
from subsystems.finance.engines.storage import FinanceStorageEngine

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


class FinanceSubsystem:
    """The only supported external facade for Finance Subsystem v1.0."""

    VERSION = "1.0.0"
    LIVING_OS_COMPATIBILITY = ">=1.2,<2.0"

    def __init__(self, root: Path, database_path: Path | None = None,
                 database_foundation: DatabaseSubsystem | None = None) -> None:
        self.root = Path(root)
        path = (
            Path(database_path) if database_path is not None
            else self.root / "data" / "finance" / "finance.sqlite3"
        )
        store = FinanceStorageEngine(path, database_foundation)
        store.register_contract(schema_version=1, migration_id="finance-schema-v1")
        ledger = LedgerEngine(store)
        budget = BudgetEngine(store, ledger)
        cash_flow = CashFlowEngine(ledger)
        savings = SavingsEngine(store)
        report = ReportEngine(store, ledger, budget, cash_flow, savings)
        migration = FinanceMigrationEngine(store)
        self._store = store
        self._ledger = ledger
        self._budget = budget
        self._cash_flow = cash_flow
        self._savings = savings
        self._report = report
        self._migration = migration

    @property
    def database_path(self) -> Path:
        return self._store.database_path

    def health(self) -> dict[str, Any]:
        return {
            **self._store.health(), "subsystem": "finance", "version": self.VERSION,
            "living_os_compatibility": self.LIVING_OS_COMPATIBILITY,
        }

    def record_income(self, amount: Any, category: Any, occurred_on: Any,
                      description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._ledger.record_income(amount, category, occurred_on, description, metadata)

    def record_expense(self, amount: Any, category: Any, occurred_on: Any,
                       description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._ledger.record_expense(amount, category, occurred_on, description, metadata)

    def list_transactions(self, **filters: Any) -> list[dict[str, Any]]:
        return self._ledger.list_transactions(**filters)

    def create_budget(self, month: Any, category: Any, amount: Any) -> dict[str, Any]:
        return self._budget.create_budget(month, category, amount)

    def list_budgets(self, month: Any) -> list[dict[str, Any]]:
        return self._budget.list_budgets(month)

    def budget_usage(self, month: Any, category: str | None = None) -> dict[str, Any]:
        return self._budget.usage(month, category)

    def remaining_budget(self, month: Any, category: str | None = None) -> int:
        return self._budget.remaining(month, category)

    def monthly_cash_flow(self, month: Any) -> dict[str, Any]:
        return self._cash_flow.monthly(month)

    def create_installment_savings(
        self, name: Any, target_amount: Any, monthly_contribution: Any,
        annual_interest_rate: Any, opened_on: Any, maturity_date: Any,
    ) -> dict[str, Any]:
        return self._savings.create_installment(
            name, target_amount, monthly_contribution,
            annual_interest_rate, opened_on, maturity_date,
        )

    def create_term_deposit(
        self, name: Any, principal: Any, annual_interest_rate: Any,
        opened_on: Any, maturity_date: Any,
    ) -> dict[str, Any]:
        return self._savings.create_deposit(
            name, principal, annual_interest_rate, opened_on, maturity_date,
        )

    def record_savings_contribution(
        self, account_id: Any, amount: Any, contributed_on: Any, note: Any = "",
    ) -> dict[str, Any]:
        return self._savings.add_contribution(account_id, amount, contributed_on, note)

    def list_savings(self, kind: str | None = None) -> list[dict[str, Any]]:
        return self._savings.list_accounts(kind)

    def savings_goal_progress(self, account_id: Any) -> dict[str, Any]:
        return self._savings.goal_progress(account_id)

    def calculate_maturity(self, account_id: Any, as_of: Any | None = None) -> dict[str, Any]:
        return self._savings.maturity(account_id, as_of)

    def monthly_close(self, month: Any) -> dict[str, Any]:
        return self._report.monthly_close(month)

    def summary_report(self, month: Any) -> dict[str, Any]:
        return self._report.summary(month)

    def render_financial_status(self, month: Any) -> str:
        return self._report.render_status(month)

    def migrate_legacy_budget(
        self, source: Path | None = None, month: Any | None = None,
    ) -> dict[str, Any]:
        path = Path(source) if source is not None else self.root / "data" / "finance_budget.json"
        return self._migration.migrate_legacy_budget(path, month)

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()
