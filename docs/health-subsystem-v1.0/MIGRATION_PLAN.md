# Health Subsystem v1.0 Migration Plan

## Inventory result

No implemented Health module, database, or Health data source exists in v1.2 Stable. `health_os` appears only as a planned legacy registry entry. Finance and all v1.2 data remain outside Health scope.

## Explicit adoption path

The optional JSON importer accepts arrays named `weights`, `body_compositions`, `health_checkups`, `sleep`, `exercise`, `nutrition`, and `goals`.

1. Select a source.
2. Run `dry_run_legacy_json`; it validates without creating storage.
3. Review accepted counts.
4. Run `migrate_legacy_json` only after owner approval.
5. One transaction writes records and a path/SHA-256 receipt.
6. Identical repeats return the receipt; changed sources are rejected.

Invalid input leaves no partial state. Source bytes are never modified. Real owner data migration remains pending explicit user approval. Rollback restores a pre-migration backup or removes a newly created isolated target.

