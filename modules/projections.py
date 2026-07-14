from __future__ import annotations

from collections import Counter
from typing import Any

from core.hub import LivingHub


REVIEWABLE_STATUSES = {"draft", "active", "review"}


def dashboard_projection(hub: LivingHub) -> dict[str, Any]:
    journals = hub.store.list_records("journal", "journal_entry")
    decisions = hub.store.list_records("decision", "decision")
    reports = hub.store.list_records("reports", "report")
    knowledge = hub.store.list_records("knowledge", "knowledge_item")
    return {
        "journal_count": len(journals),
        "decision_count": len(decisions),
        "review_count": sum(
            1 for item in decisions if str(item.get("status", "")).lower() in REVIEWABLE_STATUSES
        ),
        "report_count": len(reports),
        "knowledge_count": len(knowledge),
        "recent_journals": journals[:5],
        "recent_decisions": decisions[:5],
        "system_status": "NORMAL",
    }


def analytics_projection(hub: LivingHub) -> dict[str, Any]:
    journals = hub.store.list_records("journal", "journal_entry")
    decisions = hub.store.list_records("decision", "decision")
    knowledge = hub.store.list_records("knowledge", "knowledge_item")
    journal_tags: Counter[str] = Counter()
    knowledge_tags: Counter[str] = Counter()
    for item in journals:
        for tag in item.get("tags", []) if isinstance(item.get("tags", []), list) else []:
            if str(tag).strip():
                journal_tags[str(tag).strip()] += 1
    for item in knowledge:
        for tag in item.get("tags", []) if isinstance(item.get("tags", []), list) else []:
            if str(tag).strip():
                knowledge_tags[str(tag).strip()] += 1
    return {
        "counts": {
            "journals": len(journals),
            "decisions": len(decisions),
            "knowledge": len(knowledge),
            "reports": len(hub.store.list_records("reports", "report")),
        },
        "journal_tags": journal_tags,
        "knowledge_tags": knowledge_tags,
        "decision_statuses": Counter(str(item.get("status", "draft")) for item in decisions),
    }


def review_projection(hub: LivingHub) -> dict[str, Any]:
    decisions = hub.store.list_records("decision", "decision")
    queue = [
        item
        for item in decisions
        if str(item.get("status", "")).lower() in REVIEWABLE_STATUSES
    ]
    activity: list[dict[str, Any]] = []
    for module_id, entity_type, label, title_field in (
        ("journal", "journal_entry", "Journal", "title"),
        ("decision", "decision", "Decision", "decision"),
        ("knowledge", "knowledge_item", "Knowledge", "title"),
        ("reports", "report", "Report", "report_type"),
    ):
        for item in hub.store.list_records(module_id, entity_type):
            activity.append(
                {
                    "type": label,
                    "id": item.get("id", "-"),
                    "title": item.get(title_field, "Untitled"),
                    "updated_at": item.get("updated_at") or item.get("created_at") or "",
                }
            )
    activity.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return {"queue": queue, "activity": activity[:20]}
