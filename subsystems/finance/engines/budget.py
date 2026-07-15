from __future__ import annotations

import sqlite3
from typing import Any
from uuid import uuid4

from subsystems.finance.engines.ledger import LedgerEngine
from subsystems.finance.engines.storage import FinanceStorageEngine
from subsystems.finance.engines.validation import require_amount, require_month, require_text, utc_now_iso


class BudgetEngine:
    def __init__(self, store: FinanceStorageEngine, ledger: LedgerEngine) -> None:
        self.store = store
        self.ledger = ledger

    def create_budget(self, month: Any, category: Any, amount: Any) -> dict[str, Any]:
        now = utc_now_iso()
        record = {
            "budget_id": str(uuid4()), "month": require_month(month),
            "category": require_text(category, "category", 100),
            "amount": require_amount(amount, allow_zero=True),
            "created_at": now, "updated_at": now,
        }
        try:
            with self.store.transaction() as connection:
                connection.execute(
                    """INSERT INTO budgets(budget_id, month, category, amount, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)""", tuple(record.values())
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("A budget already exists for this month and category.") from exc
        return record

    def upsert_budget(self, month: Any, category: Any, amount: Any) -> dict[str, Any]:
        normalized_month = require_month(month)
        normalized_category = require_text(category, "category", 100)
        normalized_amount = require_amount(amount, allow_zero=True)
        now = utc_now_iso()
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO budgets(budget_id, month, category, amount, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(month, category)
                DO UPDATE SET amount=excluded.amount, updated_at=excluded.updated_at""",
                (str(uuid4()), normalized_month, normalized_category, normalized_amount, now, now),
            )
        return self.get_budget(normalized_month, normalized_category)

    def get_budget(self, month: Any, category: Any) -> dict[str, Any]:
        row = self.store.query_one(
            "SELECT * FROM budgets WHERE month=? AND category=?",
            (require_month(month), require_text(category, "category", 100)),
        )
        if row is None:
            raise KeyError("Budget not found.")
        return row

    def list_budgets(self, month: Any) -> list[dict[str, Any]]:
        return self.store.query(
            "SELECT * FROM budgets WHERE month=? ORDER BY category", (require_month(month),)
        )

    def usage(self, month: Any, category: str | None = None) -> dict[str, Any]:
        normalized = require_month(month)
        expenses = self.ledger.expenses_by_category(normalized)
        budgets = self.list_budgets(normalized)
        selected = require_text(category, "category", 100) if category is not None else None
        if selected is not None:
            budgets = [item for item in budgets if item["category"] == selected]
            expenses = {selected: expenses.get(selected, 0)}
        budget_total = sum(int(item["amount"]) for item in budgets)
        spent = sum(expenses.values())
        rate = round(spent / budget_total * 100, 2) if budget_total else (100.0 if spent else 0.0)
        return {
            "month": normalized, "category": selected, "budget": budget_total,
            "spent": spent, "usage_percent": rate, "over_budget": spent > budget_total,
        }

    def remaining(self, month: Any, category: str | None = None) -> int:
        usage = self.usage(month, category)
        return int(usage["budget"]) - int(usage["spent"])
