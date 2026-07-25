from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from subsystems.finance.engines.storage import FinanceStorageEngine
from subsystems.finance.engines.validation import (
    optional_text, require_amount, require_date, require_month, require_text, utc_now_iso,
)
from subsystems.database.engines.records import query_records


class LedgerEngine:
    def __init__(self, store: FinanceStorageEngine) -> None:
        self.store = store

    def _record(self, kind: str, amount: Any, category: Any, occurred_on: Any,
                description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if kind not in {"income", "expense"}:
            raise ValueError("kind must be income or expense.")
        record = {
            "transaction_id": str(uuid4()),
            "kind": kind,
            "amount": require_amount(amount),
            "category": require_text(category, "category", 100),
            "occurred_on": require_date(occurred_on, "occurred_on"),
            "description": optional_text(description, 500),
            "metadata": dict(metadata or {}),
            "created_at": utc_now_iso(),
        }
        try:
            metadata_json = json.dumps(record["metadata"], ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError("metadata must be JSON serializable.") from exc
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO ledger_transactions(
                    transaction_id, kind, amount, category, occurred_on,
                    description, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record["transaction_id"], record["kind"], record["amount"],
                    record["category"], record["occurred_on"], record["description"],
                    metadata_json, record["created_at"],
                ),
            )
        return record

    def record_income(self, amount: Any, category: Any, occurred_on: Any,
                      description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._record("income", amount, category, occurred_on, description, metadata)

    def record_expense(self, amount: Any, category: Any, occurred_on: Any,
                       description: Any = "", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._record("expense", amount, category, occurred_on, description, metadata)

    def list_transactions(self, start_on: Any | None = None, end_on: Any | None = None,
                          kind: str | None = None, category: str | None = None,
                          status: str | None = None, search: str | None = None,
                          sort_by: str = "occurred_on", descending: bool = True,
                          limit: int = 500) -> list[dict[str, Any]]:
        clauses: list[str] = []
        parameters: list[Any] = []
        normalized_start = require_date(start_on, "start_on") if start_on is not None else None
        normalized_end = require_date(end_on, "end_on") if end_on is not None else None
        if normalized_start and normalized_end and normalized_start > normalized_end:
            raise ValueError("start_on cannot be after end_on.")
        if normalized_start:
            clauses.append("occurred_on >= ?")
            parameters.append(normalized_start)
        if normalized_end:
            clauses.append("occurred_on <= ?")
            parameters.append(normalized_end)
        if kind is not None:
            if kind not in {"income", "expense"}:
                raise ValueError("kind must be income or expense.")
            clauses.append("kind = ?")
            parameters.append(kind)
        if category is not None:
            clauses.append("category = ?")
            parameters.append(require_text(category, "category", 100))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.store.query(
            "SELECT * FROM ledger_transactions" + where +
            " ORDER BY occurred_on DESC, created_at DESC",
            tuple(parameters),
        )
        for row in rows:
            row["metadata"] = json.loads(row.pop("metadata_json"))
            row["status"] = str(row["metadata"].get("status") or "active").lower()
            row["updated_at"] = str(row["metadata"].get("updated_at") or row["created_at"])
        return query_records(
            rows, search=search, status=status, sort_by=sort_by,
            descending=descending, limit=limit,
        )

    def get(self, transaction_id: Any) -> dict[str, Any]:
        selected = require_text(transaction_id, "transaction_id", 100)
        row = next(
            (item for item in self.list_transactions(limit=1000)
             if item["transaction_id"] == selected),
            None,
        )
        if row is None:
            raise KeyError("Finance transaction not found.")
        return row

    def update(self, transaction_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get(transaction_id)
        allowed = {"kind", "amount", "category", "occurred_on", "description", "metadata"}
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Finance transaction fields: {sorted(unexpected)}")
        kind = str(changes.get("kind", current["kind"])).lower()
        if kind not in {"income", "expense"}:
            raise ValueError("kind must be income or expense.")
        metadata = dict(current["metadata"])
        supplied_metadata = changes.get("metadata")
        if supplied_metadata is not None:
            if not isinstance(supplied_metadata, dict):
                raise ValueError("metadata must be an object.")
            metadata.update(supplied_metadata)
        metadata["updated_at"] = utc_now_iso()
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE ledger_transactions
                   SET kind=?,amount=?,category=?,occurred_on=?,description=?,metadata_json=?
                   WHERE transaction_id=?""",
                (
                    kind,
                    require_amount(changes.get("amount", current["amount"])),
                    require_text(changes.get("category", current["category"]), "category", 100),
                    require_date(changes.get("occurred_on", current["occurred_on"]), "occurred_on"),
                    optional_text(changes.get("description", current["description"]), 500),
                    json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                    current["transaction_id"],
                ),
            )
        return self.get(current["transaction_id"])

    def archive(self, transaction_id: Any) -> dict[str, Any]:
        return self.update(transaction_id, metadata={"status": "archived"})

    def restore(self, transaction_id: Any) -> dict[str, Any]:
        return self.update(transaction_id, metadata={"status": "active"})

    def delete(self, transaction_id: Any) -> bool:
        current = self.get(transaction_id)
        with self.store.transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM ledger_transactions WHERE transaction_id=?",
                (current["transaction_id"],),
            )
        return cursor.rowcount == 1

    def totals_for_month(self, month: Any) -> dict[str, int]:
        normalized = require_month(month)
        row = self.store.query_one(
            """SELECT
                COALESCE(SUM(CASE WHEN kind='income' THEN amount ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN kind='expense' THEN amount ELSE 0 END), 0) AS expense
            FROM ledger_transactions WHERE substr(occurred_on, 1, 7) = ?""",
            (normalized,),
        ) or {"income": 0, "expense": 0}
        return {"income": int(row["income"]), "expense": int(row["expense"])}

    def expenses_by_category(self, month: Any) -> dict[str, int]:
        rows = self.store.query(
            """SELECT category, SUM(amount) AS amount FROM ledger_transactions
            WHERE kind='expense' AND substr(occurred_on, 1, 7)=? GROUP BY category""",
            (require_month(month),),
        )
        return {str(row["category"]): int(row["amount"]) for row in rows}
