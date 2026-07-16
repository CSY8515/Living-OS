# Food Subsystem v1.0 Migration and Rollback Plan

No migration is included. Living OS v1.5 contains no Food implementation or declared Food owner-data source. v1.6 does not scan for, infer, import, or reinterpret Health nutrition data.

Schema version 1 is created transactionally only by the first explicit Food write. Reads, reports, health checks, exports against an absent store, startup, and page load remain non-writing.

Code rollback returns to v1.5. A Food database may remain dormant and is never deleted automatically. Any later Food data migration, removal, or restoration requires separate owner approval and a verified copy limited to `data/food/`.
