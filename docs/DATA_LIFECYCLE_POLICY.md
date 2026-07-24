# Data Lifecycle Policy

Living OS preserves history by default.

## Standard lifecycle

For lifecycle-managed records, the standard operations are:

1. Create
2. Read
3. Update
4. Archive
5. Restore

Archive removes a record from normal active views without physically deleting
its owner data. Restore returns it to the safest non-active state where one
exists:

- Knowledge → `NEW`
- Routine → `PAUSED`
- Investment → `WATCHLIST`
- Job → `SAVED`
- Personal Growth → `PLANNED`
- Collaboration → `PLANNED`
- Vehicle/Food catalog records → `active`

## Physical deletion

Physical deletion is allowed only where the existing domain contract requires
correction or ephemeral candidate removal:

- Health weight: incorrect-entry correction with explicit UI confirmation.
- Housing candidate: existing hard-delete contract.

Finance ledger and immutable monthly closings are not physically rewritten by
the lifecycle UI. Append a correcting transaction instead.

## UI language

Buttons use `Archive` and `Restore` consistently. Success and failure feedback
must identify the completed lifecycle action. Archived status must remain
visible in management views.
