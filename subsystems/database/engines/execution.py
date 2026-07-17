from __future__ import annotations

import json
import time
from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.foundation.engines.time import utc_now_iso


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
    ) -> Iterator[dict[str, Any]]:
        execution_id = str(uuid4())
        trace_id = correlation_id or str(uuid4())
        state: dict[str, Any] = {
            "execution_id": execution_id,
            "trace_id": trace_id,
            "result": {},
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
        )
        try:
            yield state
        except Exception as exc:
            self._finish(
                execution_id,
                "FAILED",
                started,
                state.get("result", {}),
                type(exc).__name__,
                str(exc),
            )
            raise
        else:
            self._finish(execution_id, "COMPLETED", started, state.get("result", {}), "", "")

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._available():
            return []
        safe_limit = max(1, min(int(limit), 500))
        with self.connections.connection(read_only=True) as connection:
            rows = connection.execute(
                "SELECT * FROM execution_records ORDER BY started_at DESC, rowid DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [
            {**dict(row), "result": json.loads(row["result_json"] or "{}")}
            for row in rows
        ]

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
    ) -> str:
        execution_id = str(uuid4())
        trace_id = correlation_id or str(uuid4())
        if not self._available():
            return execution_id
        now = utc_now_iso()
        error_code = type(error).__name__ if error else ""
        error_message = str(error)[:500] if error else ""
        with self.connections.transaction() as connection:
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
                    now,
                    now,
                    0,
                    json.dumps(result or {}, ensure_ascii=False, sort_keys=True, default=str),
                    error_code,
                    error_message,
                    actor,
                    source,
                    correlation_id,
                    trace_id,
                ),
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
    ) -> None:
        if not self._available():
            return
        with self.connections.transaction() as connection:
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
    ) -> None:
        if not self._available():
            return
        duration_ms = int((time.perf_counter() - started) * 1000)
        safe_error = error_message[:500]
        with self.connections.transaction() as connection:
            connection.execute(
                """UPDATE execution_records SET
                       status=?,completed_at=?,duration_ms=?,result_json=?,
                       error_code=?,error_message=? WHERE execution_id=?""",
                (
                    status,
                    utc_now_iso(),
                    duration_ms,
                    json.dumps(result, ensure_ascii=False, sort_keys=True, default=str),
                    error_code,
                    safe_error,
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
