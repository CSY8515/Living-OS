# Health Subsystem v1.0 Engine Map

| Engine | Public facade functions |
|---|---|
| Weight | `record_weight`, `update_weight`, `delete_weight`, `list_weights`, `weight_baseline_comparison` |
| Body Composition | `record_body_composition`, `body_composition_timeline`, `body_composition_baseline_comparison` |
| Health Checkup | `record_health_checkup`, `list_health_checkups`, `health_checkup_follow_ups`, `health_checkup_baseline_comparison` |
| Sleep | `record_sleep`, `list_sleep` |
| Exercise | `record_exercise`, `list_exercise`, `exercise_statistics` |
| Nutrition | `record_nutrition`, `list_nutrition` |
| Trend | `weight_trend`, `inbody_trend`, `sleep_trend`, `exercise_trend` |
| Goal | `create_health_goal`, `list_health_goals`, `health_goal_progress` |
| Health Report | `daily_report`, `weekly_report`, `monthly_report` |
| Migration | `dry_run_legacy_json`, `migrate_legacy_json` |
| Storage/interface | `health`, `interface_manifest`, `export_snapshot`, `database_path` |

