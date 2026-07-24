from __future__ import annotations

from dataclasses import dataclass

from subsystems.foundation.engines.runtime_config import RuntimeStorageConfig
from subsystems.foundation.engines.version import PRODUCT_VERSION


@dataclass(frozen=True)
class ReleaseGateResult:
    passed: bool
    checks: dict[str, bool]
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "product_version": PRODUCT_VERSION,
            "checks": dict(self.checks),
            "failures": list(self.failures),
        }


def evaluate_release_gate(
    config: RuntimeStorageConfig,
    *,
    owner_security_configured: bool,
) -> ReleaseGateResult:
    checks = {
        "production_profile": config.production,
        "durable_data": config.durability == "durable",
        "independent_backup": config.backup_independent,
        "authentication_required": config.authentication_required,
        "owner_security_configured": owner_security_configured,
        "separate_storage_roots": config.data_root != config.backup_root,
    }
    failures = tuple(name for name, passed in checks.items() if not passed)
    return ReleaseGateResult(not failures, checks, failures)
