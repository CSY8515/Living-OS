# v1.2 Migration Plan

1. Freeze and test v1.1.
2. Inventory definitions, imports, data roots, docs, and entry points.
3. Define subsystem ownership and dependencies.
4. Move implementation into engine packages.
5. Turn old paths into exact module aliases.
6. Rewrite canonical imports and moved-file roots.
7. Align v1.2 labels without schema changes.
8. Add architecture/compatibility tests and sync docs.
9. Compile, run all tests, inspect, and prepare release notes.

Rollback is a file revert to v1.1; runtime data is not transformed.
