from __future__ import annotations

import ast
import importlib
import unittest
from pathlib import Path

from modules.catalog import V12_STABLE_MANIFESTS, V2_STABLE_MANIFESTS


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_RUNTIME_DIRS = ("app", "core", "modules", "shared")
FORBIDDEN_CANONICAL_ROOTS = {"app", "core", "modules", "shared", "expansion"}


class SubsystemArchitectureTests(unittest.TestCase):
    def test_runtime_functions_live_below_subsystems(self) -> None:
        violations: list[str] = []
        for directory in PUBLIC_RUNTIME_DIRS:
            for path in (ROOT / directory).rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in tree.body):
                    violations.append(str(path.relative_to(ROOT)))
        self.assertEqual(violations, [])

    def test_canonical_subsystems_do_not_import_compatibility_facades(self) -> None:
        violations: list[str] = []
        for path in (ROOT / "subsystems").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".", 1)[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = {node.module.split(".", 1)[0]}
                else:
                    continue
                forbidden = roots & FORBIDDEN_CANONICAL_ROOTS
                if forbidden:
                    violations.append(f"{path.relative_to(ROOT)} -> {sorted(forbidden)}")
        self.assertEqual(violations, [])

    def test_subsystem_dependencies_follow_the_allowed_direction(self) -> None:
        allowed = {
            "foundation": {"foundation"},
            "operations": {"operations", "foundation"},
            "insight": {"insight", "foundation"},
            "experience": {"experience", "foundation", "operations", "insight", "compatibility", "finance", "health"},
            "finance": {"finance"},
            "health": {"health"},
            "compatibility": {"compatibility", "insight"},
        }
        violations: list[str] = []
        for path in (ROOT / "subsystems").rglob("*.py"):
            owner = path.relative_to(ROOT / "subsystems").parts[0]
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                if not module or not module.startswith("subsystems."):
                    continue
                target = module.split(".")[1]
                if target not in allowed[owner]:
                    violations.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(violations, [])
    def test_legacy_imports_alias_the_canonical_engine_module(self) -> None:
        pairs = (
            ("core.hub", "subsystems.foundation.engines.hub"),
            ("modules.journal.service", "subsystems.operations.engines.journal"),
            ("modules.projections", "subsystems.insight.engines.projections"),
            ("app.shell", "subsystems.experience.engines.shell"),
            ("modules.storage", "subsystems.compatibility.engines.storage"),
        )
        for facade, canonical in pairs:
            with self.subTest(facade=facade):
                self.assertIs(importlib.import_module(facade), importlib.import_module(canonical))

    def test_unreleased_v2_catalog_name_remains_a_compatibility_alias(self) -> None:
        self.assertIs(V2_STABLE_MANIFESTS, V12_STABLE_MANIFESTS)


if __name__ == "__main__":
    unittest.main()
