# Living OS v2.0 Known Issues

## Release-review candidate

- Owner data is not migrated automatically. The Hub remains in v1 compatibility mode until the owner reviews a dry run and explicitly approves migration.
- Remote access requires TLS termination from the deployment environment; Living OS provides owner authentication and device pairing but does not deploy a reverse proxy or certificate service.
- The Hub is single-owner and uses one canonical SQLite store. Multi-user operation and offline concurrent editing are not supported.
- A lost owner passphrase has no automated recovery workflow in the current scope. Keep verified backups and retain local access controls.
- Operating-system credential-store availability for optional OpenAI use remains platform-dependent.
- AI requires network access, a valid key, model access, and quota; output may be inaccurate.
- Streamlit is the current responsive shell. Native desktop and mobile shells are not included.
- Existing valid v1 text is preserved byte-for-byte during migration, including pre-existing mojibake. Invalid files or records are quarantined rather than repaired automatically.
- Legacy Finance and Housing data is preserved as compatibility input only. Their v2 domain expansions are future roadmap items.
- Calendar, Routine, Notification, Inventory, Assets, Vehicle, Health, Food, Ultra Brain, and Neural Ecosystem runtime features are not implemented.

## Storage and recovery

- The canonical store supports transactional writes and optimistic concurrency, but only one Hub authority should own it.
- Backup restore is locally atomic with best-effort rollback for operating-system failures. Severe external storage failure can still prevent rollback.
- Documents are content-addressed and integrity checked; deletion and retention-policy execution are not part of the v2.0 Documents foundation.

## Historical compatibility

The original v1 JSON/JSONL schemas, deterministic reports, read-only AI behavior, and ten v1 pages remain available in compatibility mode. Runtime v1 files retain v1.0 metadata until explicit migration.
