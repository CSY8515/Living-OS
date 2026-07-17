from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from subsystems.database.engines.component import ComponentDatabaseAdapter
from subsystems.health.engines.validation import utc_now_iso

if TYPE_CHECKING:
    from subsystems.database.subsystem import DatabaseSubsystem


SCHEMA_VERSION = 1


class HealthStorageEngine(ComponentDatabaseAdapter):
    def __init__(self, database_path: Path, foundation: DatabaseSubsystem | None = None) -> None:
        super().__init__(
            database_path,
            component_id="SUB-HEALTH",
            display_name="Health Subsystem",
            foundation=foundation,
        )

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = self._connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS health_meta (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS weight_records (
                    record_id TEXT PRIMARY KEY, measured_on TEXT NOT NULL,
                    weight_kg TEXT NOT NULL, note TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_weight_date ON weight_records(measured_on);
                CREATE TABLE IF NOT EXISTS body_compositions (
                    record_id TEXT PRIMARY KEY, measured_on TEXT NOT NULL,
                    skeletal_muscle_kg TEXT NOT NULL, body_fat_percent TEXT NOT NULL,
                    bmi TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_body_date ON body_compositions(measured_on);
                CREATE TABLE IF NOT EXISTS health_checkups (
                    record_id TEXT PRIMARY KEY, checked_on TEXT NOT NULL,
                    title TEXT NOT NULL, assessment TEXT NOT NULL,
                    follow_up_on TEXT, metrics_json TEXT NOT NULL,
                    note TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_checkup_date ON health_checkups(checked_on);
                CREATE TABLE IF NOT EXISTS sleep_records (
                    record_id TEXT PRIMARY KEY, sleep_on TEXT NOT NULL,
                    bedtime TEXT NOT NULL, wake_time TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL CHECK(duration_minutes BETWEEN 1 AND 1440),
                    fatigue INTEGER NOT NULL CHECK(fatigue BETWEEN 1 AND 5),
                    note TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_sleep_date ON sleep_records(sleep_on);
                CREATE TABLE IF NOT EXISTS exercise_records (
                    record_id TEXT PRIMARY KEY, exercised_on TEXT NOT NULL,
                    activity TEXT NOT NULL, duration_minutes INTEGER NOT NULL
                        CHECK(duration_minutes BETWEEN 1 AND 1440),
                    repetitions INTEGER CHECK(repetitions BETWEEN 0 AND 1000000),
                    note TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_exercise_date ON exercise_records(exercised_on);
                CREATE TABLE IF NOT EXISTS health_goals (
                    goal_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                    target_weight_kg TEXT, target_body_fat_percent TEXT,
                    start_on TEXT NOT NULL, target_on TEXT,
                    status TEXT NOT NULL CHECK(status IN ('active','completed','cancelled')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS nutrition_records (
                    record_id TEXT PRIMARY KEY, eaten_on TEXT NOT NULL,
                    meal_type TEXT NOT NULL, note TEXT NOT NULL,
                    goal_id TEXT REFERENCES health_goals(goal_id), created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_health_nutrition_date ON nutrition_records(eaten_on);
                CREATE TABLE IF NOT EXISTS health_migration_ledger (
                    source_key TEXT PRIMARY KEY, checksum TEXT NOT NULL,
                    result_json TEXT NOT NULL, imported_at TEXT NOT NULL
                );
                """
            )
            now = utc_now_iso()
            connection.execute(
                """INSERT INTO health_meta(key,value,updated_at) VALUES('schema_version',?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (str(SCHEMA_VERSION), now),
            )
            connection.execute(
                """INSERT INTO health_meta(key,value,updated_at) VALUES('subsystem_version','1.0.0',?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (now,),
            )
            connection.commit()
        finally:
            connection.close()
        self.register_contract(schema_version=SCHEMA_VERSION, migration_id="health-schema-v1")

    def query(self, sql: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not self.initialized:
            return []
        connection = self._connect()
        try:
            return [dict(row) for row in connection.execute(sql, parameters).fetchall()]
        finally:
            connection.close()

    def query_one(self, sql: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self.query(sql, parameters)
        return rows[0] if rows else None

    def health(self) -> dict[str, Any]:
        if not self.initialized:
            return {"status": "ready", "initialized": False, "schema_version": SCHEMA_VERSION}
        row = self.query_one("PRAGMA integrity_check")
        healthy = bool(row) and next(iter(row.values())) == "ok"
        return {
            "status": "healthy" if healthy else "degraded", "initialized": True,
            "schema_version": SCHEMA_VERSION, "database_path": str(self.database_path),
        }

    def export_snapshot(self) -> dict[str, Any]:
        tables = (
            "weight_records", "body_compositions", "health_checkups", "sleep_records",
            "exercise_records", "nutrition_records", "health_goals",
        )
        snapshot: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "privacy_class": "sensitive"}
        for table in tables:
            rows = self.query(f"SELECT * FROM {table} ORDER BY 1")
            for row in rows:
                if "metrics_json" in row:
                    row["metrics"] = json.loads(row.pop("metrics_json"))
            snapshot[table] = rows
        return snapshot
