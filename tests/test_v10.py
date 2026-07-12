from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from modules import archive, daily_log, module_manager, report_system, settings
from modules.ai_service import AI_MODELS, DEFAULT_AI_MODEL
from modules.storage import APP_VERSION, DEFAULT_SETTINGS, read_json, write_json


class VersionConsistencyTests(unittest.TestCase):
    def test_all_runtime_version_sources_are_v10_stable(self) -> None:
        self.assertEqual(APP_VERSION, "v1.0 Stable")
        self.assertEqual(app.VERSION, APP_VERSION)
        self.assertEqual(DEFAULT_SETTINGS["version"], APP_VERSION)

    def test_generated_report_uses_v10_stable(self) -> None:
        with (
            patch("modules.report_system.load_daily_logs", return_value=[]),
            patch("modules.report_system.read_decision_logs", return_value=[]),
        ):
            text = report_system.build_report_text("daily")
        self.assertIn("- Version: v1.0 Stable", text)


class StorageSafetyTests(unittest.TestCase):
    def test_atomic_json_failure_preserves_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            original = '{"items": []}'
            path.write_text(original, encoding="utf-8")
            with self.assertRaises(TypeError):
                write_json(path, {"invalid": object()})
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_malformed_daily_log_is_not_overwritten_on_add(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "daily_logs.json"
            path.write_text("{malformed", encoding="utf-8")
            with patch.object(daily_log, "DAILY_LOG_FILE", path):
                with self.assertRaises(json.JSONDecodeError):
                    daily_log.add_daily_log("2026-07-12", "Title", "Body", [], "NORMAL")
            self.assertEqual(path.read_text(encoding="utf-8"), "{malformed")

    def test_malformed_archive_is_not_overwritten_on_add(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            path.write_text("[]", encoding="utf-8")
            with patch.object(archive, "ARCHIVE_FILE", path):
                with self.assertRaises(ValueError):
                    archive.add_archive_item("Title", "Body", "test", [])
            self.assertEqual(path.read_text(encoding="utf-8"), "[]")

    def test_settings_save_preserves_unknown_v09_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            existing = {"app_name": "Living OS", "version": "v0.9", "legacy": True}
            path.write_text(json.dumps(existing), encoding="utf-8")
            with patch.object(settings, "SETTINGS_FILE", path):
                settings.save_settings({"app_name": "Personal Living OS"})
            saved = read_json(path, {})
            self.assertEqual(saved["legacy"], True)
            self.assertEqual(saved["version"], "v0.9")
            self.assertEqual(saved["app_name"], "Personal Living OS")


class ReportReliabilityTests(unittest.TestCase):
    def test_report_names_are_collision_resistant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports_dir = root / "reports"
            index_file = reports_dir / "report_index.json"
            with (
                patch.object(report_system, "REPORTS_DIR", reports_dir),
                patch.object(report_system, "REPORT_INDEX_FILE", index_file),
            ):
                first = report_system.save_report("daily", "first")
                second = report_system.save_report("daily", "second")
            self.assertNotEqual(first.name, second.name)
            self.assertEqual(len(read_json(index_file, {"reports": []})["reports"]), 2)

    def test_failed_index_update_removes_new_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reports_dir = Path(directory) / "reports"
            with (
                patch.object(report_system, "REPORTS_DIR", reports_dir),
                patch.object(report_system, "REPORT_INDEX_FILE", reports_dir / "report_index.json"),
                patch("modules.report_system.write_json", side_effect=OSError("denied")),
            ):
                with self.assertRaises(OSError):
                    report_system.save_report("daily", "content")
            self.assertEqual(list(reports_dir.glob("*.md")), [])


class BackupCompatibilityTests(unittest.TestCase):
    def test_v09_backup_restores_without_schema_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            daily = root / "data" / "daily_logs.json"
            decision = root / "logs" / "decision_log.jsonl"
            targets = [daily, decision]
            daily.parent.mkdir(parents=True)
            decision.parent.mkdir(parents=True)
            daily.write_text('{"logs": []}', encoding="utf-8")
            decision.write_text("", encoding="utf-8")
            backup = {
                "files": {
                    daily.relative_to(root).as_posix(): '{"logs": [{"id": "LOG-00001", "date": "2026-01-01"}]}',
                    decision.relative_to(root).as_posix(): '{"id": "DEC-00001", "status": "active"}\n',
                }
            }
            with (
                patch.object(settings, "BACKUP_TARGETS", targets),
                patch.object(settings, "DECISION_LOG_FILE", decision),
            ):
                restored = settings.restore_backup(json.dumps(backup))
            self.assertEqual(restored, 2)
            self.assertEqual(set(read_json(daily, {}).keys()), {"logs"})
            self.assertEqual(set(json.loads(decision.read_text(encoding="utf-8")).keys()), {"id", "status"})

    def test_invalid_backup_is_rejected_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            daily = root / "data" / "daily_logs.json"
            decision = root / "logs" / "decision_log.jsonl"
            daily.parent.mkdir(parents=True)
            decision.parent.mkdir(parents=True)
            daily.write_text('{"logs": []}', encoding="utf-8")
            decision.write_text("", encoding="utf-8")
            backup = {
                "files": {
                    str(daily.relative_to(root)): '{"logs": [{"id": "changed"}]}',
                    str(decision.relative_to(root)): "not-json\n",
                }
            }
            with (
                patch.object(settings, "BACKUP_TARGETS", [daily, decision]),
                patch.object(settings, "DECISION_LOG_FILE", decision),
            ):
                with self.assertRaises(json.JSONDecodeError):
                    settings.restore_backup(json.dumps(backup))
            self.assertEqual(daily.read_text(encoding="utf-8"), '{"logs": []}')


class AISafetyContractTests(unittest.TestCase):
    def test_model_list_preserves_verified_v09_identifiers(self) -> None:
        self.assertEqual(DEFAULT_AI_MODEL, "gpt-5.6-luna")
        self.assertEqual(AI_MODELS, ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"))

    def test_ai_source_building_never_saves(self) -> None:
        with (
            patch("modules.report_system.load_daily_logs", return_value=[]),
            patch("modules.report_system.read_decision_logs", return_value=[]),
            patch("modules.report_system.save_report") as save_report,
        ):
            source = report_system.build_ai_report_source("weekly")
        self.assertIn("Selected Living OS report inputs", source)
        save_report.assert_not_called()


class SchemaCompatibilityTests(unittest.TestCase):
    def test_new_records_keep_v09_fields_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            daily_path = root / "daily_logs.json"
            archive_path = root / "archive.json"
            with patch.object(daily_log, "DAILY_LOG_FILE", daily_path):
                log = daily_log.add_daily_log("2026-07-12", "Title", "Body", ["tag"], "NORMAL")
            with patch.object(archive, "ARCHIVE_FILE", archive_path):
                item = archive.add_archive_item("Title", "Body", "source", ["tag"])
            self.assertEqual(
                set(log),
                {"id", "date", "title", "content", "tags", "mood", "created_at", "updated_at"},
            )
            self.assertEqual(
                set(item),
                {"id", "title", "content", "source", "tags", "created_at", "updated_at"},
            )


if __name__ == "__main__":
    unittest.main()
