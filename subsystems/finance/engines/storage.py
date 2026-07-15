from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from subsystems.finance.engines.validation import utc_now_iso


SCHEMA_VERSION = 1


class FinanceStorageEngine:
    """Private transactional store with lazy creation and a stable schema boundary."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)

    @property
    def initialized(self) -> bool:
        return self.database_path.is_file()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS finance_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ledger_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
                    amount INTEGER NOT NULL CHECK (amount > 0),
                    category TEXT NOT NULL,
                    occurred_on TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_finance_ledger_date
                    ON ledger_transactions(occurred_on, kind, category);
                CREATE TABLE IF NOT EXISTS budgets (
                    budget_id TEXT PRIMARY KEY,
                    month TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount INTEGER NOT NULL CHECK (amount >= 0),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(month, category)
                );
                CREATE TABLE IF NOT EXISTS savings_accounts (
                    account_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK (kind IN ('installment', 'deposit')),
                    name TEXT NOT NULL,
                    target_amount INTEGER NOT NULL CHECK (target_amount >= 0),
                    principal INTEGER NOT NULL CHECK (principal >= 0),
                    monthly_contribution INTEGER NOT NULL CHECK (monthly_contribution >= 0),
                    annual_rate_bps INTEGER NOT NULL CHECK (annual_rate_bps BETWEEN 0 AND 10000),
                    opened_on TEXT NOT NULL,
                    maturity_date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('active', 'matured', 'closed')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS savings_contributions (
                    contribution_id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL REFERENCES savings_accounts(account_id),
                    amount INTEGER NOT NULL CHECK (amount > 0),
                    contributed_on TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_finance_savings_account
                    ON savings_contributions(account_id, contributed_on);
                CREATE TABLE IF NOT EXISTS monthly_closings (
                    month TEXT PRIMARY KEY,
                    snapshot_json TEXT NOT NULL,
                    closed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS migration_ledger (
                    source_key TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    imported_at TEXT NOT NULL
                );
                """
            )
            now = utc_now_iso()
            connection.execute(
                """
                INSERT INTO finance_meta(key, value, updated_at)
                VALUES ('schema_version', ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (str(SCHEMA_VERSION), now),
            )
            connection.execute(
                """
                INSERT INTO finance_meta(key, value, updated_at)
                VALUES ('subsystem_version', '1.0.0', ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (now,),
            )
            connection.commit()
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self.initialize()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def query(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        connection = self._connect()
        try:
            return [dict(row) for row in connection.execute(sql, parameters).fetchall()]
        finally:
            connection.close()

    def query_one(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.query(sql, parameters)
        return rows[0] if rows else None

    def export_snapshot(self) -> dict[str, Any]:
        closings = []
        for row in self.query("SELECT * FROM monthly_closings ORDER BY month"):
            snapshot_json = row.pop("snapshot_json")
            closings.append({**row, "snapshot": json.loads(snapshot_json)})
        return {
            "schema_version": SCHEMA_VERSION,
            "transactions": self.query("SELECT * FROM ledger_transactions ORDER BY occurred_on, transaction_id"),
            "budgets": self.query("SELECT * FROM budgets ORDER BY month, category"),
            "savings_accounts": self.query("SELECT * FROM savings_accounts ORDER BY opened_on, account_id"),
            "savings_contributions": self.query(
                "SELECT * FROM savings_contributions ORDER BY contributed_on, contribution_id"
            ),
            "monthly_closings": closings,
        }

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "ready", "initialized": False, "schema_version": SCHEMA_VERSION}
        row = self.query_one("PRAGMA integrity_check")
        healthy = bool(row) and next(iter(row.values())) == "ok"
        return {
            "status": "healthy" if healthy else "degraded",
            "initialized": True,
            "schema_version": SCHEMA_VERSION,
            "database_path": str(self.database_path),
        }
