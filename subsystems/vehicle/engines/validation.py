from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_text(value: Any, field: str, maximum: int = 500) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required.")
    if len(text) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters.")
    return text


def optional_text(value: Any, field: str, maximum: int = 4000) -> str:
    text = str(value or "").strip()
    if len(text) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters.")
    return text


def require_date(value: Any, field: str) -> str:
    text = require_text(value, field, 10)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD).") from exc
    return parsed.isoformat()


def optional_date(value: Any, field: str) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return require_date(value, field)


def require_non_negative_integer(value: Any, field: str,
                                 maximum: int = 10_000_000_000) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a non-negative integer.")
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be a non-negative integer.") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{field} must be a non-negative integer.")
    if number < 0 or number > maximum:
        raise ValueError(f"{field} must be between 0 and {maximum}.")
    return number


def optional_non_negative_integer(value: Any, field: str,
                                  maximum: int = 10_000_000_000) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    return require_non_negative_integer(value, field, maximum)


def require_choice(value: Any, field: str, choices: set[str]) -> str:
    clean = str(value or "").strip().lower()
    if clean not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(choices))}.")
    return clean


def optional_model_year(value: Any) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    maximum = date.today().year + 1
    number = require_non_negative_integer(value, "model_year", maximum)
    if number < 1886:
        raise ValueError(f"model_year must be between 1886 and {maximum}.")
    return number


def require_positive_milliunits(value: Any, field: str = "quantity") -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive number with at most three decimals.")
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a positive number with at most three decimals.") from exc
    scaled = decimal * 1000
    if not decimal.is_finite() or decimal <= 0 or scaled != scaled.to_integral_value():
        raise ValueError(f"{field} must be a positive number with at most three decimals.")
    if scaled > 10_000_000_000:
        raise ValueError(f"{field} is too large.")
    return int(scaled)
