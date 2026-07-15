from __future__ import annotations

import hashlib
import hmac
import os
from contextlib import closing
from dataclasses import dataclass
from uuid import uuid4

from subsystems.foundation.engines.audit import append_audit
from subsystems.foundation.engines.contracts import CommandEnvelope
from subsystems.foundation.engines.storage import HubStore
from subsystems.foundation.engines.time import utc_now_iso


@dataclass(frozen=True)
class PairedDevice:
    device_id: str
    name: str
    platform: str
    paired_at: str
    last_seen_at: str
    revoked_at: str | None


class OwnerSecurityService:
    """Single-owner authentication and revocable device pairing."""

    ITERATIONS = 600_000

    def __init__(self, store: HubStore) -> None:
        self.store = store

    @property
    def configured(self) -> bool:
        return bool(self.store.get_meta("owner_secret_hash", ""))

    def configure(self, passphrase: str) -> None:
        clean = passphrase.strip()
        if len(clean) < 12:
            raise ValueError("Owner passphrase must contain at least 12 characters.")
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", clean.encode("utf-8"), salt, self.ITERATIONS)
        command = CommandEnvelope(
            "settings", "configure_owner_security", {}, reason="enable-owner-security"
        )
        self.store.initialize()
        with self.store.transaction() as connection:
            self.store._set_meta(connection, "owner_secret_salt", salt.hex())
            self.store._set_meta(connection, "owner_secret_hash", digest.hex())
            self.store._set_meta(connection, "owner_security_required", "true")
            append_audit(connection, command, "accepted", {"secret_stored": False})

    def verify(self, passphrase: str) -> bool:
        salt_hex = self.store.get_meta("owner_secret_salt", "")
        expected_hex = self.store.get_meta("owner_secret_hash", "")
        if not salt_hex or not expected_hex:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            passphrase.encode("utf-8"),
            bytes.fromhex(salt_hex),
            self.ITERATIONS,
        )
        return hmac.compare_digest(candidate.hex(), expected_hex)

    def pair_device(self, passphrase: str, name: str, platform: str) -> PairedDevice:
        if not self.verify(passphrase):
            raise ValueError("Owner authentication failed.")
        clean_name = name.strip() or "Living OS Device"
        clean_platform = platform.strip() or "browser"
        device_id = str(uuid4())
        now = utc_now_iso()
        command = CommandEnvelope(
            "settings",
            "pair_device",
            {"device_id": device_id, "name": clean_name, "platform": clean_platform},
            reason="pair-owner-device",
        )
        self.store.initialize()
        with self.store.transaction() as connection:
            connection.execute(
                """INSERT INTO paired_devices (
                    device_id, name, platform, paired_at, last_seen_at, revoked_at
                ) VALUES (?, ?, ?, ?, ?, NULL)""",
                (device_id, clean_name, clean_platform, now, now),
            )
            append_audit(connection, command, "accepted", {"device_id": device_id})
        return PairedDevice(device_id, clean_name, clean_platform, now, now, None)

    def validate_device(self, device_id: str) -> bool:
        self.store.initialize()
        with self.store.transaction() as connection:
            row = connection.execute(
                "SELECT revoked_at FROM paired_devices WHERE device_id=?", (device_id,)
            ).fetchone()
            if row is None or row["revoked_at"]:
                return False
            connection.execute(
                "UPDATE paired_devices SET last_seen_at=? WHERE device_id=?",
                (utc_now_iso(), device_id),
            )
        return True

    def revoke(self, device_id: str) -> None:
        self.store.initialize()
        command = CommandEnvelope(
            "settings",
            "revoke_device",
            {"device_id": device_id},
            reason="revoke-owner-device",
        )
        with self.store.transaction() as connection:
            updated = connection.execute(
                "UPDATE paired_devices SET revoked_at=? WHERE device_id=? AND revoked_at IS NULL",
                (utc_now_iso(), device_id),
            ).rowcount
            if updated:
                append_audit(connection, command, "accepted", {"device_id": device_id})
        if not updated:
            raise ValueError("Active paired device was not found.")

    def list_devices(self) -> list[PairedDevice]:
        self.store.initialize()
        with closing(self.store.connect()) as connection:
            rows = connection.execute(
                """SELECT device_id, name, platform, paired_at, last_seen_at, revoked_at
                   FROM paired_devices ORDER BY paired_at DESC"""
            ).fetchall()
        return [PairedDevice(**dict(row)) for row in rows]
