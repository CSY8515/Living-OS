from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from subsystems.foundation.engines.hub import LivingHub
from subsystems.foundation.engines.release_gate import evaluate_release_gate
from subsystems.foundation.engines.runtime_config import RuntimeConfigurationError


def main() -> int:
    try:
        hub = LivingHub(ROOT)
        hub.runtime_config.prepare()
        hub.database.initialize(apply_migrations=True, actor="release-gate")
        result = evaluate_release_gate(
            hub.runtime_config,
            owner_security_configured=hub.security.configured,
        )
    except RuntimeConfigurationError as exc:
        print(json.dumps({"passed": False, "failures": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(result.to_dict(), indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
