from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, cast


F = TypeVar("F", bound=Callable[..., Any])


def _foundation(instance: Any) -> Any:
    direct = getattr(instance, "database_foundation", None)
    if direct is not None:
        return direct
    store = getattr(instance, "_store", None)
    if store is not None and getattr(store, "foundation", None) is not None:
        return store.foundation
    repository = getattr(instance, "repository", None)
    if repository is not None and getattr(repository, "foundation", None) is not None:
        return repository.foundation
    return None


def _component_id(instance: Any) -> str:
    direct = str(getattr(instance, "subsystem_id", "")).strip()
    if direct:
        return direct
    for candidate in (
        getattr(instance, "_store", None),
        getattr(instance, "repository", None),
    ):
        value = str(getattr(candidate, "component_id", "")).strip()
        if value:
            return value
    return type(instance).__name__


def record_failures(action: str) -> Callable[[F], F]:
    """Record validation and domain failures without changing the original API."""

    def decorate(function: F) -> F:
        @wraps(function)
        def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
            try:
                return function(self, *args, **kwargs)
            except Exception as exc:
                foundation = _foundation(self)
                try:
                    if (
                        foundation is not None
                        and foundation.current_schema_version()
                        >= foundation.expected_schema_version
                    ):
                        validation_failure = isinstance(exc, (ValueError, KeyError))
                        foundation.executions.record(
                            _component_id(self),
                            action,
                            f"{type(self).__name__}.{function.__name__}",
                            "FAILED",
                            actor=_component_id(self),
                            error=exc,
                            validation_result="FAILED" if validation_failure else "NOT_APPLICABLE",
                            failure_context={
                                "operation": function.__name__,
                                "argument_count": len(args),
                                "keyword_fields": sorted(str(key) for key in kwargs),
                            },
                        )
                except Exception:
                    # Observability must not replace the original domain error.
                    pass
                raise

        return cast(F, wrapped)

    return decorate
