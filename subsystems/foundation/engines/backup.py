from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from subsystems.foundation.engines.time import utc_now_iso


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BackupService:
    def __init__(self, database_path: Path, backup_root: Path, repository_root: Path) -> None:
        self.database_path = database_path
        self.backup_root = backup_root
        self.repository_root = repository_root

    def create(self, legacy_paths: list[Path] | None = None) -> Path:
        self.backup_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        archive_path = self.backup_root / f"living_os_v1_7_database_{stamp}.zip"
        snapshot_path = self.backup_root / f".{archive_path.stem}.sqlite3"
        schema_version = "0"
        if self.database_path.exists():
            metadata_connection = sqlite3.connect(self.database_path)
            try:
                row = metadata_connection.execute(
                    "SELECT value FROM system_meta WHERE key='schema_version'"
                ).fetchone()
                schema_version = str(row[0]) if row else "0"
            except sqlite3.Error:
                schema_version = "0"
            finally:
                metadata_connection.close()
        manifest: dict[str, object] = {
            "format": "living-os-database-backup",
            "format_version": 1,
            "product_version": "v1.7",
            "schema_version": schema_version,
            "created_at": utc_now_iso(),
            "files": {},
        }
        try:
            if self.database_path.exists():
                source = sqlite3.connect(self.database_path)
                target = sqlite3.connect(snapshot_path)
                try:
                    source.backup(target)
                finally:
                    target.close()
                    source.close()

            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                if snapshot_path.exists():
                    archive.write(snapshot_path, "hub/living_os.sqlite3")
                    manifest["files"]["hub/living_os.sqlite3"] = sha256_file(snapshot_path)  # type: ignore[index]
                for path in legacy_paths or []:
                    if not path.exists() or not path.is_file():
                        continue
                    relative = path.relative_to(self.repository_root).as_posix()
                    archive_name = f"legacy/{relative}"
                    archive.write(path, archive_name)
                    manifest["files"][archive_name] = sha256_file(path)  # type: ignore[index]
                archive.writestr(
                    "manifest.json",
                    json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
                )
        finally:
            snapshot_path.unlink(missing_ok=True)
        return archive_path

    @staticmethod
    def verify(archive_path: Path) -> bool:
        with zipfile.ZipFile(archive_path, "r") as archive:
            manifest = json.loads(archive.read("manifest.json"))
            files = manifest.get("files", {})
            if not isinstance(files, dict):
                return False
            for name, expected in files.items():
                actual = hashlib.sha256(archive.read(str(name))).hexdigest()
                if actual != expected:
                    return False
        return True

    def restore(self, archive_path: Path) -> Path:
        """Restore a verified Hub backup with a pre-restore safety backup and rollback."""
        if not self.verify(archive_path):
            raise ValueError("Backup verification failed.")
        staged: dict[Path, Path] = {}
        originals: dict[Path, bytes | None] = {}
        legacy_targets: list[Path] = []
        with zipfile.ZipFile(archive_path, "r") as archive:
            manifest = json.loads(archive.read("manifest.json"))
            names = [str(name) for name in manifest.get("files", {})]
            for name in names:
                if name == "hub/living_os.sqlite3":
                    target = self.database_path
                elif name.startswith("legacy/"):
                    relative = Path(name.removeprefix("legacy/"))
                    target = (self.repository_root / relative).resolve()
                    try:
                        target.relative_to(self.repository_root.resolve())
                    except ValueError as exc:
                        raise ValueError("Backup contains an unsafe legacy path.") from exc
                    legacy_targets.append(target)
                else:
                    raise ValueError("Backup contains an unrecognized file.")
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_suffix(target.suffix + f".{uuid4()}.restore")
                with temporary.open("wb") as stream:
                    stream.write(archive.read(name))
                    stream.flush()
                    os.fsync(stream.fileno())
                staged[target] = temporary

        database_stage = staged.get(self.database_path)
        if database_stage is not None:
            connection = sqlite3.connect(database_stage)
            try:
                result = connection.execute("PRAGMA integrity_check").fetchone()
            finally:
                connection.close()
            if not result or result[0] != "ok":
                for temporary in staged.values():
                    temporary.unlink(missing_ok=True)
                raise ValueError("The restored Hub database failed its integrity check.")

        safety_backup = self.create(legacy_targets)
        if not self.verify(safety_backup):
            for temporary in staged.values():
                temporary.unlink(missing_ok=True)
            raise ValueError("The pre-restore safety backup could not be verified.")

        restored: list[Path] = []
        try:
            for target, temporary in staged.items():
                originals[target] = target.read_bytes() if target.exists() else None
                temporary.replace(target)
                restored.append(target)
            for suffix in ("-wal", "-shm"):
                Path(str(self.database_path) + suffix).unlink(missing_ok=True)
        except OSError:
            for target in reversed(restored):
                original = originals[target]
                try:
                    if original is None:
                        target.unlink(missing_ok=True)
                    else:
                        rollback = target.with_suffix(target.suffix + f".{uuid4()}.rollback")
                        rollback.write_bytes(original)
                        rollback.replace(target)
                except OSError:
                    pass
            raise
        finally:
            for temporary in staged.values():
                temporary.unlink(missing_ok=True)
        return safety_backup
