from __future__ import annotations

import json
import time
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.foundation.engines.time import utc_now_iso
from subsystems.foundation.engines.version import PRODUCT_VERSION


class ExecutionRecorder:
    def __init__(self, connections: SQLiteConnectionLayer) -> None:
        self.connections = connections

    @contextmanager
    def track(
        self,
        subsystem: str,
        action: str,
        target: str,
        *,
        actor: str,
        source: str = "living-os",
        correlation_id: str = "",
        retry_count: int = 0,
        recovery_result: str = "",
        validation_result: str = "PENDING",
        failure_context: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        execution_id = str(uuid4())
        trace_id = correlation_id or str(uuid4())
        state: dict[str, Any] = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "result": {},
            "retry_count": max(0, int(retry_count)),
            "recovery_result": recovery_result,
            "validation_result": validation_result,
            "failure_context": dict(failure_context or {}),
        }
        started_at = utc_now_iso()
        started = time.perf_counter()
        self._insert(
            execution_id,
            subsystem,
            action,
            target,
            "RUNNING",
            started_at,
            actor,
            source,
            correlation_id,
            trace_id,
            state,
        )
        try:
            yield state
        except Exception as exc:
            context = {
                **dict(state.get("failure_context", {})),
                "exception_type": type(exc).__name__,
                "action": action,
                "target": target,
            }
            validation = str(state.get("validation_result", ""))
            if isinstance(exc, (ValueError, KeyError)):
                validation = "FAILED"
            elif validation == "PENDING":
                validation = "NOT_APPLICABLE"
            self._finish(
                execution_id,
                "FAILED",
                started,
                state.get("result", {}),
                type(exc).__name__,
                str(exc),
                retry_count=int(state.get("retry_count", 0)),
                recovery_result=str(state.get("recovery_result", "")),
                validation_result=validation,
                failure_context=context,
            )
            raise
        else:
            validation = str(state.get("validation_result", "PENDING"))
            self._finish(
                execution_id,
                "COMPLETED",
                started,
                state.get("result", {}),
                "",
                "",
                retry_count=int(state.get("retry_count", 0)),
                recovery_result=str(state.get("recovery_result", "")),
                validation_result="PASSED" if validation == "PENDING" else validation,
                failure_context=dict(state.get("failure_context", {})),
            )

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._available():
            return []
        safe_limit = max(1, min(int(limit), 500))
        with self.connections.connection(read_only=True) as connection:
            rows = connection.execute(
                "SELECT * FROM execution_records ORDER BY started_at DESC, rowid DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["result"] = self._json_object(item.pop("result_json", "{}"))
            item["failure_context"] = self._json_object(
                item.pop("failure_context_json", "{}")
            )
            item.setdefault("retry_count", 0)
            item.setdefault("recovery_result", "")
            item.setdefault("product_version", "")
            item.setdefault("validation_result", "")
            item.setdefault("recorded_at", item.get("started_at", ""))
            result.append(item)
        return result

    def record(
        self,
        subsystem: str,
        action: str,
        target: str,
        status: str,
        *,
        actor: str,
        result: Any = None,
        error: Exception | None = None,
        source: str = "living-os",
        correlation_id: str = "",
        retry_count: int = 0,
        recovery_result: str = "",
        product_version: str = PRODUCT_VERSION,
        validation_result: str = "",
        failure_context: dict[str, Any] | None = None,
    ) -> str:
        execution_id = str(uuid4())
        trace_id = correlation_id or str(uuid4())
        if not self._available():
            return execution_id
        now = utc_now_iso()
        error_code = type(error).__name__ if error else ""
        error_message = str(error)[:500] if error else ""
        context = dict(failure_context or {})
        if error:
            context.setdefault("exception_type", type(error).__name__)
            context.setdefault("action", action)
            context.setdefault("target", target)
        validation = validation_result or (
            "FAILED" if isinstance(error, (ValueError, KeyError)) else "NOT_APPLICABLE"
            if error
            else "PASSED"
        )
        with self.connections.transaction() as connection:
            if self._extended_available(connection):
                connection.execute(
                    """INSERT INTO execution_records(
                           execution_id,subsystem,action,target,status,started_at,completed_at,
                           duration_ms,result_json,error_code,error_message,actor,source,
                           correlation_id,trace_id,retry_count,recovery_result,product_version,
                           validation_result,failure_context_json,recorded_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        execution_id,
                        subsystem,
                        action,
                        target,
                        status,
                        now,
                        now,
                        0,
                        self._json(result or {}),
                        error_code,
                        error_message,
                        actor,
                        source,
                        correlation_id,
                        trace_id,
                        max(0, int(retry_count)),
                        recovery_result,
                        product_version,
                        validation,
                        self._json(context),
                        now,
                    ),
                )
            else:
                self._legacy_insert(
                    connection,
                    execution_id,
                    subsystem,
                    action,
                    target,
                    status,
                    now,
                    now,
                    0,
                    result or {},
                    error_code,
                    error_message,
                    actor,
                    source,
                    correlation_id,
                    trace_id,
                )
        return execution_id

    def _insert(
        self,
        execution_id: str,
        subsystem: str,
        action: str,
        target: str,
        status: str,
        started_at: str,
        actor: str,
        source: str,
        correlation_id: str,
        trace_id: str,
        state: dict[str, Any],
    ) -> None:
        if not self._available():
            return
        with self.connections.transaction() as connection:
            if self._extended_available(connection):
                connection.execute(
                    """INSERT INTO execution_records(
                           execution_id,subsystem,action,target,status,started_at,
                           actor,source,correlation_id,trace_id,retry_count,recovery_result,
                           product_version,validation_result,failure_context_json,recorded_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        execution_id,
                        subsystem,
                        action,
                        target,
                        status,
                        started_at,
                        actor,
                        source,
                        correlation_id,
                        trace_id,
                        int(state.get("retry_count", 0)),
                        str(state.get("recovery_result", "")),
                        PRODUCT_VERSION,
                        str(state.get("validation_result", "PENDING")),
                        self._json(state.get("failure_context", {})),
                        started_at,
                    ),
                )
            else:
                connection.execute(
                    """INSERT INTO execution_records(
                           execution_id,subsystem,action,target,status,started_at,
                           actor,source,correlation_id,trace_id
                       ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (
                        execution_id,
                        subsystem,
                        action,
                        target,
                        status,
                        started_at,
                        actor,
                        source,
                        correlation_id,
                        trace_id,
                    ),
                )

    def _finish(
        self,
        execution_id: str,
        status: str,
        started: float,
        result: Any,
        error_code: str,
        error_message: str,
        *,
        retry_count: int,
        recovery_result: str,
        validation_result: str,
        failure_context: dict[str, Any],
    ) -> None:
        if not self._available():
            return
        duration_ms = int((time.perf_counter() - started) * 1000)
        with self.connections.transaction() as connection:
            if self._extended_available(connection):
                connection.execute(
                    """UPDATE execution_records SET
                           status=?,completed_at=?,duration_ms=?,result_json=?,
                           error_code=?,error_message=?,retry_count=?,recovery_result=?,
                           product_version=?,validation_result=?,failure_context_json=?
                       WHERE execution_id=?""",
                    (
                        status,
                        utc_now_iso(),
                        duration_ms,
                        self._json(result),
                        error_code,
                        error_message[:500],
                        max(0, int(retry_count)),
                        recovery_result,
                        PRODUCT_VERSION,
                        validation_result,
                        self._json(failure_context),
                        execution_id,
                    ),
                )
            else:
                connection.execute(
                    """UPDATE execution_records SET
                           status=?,completed_at=?,duration_ms=?,result_json=?,
                           error_code=?,error_message=? WHERE execution_id=?""",
                    (
                        status,
                        utc_now_iso(),
                        duration_ms,
                        self._json(result),
                        error_code,
                        error_message[:500],
                        execution_id,
                    ),
                )

    def _available(self) -> bool:
        if not self.connections.database_path.is_file():
            return False
        try:
            with self.connections.connection(read_only=True) as connection:
                row = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='execution_records'"
                ).fetchone()
            return row is not None
        except Exception:
            return False

    @staticmethod
    def _extended_available(connection: Any) -> bool:
        columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(execution_records)").fetchall()
        }
        return {
            "retry_count",
            "recovery_result",
            "product_version",
            "validation_result",
            "failure_context_json",
            "recorded_at",
        }.issubset(columns)

    @staticmethod
    def _legacy_insert(
        connection: Any,
        execution_id: str,
        subsystem: str,
        action: str,
        target: str,
        status: str,
        started_at: str,
        completed_at: str,
        duration_ms: int,
        result: Any,
        error_code: str,
        error_message: str,
        actor: str,
        source: str,
        correlation_id: str,
        trace_id: str,
    ) -> None:
        connection.execute(
            """INSERT INTO execution_records(
                   execution_id,subsystem,action,target,status,started_at,completed_at,
                   duration_ms,result_json,error_code,error_message,actor,source,
                   correlation_id,trace_id
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                execution_id,
                subsystem,
                action,
                target,
                status,
                started_at,
                completed_at,
                duration_ms,
                ExecutionRecorder._json(result),
                error_code,
                error_message,
                actor,
                source,
                correlation_id,
                trace_id,
            ),
        )

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)

    @staticmethod
    def _json_object(value: Any) -> dict[str, Any]:
        try:
            decoded = json.loads(str(value or "{}"))
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {"value": decoded}
