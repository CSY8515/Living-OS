# Living OS v2.0.6 — Timeline & Report Foundation

Status: Implementation complete; owner approval pending.

## Timeline

- Common contract: Record ID, Subsystem, Record Type, Event Type, Title,
  Summary, Event Time, Created Time, Updated Time, Status, Source, Metadata.
- Common source adapter for all eleven governed Subsystems.
- Global query with date ordering, period filter, Subsystem filter, record
  navigation reference, status history, and Archive distinction.
- Existing Domain Events and Execution Database history remain the source of
  truth; no automatic business-data migration is introduced.

## Report Foundation

- Deterministic Daily, Weekly, and Monthly reports.
- Schema-versioned create, save, get, list, and Archive lifecycle.
- Existing sources: Journal, Decision, Finance, Health, Vehicle, Housing, Food.
- Basic sources: Investment, Job, Knowledge, Routine, Personal Growth,
  Collaboration.

## Exclusions

No Chat, OCR, Voice, automatic classification, AI Assistant, automation,
scheduler, trigger, Wardrobe, official UI, full Korean patch, or advanced
Analytics is included.

## Release Control

Commit, Push, Tag, Release, and Deploy require explicit owner approval.
