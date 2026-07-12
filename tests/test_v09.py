from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from modules.ai_credentials import (
    CredentialError,
    credential_status,
    mask_api_key,
    resolve_api_key,
)
from modules.ai_service import (
    AIServiceError,
    DEFAULT_AI_MODEL,
    MAX_SOURCE_CHARACTERS,
    analyze_daily_log,
    test_connection as check_connection,
)
from modules.report_system import build_ai_report_source


class CredentialTests(unittest.TestCase):
    def test_mask_never_displays_full_key(self) -> None:
        secret = "sk-test-super-secret"
        masked = mask_api_key(secret)
        self.assertNotIn(secret, masked)
        self.assertTrue(masked.startswith("sk-"))

    def test_resolution_precedence_is_session_saved_environment(self) -> None:
        with (
            patch("modules.ai_credentials.load_saved_api_key", return_value="saved-key"),
            patch.dict(os.environ, {"OPENAI_API_KEY": "environment-key"}),
        ):
            self.assertEqual(resolve_api_key("session-key"), ("session-key", "session"))
            self.assertEqual(resolve_api_key(), ("saved-key", "operating-system credential store"))

        with (
            patch("modules.ai_credentials.load_saved_api_key", side_effect=CredentialError("unavailable")),
            patch.dict(os.environ, {"OPENAI_API_KEY": "environment-key"}),
        ):
            self.assertEqual(resolve_api_key(), ("environment-key", "environment"))

    def test_status_does_not_expose_full_key(self) -> None:
        with patch("modules.ai_credentials.resolve_api_key", return_value=("sk-private-value", "session")):
            status = credential_status()
        self.assertTrue(status.configured)
        self.assertNotIn("sk-private-value", status.masked)


class AIServiceTests(unittest.TestCase):
    def test_no_request_is_made_until_analysis_function_is_called(self) -> None:
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text="Read-only result")
        with patch("modules.ai_service._client", return_value=client):
            self.assertFalse(client.responses.create.called)
            result = analyze_daily_log("sk-secret", DEFAULT_AI_MODEL, "record text")
        self.assertEqual(result, "Read-only result")
        client.responses.create.assert_called_once()

    def test_source_is_capped_and_marked(self) -> None:
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text="Result")
        with patch("modules.ai_service._client", return_value=client):
            analyze_daily_log("sk-secret", DEFAULT_AI_MODEL, "x" * (MAX_SOURCE_CHARACTERS + 100))
        sent = client.responses.create.call_args.kwargs["input"]
        self.assertIn("[Source truncated by Living OS]", sent)
        self.assertLess(len(sent), MAX_SOURCE_CHARACTERS + 100)

    def test_connection_errors_are_sanitized(self) -> None:
        class AuthenticationError(Exception):
            pass

        with patch("modules.ai_service._client", side_effect=AuthenticationError("sk-secret leaked")):
            result = check_connection("sk-secret")
        self.assertFalse(result.ok)
        self.assertNotIn("sk-secret", result.message)
        self.assertIn("rejected", result.message)

    def test_empty_source_fails_before_client_creation(self) -> None:
        with patch("modules.ai_service._client") as client:
            with self.assertRaises(AIServiceError):
                analyze_daily_log("sk-secret", DEFAULT_AI_MODEL, "")
        client.assert_not_called()


class AIReportTests(unittest.TestCase):
    def test_report_source_reads_existing_data_without_saving(self) -> None:
        with (
            patch("modules.report_system.load_daily_logs", return_value=[]),
            patch("modules.report_system.read_decision_logs", return_value=[]),
            patch("modules.report_system.save_report") as save_report,
        ):
            source = build_ai_report_source("daily")
        self.assertIn("daily_logs: []", source)
        self.assertIn("recent_decisions: []", source)
        save_report.assert_not_called()


if __name__ == "__main__":
    unittest.main()
