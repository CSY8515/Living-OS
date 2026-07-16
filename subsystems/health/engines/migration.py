from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from subsystems.health.engines.storage import HealthStorageEngine
from subsystems.health.engines.validation import (
    optional_decimal, optional_text, require_date, require_datetime, require_decimal,
    require_integer, require_metrics, require_text, utc_now_iso,
)


KINDS = ("weights", "body_compositions", "health_checkups", "sleep", "exercise", "nutrition", "goals")


class HealthMigrationEngine:
    def __init__(self, store: HealthStorageEngine) -> None:
        self.store = store

    def dry_run_legacy_json(self, source: Path) -> dict[str, Any]:
        path, raw, checksum, payload = self._read(source)
        normalized = self._normalize(payload)
        return {
            "source": str(path.resolve()), "checksum": checksum, "dry_run": True,
            "accepted": {key: len(normalized[key]) for key in KINDS}, "database_created": False,
        }

    def migrate_legacy_json(self, source: Path) -> dict[str, Any]:
        path, raw, checksum, payload = self._read(source)
        source_key = str(path.resolve())
        existing = self.store.query_one(
            "SELECT checksum,result_json,imported_at FROM health_migration_ledger WHERE source_key=?", (source_key,)
        )
        if existing:
            if existing["checksum"] != checksum:
                raise ValueError("Legacy Health source changed after migration; review before importing again.")
            return {**json.loads(existing["result_json"]), "already_migrated": True, "imported_at": existing["imported_at"]}
        normalized = self._normalize(payload)
        imported_at = utc_now_iso()
        result = {
            "source": source_key, "checksum": checksum, "dry_run": False,
            "accepted": {key: len(normalized[key]) for key in KINDS}, "already_migrated": False,
        }
        with self.store.transaction() as connection:
            for row in normalized["weights"]:
                connection.execute("INSERT INTO weight_records VALUES(?,?,?,?,?,?)", (
                    row["record_id"], row["measured_on"], row["weight_kg"], row["note"], imported_at, imported_at,
                ))
            for row in normalized["body_compositions"]:
                connection.execute("INSERT INTO body_compositions VALUES(?,?,?,?,?,?,?)", (
                    row["record_id"], row["measured_on"], row["skeletal_muscle_kg"],
                    row["body_fat_percent"], row["bmi"], row["note"], imported_at,
                ))
            for row in normalized["health_checkups"]:
                connection.execute("INSERT INTO health_checkups VALUES(?,?,?,?,?,?,?,?)", (
                    row["record_id"], row["checked_on"], row["title"], row["assessment"],
                    row["follow_up_on"], json.dumps(row["metrics"], sort_keys=True), row["note"], imported_at,
                ))
            for row in normalized["sleep"]:
                connection.execute("INSERT INTO sleep_records VALUES(?,?,?,?,?,?,?,?)", (
                    row["record_id"], row["sleep_on"], row["bedtime"], row["wake_time"],
                    row["duration_minutes"], row["fatigue"], row["note"], imported_at,
                ))
            for row in normalized["exercise"]:
                connection.execute("INSERT INTO exercise_records VALUES(?,?,?,?,?,?,?)", (
                    row["record_id"], row["exercised_on"], row["activity"], row["duration_minutes"],
                    row["repetitions"], row["note"], imported_at,
                ))
            for row in normalized["goals"]:
                connection.execute("INSERT INTO health_goals VALUES(?,?,?,?,?,?,?,?,?)", (
                    row["goal_id"], row["name"], row["target_weight_kg"], row["target_body_fat_percent"],
                    row["start_on"], row["target_on"], row["status"], imported_at, imported_at,
                ))
            goal_ids = {row["goal_id"] for row in normalized["goals"]}
            for row in normalized["nutrition"]:
                if row["goal_id"] is not None and row["goal_id"] not in goal_ids:
                    raise ValueError("Migrated nutrition goal_id must reference a goal in the same source.")
                connection.execute("INSERT INTO nutrition_records VALUES(?,?,?,?,?,?)", (
                    row["record_id"], row["eaten_on"], row["meal_type"], row["note"], row["goal_id"], imported_at,
                ))
            connection.execute("INSERT INTO health_migration_ledger VALUES(?,?,?,?)", (
                source_key, checksum, json.dumps(result, sort_keys=True), imported_at,
            ))
        return {**result, "imported_at": imported_at}

    @staticmethod
    def _read(source: Path) -> tuple[Path, bytes, str, dict[str, Any]]:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        checksum = hashlib.sha256(raw).hexdigest()
        try:
            payload = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Legacy Health source must be valid UTF-8 JSON.") from exc
        if not isinstance(payload, dict):
            raise ValueError("Legacy Health source must be a JSON object.")
        return path, raw, checksum, payload

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        for key in KINDS:
            if not isinstance(payload.get(key, []), list):
                raise ValueError(f"{key} must be a list.")
            if any(not isinstance(item, dict) for item in payload.get(key, [])):
                raise ValueError(f"Every {key} entry must be an object.")
        normalized: dict[str, list[dict[str, Any]]] = {key: [] for key in KINDS}
        for item in payload.get("weights", []):
            normalized["weights"].append({
                "record_id": str(uuid4()), "measured_on": require_date(item.get("measured_on"), "measured_on"),
                "weight_kg": require_decimal(item.get("weight_kg"), "weight_kg", "20", "500"), "note": optional_text(item.get("note", "")),
            })
        for item in payload.get("body_compositions", []):
            normalized["body_compositions"].append({
                "record_id": str(uuid4()), "measured_on": require_date(item.get("measured_on"), "measured_on"),
                "skeletal_muscle_kg": require_decimal(item.get("skeletal_muscle_kg"), "skeletal_muscle_kg", "1", "150"),
                "body_fat_percent": require_decimal(item.get("body_fat_percent"), "body_fat_percent", "1", "75"),
                "bmi": require_decimal(item.get("bmi"), "bmi", "5", "100"), "note": optional_text(item.get("note", "")),
            })
        for item in payload.get("health_checkups", []):
            checked = require_date(item.get("checked_on"), "checked_on")
            follow = require_date(item["follow_up_on"], "follow_up_on") if item.get("follow_up_on") else None
            if follow and follow < checked:
                raise ValueError("follow_up_on cannot be before checked_on.")
            normalized["health_checkups"].append({
                "record_id": str(uuid4()), "checked_on": checked, "title": require_text(item.get("title"), "title", 200),
                "assessment": require_text(item.get("assessment"), "assessment", 1000), "follow_up_on": follow,
                "metrics": require_metrics(item.get("metrics")), "note": optional_text(item.get("note", "")),
            })
        for item in payload.get("sleep", []):
            bed, wake = require_datetime(item.get("bedtime"), "bedtime"), require_datetime(item.get("wake_time"), "wake_time")
            minutes = int((datetime.fromisoformat(wake) - datetime.fromisoformat(bed)).total_seconds() // 60)
            if minutes < 1 or minutes > 1440:
                raise ValueError("sleep duration must be between 1 and 1440 minutes.")
            normalized["sleep"].append({
                "record_id": str(uuid4()), "sleep_on": bed[:10], "bedtime": bed, "wake_time": wake,
                "duration_minutes": minutes, "fatigue": require_integer(item.get("fatigue"), "fatigue", 1, 5),
                "note": optional_text(item.get("note", "")),
            })
        for item in payload.get("exercise", []):
            repetitions = item.get("repetitions")
            normalized["exercise"].append({
                "record_id": str(uuid4()), "exercised_on": require_date(item.get("exercised_on"), "exercised_on"),
                "activity": require_text(item.get("activity"), "activity", 120),
                "duration_minutes": require_integer(item.get("duration_minutes"), "duration_minutes", 1, 1440),
                "repetitions": None if repetitions is None else require_integer(repetitions, "repetitions", 0, 1000000),
                "note": optional_text(item.get("note", "")),
            })
        for item in payload.get("goals", []):
            weight = optional_decimal(item.get("target_weight_kg"), "target_weight_kg", "20", "500")
            fat = optional_decimal(item.get("target_body_fat_percent"), "target_body_fat_percent", "1", "75")
            if weight is None and fat is None:
                raise ValueError("At least one Health target is required.")
            normalized["goals"].append({
                "goal_id": require_text(item.get("goal_id") or str(uuid4()), "goal_id", 80),
                "name": require_text(item.get("name"), "name", 150), "target_weight_kg": weight,
                "target_body_fat_percent": fat, "start_on": require_date(item.get("start_on"), "start_on"),
                "target_on": require_date(item["target_on"], "target_on") if item.get("target_on") else None,
                "status": item.get("status", "active"),
            })
            if normalized["goals"][-1]["status"] not in {"active", "completed", "cancelled"}:
                raise ValueError("Unknown goal status.")
        for item in payload.get("nutrition", []):
            normalized["nutrition"].append({
                "record_id": str(uuid4()), "eaten_on": require_date(item.get("eaten_on"), "eaten_on"),
                "meal_type": require_text(item.get("meal_type"), "meal_type", 80), "note": optional_text(item.get("note", "")),
                "goal_id": require_text(item["goal_id"], "goal_id", 80) if item.get("goal_id") else None,
            })
        return normalized
