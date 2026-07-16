# Housing Subsystem v1.0 Migration and Rollback Report

## Source and authority

The optional importer reads `data/housing_candidates.json`. The source is never modified or removed. Until an owner explicitly applies migration, the legacy source remains authoritative and the new database need not exist.

## Migration controls

1. `dry_run_legacy_json` reads and validates every candidate, computes the source SHA-256, reports accepted counts, and creates no database.
2. The owner reviews the dry-run result.
3. `migrate_legacy_json` is invoked separately and explicitly.
4. One SQLite transaction inserts all candidates and the migration receipt.
5. Invalid input rolls back without partial state.
6. An identical repeat returns the prior receipt; changed source bytes are rejected.

No real user-data migration was run during v1.4 release preparation.

## Rollback

Before a future owner-approved migration, copy the isolated target database if it already exists. Rollback restores that copy or removes only a newly created `data/housing/housing.sqlite3` after explicit owner approval. Reverting v1.4 code leaves all v1.3 data, legacy Housing code, and `data/housing_candidates.json` intact.
