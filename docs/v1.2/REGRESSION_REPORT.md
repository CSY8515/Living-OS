# v1.2 Regression Report

Baseline: 44/44 tests passed. Architecture migration checkpoint: 49/49 passed. Final integrated release: 60/60 passed.

Coverage includes historical compatibility, storage/schema safety, rollback, commands/events/audit, migration/security/integrations, both Streamlit shells, subsystem placement, forbidden imports, facade identity, catalog alias compatibility, and the complete Finance Subsystem.

```text
python -m compileall -q app.py app core modules shared subsystems tests
python -m unittest discover -s tests -v
```

Compilation and all tests pass. Streamlit bare-mode `ScriptRunContext` warnings are expected in headless smoke tests.