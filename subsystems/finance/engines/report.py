from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from subsystems.finance.engines.budget import BudgetEngine
from subsystems.finance.engines.cash_flow import CashFlowEngine
from subsystems.finance.engines.ledger import LedgerEngine
from subsystems.finance.engines.savings import SavingsEngine
from subsystems.finance.engines.storage import FinanceStorageEngine
from subsystems.finance.engines.validation import require_month, utc_now_iso


class ReportEngine:
    def __init__(self, store: FinanceStorageEngine, ledger: LedgerEngine,
                 budget: BudgetEngine, cash_flow: CashFlowEngine,
                 savings: SavingsEngine) -> None:
        self.store = store
        self.ledger = ledger
        self.budget = budget
        self.cash_flow = cash_flow
        self.savings = savings

    def summary(self, month: Any) -> dict[str, Any]:
        normalized = require_month(month)
        flow = self.cash_flow.monthly(normalized)
        budget = self.budget.usage(normalized)
        accounts = self.savings.list_accounts()
        savings_total = sum(
            self.savings.goal_progress(item["account_id"])["current_amount"]
            for item in accounts
        )
        return {
            "month": normalized,
            "cash_flow": flow,
            "budget": {**budget, "remaining": self.budget.remaining(normalized)},
            "savings": {"account_count": len(accounts), "current_total": savings_total},
            "transaction_count": len(self.ledger.list_transactions(
                start_on=f"{normalized}-01", end_on=self._month_end(normalized)
            )),
        }

    def monthly_close(self, month: Any) -> dict[str, Any]:
        normalized = require_month(month)
        existing = self.store.query_one(
            "SELECT snapshot_json, closed_at FROM monthly_closings WHERE month=?",
            (normalized,),
        )
        if existing:
            return {
                "month": normalized, "snapshot": json.loads(existing["snapshot_json"]),
                "closed_at": existing["closed_at"], "immutable": True,
            }
        snapshot = self.summary(normalized)
        closed_at = utc_now_iso()
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO monthly_closings(month, snapshot_json, closed_at) VALUES (?, ?, ?)",
                (normalized, json.dumps(snapshot, ensure_ascii=False, sort_keys=True), closed_at),
            )
        return {
            "month": normalized, "snapshot": snapshot,
            "closed_at": closed_at, "immutable": True,
        }

    def render_status(self, month: Any) -> str:
        report = self.summary(month)
        flow, budget, savings = report["cash_flow"], report["budget"], report["savings"]
        return "\n".join([
            f"# Finance Status - {report['month']}", "",
            f"- Income: {flow['income']:,}",
            f"- Expense: {flow['expense']:,}",
            f"- Net Cash Flow: {flow['net_cash_flow']:,}",
            f"- Budget: {budget['budget']:,}",
            f"- Budget Spent: {budget['spent']:,} ({budget['usage_percent']:.2f}%)",
            f"- Budget Remaining: {budget['remaining']:,}",
            f"- Savings: {savings['current_total']:,} across {savings['account_count']} accounts",
            f"- Transactions: {report['transaction_count']}",
        ])

    @staticmethod
    def _month_end(month: str) -> str:
        year, number = (int(value) for value in month.split("-"))
        if number == 12:
            return f"{year}-12-31"
        return (date(year, number + 1, 1) - timedelta(days=1)).isoformat()
