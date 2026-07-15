from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_text(value: Any, field: str, maximum: int = 200) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required.")
    if len(text) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters.")
    return text


def optional_text(value: Any, maximum: int = 1000) -> str:
    text = str(value or "").strip()
    if len(text) > maximum:
        raise ValueError(f"Text must be at most {maximum} characters.")
    return text


def require_amount(value: Any, field: str = "amount", allow_zero: bool = False) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer monetary amount.")
    try:
        numeric = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be an integer monetary amount.") from exc
    if not numeric.is_finite() or numeric != numeric.to_integral_value():
        raise ValueError(f"{field} must be an integer monetary amount.")
    amount = int(numeric)
    minimum = 0 if allow_zero else 1
    if amount < minimum:
        qualifier = "zero or greater" if allow_zero else "greater than zero"
        raise ValueError(f"{field} must be {qualifier}.")
    if amount > 9_000_000_000_000_000:
        raise ValueError(f"{field} exceeds the supported range.")
    return amount


def require_date(value: Any, field: str = "date") -> str:
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    else:
        try:
            parsed = date.fromisoformat(str(value or "").strip())
        except ValueError as exc:
            raise ValueError(f"{field} must use YYYY-MM-DD.") from exc
    return parsed.isoformat()


def require_month(value: Any) -> str:
    text = str(value or "").strip()
    try:
        parsed = date.fromisoformat(f"{text}-01")
    except ValueError as exc:
        raise ValueError("month must use YYYY-MM.") from exc
    return parsed.strftime("%Y-%m")


def require_rate_bps(value: Any) -> int:
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("annual_interest_rate must be a number.") from exc
    if rate < 0 or rate > 100:
        raise ValueError("annual_interest_rate must be between 0 and 100.")
    return int((rate * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def rate_percent(basis_points: int) -> str:
    return format(Decimal(basis_points) / Decimal(100), "f")
