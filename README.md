# Living OS v1.0 Stable

Living OS is a local-first, single-user Streamlit application for daily records, decisions, reports, archives, analytics, review, module planning, backups, and optional user-triggered OpenAI assistance.

## Stable-release guarantees

- All v0.9 pages and JSON/JSONL schemas are preserved.
- Existing v0.9 data loads without migration.
- AI is optional, foreground-only, and read-only by default.
- AI requests occur only after the user selects displayed content and presses an action button.
- AI output never changes records. Saving an AI report draft requires a separate explicit action.
- There is no database, authentication, notification service, background automation, or autonomous AI action.

## Pages

- Dashboard
- Daily Log
- Decision Log
- Reports
- Archive
- Analytics
- Review
- AI Analysis
- Module Manager
- Settings

The historical Finance and Housing source modules and data assets remain available for backward compatibility but are not navigation pages.

## Requirements

- Python 3.11 or newer
- A local environment able to install `requirements.txt`
- Optional AI use: network access, an OpenAI API key, access to a configured model, and available quota

## Install and run

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Living OS reads and writes within the repository's `data`, `logs`, `reports`, `state`, `config`, and `backups` directories. Run it from a location where the current user has write access.

## Data and compatibility

- Daily Logs: `data/daily_logs.json`
- Decisions: `logs/decision_log.jsonl`
- Archive: `data/archive.json`
- Report index and Markdown reports: `reports/`
- Settings: `state/settings.json`
- Module registry: `config/module_registry.json`
- Backups: `backups/`

Do not edit malformed data through the application. v1.0 refuses affected saves rather than silently replacing unreadable existing JSON. Use a verified backup or repair the source manually outside Living OS.

## Optional OpenAI configuration

OpenAI credentials are resolved in this order:

1. Session-only key entered in Settings
2. Operating-system credential store
3. `OPENAI_API_KEY` environment variable

API keys are never stored in Living OS JSON/JSONL files. Settings provides explicit controls to save or remove a credential and to test the connection manually. Selected record fields are shown before they are sent.

AI output is untrusted and may be inaccurate. Daily Log and Decision analysis remains session-only. An AI report draft can be edited and saved only through the separately labeled explicit save control.

## Backup and restore

Settings can create a JSON backup of the configured Living OS data targets. Restore validates all recognized JSON/JSONL content before writing. Invalid input is rejected before any target is changed. Backups are not full filesystem snapshots and do not include arbitrary attachments.

## Verification

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app.py modules tests
```

Before release, also start Streamlit headlessly and smoke-test every page. Tests use temporary files and mocks rather than real user data.

## Known limitations

- Local, single-user operation only
- No support for concurrent writers or very large datasets
- Invalid dates are excluded from bounded date filters
- Malformed data is not repaired automatically
- Credential-store availability depends on the operating system
- OpenAI use can incur charges and sends only explicitly selected displayed content to OpenAI

See `KNOWN_ISSUES.md`, `CHANGELOG.md`, and `docs/ROADMAP_v1.0.md` for release details.
