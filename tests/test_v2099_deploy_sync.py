from __future__ import annotations

from pathlib import Path
import runpy

import app.shell as cached_shell
import subsystems.foundation.engines.version as cached_version


ROOT = Path(__file__).resolve().parents[1]


def test_entrypoint_refreshes_stale_modules_after_repository_update() -> None:
    cached_version.PRODUCT_VERSION = "v2.0.9.8"
    cached_shell.VERSION = "v2.0.9.8"

    namespace = runpy.run_path(str(ROOT / "app.py"), run_name="living_deploy_sync_check")

    assert namespace["VERSION"] == "v2.0.9.9"
    assert cached_version.PRODUCT_VERSION == "v2.0.9.9"
