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
from subsystems.database.engines.observability import record_failures
from subsystems.database.engines.records import dashboard_counts

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


class FinanceSubsystem:
    """The only supported external facade for Finance Subsystem v1.0."""

    VERSION = "1.0.0"
    subsystem_id = "SUB-FINANCE"
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

    @record_failures("record_income")
    def record_income(self, amount: Any, category: Any, occurred_on: Any,
                      description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._ledger.record_income(amount, category, occurred_on, description, metadata)

    @record_failures("record_expense")
    def record_expense(self, amount: Any, category: Any, occurred_on: Any,
                       description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._ledger.record_expense(amount, category, occurred_on, description, metadata)

    def list_transactions(self, **filters: Any) -> list[dict[str, Any]]:
        return self._ledger.list_transactions(**filters)

    def get_transaction(self, transaction_id: Any) -> dict[str, Any]:
        return self._ledger.get(transaction_id)

    @record_failures("update_transaction")
    def update_transaction(self, transaction_id: Any, **changes: Any) -> dict[str, Any]:
        return self._ledger.update(transaction_id, **changes)

    @record_failures("archive_transaction")
    def archive_transaction(self, transaction_id: Any) -> dict[str, Any]:
        return self._ledger.archive(transaction_id)

    @record_failures("restore_transaction")
    def restore_transaction(self, transaction_id: Any) -> dict[str, Any]:
        return self._ledger.restore(transaction_id)

    @record_failures("delete_transaction")
    def delete_transaction(self, transaction_id: Any) -> bool:
        return self._ledger.delete(transaction_id)

    @record_failures("create_budget")
    def create_budget(self, month: Any, category: Any, amount: Any) -> dict[str, Any]:
        return self._budget.create_budget(month, category, amount)

    @record_failures("upsert_budget")
    def upsert_budget(self, month: Any, category: Any, amount: Any) -> dict[str, Any]:
        return self._budget.upsert_budget(month, category, amount)

    @record_failures("delete_budget")
    def delete_budget(self, month: Any, category: Any) -> bool:
        return self._budget.delete_budget(month, category)

    def list_budgets(self, month: Any) -> list[dict[str, Any]]:
        return self._budget.list_budgets(month)

    def budget_usage(self, month: Any, category: str | None = None) -> dict[str, Any]:
        return self._budget.usage(month, category)

    def remaining_budget(self, month: Any, category: str | None = None) -> int:
        return self._budget.remaining(month, category)

    def monthly_cash_flow(self, month: Any) -> dict[str, Any]:
        return self._cash_flow.monthly(month)

    @record_failures("create_installment_savings")
    def create_installment_savings(
        self, name: Any, target_amount: Any, monthly_contribution: Any,
        annual_interest_rate: Any, opened_on: Any, maturity_date: Any,
    ) -> dict[str, Any]:
        return self._savings.create_installment(
            name, target_amount, monthly_contribution,
            annual_interest_rate, opened_on, maturity_date,
        )

    @record_failures("create_term_deposit")
    def create_term_deposit(
        self, name: Any, principal: Any, annual_interest_rate: Any,
        opened_on: Any, maturity_date: Any,
    ) -> dict[str, Any]:
        return self._savings.create_deposit(
            name, principal, annual_interest_rate, opened_on, maturity_date,
        )

    @record_failures("record_savings_contribution")
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

    @record_failures("monthly_close")
    def monthly_close(self, month: Any) -> dict[str, Any]:
        return self._report.monthly_close(month)

    def summary_report(self, month: Any) -> dict[str, Any]:
        return self._report.summary(month)

    def render_financial_status(self, month: Any) -> str:
        return self._report.render_status(month)

    @record_failures("migrate_legacy_budget")
    def migrate_legacy_budget(
        self, source: Path | None = None, month: Any | None = None,
    ) -> dict[str, Any]:
        path = Path(source) if source is not None else self.root / "data" / "finance_budget.json"
        return self._migration.migrate_legacy_budget(path, month)

    def export_snapshot(self) -> dict[str, Any]:
        return self._store.export_snapshot()

    def owner_data_count(self) -> int:
        snapshot = self.export_snapshot()
        return sum(len(value) for value in snapshot.values() if isinstance(value, list))

    def reset_owner_data(self) -> dict[str, int]:
        return self._store.reset_tables(
            (
                "savings_contributions",
                "monthly_closings",
                "budgets",
                "ledger_transactions",
                "savings_accounts",
            )
        )

    def dashboard(self, month: Any) -> dict[str, Any]:
        snapshot = self.export_snapshot()
        return {**dashboard_counts(snapshot), **self.summary_report(month)}
