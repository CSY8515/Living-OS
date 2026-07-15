# v1.2 Changed Files

Generated from the final pre-release working tree on 2026-07-15.

## Change groups

- Canonical runtime: subsystems/ with Foundation, Operations, Insight, Experience, Compatibility, and Finance.
- Compatibility facades: pp/, core/, modules/, and shared/.
- Finance integration: catalog, Streamlit pages, isolated storage rules, migration, and tests.
- Release documentation: root architecture/version/release files plus docs/v1.2/, docs/finance-subsystem-v1.0/, and docs/releases/v1.2/.
- Regression suite: historical v0.8/v1.0 coverage, v1.2 architecture coverage, and Finance Subsystem v1.0 coverage.
- Historical v2.0 draft artifacts are archived under docs/archive/ and replaced by v1.2-named tests and release documents.

## Git change inventory

`	ext
 M .gitignore
 M ARCHITECTURE.md
 M CHANGELOG.md
 M KNOWN_ISSUES.md
 M MASTER_DESIGN.md
 M README.md
 D RELEASE_NOTES_v2.0.md
 M ROADMAP.md
 M STRUCTURE.md
 M VERSION.md
 M app.py
 M app/__init__.py
 M app/pages.py
 M app/responsive.py
 M app/shell.py
 M config/modules/README.md
 M core/__init__.py
 M core/audit.py
 M core/backup.py
 M core/commands.py
 M core/contracts.py
 M core/documents.py
 M core/errors.py
 M core/hub.py
 M core/integrations.py
 M core/migration.py
 M core/module_runtime.py
 M core/relationships.py
 M core/schemas.py
 M core/security.py
 M core/storage.py
 M docs/README.md
 M docs/ai-developer-guide.md.txt
 M docs/architecture.md.txt
 M docs/master-blueprint.md.txt
 M docs/release-plan.md.txt
 M expansion/README.md
 M modules/ai_analysis.py
 M modules/ai_briefing/service.py
 M modules/ai_credentials.py
 M modules/ai_service.py
 M modules/analytics.py
 M modules/archive.py
 M modules/catalog.py
 M modules/daily_log.py
 M modules/dashboard.py
 M modules/date_utils.py
 M modules/decision/service.py
 M modules/decision_log.py
 M modules/finance.py
 M modules/formatting.py
 M modules/housing.py
 M modules/hub_settings.py
 M modules/journal/service.py
 M modules/knowledge/service.py
 M modules/module_manager.py
 M modules/projections.py
 M modules/report_system.py
 M modules/reports/service.py
 M modules/review.py
 M modules/settings.py
 M modules/storage.py
 M scripts/README.md
 M shared/time.py
 M tests/test_streamlit.py
 M tests/test_v08.py
 M tests/test_v10.py
 D tests/test_v20_core.py
 D tests/test_v20_modules.py
 D tests/test_v20_security_integration.py
 D tests/test_v20_streamlit.py
?? RELEASE_NOTES_FINANCE_SUBSYSTEM_v1.0.md
?? RELEASE_NOTES_v1.2.md
?? docs/archive/
?? docs/finance-subsystem-v1.0/
?? docs/releases/
?? docs/v1.2/
?? subsystems/
?? tests/test_finance_subsystem_v10.py
?? tests/test_v12_architecture.py
?? tests/test_v12_core.py
?? tests/test_v12_modules.py
?? tests/test_v12_security_integration.py
?? tests/test_v12_streamlit.py
`

Rename detection during staging may present compatibility moves more compactly than this unstaged inventory.