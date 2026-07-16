from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from subsystems.housing.engines.validation import utc_now_iso


SCHEMA_VERSION = 1


class HousingStorageEngine:
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
                CREATE TABLE IF NOT EXISTS housing_meta (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS housing_candidates (
                    candidate_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    deposit INTEGER NOT NULL CHECK(deposit >= 0),
                    monthly_rent INTEGER NOT NULL CHECK(monthly_rent >= 0),
                    maintenance_fee INTEGER NOT NULL CHECK(maintenance_fee >= 0),
                    maintenance_fee_provided INTEGER NOT NULL CHECK(maintenance_fee_provided IN (0,1)),
                    total_monthly_cost INTEGER NOT NULL CHECK(total_monthly_cost >= 0),
                    commute_minutes INTEGER NOT NULL CHECK(commute_minutes BETWEEN 0 AND 1440),
                    parking_available INTEGER NOT NULL CHECK(parking_available IN (0,1)),
                    options_memo TEXT NOT NULL,
                    special_notes TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
                    grade TEXT NOT NULL CHECK(grade IN ('A','B','C','D')),
                    deductions_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('active','shortlisted','rejected','selected')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_housing_candidate_rank
                    ON housing_candidates(status, score DESC, total_monthly_cost, commute_minutes);
                CREATE TABLE IF NOT EXISTS housing_migration_ledger (
                    source_key TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    imported_at TEXT NOT NULL
                );
                """
            )
            now = utc_now_iso()
            connection.execute(
                """INSERT INTO housing_meta(key,value,updated_at) VALUES('schema_version',?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (str(SCHEMA_VERSION), now),
            )
            connection.execute(
                """INSERT INTO housing_meta(key,value,updated_at) VALUES('subsystem_version','1.0.0',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
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
            return [self._decode(dict(row)) for row in connection.execute(sql, parameters).fetchall()]
        finally:
            connection.close()

    def query_one(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.query(sql, parameters)
        return rows[0] if rows else None

    @staticmethod
    def _decode(row: dict[str, Any]) -> dict[str, Any]:
        if "deductions_json" in row:
            row["deductions"] = json.loads(row.pop("deductions_json"))
        for key in ("maintenance_fee_provided", "parking_available"):
            if key in row:
                row[key] = bool(row[key])
        return row

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

    def export_snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "privacy_class": "sensitive",
            "candidates": self.query("SELECT * FROM housing_candidates ORDER BY candidate_id"),
        }
