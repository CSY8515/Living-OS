# Living OS v2.0.5

## Persistence & Core Stability Release

Living OS v2.0.5 strengthens owner-data persistence, recovery, operational
records, existing Backend-to-UI coverage, and the documentation foundation for
future official UI work.

## Highlights

- **Persistence** — separates development and production storage profiles,
  validates configured paths, and fails closed on unsafe production storage.
- **Backup** — verifies generated backups and retains independently configured
  backup roots.
- **Restore** — validates integrity, foreign keys, and schema compatibility,
  creates a safety backup, and records rollback outcomes.
- **Release Gate** — requires a production profile, durable data, independent
  backup, required authentication, configured Owner security, and isolated
  storage roots.
- **Execution Database** — records retry count, recovery result, product
  version, validation result, failure context, timestamp, error, and duration.
- **Backend ↔ UI** — connects existing Health checkup, exercise, nutrition,
  trend, goal-progress, and daily/weekly/monthly report capabilities.
- **CRUD / Archive** — adds consistent Archive and Restore actions while
  preserving explicit permanent-delete contracts.
- **Design Docs Foundation** — adds the official Design Bible, visual language,
  interaction, Korean UI, responsive/accessibility, and Concept Art governance
  documents under `docs/ui/`.

## Validation

- 128 automated tests passed; 0 failed.
- Streamlit all-page smoke test passed.
- Database Foundation Schema 4 is current and HEALTHY.
- Integrity check: `ok`.
- Foreign-key violations: 0.
- Migration, backup, restore, rollback, restart persistence, authentication,
  release-gate, architecture, registry, and regression checks passed.

## Known limitations

- Living OS remains a single-owner SQLite application; horizontal multi-instance
  writes are unsupported.
- Every production target must supply durable data storage, independently
  retained backup storage, TLS, and configured Owner Authentication.
- Streamlit Community Cloud application-local storage alone does not satisfy
  the v2.0.5 persistence contract.
- Global search/timeline, integrated reporting, advanced cross-analysis, Chat,
  OCR, Voice, automation, scheduler, triggers, and external integrations remain
  outside this release.
- v2.0.5 stores the Design Docs Foundation but does not apply the future full
  official UI redesign.
