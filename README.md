# Living OS v2.0 Implementation Candidate

Living OS is a single-owner modular personal operating Hub. The approved v2.0 Stable scope provides one canonical Core, explicit audited commands, module-owned domains, verified migration and backup, responsive connected-device access, and full Living OS v1 compatibility.

Status: implementation complete; release review pending. No release or deployment has occurred.

## Implemented scope

- Transactional SQLite Hub store behind a Core storage port
- Stable record references, versioned schemas, optimistic concurrency, domain events, audit, and typed relationships
- Dry-run-first v1 migration with checksums, quarantine reporting, verified backup, and no source rewriting
- Verified v2 backup, restore, pre-restore safety backup, integrity checking, and rollback
- Canonical Journal, Decision, Reports, Knowledge, Settings, Dashboard, Analytics, and Review
- Documents foundation with SHA-256 integrity and privacy classification
- Real Module Manager lifecycle and health states
- Provider-neutral, explicit-approval, draft-only AI Integration Layer
- Single-owner passphrase security and revocable device pairing
- Responsive Streamlit Hub shell for desktop, notebook, tablet, and mobile browsers
- v1 compatibility mode until the owner explicitly approves migration

Future roadmap modules are not implemented. See `ROADMAP.md`.

## Requirements

- Python 3.11 or newer
- Dependencies from `requirements.txt`
- A writable local repository directory
- Optional AI: network access, an API key, model access, and quota
- Remote access: a deployment profile that terminates TLS

## Run

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For a remotely reachable Hub, set `LIVING_OS_REMOTE_ACCESS=1`. Living OS then requires owner-security setup before opening. TLS must still be supplied by the deployment environment.

## Compatibility and migration

The Hub starts in v1 compatibility mode when migration has not been approved. Existing JSON, JSONL, Markdown reports, settings, module registry, Finance data, and Housing data remain untouched.

Settings provides:

1. A read-only migration dry run.
2. Source checksums, accepted counts, canonical count, and quarantine reasons.
3. Explicit approval.
4. A verified pre-migration backup.
5. Transactional canonical import.

Migration is never triggered by startup, navigation, or page load.

## Data

- Canonical Hub: `data/hub/living_os.sqlite3` (ignored by Git)
- Canonical documents: `data/hub/documents/` (ignored by Git)
- Backups: `backups/v2/` (ignored by Git)
- v1 compatibility sources: existing `data/`, `logs/`, `reports/`, `state/`, and `config/` files

Private runtime data, secrets, documents, and backups must not enter release artifacts.

## AI safety

AI requests require an explicit action and use a visible selected context. The provider is isolated behind the AI gateway. Output is untrusted and draft-only. AI cannot directly change canonical records; saving an AI report draft is a separate audited command.

## Verification

```powershell
python -m compileall -q app.py app core modules shared tests
python -m unittest discover -s tests -v
```

Release review additionally requires headless startup, every-page smoke verification, documentation review, artifact inspection, and explicit user approval.

## Documentation

- `MASTER_DESIGN.md` — architectural authority
- `ARCHITECTURE.md` — architecture and dependency direction
- `STRUCTURE.md` — repository ownership
- `ROADMAP.md` — release and future-module sequence
- `VERSION.md` — lifecycle status
- `RELEASE_NOTES_v2.0.md` — release-review draft
- `KNOWN_ISSUES.md` — current limitations
