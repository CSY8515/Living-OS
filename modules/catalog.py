from __future__ import annotations

from core.contracts import ModuleManifest


V2_STABLE_MANIFESTS = (
    ModuleManifest(
        "journal", "Journal", "2.0.0", ">=2.0,<3.0", "Daily operating capture.",
        status="enabled", capabilities=("commands", "queries", "events"),
    ),
    ModuleManifest(
        "decision", "Decision", "2.0.0", ">=2.0,<3.0", "Versioned decision lifecycle.",
        status="enabled", capabilities=("commands", "queries", "events", "review"),
    ),
    ModuleManifest(
        "reports", "Reports", "2.0.0", ">=2.0,<3.0", "Deterministic attributable reports.",
        status="enabled", capabilities=("commands", "queries", "artifacts"),
    ),
    ModuleManifest(
        "knowledge", "Knowledge", "2.0.0", ">=2.0,<3.0", "Notes, archive, and casebook.",
        status="enabled", capabilities=("commands", "queries", "events"),
    ),
    ModuleManifest(
        "documents", "Documents", "2.0.0", ">=2.0,<3.0", "Document integrity and references.",
        status="enabled", capabilities=("commands", "queries", "content-integrity"),
    ),
    ModuleManifest(
        "dashboard", "Dashboard", "2.0.0", ">=2.0,<3.0", "Current operating projection.",
        status="enabled", capabilities=("projection",),
    ),
    ModuleManifest(
        "analytics", "Analytics", "2.0.0", ">=2.0,<3.0", "Read-only pattern summaries.",
        status="enabled", capabilities=("projection",),
    ),
    ModuleManifest(
        "review", "Review", "2.0.0", ">=2.0,<3.0", "Human review queues.",
        status="enabled", capabilities=("projection", "commands"),
    ),
    ModuleManifest(
        "ai_briefing", "AI Briefing", "2.0.0", ">=2.0,<3.0", "Source-attributed draft analysis.",
        status="enabled", capabilities=("projection", "draft-only"),
        permissions=("explicit-ai-request",),
    ),
    ModuleManifest(
        "module_manager", "Module Manager", "2.0.0", ">=2.0,<3.0", "Module lifecycle and health.",
        status="enabled", capabilities=("lifecycle", "diagnostics"),
    ),
    ModuleManifest(
        "settings", "Settings/Admin", "2.0.0", ">=2.0,<3.0", "Owner and Hub administration.",
        status="enabled", capabilities=("configuration", "backup", "migration"),
    ),
)
