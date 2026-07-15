from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

from subsystems.finance.engines.storage import FinanceStorageEngine
from subsystems.finance.engines.validation import (
    optional_text, rate_percent, require_amount, require_date,
    require_rate_bps, require_text, utc_now_iso,
)


class SavingsEngine:
    def __init__(self, store: FinanceStorageEngine) -> None:
        self.store = store

    def _create(self, kind: str, name: Any, target_amount: Any, principal: Any,
                monthly_contribution: Any, annual_interest_rate: Any,
                opened_on: Any, maturity_date: Any) -> dict[str, Any]:
        opened = require_date(opened_on, "opened_on")
        maturity = require_date(maturity_date, "maturity_date")
        if maturity <= opened:
            raise ValueError("maturity_date must be after opened_on.")
        now = utc_now_iso()
        record = {
            "account_id": str(uuid4()), "kind": kind,
            "name": require_text(name, "name", 120),
            "target_amount": require_amount(target_amount, "target_amount", allow_zero=True),
            "principal": require_amount(principal, "principal", allow_zero=True),
            "monthly_contribution": require_amount(
                monthly_contribution, "monthly_contribution", allow_zero=True
            ),
            "annual_rate_bps": require_rate_bps(annual_interest_rate),
            "opened_on": opened, "maturity_date": maturity, "status": "active",
            "created_at": now, "updated_at": now,
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO savings_accounts(
                    account_id, kind, name, target_amount, principal,
                    monthly_contribution, annual_rate_bps, opened_on,
                    maturity_date, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(record.values()),
            )
        return self._public(record)

    def create_installment(self, name: Any, target_amount: Any, monthly_contribution: Any,
                           annual_interest_rate: Any, opened_on: Any,
                           maturity_date: Any) -> dict[str, Any]:
        return self._create(
            "installment", name, target_amount, 0, monthly_contribution,
            annual_interest_rate, opened_on, maturity_date,
        )

    def create_deposit(self, name: Any, principal: Any, annual_interest_rate: Any,
                       opened_on: Any, maturity_date: Any) -> dict[str, Any]:
        amount = require_amount(principal, "principal")
        return self._create(
            "deposit", name, amount, amount, 0,
            annual_interest_rate, opened_on, maturity_date,
        )

    def add_contribution(self, account_id: Any, amount: Any, contributed_on: Any,
                         note: Any = "") -> dict[str, Any]:
        account = self._account(account_id)
        if account["kind"] != "installment":
            raise ValueError("Contributions can only be added to installment savings.")
        if account["status"] != "active":
            raise ValueError("Savings account is not active.")
        contributed = require_date(contributed_on, "contributed_on")
        if contributed < account["opened_on"] or contributed > account["maturity_date"]:
            raise ValueError("contributed_on must fall within the savings term.")
        record = {
            "contribution_id": str(uuid4()), "account_id": account["account_id"],
            "amount": require_amount(amount), "contributed_on": contributed,
            "note": optional_text(note, 300), "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO savings_contributions(
                    contribution_id, account_id, amount, contributed_on, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)""", tuple(record.values())
            )
        return record

    def list_accounts(self, kind: str | None = None) -> list[dict[str, Any]]:
        if kind is not None and kind not in {"installment", "deposit"}:
            raise ValueError("kind must be installment or deposit.")
        sql = "SELECT * FROM savings_accounts"
        parameters: tuple[Any, ...] = ()
        if kind is not None:
            sql += " WHERE kind=?"
            parameters = (kind,)
        return [self._public(row) for row in self.store.query(
            sql + " ORDER BY maturity_date, name", parameters
        )]

    def goal_progress(self, account_id: Any) -> dict[str, Any]:
        account = self._account(account_id)
        current = self._current_amount(account)
        target = int(account["target_amount"])
        percent = round(current / target * 100, 2) if target else 0.0
        return {
            "account_id": account["account_id"], "name": account["name"],
            "kind": account["kind"], "current_amount": current,
            "target_amount": target, "remaining_amount": max(0, target - current),
            "progress_percent": percent, "target_reached": target > 0 and current >= target,
        }

    def maturity(self, account_id: Any, as_of: Any | None = None) -> dict[str, Any]:
        account = self._account(account_id)
        maturity = date.fromisoformat(account["maturity_date"])
        reference = (
            date.fromisoformat(require_date(as_of, "as_of"))
            if as_of is not None else date.today()
        )
        contributions = self.store.query(
            "SELECT amount, contributed_on FROM savings_contributions WHERE account_id=?",
            (account["account_id"],),
        )
        if account["kind"] == "deposit":
            bases = [(int(account["principal"]), date.fromisoformat(account["opened_on"]))]
        else:
            bases = [
                (int(item["amount"]), date.fromisoformat(item["contributed_on"]))
                for item in contributions
            ]
        rate = Decimal(int(account["annual_rate_bps"])) / Decimal(10000)
        interest = Decimal(0)
        principal = 0
        for amount, start in bases:
            principal += amount
            days = max(0, (maturity - start).days)
            interest += Decimal(amount) * rate * Decimal(days) / Decimal(365)
        projected_interest = int(interest.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return {
            "account_id": account["account_id"], "maturity_date": account["maturity_date"],
            "days_remaining": max(0, (maturity - reference).days),
            "matured": reference >= maturity, "principal_at_maturity": principal,
            "projected_interest": projected_interest,
            "projected_total": principal + projected_interest,
        }

    def _account(self, account_id: Any) -> dict[str, Any]:
        identifier = require_text(account_id, "account_id", 80)
        row = self.store.query_one(
            "SELECT * FROM savings_accounts WHERE account_id=?", (identifier,)
        )
        if row is None:
            raise KeyError("Savings account not found.")
        return row

    def _current_amount(self, account: dict[str, Any]) -> int:
        if account["kind"] == "deposit":
            return int(account["principal"])
        row = self.store.query_one(
            "SELECT COALESCE(SUM(amount), 0) AS amount FROM savings_contributions WHERE account_id=?",
            (account["account_id"],),
        )
        return int(row["amount"]) if row else 0

    @staticmethod
    def _public(row: dict[str, Any]) -> dict[str, Any]:
        value = dict(row)
        value["annual_interest_rate"] = rate_percent(int(value.pop("annual_rate_bps")))
        return value
