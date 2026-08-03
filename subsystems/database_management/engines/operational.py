from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from typing import Any

from subsystems.database.engines.contracts import (
    DatabaseControlInterface,
    OPERATIONAL_DATA_REGISTRY,
    OPERATIONAL_SEVERITIES,
)


SEVERITY_RANK = {name: index for index, name in enumerate(OPERATIONAL_SEVERITIES)}


def _fingerprint(payload: dict[str, Any]) -> str:
    source = {
        "categories": sorted(str(item) for item in payload.get("categories", [])),
        "source_subsystem": str(payload.get("source_subsystem", "")),
        "title": str(payload.get("title", "")),
        "summary": str(payload.get("summary", "")),
    }
    encoded = json.dumps(source, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _execution_categories(item: dict[str, Any]) -> list[str]:
    categories: list[str] = []
    status = str(item.get("status", "")).upper()
    error_code = str(item.get("error_code", ""))
    validation = str(item.get("validation_result", "")).upper()
    recovery = str(item.get("recovery_result", "")).upper()
    context = item.get("failure_context", {})
    if not isinstance(context, dict):
        context = {}

    if status in {"COMPLETED", "SUCCESS", "SUCCEEDED"} and validation != "FAILED" and not error_code:
        categories.append("SUCCESS")
    if status in {"FAILED", "FAILURE", "ERROR"}:
        categories.extend(("FAILURE", "EXECUTION_FAILURE"))
    if status == "WARNING":
        categories.append("WARNING")
    if error_code:
        categories.append("ERROR")
    if validation == "FAILED":
        categories.append("VALIDATION_FAILURE")
        if error_code in {"ValueError", "KeyError"}:
            categories.append("INVALID_DATA")
    if recovery and recovery not in {"NOT_ATTEMPTED", "NOT_REQUIRED"}:
        categories.append("RECOVERY")
    if recovery in {"ROLLED_BACK", "ROLLBACK_FAILED"}:
        categories.append("ROLLBACK")
    declared = str(context.get("operational_type", "")).upper()
    if declared in OPERATIONAL_DATA_REGISTRY:
        categories.append(declared)
    return list(dict.fromkeys(categories))


class OperationalAnalysisEngine:
    """Read-only control-plane analysis over preserved operational records."""

    def __init__(self, database: DatabaseControlInterface) -> None:
        self.database = database

    def collect(self, *, limit: int = 1000) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for item in self.database.operational_data(limit=limit):
            data_type = str(item.get("data_type", ""))
            metadata = item.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {"invalid_metadata_type": type(metadata).__name__}
            normalized = {
                "record_id": str(item.get("operational_id", item.get("id", ""))),
                "record_kind": "operational_data",
                "categories": [data_type],
                "source_subsystem": str(item.get("source_subsystem", "")),
                "title": str(item.get("title", "")),
                "summary": str(item.get("summary", "")),
                "severity": str(item.get("severity", "INFO")),
                "resolution_status": str(item.get("resolution_status", "OPEN")),
                "occurred_at": str(item.get("occurred_at", item.get("_created_at", ""))),
                "related_execution_id": str(item.get("related_execution_id", "")),
                "recovery_result": str(item.get("recovery_result", "")),
                "validation_result": str(item.get("validation_result", "")),
                "recoverable": item.get("recoverable"),
                "retryable": item.get("retryable"),
                "fingerprint": str(item.get("fingerprint", "")),
                "metadata": metadata,
            }
            normalized["fingerprint"] = normalized["fingerprint"] or _fingerprint(normalized)
            records.append(normalized)

        for item in self.database.execution_records(limit):
            categories = _execution_categories(item)
            if not categories:
                continue
            severity = max(
                (OPERATIONAL_DATA_REGISTRY[name]["severity"] for name in categories),
                key=lambda name: SEVERITY_RANK[name],
            )
            status = str(item.get("status", "")).upper()
            action = str(item.get("action", "execution"))
            error_code = str(item.get("error_code", ""))
            normalized = {
                "record_id": str(item.get("execution_id", "")),
                "record_kind": "execution_record",
                "categories": categories,
                "source_subsystem": str(item.get("subsystem", "")),
                "title": action,
                "summary": f"{status}: {error_code or 'no-error-code'}",
                "severity": severity,
                "resolution_status": (
                    "OPEN"
                    if {"FAILURE", "ERROR", "EXECUTION_FAILURE", "UNRESOLVED_ISSUE"}
                    .intersection(categories)
                    else "RESOLVED"
                ),
                "occurred_at": str(item.get("recorded_at", item.get("started_at", ""))),
                "related_execution_id": str(item.get("execution_id", "")),
                "recovery_result": str(item.get("recovery_result", "")),
                "validation_result": str(item.get("validation_result", "")),
                "metadata": {
                    "action": action,
                    "status": status,
                    "error_code": error_code,
                    "retry_count": int(item.get("retry_count", 0)),
                },
            }
            normalized["fingerprint"] = _fingerprint(normalized)
            records.append(normalized)
        return records

    def analyze(self, *, limit: int = 1000) -> dict[str, Any]:
        records = self.collect(limit=limit)
        valid: list[dict[str, Any]] = []
        invalid: list[dict[str, Any]] = []
        fingerprints: dict[str, str] = {}
        canonical: list[dict[str, Any]] = []
        duplicates: list[dict[str, str]] = []

        for item in records:
            categories = item.get("categories", [])
            if (
                not item.get("record_id")
                or not item.get("source_subsystem")
                or not categories
                or any(category not in OPERATIONAL_DATA_REGISTRY for category in categories)
                or item.get("severity") not in OPERATIONAL_SEVERITIES
            ):
                invalid.append(item)
                continue
            valid.append(item)
            fingerprint = str(item["fingerprint"])
            duplicate_of = fingerprints.get(fingerprint)
            if duplicate_of:
                duplicates.append(
                    {"record_id": str(item["record_id"]), "duplicate_of": duplicate_of}
                )
            else:
                fingerprints[fingerprint] = str(item["record_id"])
                canonical.append(item)

        classification = Counter(
            category for item in valid for category in item["categories"]
        )
        by_source = Counter(str(item["source_subsystem"]) for item in valid)
        fingerprint_counts = Counter(str(item["fingerprint"]) for item in valid)
        repeated = [
            {"fingerprint": key, "count": count, "canonical_record": fingerprints[key]}
            for key, count in fingerprint_counts.items()
            if count > 1
        ]
        unresolved = [
            item
            for item in valid
            if item["resolution_status"] == "OPEN"
            or "UNRESOLVED_ISSUE" in item["categories"]
        ]

        recommendations: list[str] = []
        if classification["INCIDENT"]:
            recommendations.append("Review active incidents and confirm recovery ownership.")
        if classification["UNRESOLVED_ISSUE"] or unresolved:
            recommendations.append("Prioritize unresolved operational issues by severity.")
        if classification["VALIDATION_FAILURE"] or classification["INVALID_DATA"]:
            recommendations.append("Review the failing validation boundary before retrying writes.")
        if duplicates:
            recommendations.append(
                "Consolidate duplicate reporting paths while preserving every source record."
            )
        if not recommendations:
            recommendations.append("No immediate operational remediation is required.")

        rule_candidates = [
            {
                "candidate_id": f"RULE-CANDIDATE-{item['fingerprint'][:12]}",
                "status": "CANDIDATE",
                "reason": f"The same operational pattern occurred {item['count']} times.",
                "source_fingerprint": item["fingerprint"],
            }
            for item in repeated
            if item["count"] >= 3
        ]
        category_sources: dict[str, set[str]] = defaultdict(set)
        for item in valid:
            for category in item["categories"]:
                category_sources[category].add(str(item["source_subsystem"]))
        standard_candidates = [
            {
                "candidate_id": f"STANDARD-CANDIDATE-{category}",
                "status": "CANDIDATE",
                "reason": (
                    f"{category} appeared {classification[category]} times across "
                    f"{len(sources)} subsystems."
                ),
                "category": category,
            }
            for category, sources in category_sources.items()
            if classification[category] >= 3 and len(sources) >= 2
        ]

        priority = "LOW"
        if any(item["severity"] == "CRITICAL" for item in unresolved):
            priority = "CRITICAL"
        elif classification["INCIDENT"] or classification["EXECUTION_FAILURE"]:
            priority = "HIGH"
        elif classification["WARNING"] or unresolved:
            priority = "MEDIUM"

        return {
            "records_total": len(records),
            "records_preserved": len(records),
            "valid_records": len(valid),
            "invalid_records": invalid,
            "logical_records": len(canonical),
            "duplicates": duplicates,
            "classification": dict(sorted(classification.items())),
            "by_source": dict(sorted(by_source.items())),
            "patterns": {"repeated_fingerprints": repeated},
            "unresolved_issues": unresolved,
            "recommendations": recommendations,
            "rule_candidates": rule_candidates,
            "standard_candidates": standard_candidates,
            "priority": priority,
        }
