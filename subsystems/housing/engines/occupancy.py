from __future__ import annotations

from typing import Any
from uuid import uuid4

from subsystems.housing.engines.storage import HousingStorageEngine
from subsystems.housing.engines.validation import (
    optional_text,
    require_non_negative_integer,
    require_text,
    utc_now_iso,
)


def _date(value: Any, field: str) -> str:
    from datetime import date

    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date.") from exc


class HousingOccupancyEngine:
    """Operational rental contracts and recurring housing charges."""

    def __init__(self, store: HousingStorageEngine) -> None:
        self.store = store

    def _available(self) -> bool:
        return bool(self.store.query_one(
            "SELECT 1 AS present FROM sqlite_master WHERE type='table' AND name='housing_contracts'"
        ))

    def _ensure_schema(self) -> None:
        if self._available():
            return
        with self.store.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS housing_contracts (
                    contract_id TEXT PRIMARY KEY, name TEXT NOT NULL, address TEXT NOT NULL,
                    start_on TEXT NOT NULL, end_on TEXT NOT NULL,
                    deposit INTEGER NOT NULL CHECK(deposit >= 0),
                    monthly_rent INTEGER NOT NULL CHECK(monthly_rent >= 0),
                    maintenance_fee INTEGER NOT NULL CHECK(maintenance_fee >= 0),
                    status TEXT NOT NULL CHECK(status IN ('active','completed','archived')),
                    note TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS housing_charges (
                    charge_id TEXT PRIMARY KEY, contract_id TEXT NOT NULL,
                    charged_on TEXT NOT NULL,
                    kind TEXT NOT NULL CHECK(kind IN ('rent','maintenance','utility','other')),
                    amount INTEGER NOT NULL CHECK(amount >= 0), note TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(contract_id) REFERENCES housing_contracts(contract_id)
                );
                CREATE INDEX IF NOT EXISTS ix_housing_contract_status
                    ON housing_contracts(status,start_on);
                CREATE INDEX IF NOT EXISTS ix_housing_charge_date
                    ON housing_charges(contract_id,charged_on,kind);
                """
            )

    def create_contract(
        self,
        name: Any,
        address: Any,
        start_on: Any,
        end_on: Any,
        deposit: Any,
        monthly_rent: Any,
        maintenance_fee: Any = 0,
        note: Any = "",
    ) -> dict[str, Any]:
        self._ensure_schema()
        start, end = _date(start_on, "start_on"), _date(end_on, "end_on")
        if start > end:
            raise ValueError("start_on cannot be after end_on.")
        now = utc_now_iso()
        row = {
            "contract_id": str(uuid4()),
            "name": require_text(name, "name", 200),
            "address": require_text(address, "address", 500),
            "start_on": start,
            "end_on": end,
            "deposit": require_non_negative_integer(deposit, "deposit"),
            "monthly_rent": require_non_negative_integer(monthly_rent, "monthly_rent"),
            "maintenance_fee": require_non_negative_integer(
                maintenance_fee, "maintenance_fee"
            ),
            "status": "active",
            "note": optional_text(note, "note"),
            "created_at": now,
            "updated_at": now,
        }
        columns = tuple(row)
        with self.store.transaction() as connection:
            connection.execute(
                f"INSERT INTO housing_contracts({','.join(columns)}) "
                f"VALUES({','.join('?' for _ in columns)})",
                tuple(row[column] for column in columns),
            )
        return row

    def get_contract(self, contract_id: Any) -> dict[str, Any]:
        if not self._available():
            raise KeyError("Housing contract not found.")
        key = require_text(contract_id, "contract_id", 100)
        row = self.store.query_one(
            "SELECT * FROM housing_contracts WHERE contract_id=?", (key,)
        )
        if row is None:
            raise KeyError("Housing contract not found.")
        return row

    def list_contracts(
        self, status: Any | None = None, search: str | None = None
    ) -> list[dict[str, Any]]:
        if not self._available():
            return []
        rows = self.store.query(
            "SELECT * FROM housing_contracts ORDER BY start_on DESC,created_at DESC"
        )
        selected = str(status or "").strip().lower()
        needle = str(search or "").strip().casefold()
        return [
            row
            for row in rows
            if (not selected or row["status"] == selected)
            and (
                not needle
                or needle
                in f"{row['name']} {row['address']} {row['note']}".casefold()
            )
        ]

    def update_contract(self, contract_id: Any, **changes: Any) -> dict[str, Any]:
        current = self.get_contract(contract_id)
        allowed = {
            "name", "address", "start_on", "end_on", "deposit",
            "monthly_rent", "maintenance_fee", "status", "note",
        }
        unexpected = set(changes) - allowed
        if unexpected:
            raise ValueError(f"Unsupported Housing contract fields: {sorted(unexpected)}")
        start = _date(changes.get("start_on", current["start_on"]), "start_on")
        end = _date(changes.get("end_on", current["end_on"]), "end_on")
        if start > end:
            raise ValueError("start_on cannot be after end_on.")
        status = str(changes.get("status", current["status"])).strip().lower()
        if status not in {"active", "completed", "archived"}:
            raise ValueError("status must be active, completed, or archived.")
        values = (
            require_text(changes.get("name", current["name"]), "name", 200),
            require_text(changes.get("address", current["address"]), "address", 500),
            start,
            end,
            require_non_negative_integer(changes.get("deposit", current["deposit"]), "deposit"),
            require_non_negative_integer(
                changes.get("monthly_rent", current["monthly_rent"]), "monthly_rent"
            ),
            require_non_negative_integer(
                changes.get("maintenance_fee", current["maintenance_fee"]),
                "maintenance_fee",
            ),
            status,
            optional_text(changes.get("note", current["note"]), "note"),
            utc_now_iso(),
            current["contract_id"],
        )
        with self.store.transaction() as connection:
            connection.execute(
                """UPDATE housing_contracts SET name=?,address=?,start_on=?,end_on=?,
                   deposit=?,monthly_rent=?,maintenance_fee=?,status=?,note=?,updated_at=?
                   WHERE contract_id=?""",
                values,
            )
        return self.get_contract(current["contract_id"])

    def record_charge(
        self, contract_id: Any, charged_on: Any, kind: Any, amount: Any, note: Any = ""
    ) -> dict[str, Any]:
        contract = self.get_contract(contract_id)
        charge_kind = str(kind or "").strip().lower()
        if charge_kind not in {"rent", "maintenance", "utility", "other"}:
            raise ValueError("kind must be rent, maintenance, utility, or other.")
        row = {
            "charge_id": str(uuid4()),
            "contract_id": contract["contract_id"],
            "charged_on": _date(charged_on, "charged_on"),
            "kind": charge_kind,
            "amount": require_non_negative_integer(amount, "amount"),
            "note": optional_text(note, "note"),
            "created_at": utc_now_iso(),
        }
        with self.store.transaction() as connection:
            connection.execute(
                "INSERT INTO housing_charges VALUES(?,?,?,?,?,?,?)", tuple(row.values())
            )
        return row

    def list_charges(
        self,
        contract_id: Any,
        start_on: Any | None = None,
        end_on: Any | None = None,
        kind: Any | None = None,
    ) -> list[dict[str, Any]]:
        contract = self.get_contract(contract_id)
        sql, params = "SELECT * FROM housing_charges WHERE contract_id=?", [
            contract["contract_id"]
        ]
        if start_on is not None:
            sql += " AND charged_on>=?"
            params.append(_date(start_on, "start_on"))
        if end_on is not None:
            sql += " AND charged_on<=?"
            params.append(_date(end_on, "end_on"))
        if len(params) >= 3 and params[-2] > params[-1]:
            raise ValueError("start_on cannot be after end_on.")
        if kind is not None:
            selected = str(kind).strip().lower()
            if selected not in {"rent", "maintenance", "utility", "other"}:
                raise ValueError("Unsupported charge kind.")
            sql += " AND kind=?"
            params.append(selected)
        return self.store.query(sql + " ORDER BY charged_on DESC,created_at DESC", tuple(params))

    def delete_charge(self, charge_id: Any) -> bool:
        key = require_text(charge_id, "charge_id", 100)
        with self.store.transaction() as connection:
            cursor = connection.execute(
                "DELETE FROM housing_charges WHERE charge_id=?", (key,)
            )
        if cursor.rowcount != 1:
            raise KeyError("Housing charge not found.")
        return True

    def report(self, contract_id: Any) -> dict[str, Any]:
        contract = self.get_contract(contract_id)
        charges = self.list_charges(contract_id)
        totals: dict[str, int] = {"rent": 0, "maintenance": 0, "utility": 0, "other": 0}
        for row in charges:
            totals[row["kind"]] += int(row["amount"])
        return {
            "contract": contract,
            "charge_count": len(charges),
            "totals": totals,
            "total_paid": sum(totals.values()),
            "expected_monthly_cost": int(contract["monthly_rent"])
            + int(contract["maintenance_fee"]),
            "charges": charges,
        }
