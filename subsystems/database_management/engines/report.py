from __future__ import annotations

from typing import Any

from subsystems.foundation.engines.time import utc_now_iso


def build_management_report(
    health: dict[str, Any],
    schema: dict[str, Any],
    backups: list[dict[str, Any]],
    restores: list[dict[str, Any]],
    failures: list[dict[str, Any]],
) -> dict[str, Any]:
    recommendations: list[str] = []
    if health.get("migration_status") == "PENDING":
        recommendations.append("Review and explicitly apply the pending v1.7 database migration.")
    if health.get("integrity_status") != "ok":
        recommendations.append("Run an explicit integrity check and review recovery readiness.")
    if not backups:
        recommendations.append("Create and verify a manual database backup.")
    if failures:
        recommendations.append("Review failed migration records before further schema changes.")
    if not recommendations:
        recommendations.append("No immediate database management action is required.")
    return {
        "report_type": "database_management",
        "generated_at": utc_now_iso(),
        "database_status": health.get("status"),
        "schema_status": {
            "current": schema.get("schema_version"),
            "expected": schema.get("expected_schema_version"),
            "tables": len(schema.get("tables", [])),
            "indexes": len(schema.get("indexes", [])),
        },
        "migration_status": health.get("migration_status"),
        "backup_status": {
            "count": len(backups),
            "latest": backups[0].get("created_at", "") if backups else "",
        },
        "restore_status": {
            "count": len(restores),
            "latest": restores[0].get("completed_at", "") if restores else "",
        },
        "integrity_status": health.get("integrity_status"),
        "performance_status": {
            "health_check_duration_ms": health.get("health_check_duration_ms", 0),
            "degraded_check_ms": health.get("degraded_check_ms", 0),
        },
        "capacity_status": {
            "status": health.get("capacity_status", "UNKNOWN"),
            "size_bytes": health.get("file_size", 0),
            "warning_bytes": health.get("capacity_warning_bytes", 0),
        },
        "recent_error": health.get("recent_error", ""),
        "recommendations": recommendations,
    }
