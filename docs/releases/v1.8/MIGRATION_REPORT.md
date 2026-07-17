# Migration Report

Knowledge migration `knowledge-schema-v1` and Routine migration `routine-schema-v1` are additive, idempotent `CREATE TABLE/INDEX IF NOT EXISTS` migrations with a subsystem-owned migration ledger and schema metadata.

The schemas are lazy: construction registers contracts but does not create domain database files. First domain write or an explicit Database Management initialization creates the schema transactionally. Failed transactions roll back. Existing v1 and v1.7.1 data are untouched.

Test result: schema initialization and repeated test setup succeeded with zero migration failures. Canonical Database Foundation remains schema version 3; component schema versions are 1.
