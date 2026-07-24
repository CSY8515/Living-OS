from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import tempfile
from typing import Mapping
from uuid import uuid4


class RuntimeConfigurationError(RuntimeError):
    """Raised when the selected runtime profile cannot protect owner data."""


TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class RuntimeStorageConfig:
    repository_root: Path
    environment: str
    data_root: Path
    backup_root: Path
    durability: str
    backup_independent: bool
    authentication_required: bool

    @property
    def production(self) -> bool:
        return self.environment == "production"

    @classmethod
    def from_environment(
        cls,
        repository_root: Path,
        environment: Mapping[str, str] | None = None,
    ) -> "RuntimeStorageConfig":
        values = os.environ if environment is None else environment
        repository = Path(repository_root).resolve()
        requested_environment = str(values.get("LIVING_OS_ENV", "development")).strip().lower()
        remote_access = _enabled(values.get("LIVING_OS_REMOTE_ACCESS"))
        selected_environment = "production" if remote_access else requested_environment
        if selected_environment not in {"development", "test", "production"}:
            raise RuntimeConfigurationError(
                "LIVING_OS_ENV must be development, test, or production."
            )

        raw_data = str(values.get("LIVING_OS_DATA_ROOT", "")).strip()
        raw_backup = str(values.get("LIVING_OS_BACKUP_ROOT", "")).strip()
        if selected_environment == "production" and (not raw_data or not raw_backup):
            raise RuntimeConfigurationError(
                "Production requires absolute LIVING_OS_DATA_ROOT and LIVING_OS_BACKUP_ROOT paths."
            )

        data_root = Path(raw_data).expanduser() if raw_data else repository / "data"
        backup_root = Path(raw_backup).expanduser() if raw_backup else repository / "backups"
        if selected_environment == "production" and (
            not data_root.is_absolute() or not backup_root.is_absolute()
        ):
            raise RuntimeConfigurationError("Production storage paths must be absolute.")
        data_root = data_root.resolve()
        backup_root = backup_root.resolve()

        durability = str(
            values.get(
                "LIVING_OS_STORAGE_DURABILITY",
                "durable" if selected_environment == "production" else "local-development",
            )
        ).strip().lower()
        backup_independent = _enabled(values.get("LIVING_OS_BACKUP_INDEPENDENT"))
        authentication_required = _enabled(values.get("LIVING_OS_REQUIRE_AUTH")) or remote_access

        config = cls(
            repository_root=repository,
            environment=selected_environment,
            data_root=data_root,
            backup_root=backup_root,
            durability=durability,
            backup_independent=backup_independent,
            authentication_required=authentication_required,
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.data_root == self.backup_root:
            raise RuntimeConfigurationError("Data and backup roots must be different.")
        if _inside(self.backup_root, self.data_root) or _inside(self.data_root, self.backup_root):
            raise RuntimeConfigurationError(
                "Data and backup roots must not contain one another."
            )
        if not self.production:
            return

        temporary_root = Path(tempfile.gettempdir()).resolve()
        if self.durability != "durable":
            raise RuntimeConfigurationError(
                "Production requires LIVING_OS_STORAGE_DURABILITY=durable."
            )
        if not self.backup_independent:
            raise RuntimeConfigurationError(
                "Production requires LIVING_OS_BACKUP_INDEPENDENT=true."
            )
        if not self.authentication_required:
            raise RuntimeConfigurationError(
                "Production requires LIVING_OS_REQUIRE_AUTH=true."
            )
        for label, path in (("data", self.data_root), ("backup", self.backup_root)):
            if _inside(path, self.repository_root):
                raise RuntimeConfigurationError(
                    f"Production {label} storage must be outside the application checkout."
                )
            if _inside(path, temporary_root):
                raise RuntimeConfigurationError(
                    f"Production {label} storage must not use a temporary directory."
                )

    def prepare(self) -> None:
        """Create and write-probe both roots before the database is opened."""
        for label, path in (("data", self.data_root), ("backup", self.backup_root)):
            try:
                path.mkdir(parents=True, exist_ok=True)
                probe = path / f".living-os-{label}-{uuid4().hex}.probe"
                with probe.open("x", encoding="utf-8") as stream:
                    stream.write("Living OS storage validation\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                probe.unlink()
            except OSError as exc:
                raise RuntimeConfigurationError(
                    f"Living OS cannot write to the configured {label} root: {path}"
                ) from exc

    def component_database_path(self, component: str) -> Path:
        clean = component.strip().lower().replace("_", "-")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", clean):
            raise RuntimeConfigurationError("Invalid component storage name.")
        directory = clean.replace("-", "_")
        return self.data_root / directory / f"{directory}.sqlite3"

    def status(self) -> dict[str, object]:
        return {
            "environment": self.environment,
            "production": self.production,
            "data_root": str(self.data_root),
            "backup_root": str(self.backup_root),
            "durability": self.durability,
            "backup_independent": self.backup_independent,
            "authentication_required": self.authentication_required,
        }
