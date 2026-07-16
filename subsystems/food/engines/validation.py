from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


UNITS = {"g", "kg", "ml", "l", "item", "serving"}
MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack", "other"}
NUTRIENTS = ("calories", "protein", "carbohydrate", "fat")


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
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD).") from exc


def optional_identifier(value: Any, field: str) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return require_text(value, field, 200)


def require_choice(value: Any, field: str, choices: set[str]) -> str:
    clean = str(value or "").strip().lower()
    if clean not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(choices))}.")
    return clean


def decimal_string(value: Any, field: str, *, positive: bool = False,
                   maximum: Decimal = Decimal("1000000000")) -> str:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a valid decimal number.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field} must be a valid decimal number.") from exc
    if not number.is_finite() or number < 0 or (positive and number <= 0) or number > maximum:
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{field} must be a {qualifier} finite decimal number.")
    if number.as_tuple().exponent < -3:
        raise ValueError(f"{field} must have at most three decimal places.")
    normalized = format(number.normalize(), "f")
    return "0" if normalized in {"-0", ""} else normalized


def optional_decimal_string(value: Any, field: str) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return decimal_string(value, field)


def require_positive_integer(value: Any, field: str, maximum: int = 1_000_000) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer.")
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be a positive integer.") from exc
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{field} must be a positive integer.")
    if number <= 0 or number > maximum:
        raise ValueError(f"{field} must be between 1 and {maximum}.")
    return number


def instructions_json(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("instructions must be a list of text steps.")
    if len(value) > 200:
        raise ValueError("instructions must contain at most 200 steps.")
    return tuple(require_text(step, "instruction", 2000) for step in value)


def nutrition_values(value: Any, *, allow_none: bool = True) -> dict[str, str | None]:
    if value is None:
        if allow_none:
            return {name: None for name in NUTRIENTS}
        raise ValueError("nutrition values are required.")
    if not isinstance(value, dict):
        raise ValueError("nutrition must be a mapping.")
    unexpected = set(value) - set(NUTRIENTS)
    if unexpected:
        raise ValueError(f"Unsupported nutrition fields: {sorted(unexpected)}")
    return {
        name: optional_decimal_string(value.get(name), name)
        for name in NUTRIENTS
    }
