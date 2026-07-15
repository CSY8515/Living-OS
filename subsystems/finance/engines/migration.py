from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.finance.engines.storage import FinanceStorageEngine
from subsystems.finance.engines.validation import (
    require_amount, require_month, require_text, utc_now_iso,
)


class FinanceMigrationEngine:
    """Explicit, checksum-guarded, transactional migration from the legacy JSON budget."""

    def __init__(self, store: FinanceStorageEngine) -> None:
        self.store = store

    def migrate_legacy_budget(self, source: Path, month: Any | None = None) -> dict[str, Any]:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        raw_bytes = path.read_bytes()
        checksum = hashlib.sha256(raw_bytes).hexdigest()
        source_key = str(path.resolve())
        existing = self.store.query_one(
            "SELECT checksum, result_json, imported_at FROM migration_ledger WHERE source_key=?",
            (source_key,),
        )
        if existing:
            if existing["checksum"] != checksum:
                raise ValueError(
                    "Legacy source changed after migration; review before importing again."
                )
            return {
                **json.loads(existing["result_json"]), "already_migrated": True,
                "imported_at": existing["imported_at"],
            }
        try:
            payload = json.loads(raw_bytes.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Legacy finance budget must be valid UTF-8 JSON.") from exc
        if not isinstance(payload, dict):
            raise ValueError("Legacy finance budget must be a JSON object.")

        normalized_month = require_month(month or date.today().strftime("%Y-%m"))
        first_day = f"{normalized_month}-01"
        income = require_amount(
            payload.get("monthly_income", 0), "monthly_income", allow_zero=True
        )
        raw_expenses = payload.get("fixed_expenses", [])
        raw_goals = payload.get("savings_goals", [])
        if not isinstance(raw_expenses, list):
            raise ValueError("fixed_expenses must be a list.")
        if not isinstance(raw_goals, list):
            raise ValueError("savings_goals must be a list.")

        budgets: list[tuple[str, int]] = []
        for index, item in enumerate(raw_expenses):
            if not isinstance(item, dict):
                continue
            budgets.append((
                require_text(
                    item.get("name") or f"Legacy Fixed Expense {index + 1}",
                    "fixed expense name", 100,
                ),
                require_amount(item.get("amount", 0), "fixed expense", allow_zero=True),
            ))
        goals: list[tuple[str, int]] = []
        for index, item in enumerate(raw_goals):
            if not isinstance(item, dict):
                continue
            goals.append((
                require_text(
                    item.get("name") or f"Legacy Savings Goal {index + 1}",
                    "savings goal name", 120,
                ),
                require_amount(item.get("amount", 0), "savings goal", allow_zero=True),
            ))

        year, number = (int(value) for value in normalized_month.split("-"))
        maturity = date(year + 1, number, 1).isoformat()
        imported_at = utc_now_iso()
        accepted = {
            "income": 1 if income else 0,
            "budgets": len(budgets),
            "savings": len(goals),
        }
        result = {
            "source": source_key, "checksum": checksum,
            "month": normalized_month, "accepted": accepted,
            "already_migrated": False,
        }

        with self.store.transaction() as connection:
            if income:
                connection.execute(
                    """INSERT INTO ledger_transactions(
                        transaction_id, kind, amount, category, occurred_on,
                        description, metadata_json, created_at
                    ) VALUES (?, 'income', ?, ?, ?, ?, ?, ?)""",
                    (
                        str(uuid4()), income, "Legacy Monthly Income", first_day,
                        "Imported from legacy Finance budget.",
                        json.dumps({
                            "legacy_source": source_key,
                            "legacy_checksum": checksum,
                        }, sort_keys=True),
                        imported_at,
                    ),
                )
            for name, amount in budgets:
                connection.execute(
                    """INSERT INTO budgets(
                        budget_id, month, category, amount, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(month, category)
                    DO UPDATE SET amount=excluded.amount, updated_at=excluded.updated_at""",
                    (str(uuid4()), normalized_month, name, amount, imported_at, imported_at),
                )
            for name, target in goals:
                connection.execute(
                    """INSERT INTO savings_accounts(
                        account_id, kind, name, target_amount, principal,
                        monthly_contribution, annual_rate_bps, opened_on,
                        maturity_date, status, created_at, updated_at
                    ) VALUES (?, 'installment', ?, ?, 0, 0, 0, ?, ?, 'active', ?, ?)""",
                    (str(uuid4()), name, target, first_day, maturity, imported_at, imported_at),
                )
            connection.execute(
                """INSERT INTO migration_ledger(
                    source_key, checksum, result_json, imported_at
                ) VALUES (?, ?, ?, ?)""",
                (source_key, checksum, json.dumps(result, sort_keys=True), imported_at),
            )
        return {**result, "imported_at": imported_at}
