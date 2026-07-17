# Living OS v1.7 Migration and Rollback Plan

## Migration

Schema v2 is an additive Migration from the existing Hub Schema v1.

It adds record lifecycle Metadata, Migration history, Execution records, Backup history, Restore history and required indexes. Existing Tables and data are not renamed or deleted.

## Preconditions

- User reviews the pending Migration in Settings.
- User explicitly approves the Migration.
- Current application and Database path are confirmed.
- A verified pre-change Backup is available for Production execution.
- Tests and Release Candidate versions match.

## Execution

1. Open Settings / Database Management.
2. Confirm current Schema and pending Migration.
3. Approve and apply the v1.7 Migration.
4. Verify Schema Version 2.
5. Run and record Integrity and Health checks.
6. Create and verify a v1.7 Database Backup.
7. Confirm existing Module pages and core records.

## Failure Behavior

- Migration statements run in one SQLite Transaction.
- Any statement failure rolls back the Migration.
- Failure type is recorded in the Migration failure ledger when possible.
- Schema Version remains unchanged after rollback.
- No automatic retry runs.

## Rollback

The additive Migration does not remove old columns or Tables, so application rollback first uses the previous v1.6 code against preserved data. If Database recovery is required, restore the verified pre-Migration Backup through the approved Restore workflow.

Restore performs checksum verification, Schema compatibility validation, staging, SQLite Integrity Check and a pre-Restore safety Backup. A failed file replacement attempts to restore the original bytes.

## Real Data Status

No real workspace Database Migration has been executed during Release Candidate implementation and testing.
