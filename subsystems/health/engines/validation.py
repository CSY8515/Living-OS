from __future__ import annotations

import math
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_text(value: Any, field: str, maximum: int = 500) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required.")
    if len(text) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters.")
    return text


def optional_text(value: Any, maximum: int = 2000) -> str:
    text = str(value or "").strip()
    if len(text) > maximum:
        raise ValueError(f"Text must be at most {maximum} characters.")
    return text


def require_date(value: Any, field: str) -> str:
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.isoformat()
    try:
        return date.fromisoformat(str(value)).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date.") from exc


def require_datetime(value: Any, field: str) -> str:
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be an ISO date-time.") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone offset.")
    return parsed.isoformat()


def require_decimal(value: Any, field: str, minimum: str, maximum: str) -> str:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric.")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be numeric.") from exc
    if not number.is_finite() or number < Decimal(minimum) or number > Decimal(maximum):
        raise ValueError(f"{field} must be between {minimum} and {maximum}.")
    return str(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def optional_decimal(value: Any, field: str, minimum: str, maximum: str) -> str | None:
    return None if value is None or value == "" else require_decimal(value, field, minimum, maximum)


def require_integer(value: Any, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer.")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer.") from exc
    if str(value).strip() not in {str(number), f"{number}.0"} and not isinstance(value, int):
        raise ValueError(f"{field} must be an integer.")
    if number < minimum or number > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}.")
    return number


def require_metrics(value: Any) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("metrics must be an object.")
    result: dict[str, float] = {}
    for raw_key, raw_value in value.items():
        key = require_text(raw_key, "metric name", 80)
        if isinstance(raw_value, bool):
            raise ValueError("metric values must be finite numbers.")
        try:
            number = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError("metric values must be finite numbers.") from exc
        if not math.isfinite(number):
            raise ValueError("metric values must be finite numbers.")
        result[key] = number
    return result
