from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso
from subsystems.investment.models import InvestmentRecord
from subsystems.investment.repository import InvestmentRepository


class InvestmentSubsystem:
    subsystem_id = "SUB-INVESTMENT"
    VERSION = "1.0.0"

    def __init__(self, root: Path, database_path: Path | None = None, database_foundation: Any = None) -> None:
        path = Path(database_path) if database_path else Path(root) / "data" / "investment" / "investment.sqlite3"
        self.repository = InvestmentRepository(path, database_foundation)
        self.repository.register_contract(
            schema_version=1, migration_id="investment-schema-v1", integration_mode="record-repository"
        )
        self.database_foundation = database_foundation

    def create(self, name: str, **fields: Any) -> dict[str, Any]:
        now = utc_now_iso()
        record = InvestmentRecord(
            investment_id=str(fields.pop("investment_id", "") or uuid4()), name=name,
            created_at=now, updated_at=now, **fields,
        )
        result = self.repository.create(record.to_dict())
        self._execution("create", result["investment_id"])
        return result

    def get(self, investment_id: str) -> dict[str, Any] | None:
        result = self.repository.get(investment_id)
        self._execution("read", investment_id)
        return result

    def update(self, investment_id: str, **changes: Any) -> dict[str, Any]:
        current = self.repository.get(investment_id)
        if current is None:
            raise KeyError(investment_id)
        payload = {**current, **changes, "investment_id": investment_id, "updated_at": utc_now_iso()}
        InvestmentRecord(**payload).validate()
        result = self.repository.update(investment_id, payload)
        self._execution("update", investment_id)
        return result

    def update_valuation(self, investment_id: str, current_price: float) -> dict[str, Any]:
        result = self.update(investment_id, current_price=current_price)
        self._execution("valuation", investment_id)
        return result

    def archive(self, investment_id: str) -> dict[str, Any]:
        result = self.update(investment_id, status="ARCHIVED")
        self._execution("archive", investment_id)
        return result

    def list(self, **filters: Any) -> list[dict[str, Any]]:
        return self.repository.list(**filters)

    def health(self) -> dict[str, Any]:
        return self.repository.health()

    def management_summary(self) -> dict[str, Any]:
        records = self.list(include_archived=True, limit=1000)
        active = [item for item in records if item["status"] == "ACTIVE"]
        by_currency: dict[str, dict[str, float]] = defaultdict(lambda: {"cost": 0.0, "value": 0.0, "gain": 0.0})
        for item in active:
            cost = float(item["quantity"]) * float(item["unit_cost"])
            value = float(item["quantity"]) * float(item["current_price"])
            bucket = by_currency[item["currency"]]
            bucket["cost"] += cost
            bucket["value"] += value
            bucket["gain"] += value - cost
        executions = self._executions()
        return {
            "total": len(records), "active": len(active), "archived": sum(r["status"] == "ARCHIVED" for r in records),
            "by_status": dict(Counter(r["status"] for r in records)),
            "by_asset_type": dict(Counter(r["asset_type"] for r in records)),
            "valuation_by_currency": dict(by_currency), "health": self.health(),
            "execution_success": sum(e["status"] == "COMPLETED" for e in executions),
            "execution_failure": sum(e["status"] == "FAILED" for e in executions),
            "registry_registered": any(e.get("component_id") == self.subsystem_id for e in
                                       (self.database_foundation.registered_components() if self.database_foundation else [])),
        }

    def _execution(self, action: str, target: str) -> None:
        try:
            if self.database_foundation and self.database_foundation.current_schema_version() >= self.database_foundation.expected_schema_version:
                self.database_foundation.executions.record(
                    self.subsystem_id, action, target, "COMPLETED", actor="investment",
                    result={"target_id": target, "version": "v1.9"},
                )
        except Exception:
            return

    def _executions(self) -> list[dict[str, Any]]:
        records = self.database_foundation.execution_records(500) if self.database_foundation else []
        return [item for item in records if item.get("subsystem") == self.subsystem_id]
