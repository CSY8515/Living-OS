from __future__ import annotations

import json
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent

DAILY_LOG_FILE = BASE_DIR / "data" / "daily_logs.json"
DECISION_LOG_FILE = BASE_DIR / "logs" / "decision_log.jsonl"
ARCHIVE_FILE = BASE_DIR / "data" / "archive.json"
REPORT_INDEX_FILE = BASE_DIR / "reports" / "report_index.json"
SETTINGS_FILE = BASE_DIR / "state" / "settings.json"
MODULE_REGISTRY_FILE = BASE_DIR / "config" / "module_registry.json"

REPORTS_DIR = BASE_DIR / "reports"
BACKUPS_DIR = BASE_DIR / "backups"


DEFAULT_DAILY_LOGS = {"logs": []}
DEFAULT_ARCHIVE = {"items": []}
DEFAULT_REPORT_INDEX = {"reports": []}
DEFAULT_SETTINGS = {
    "app_name": "Living OS",
    "version": "v0.9",
    "default_report_range": "daily",
    "date_format": "YYYY-MM-DD",
}
DEFAULT_MODULE_REGISTRY = {
    "modules": [
        {
            "id": "vehicle_os",
            "name": "Vehicle OS",
            "status": "planned",
            "description": "Vehicle, driving, maintenance, mobility records.",
        },
        {
            "id": "food_os",
            "name": "Food OS",
            "status": "planned",
            "description": "Meals, ingredients, cooking, nutrition records.",
        },
        {
            "id": "finance_os",
            "name": "Finance OS",
            "status": "planned",
            "description": "Budget, expenses, savings, financial decisions.",
        },
        {
            "id": "health_os",
            "name": "Health OS",
            "status": "planned",
            "description": "Health logs and body condition records.",
        },
        {
            "id": "housing_os",
            "name": "Housing OS",
            "status": "planned",
            "description": "Housing candidates, home records, living environment.",
        },
        {
            "id": "learning_os",
            "name": "Learning OS",
            "status": "planned",
            "description": "Learning packs, notes, reports, casebook.",
        },
    ]
}


FILES: dict[str, tuple[Path, Any]] = {
    "daily_logs": (DAILY_LOG_FILE, DEFAULT_DAILY_LOGS),
    "archive": (ARCHIVE_FILE, DEFAULT_ARCHIVE),
    "report_index": (REPORT_INDEX_FILE, DEFAULT_REPORT_INDEX),
    "settings": (SETTINGS_FILE, DEFAULT_SETTINGS),
    "module_registry": (MODULE_REGISTRY_FILE, DEFAULT_MODULE_REGISTRY),
    # v0.1 compatibility: kept as future Finance OS / Housing OS source assets.
    "finance_budget": (
        BASE_DIR / "data" / "finance_budget.json",
        {
            "monthly_income": 0,
            "fixed_expenses": [],
            "savings_goals": [],
            "summary": {
                "total_fixed_expenses": 0,
                "total_savings_goals": 0,
                "remaining_amount": 0,
                "fixed_expense_ratio": 0.0,
                "risk_level": "NORMAL",
            },
        },
    ),
    "housing_candidates": (
        BASE_DIR / "data" / "housing_candidates.json",
        {"candidates": []},
    ),
}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today_str() -> str:
    return date.today().isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
    temporary_path.replace(path)


def read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists() or path.stat().st_size == 0:
            return deepcopy(default)
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return deepcopy(default)


def ensure_data_files() -> None:
    for path, default in FILES.values():
        if not path.exists() or path.stat().st_size == 0:
            write_json(path, deepcopy(default))

    DECISION_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DECISION_LOG_FILE.exists():
        DECISION_LOG_FILE.touch()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        if not path.exists() or path.stat().st_size == 0:
            return records
        with path.open("r", encoding="utf-8-sig") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    records.append(value)
    except (OSError, UnicodeError):
        return []
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def list_report_files() -> list[Path]:
    if not REPORTS_DIR.exists():
        return []
    files: list[tuple[float, Path]] = []
    try:
        for path in REPORTS_DIR.glob("*.md"):
            if path.name == "living_os_report.md":
                continue
            try:
                files.append((path.stat().st_mtime, path))
            except OSError:
                continue
    except OSError:
        return []
    return [path for _, path in sorted(files, key=lambda item: item[0], reverse=True)]


def load_dashboard_data() -> dict[str, Any]:
    from modules.daily_log import load_daily_logs
    from modules.decision_log import read_decision_logs

    daily_logs = load_daily_logs()
    decisions = read_decision_logs()
    report_files = list_report_files()

    today = today_str()
    today_logs = [item for item in daily_logs if item.get("date") == today]
    recent_logs = sorted(
        daily_logs,
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )[:5]
    recent_decisions = sorted(
        decisions,
        key=lambda item: item.get("updated_at") or item.get("created_at") or "",
        reverse=True,
    )[:5]

    reviewable_decisions = [
        item
        for item in decisions
        if str(item.get("status", "")).lower() in {"active", "review", "draft"}
    ]

    return {
        "today": today,
        "today_log_count": len(today_logs),
        "total_log_count": len(daily_logs),
        "recent_logs": recent_logs,
        "recent_decisions": recent_decisions,
        "decision_count": len(decisions),
        "reviewable_decision_count": len(reviewable_decisions),
        "recent_report": report_files[0].name if report_files else None,
        "report_count": len(report_files),
        "system_status": "NORMAL",
    }
