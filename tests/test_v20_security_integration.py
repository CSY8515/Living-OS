from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.errors import CommandRejected
from core.hub import LivingHub
from core.integrations import AIContextPackage, AIGateway
from modules.hub_settings import HubSettingsService


class FakeAIProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, model: str, instructions: str, source: str) -> str:
        self.calls += 1
        return "Draft only"


class SecurityAndIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.hub = LivingHub(Path(self.temporary.name))
        self.hub.bootstrap(())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_owner_secret_is_hashed_and_devices_are_revocable(self) -> None:
        secret = "correct horse battery staple"
        self.hub.security.configure(secret)
        self.assertTrue(self.hub.security.configured)
        self.assertTrue(self.hub.security.verify(secret))
        self.assertFalse(self.hub.security.verify("wrong passphrase"))
        self.assertNotIn(secret.encode("utf-8"), self.hub.store.database_path.read_bytes())

        device = self.hub.security.pair_device(secret, "Tablet", "tablet")
        self.assertTrue(self.hub.security.validate_device(device.device_id))
        self.hub.security.revoke(device.device_id)
        self.assertFalse(self.hub.security.validate_device(device.device_id))
        self.assertEqual(self.hub.store.count("paired_devices"), 1)

    def test_ai_gateway_requires_explicit_approval_and_never_writes_records(self) -> None:
        provider = FakeAIProvider()
        gateway = AIGateway(self.hub.store, provider)
        package = AIContextPackage("journal", "selected source")
        with self.assertRaises(CommandRejected):
            gateway.request(
                package,
                model="test-model",
                instructions="Read only",
                explicitly_approved=False,
            )
        self.assertEqual(provider.calls, 0)
        result = gateway.request(
            package,
            model="test-model",
            instructions="Read only",
            explicitly_approved=True,
        )
        self.assertEqual(result, "Draft only")
        self.assertEqual(provider.calls, 1)
        self.assertEqual(self.hub.store.count("records"), 0)
        self.assertEqual(self.hub.store.count("audit_entries"), 2)

    def test_settings_updates_are_versioned_and_preserve_unknown_fields(self) -> None:
        service = HubSettingsService(self.hub)
        first = service.update("Personal Living OS", "weekly", 0)
        self.assertEqual(first["_version"], 1)
        second = service.update("Living OS", "monthly", 1)
        self.assertEqual(second["_version"], 2)
        self.assertEqual(second["version"], "v2.0")


if __name__ == "__main__":
    unittest.main()
