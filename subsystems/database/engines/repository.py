from __future__ import annotations

import json
import sqlite3
from typing import Any

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.foundation.engines.errors import ConcurrencyError
from subsystems.foundation.engines.time import utc_now_iso


class RecordRepository:
    """Public repository for versioned canonical records."""

    def __init__(self, connections: SQLiteConnectionLayer) -> None:
        self.connections = connections

    def create(
        self,
        module_id: str,
        entity_type: str,
        record_id: str,
        payload: dict[str, Any],
        *,
        owner: str = "owner",
        source: str = "living-os",
        privacy_class: str = "personal",
        correlation_id: str = "",
        connection: sqlite3.Connection | None = None,
    ) -> dict[str, Any]:
        if connection is None:
            with self.connections.transaction() as owned:
                return self.create(
                    module_id,
                    entity_type,
                    record_id,
                    payload,
                    owner=owner,
                    source=source,
                    privacy_class=privacy_class,
                    correlation_id=correlation_id,
                    connection=owned,
                )
        now = utc_now_iso()
        connection.execute(
            """INSERT INTO records(
                   module_id,entity_type,record_id,version,payload_json,privacy_class,
                   created_at,updated_at,status,owner,source,archived_at,correlation_id
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                module_id,
                entity_type,
                record_id,
                1,
                self._encode(payload),
                privacy_class,
                now,
                now,
                "ACTIVE",
                owner,
                source,
                None,
                correlation_id,
            ),
        )
        return self.read(module_id, entity_type, record_id, connection=connection) or {}

    def read(
        self,
        module_id: str,
        entity_type: str,
        record_id: str,
        *,
        connection: sqlite3.Connection | None = None,
    ) -> dict[str, Any] | None:
        if connection is None:
            with self.connections.connection(read_only=True) as owned:
                return self.read(module_id, entity_type, record_id, connection=owned)
        row = connection.execute(
            """SELECT * FROM records
               WHERE module_id=? AND entity_type=? AND record_id=?""",
            (module_id, entity_type, record_id),
        ).fetchone()
        return self._decode(row) if row else None

    def update(
        self,
        module_id: str,
        entity_type: str,
        record_id: str,
        payload: dict[str, Any],
        *,
        expected_version: int,
        source: str = "living-os",
        correlation_id: str = "",
        connection: sqlite3.Connection | None = None,
    ) -> dict[str, Any]:
        if connection is None:
            with self.connections.transaction() as owned:
                return self.update(
                    module_id,
                    entity_type,
                    record_id,
                    payload,
                    expected_version=expected_version,
                    source=source,
                    correlation_id=correlation_id,
                    connection=owned,
                )
        cursor = connection.execute(
            """UPDATE records SET
                   payload_json=?,version=version+1,updated_at=?,source=?,correlation_id=?
               WHERE module_id=? AND entity_type=? AND record_id=?
                 AND version=? AND status!='ARCHIVED'""",
            (
                self._encode(payload),
                utc_now_iso(),
                source,
                correlation_id,
                module_id,
                entity_type,
                record_id,
                expected_version,
            ),
        )
        if cursor.rowcount != 1:
            raise ConcurrencyError("Record is missing, archived, or has a newer version.")
        return self.read(module_id, entity_type, record_id, connection=connection) or {}

    def archive(
        self,
        module_id: str,
        entity_type: str,
        record_id: str,
        *,
        expected_version: int,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        with self.connections.transaction() as connection:
            now = utc_now_iso()
            cursor = connection.execute(
                """UPDATE records SET
                       status='ARCHIVED',archived_at=?,updated_at=?,version=version+1,
                       correlation_id=?
                   WHERE module_id=? AND entity_type=? AND record_id=?
                     AND version=? AND status!='ARCHIVED'""",
                (
                    now,
                    now,
                    correlation_id,
                    module_id,
                    entity_type,
                    record_id,
                    expected_version,
                ),
            )
            if cursor.rowcount != 1:
                raise ConcurrencyError("Record is missing, archived, or has a newer version.")
            return self.read(module_id, entity_type, record_id, connection=connection) or {}

    def list(
        self,
        module_id: str,
        entity_type: str,
        *,
        include_archived: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 1000))
        sql = "SELECT * FROM records WHERE module_id=? AND entity_type=?"
        parameters: list[Any] = [module_id, entity_type]
        if not include_archived:
            sql += " AND status!='ARCHIVED'"
        sql += " ORDER BY updated_at DESC LIMIT ?"
        parameters.append(safe_limit)
        with self.connections.connection(read_only=True) as connection:
            rows = connection.execute(sql, tuple(parameters)).fetchall()
        return [self._decode(row) for row in rows]

    def search(
        self,
        module_id: str,
        entity_type: str,
        query: str,
        *,
        include_archived: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        value = query.strip().lower()
        if not value:
            return self.list(
                module_id, entity_type, include_archived=include_archived, limit=limit
            )
        safe_limit = max(1, min(int(limit), 1000))
        sql = """SELECT * FROM records
                 WHERE module_id=? AND entity_type=?
                   AND (lower(record_id) LIKE ? OR lower(payload_json) LIKE ?)"""
        parameters: list[Any] = [module_id, entity_type, f"%{value}%", f"%{value}%"]
        if not include_archived:
            sql += " AND status!='ARCHIVED'"
        sql += " ORDER BY updated_at DESC LIMIT ?"
        parameters.append(safe_limit)
        with self.connections.connection(read_only=True) as connection:
            rows = connection.execute(sql, tuple(parameters)).fetchall()
        return [self._decode(row) for row in rows]

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        return {
            **json.loads(row["payload_json"]),
            "id": row["record_id"],
            "_module_id": row["module_id"],
            "_entity_type": row["entity_type"],
            "_version": int(row["version"]),
            "_status": row["status"],
            "_owner": row["owner"],
            "_source": row["source"],
            "_privacy_class": row["privacy_class"],
            "_created_at": row["created_at"],
            "_updated_at": row["updated_at"],
            "_archived_at": row["archived_at"],
            "_correlation_id": row["correlation_id"],
        }
