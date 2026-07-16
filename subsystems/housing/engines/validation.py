from __future__ import annotations

from datetime import datetime, timezone
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


def require_non_negative_integer(value: Any, field: str, maximum: int = 10_000_000_000) -> int:
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


def require_boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean.")
    return value


def require_status(value: Any) -> str:
    status = str(value or "active").strip().lower()
    if status not in {"active", "shortlisted", "rejected", "selected"}:
        raise ValueError("status must be active, shortlisted, rejected, or selected.")
    return status
