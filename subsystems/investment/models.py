from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any


INVESTMENT_STATUSES = ("WATCHLIST", "ACTIVE", "CLOSED", "ARCHIVED")
ASSET_TYPES = ("STOCK", "ETF", "FUND", "BOND", "CRYPTO", "CASH", "OTHER")


@dataclass
class InvestmentRecord:
    investment_id: str
    name: str
    asset_type: str = "STOCK"
    symbol: str = ""
    quantity: float = 0.0
    unit_cost: float = 0.0
    current_price: float = 0.0
    currency: str = "KRW"
    status: str = "WATCHLIST"
    opened_on: str = ""
    closed_on: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.investment_id.strip() or not self.name.strip():
            raise ValueError("investment_id and name are required.")
        if self.asset_type not in ASSET_TYPES:
            raise ValueError(f"Unsupported asset type: {self.asset_type}")
        if self.status not in INVESTMENT_STATUSES:
            raise ValueError(f"Unsupported Investment status: {self.status}")
        if float(self.quantity) < 0 or float(self.unit_cost) < 0 or float(self.current_price) < 0:
            raise ValueError("quantity and prices cannot be negative.")
        if not self.currency.strip():
            raise ValueError("currency is required.")
        for field_name in ("opened_on", "closed_on"):
            value = getattr(self, field_name)
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO date.") from exc
        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)
            if value:
                try:
                    datetime.fromisoformat(value)
                except ValueError as exc:
                    raise ValueError(f"{field_name} must be an ISO timestamp.") from exc
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
