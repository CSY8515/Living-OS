from __future__ import annotations

import json
import sqlite3
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from subsystems.database.engines.connection import SQLiteConnectionLayer
from subsystems.database.engines.component import DatabaseIntegrationContract
from subsystems.database.engines.contracts import IntegrityResult, RestoreCandidate
from subsystems.database.engines.execution import ExecutionRecorder
from subsystems.database.engines.integrity import IntegrityEngine
from subsystems.database.engines.migrations import MigrationRegistry
from subsystems.database.engines.repository import RecordRepository
from subsystems.foundation.engines.backup import BackupService, sha256_file
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.time import utc_now_iso


class DatabaseSubsystem:
    """Living OS v1.7 data-plane facade for the canonical SQLite database."""

    subsystem_id = "SUB-DATABASE"
    version = "1.7.1"
    expected_schema_version = 3

    def __init__(
        self,
        database_path: Path,
        backup_root: Path,
        repository_root: Path,
        *,
        store: HubStore | None = None,
    ) -> None:
        self.database_path = Path(database_path)
        self.repository_root = Path(repository_root).resolve()
        self.backup_root = Path(backup_root)
        self.store = store or HubStore(self.database_path)
        self.connections = SQLiteConnectionLayer(self.database_path)
        self.migrations = MigrationRegistry(self.connections)
        self.repository = RecordRepository(self.connections)
        self.integrity = IntegrityEngine(self.connections)
        self.executions = ExecutionRecorder(self.connections)
        self.backups = BackupService(self.database_path, self.backup_root, self.repository_root)
        self._component_adapters: dict[str, Any] = {}

    def attach_component_adapter(self, adapter: Any) -> None:
        component_id = str(getattr(adapter, "component_id", "")).strip()
        if not component_id or not callable(getattr(adapter, "initialize", None)):
            raise ValueError("A component adapter must expose component_id and initialize().")
        self._component_adapters[component_id] = adapter

    def initialize(self, *, apply_migrations: bool = False, actor: str = "system") -> dict[str, Any]:
        self.store.initialize()
        applied: list[dict[str, Any]] = []
        if apply_migrations:
            applied = self.apply_migrations(actor=actor)
            self.executions.record(
                self.subsystem_id,
                "database_initialize",
                str(self.database_path),
                "COMPLETED",
                actor=actor,
                result={"schema_version": self.current_schema_version()},
            )
        return {
            "database_path": str(self.database_path),
            "schema_version": self.current_schema_version(),
            "expected_schema_version": self.expected_schema_version,
            "applied_migrations": applied,
        }

    @contextmanager
    def transaction(
        self, *, actor: str = "owner", correlation_id: str = ""
    ) -> Iterator[sqlite3.Connection]:
        with self.executions.track(
            self.subsystem_id,
            "transaction",
            str(self.database_path),
            actor=actor,
            correlation_id=correlation_id,
        ) as execution:
            with self.connections.transaction() as connection:
                yield connection
            execution["result"] = {"committed": True}

    def current_schema_version(self) -> int:
        return self.migrations.current_version()

    def pending_migrations(self) -> list[dict[str, Any]]:
        return [
            {"version": item.version, "name": item.name, "status": "PENDING"}
            for item in self.migrations.pending()
        ]

    def applied_migrations(self) -> list[dict[str, Any]]:
        return self.migrations.history("APPLIED")

    def failed_migrations(self) -> list[dict[str, Any]]:
        return self.migrations.failures()

    def apply_migrations(
        self, *, actor: str, correlation_id: str = ""
    ) -> list[dict[str, Any]]:
        self.store.initialize()
        pending = self.pending_migrations()
        if not pending:
            return []
        # The first v1.7 migration creates the Execution Database table, so its
        # own migration ledger is the durable initialization record.
        try:
            applied = self.migrations.apply_pending()
        except Exception as exc:
            self.executions.record(
                self.subsystem_id,
                "migration",
                str(self.database_path),
                "FAILED",
                actor=actor,
                correlation_id=correlation_id,
                error=exc,
            )
            raise
        else:
            self.executions.record(
                self.subsystem_id,
                "migration",
                str(self.database_path),
                "COMPLETED",
                actor=actor,
                correlation_id=correlation_id,
                result={"applied": applied},
            )
            return applied

    def create(self, *args: Any, actor: str = "owner", **kwargs: Any) -> dict[str, Any]:
        with self.executions.track(
            self.subsystem_id,
            "create",
            ".".join(str(value) for value in args[:3]),
            actor=actor,
            correlation_id=str(kwargs.get("correlation_id", "")),
        ) as execution:
            record = self.repository.create(*args, **kwargs)
            execution["result"] = {"record_id": record.get("id"), "version": record.get("_version")}
            return record

    def read(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
        return self.repository.read(*args, **kwargs)

    def update(self, *args: Any, actor: str = "owner", **kwargs: Any) -> dict[str, Any]:
        with self.executions.track(
            self.subsystem_id,
            "update",
            ".".join(str(value) for value in args[:3]),
            actor=actor,
            correlation_id=str(kwargs.get("correlation_id", "")),
        ) as execution:
            record = self.repository.update(*args, **kwargs)
            execution["result"] = {"record_id": record.get("id"), "version": record.get("_version")}
            return record

    def archive(self, *args: Any, actor: str = "owner", **kwargs: Any) -> dict[str, Any]:
        with self.executions.track(
            self.subsystem_id,
            "archive",
            ".".join(str(value) for value in args[:3]),
            actor=actor,
            correlation_id=str(kwargs.get("correlation_id", "")),
        ) as execution:
            record = self.repository.archive(*args, **kwargs)
            execution["result"] = {"record_id": record.get("id"), "status": record.get("_status")}
            return record

    def list(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return self.repository.list(*args, **kwargs)

    def search(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return self.repository.search(*args, **kwargs)

    def integrity_check(
        self, *, record: bool = True, actor: str = "system"
    ) -> IntegrityResult:
        if not record or self.current_schema_version() < self.expected_schema_version:
            return self.integrity.check(self.expected_schema_version)
        with self.executions.track(
            self.subsystem_id,
            "integrity_check",
            str(self.database_path),
            actor=actor,
        ) as execution:
            result = self.integrity.check(self.expected_schema_version)
            execution["result"] = {
                "status": result.status,
                "integrity": result.integrity,
                "foreign_key_violations": result.foreign_key_violations,
            }
            return result

    def schema_registry(self) -> dict[str, Any]:
        if not self.database_path.is_file():
            return {"schema_version": 0, "expected_schema_version": self.expected_schema_version, "tables": [], "indexes": []}
        with self.connections.connection(read_only=True) as connection:
            tables = [
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
                if not str(row[0]).startswith("sqlite_")
            ]
            indexes = [
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
                ).fetchall()
                if not str(row[0]).startswith("sqlite_")
            ]
        return {
            "schema_version": self.current_schema_version(),
            "expected_schema_version": self.expected_schema_version,
            "tables": tables,
            "indexes": indexes,
            "pending_migrations": self.pending_migrations(),
        }

    def create_backup(self, *, actor: str, correlation_id: str = "") -> Path:
        try:
            archive = self.backups.create()
            if not self.backups.verify(archive):
                raise ValueError("Backup verification failed.")
            checksum = sha256_file(archive)
            created_at = utc_now_iso()
            schema_version = self.current_schema_version()
            execution_id = self.executions.record(
                self.subsystem_id,
                "backup_create",
                str(self.database_path),
                "COMPLETED",
                actor=actor,
                correlation_id=correlation_id,
                result={"backup_path": str(archive), "checksum": checksum},
            )
            with self.connections.transaction() as connection:
                connection.execute(
                    """INSERT INTO backup_history(
                           backup_id,path,status,schema_version,size_bytes,checksum,
                           created_at,verified_at,execution_id
                       ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        str(uuid4()),
                        str(archive.resolve()),
                        "VERIFIED",
                        schema_version,
                        archive.stat().st_size,
                        checksum,
                        created_at,
                        utc_now_iso(),
                        execution_id,
                    ),
                )
            return archive
        except Exception as exc:
            self.executions.record(
                self.subsystem_id,
                "backup_create",
                str(self.database_path),
                "FAILED",
                actor=actor,
                correlation_id=correlation_id,
                error=exc,
            )
            raise

    def list_backups(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        if self.current_schema_version() >= self.expected_schema_version:
            with self.connections.connection(read_only=True) as connection:
                rows = [
                    dict(row)
                    for row in connection.execute(
                        "SELECT * FROM backup_history ORDER BY created_at DESC"
                    ).fetchall()
                ]
        known = {str(Path(row["path"]).resolve()) for row in rows}
        for path in sorted(self.backup_root.glob("*.zip"), reverse=True):
            if str(path.resolve()) not in known:
                candidate = self.validate_restore(path)
                rows.append(
                    {
                        "backup_id": "unregistered",
                        "path": str(path.resolve()),
                        "status": "VERIFIED" if candidate.valid else "INVALID",
                        "schema_version": candidate.schema_version,
                        "size_bytes": path.stat().st_size,
                        "checksum": sha256_file(path),
                        "created_at": candidate.created_at,
                        "verified_at": "",
                        "execution_id": "",
                    }
                )
        return sorted(rows, key=lambda item: str(item.get("created_at", "")), reverse=True)

    def validate_restore(self, archive_path: Path) -> RestoreCandidate:
        archive_path = Path(archive_path)
        try:
            if not archive_path.is_file() or not self.backups.verify(archive_path):
                raise ValueError("Backup verification failed.")
            with zipfile.ZipFile(archive_path, "r") as archive:
                manifest = json.loads(archive.read("manifest.json"))
                if "hub/living_os.sqlite3" not in archive.namelist():
                    raise ValueError("Backup does not contain the canonical database.")
                with tempfile.TemporaryDirectory() as directory:
                    staged = Path(directory) / "candidate.sqlite3"
                    staged.write_bytes(archive.read("hub/living_os.sqlite3"))
                    connection = sqlite3.connect(staged)
                    try:
                        integrity = connection.execute("PRAGMA integrity_check").fetchone()
                        row = connection.execute(
                            "SELECT value FROM system_meta WHERE key='schema_version'"
                        ).fetchone()
                    finally:
                        connection.close()
            if not integrity or integrity[0] != "ok":
                raise ValueError("Backup database failed its integrity check.")
            schema_version = int(row[0]) if row else 0
            if schema_version != self.expected_schema_version:
                raise ValueError("Backup schema version is not compatible with v1.7.")
            return RestoreCandidate(
                archive_path,
                True,
                schema_version,
                str(manifest.get("created_at", "")),
            )
        except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile, sqlite3.Error) as exc:
            return RestoreCandidate(archive_path, False, None, "", type(exc).__name__)

    def restore(
        self, archive_path: Path, *, actor: str, correlation_id: str = ""
    ) -> dict[str, Any]:
        candidate = self.validate_restore(archive_path)
        if not candidate.valid:
            raise ValueError(f"Restore candidate is invalid: {candidate.error}")
        target = str(Path(archive_path).resolve())
        safety_backup: Path | None = None
        try:
            restore_id = str(uuid4())
            started_at = utc_now_iso()
            control_plane_history = self._control_plane_history()
            safety_backup = self.backups.restore(Path(archive_path))
            try:
                result = self.integrity.check(self.expected_schema_version)
                if not result.healthy:
                    raise ValueError("Restored database did not pass v1.7 integrity checks.")
                self._merge_control_plane_history(control_plane_history)
            except Exception as validation_error:
                try:
                    self.backups.restore(safety_backup)
                except Exception as rollback_error:
                    raise RuntimeError(
                        "Restore validation and safety rollback both failed."
                    ) from rollback_error
                raise
            execution_id = self.executions.record(
                self.subsystem_id,
                "restore",
                target,
                "COMPLETED",
                actor=actor,
                correlation_id=correlation_id,
                result={
                    "restore_id": restore_id,
                    "safety_backup_path": str(safety_backup),
                },
            )
            with self.connections.transaction() as connection:
                connection.execute(
                    """INSERT INTO restore_history(
                           restore_id,backup_path,safety_backup_path,status,schema_version,
                           started_at,completed_at,error,execution_id
                       ) VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        restore_id,
                        str(Path(archive_path).resolve()),
                        str(safety_backup.resolve()),
                        "COMPLETED",
                        candidate.schema_version,
                        started_at,
                        utc_now_iso(),
                        "",
                        execution_id,
                    ),
                )
            return {
                "restore_id": restore_id,
                "safety_backup_path": str(safety_backup),
            }
        except Exception as exc:
            self.executions.record(
                self.subsystem_id,
                "restore",
                target,
                "FAILED",
                actor=actor,
                correlation_id=correlation_id,
                error=exc,
            )
            raise

    def restore_history(self) -> list[dict[str, Any]]:
        if self.current_schema_version() < self.expected_schema_version:
            return []
        with self.connections.connection(read_only=True) as connection:
            rows = connection.execute(
                "SELECT * FROM restore_history ORDER BY started_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def execution_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.executions.list(limit)

    def record_execution(
        self,
        subsystem: str,
        action: str,
        *,
        actor: str,
        result: dict[str, Any],
    ) -> str:
        return self.executions.record(
            subsystem,
            action,
            str(self.database_path),
            "COMPLETED",
            actor=actor,
            result=result,
        )

    def register_component(
        self,
        contract: DatabaseIntegrationContract,
        *,
        actor: str = "system",
    ) -> dict[str, Any]:
        """Persist an integration contract through the canonical RecordRepository."""
        payload = contract.to_payload()
        target = Path(contract.database_path).resolve()
        try:
            target.relative_to(self.repository_root)
        except ValueError as exc:
            raise ValueError("Component databases must remain inside the repository root.") from exc
        if self.current_schema_version() < self.expected_schema_version:
            raise RuntimeError("Database Foundation migration v3 is required before registration.")
        existing = self.repository.read(
            self.subsystem_id, "component_registration", contract.component_id
        )
        if existing:
            if all(existing.get(key) == value for key, value in payload.items()):
                return existing
            result = self.repository.update(
                self.subsystem_id,
                "component_registration",
                contract.component_id,
                payload,
                expected_version=int(existing["_version"]),
                source="database-foundation",
            )
        else:
            result = self.repository.create(
                self.subsystem_id,
                "component_registration",
                contract.component_id,
                payload,
                owner=contract.owner,
                source="database-foundation",
                privacy_class="system",
            )
        self.record_execution(
            contract.component_id,
            "database_contract_registration",
            actor=actor,
            result={"schema_version": contract.schema_version, "mode": contract.integration_mode},
        )
        return result

    def registered_components(self) -> list[dict[str, Any]]:
        if self.current_schema_version() < self.expected_schema_version:
            return []
        return self.repository.list(
            self.subsystem_id, "component_registration", limit=1000
        )

    def component_status(self) -> list[dict[str, Any]]:
        executions = self.execution_records(1000)
        statuses: list[dict[str, Any]] = []
        for registration in self.registered_components():
            path = Path(str(registration["database_path"]))
            initialized = path.is_file()
            integrity = "not-initialized"
            foreign_keys = 0
            actual_schema_version: int | None = None
            tables: list[str] = []
            size_bytes = path.stat().st_size if initialized else 0
            if initialized:
                layer = SQLiteConnectionLayer(path)
                try:
                    with layer.connection(read_only=True) as connection:
                        row = connection.execute("PRAGMA integrity_check").fetchone()
                        integrity = str(row[0]) if row else "unknown"
                        foreign_keys = len(connection.execute("PRAGMA foreign_key_check").fetchall())
                        tables = [
                            str(item[0])
                            for item in connection.execute(
                                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                            ).fetchall()
                        ]
                        for table in (name for name in tables if name.endswith("_meta")):
                            safe_table = table.replace('"', '""')
                            version_row = connection.execute(
                                f'SELECT value FROM "{safe_table}" WHERE key=?',
                                ("schema_version",),
                            ).fetchone()
                            if version_row:
                                actual_schema_version = int(version_row[0])
                                break
                except (OSError, sqlite3.Error, ValueError) as exc:
                    integrity = f"error:{type(exc).__name__}"
            component_executions = [
                item for item in executions if item.get("subsystem") == registration["component_id"]
            ]
            statuses.append(
                {
                    "component_id": registration["component_id"],
                    "display_name": registration["display_name"],
                    "layer": registration["layer"],
                    "owner": registration["owner"],
                    "integration_mode": registration["integration_mode"],
                    "database_path": str(path),
                    "initialized": initialized,
                    "schema_version": registration["schema_version"],
                    "actual_schema_version": actual_schema_version,
                    "tables": tables,
                    "migration_id": registration["migration_id"],
                    "integrity": integrity,
                    "foreign_key_violations": foreign_keys,
                    "size_bytes": size_bytes,
                    "execution_count": len(component_executions),
                    "last_execution": component_executions[0] if component_executions else None,
                    "migration_status": (
                        "PENDING_INITIALIZATION"
                        if not initialized
                        else "CURRENT"
                        if actual_schema_version == int(registration["schema_version"])
                        else "SCHEMA_MISMATCH"
                    ),
                    "status": (
                        "READY"
                        if not initialized
                        else "HEALTHY"
                        if (
                            integrity == "ok"
                            and not foreign_keys
                            and actual_schema_version == int(registration["schema_version"])
                        )
                        else "DEGRADED"
                    ),
                }
            )
        return statuses

    def initialize_component(self, component_id: str, *, actor: str) -> dict[str, Any]:
        self._registered_component(component_id)
        adapter = self._component_adapters.get(component_id)
        if adapter is None:
            raise RuntimeError("The component adapter is not attached to this runtime.")
        adapter.initialize()
        status = next(
            item for item in self.component_status() if item["component_id"] == component_id
        )
        if status["status"] != "HEALTHY":
            raise RuntimeError("Component schema initialization failed health verification.")
        self.record_execution(
            component_id,
            "component_schema_initialize",
            actor=actor,
            result={"schema_version": status["schema_version"]},
        )
        return status

    def create_component_backup(self, component_id: str, *, actor: str) -> Path:
        component = self._registered_component(component_id)
        source_path = Path(str(component["database_path"]))
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        destination_root = self.backup_root / "components" / component_id.lower()
        destination_root.mkdir(parents=True, exist_ok=True)
        destination = destination_root / (
            f"{component_id.lower()}-{utc_now_iso().replace(':', '')}-{uuid4().hex[:8]}.sqlite3"
        )
        source = SQLiteConnectionLayer(source_path)
        target = SQLiteConnectionLayer(destination)
        with source.connection(read_only=True) as source_connection:
            with target.connection() as target_connection:
                source_connection.backup(target_connection)
        with target.connection(read_only=True) as verification:
            check = verification.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            destination.unlink(missing_ok=True)
            raise RuntimeError("Component backup integrity verification failed.")
        backup_id = f"{component_id}-{uuid4()}"
        self.repository.create(
            self.subsystem_id,
            "component_backup",
            backup_id,
            {
                "component_id": component_id,
                "path": str(destination),
                "checksum": sha256_file(destination),
                "size_bytes": destination.stat().st_size,
                "status": "VERIFIED",
            },
            owner=component["owner"],
            source="database-management",
            privacy_class="system",
        )
        self.record_execution(
            component_id,
            "component_backup",
            actor=actor,
            result={"backup_id": backup_id, "path": str(destination)},
        )
        return destination

    def component_backups(self, component_id: str | None = None) -> list[dict[str, Any]]:
        if self.current_schema_version() < self.expected_schema_version:
            return []
        records = self.repository.list(
            self.subsystem_id, "component_backup", limit=1000
        )
        if component_id is not None:
            records = [item for item in records if item.get("component_id") == component_id]
        return records

    def restore_component_backup(
        self, component_id: str, backup_path: Path, *, actor: str
    ) -> dict[str, Any]:
        component = self._registered_component(component_id)
        candidate = Path(backup_path).resolve()
        allowed_root = (self.backup_root / "components" / component_id.lower()).resolve()
        try:
            candidate.relative_to(allowed_root)
        except ValueError as exc:
            raise ValueError("Backup is outside the registered component backup root.") from exc
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        with SQLiteConnectionLayer(candidate).connection(read_only=True) as connection:
            check = connection.execute("PRAGMA integrity_check").fetchone()
        if not check or check[0] != "ok":
            raise RuntimeError("Component restore candidate failed integrity validation.")
        safety = self.create_component_backup(component_id, actor=actor)
        target_path = Path(str(component["database_path"]))
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with SQLiteConnectionLayer(candidate).connection(read_only=True) as source:
                with SQLiteConnectionLayer(target_path).connection() as target:
                    source.backup(target)
            with SQLiteConnectionLayer(target_path).connection(read_only=True) as verification:
                restored_check = verification.execute("PRAGMA integrity_check").fetchone()
            if not restored_check or restored_check[0] != "ok":
                raise RuntimeError("Restored component failed integrity verification.")
        except Exception:
            with SQLiteConnectionLayer(safety).connection(read_only=True) as source:
                with SQLiteConnectionLayer(target_path).connection() as target:
                    source.backup(target)
            raise
        self.record_execution(
            component_id,
            "component_restore",
            actor=actor,
            result={"backup_path": str(candidate), "safety_backup": str(safety)},
        )
        return {"component_id": component_id, "restored_from": str(candidate), "safety_backup": str(safety)}

    def _registered_component(self, component_id: str) -> dict[str, Any]:
        record = self.repository.read(
            self.subsystem_id, "component_registration", component_id
        )
        if record is None or record.get("_status") == "ARCHIVED":
            raise KeyError(f"Unregistered database component: {component_id}")
        return record

    def _control_plane_history(self) -> dict[str, list[dict[str, Any]]]:
        if self.current_schema_version() < self.expected_schema_version:
            return {}
        history: dict[str, list[dict[str, Any]]] = {}
        with self.connections.connection(read_only=True) as connection:
            for table in ("execution_records", "backup_history", "restore_history"):
                history[table] = [
                    dict(row) for row in connection.execute(f"SELECT * FROM {table}").fetchall()
                ]
        return history

    def _merge_control_plane_history(
        self, history: dict[str, list[dict[str, Any]]]
    ) -> None:
        if not history:
            return
        columns = {
            "execution_records": (
                "execution_id", "subsystem", "action", "target", "status", "started_at",
                "completed_at", "duration_ms", "result_json", "error_code", "error_message",
                "actor", "source", "correlation_id", "trace_id",
            ),
            "backup_history": (
                "backup_id", "path", "status", "schema_version", "size_bytes", "checksum",
                "created_at", "verified_at", "execution_id",
            ),
            "restore_history": (
                "restore_id", "backup_path", "safety_backup_path", "status", "schema_version",
                "started_at", "completed_at", "error", "execution_id",
            ),
        }
        with self.connections.transaction() as connection:
            for table, rows in history.items():
                table_columns = columns[table]
                placeholders = ",".join("?" for _ in table_columns)
                names = ",".join(table_columns)
                for row in rows:
                    connection.execute(
                        f"INSERT OR IGNORE INTO {table}({names}) VALUES({placeholders})",
                        tuple(row[name] for name in table_columns),
                    )
