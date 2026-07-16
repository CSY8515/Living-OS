# Vehicle Subsystem v1.0 Migration and Rollback Plan

## Migration

No migration is included. Living OS v1.4 contains no Vehicle implementation or Vehicle owner-data source. v1.5 must not scan for, infer, or import one. Schema version 1 is created transactionally only by the first explicit Vehicle write; reads, reports, startup, and page load remain non-writing.

## Rollback

Code rollback returns to v1.4. The isolated Vehicle database may remain dormant and is never deleted automatically. Any future removal or restoration requires separate owner approval, a verified database copy, and operations limited to `data/vehicle/`. No v1.4 store is a Vehicle rollback target.

Status: approved plan; no migration or rollback operation authorized or performed.
