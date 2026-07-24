# Persistence and Release Gate

## Purpose

Living OS v2.0.5 separates a convenient local development profile from the
production contract required to protect owner data. Production must fail closed;
an application process is not considered a storage service.

## Development profile

With no environment variables, Living OS uses:

- data: `<repository>/data`
- backup: `<repository>/backups`
- authentication: optional until explicitly configured

This profile is for a trusted local, single-owner workstation. It is never a
production-readiness signal.

## Production profile

Set all of the following:

```text
LIVING_OS_ENV=production
LIVING_OS_DATA_ROOT=<absolute durable data root>
LIVING_OS_BACKUP_ROOT=<absolute independently retained backup root>
LIVING_OS_STORAGE_DURABILITY=durable
LIVING_OS_BACKUP_INDEPENDENT=true
LIVING_OS_REQUIRE_AUTH=true
```

`LIVING_OS_REMOTE_ACCESS=true` also selects the production safety policy for
backward compatibility.

Production validation rejects relative paths, temporary directories, storage
inside the application checkout, identical roots, nested roots, missing
durability declarations, non-independent backup, and optional authentication.
Both roots are write-probed before the database is opened.

## Owner Authentication

The production database must already contain an Owner Authentication secret.
An unconfigured production deployment is locked; it does not expose a public
first-owner claim screen. Provision and verify the owner database in the trusted
deployment environment before release.

To provision a new durable database, point `LIVING_OS_DATA_ROOT` and
`LIVING_OS_BACKUP_ROOT` at the approved roots in a trusted, non-production
session, set `LIVING_OS_REQUIRE_AUTH=true`, complete Owner Setup locally, then
stop the process and enable the production profile. Never expose the initial
setup session through a public endpoint.

## Release gate

Run:

```text
python scripts/release_gate.py
```

PASS requires:

1. production profile;
2. durable data;
3. independent backup;
4. authentication required;
5. Owner Authentication configured;
6. distinct data and backup roots.

The gate never substitutes for provider-level proof of persistence. The release
operator must also verify restart persistence and backup retention on the target
hosting platform.

## Backup and restore

- Backups are checksum verified.
- Restore candidates are checked before replacement.
- A safety backup is created before restore.
- Restored databases must pass integrity and foreign-key verification.
- A v2.0.4 Schema 3 backup is migrated additively to Schema 4 after restore.
- Failed post-restore validation triggers rollback.
- Execution records store the recovery result.
