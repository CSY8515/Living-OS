from __future__ import annotations

from typing import Any

from subsystems.finance.engines.ledger import LedgerEngine
from subsystems.finance.engines.validation import require_month


class CashFlowEngine:
    def __init__(self, ledger: LedgerEngine) -> None:
        self.ledger = ledger

    def monthly(self, month: Any) -> dict[str, int | str]:
        normalized = require_month(month)
        totals = self.ledger.totals_for_month(normalized)
        return {
            "month": normalized, "income": totals["income"], "expense": totals["expense"],
            "net_cash_flow": totals["income"] - totals["expense"],
        }
