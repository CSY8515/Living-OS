from __future__ import annotations

from subsystems.foundation.engines.contracts import ModuleManifest


V12_STABLE_MANIFESTS = (
    ModuleManifest(
        "journal", "Journal", "1.2.0", ">=1.2,<2.0", "Daily operating capture.",
        status="enabled", capabilities=("commands", "queries", "events"),
    ),
    ModuleManifest(
        "decision", "Decision", "1.2.0", ">=1.2,<2.0", "Versioned decision lifecycle.",
        status="enabled", capabilities=("commands", "queries", "events", "review"),
    ),
    ModuleManifest(
        "reports", "Reports", "1.2.0", ">=1.2,<2.0", "Deterministic attributable reports.",
        status="enabled", capabilities=("commands", "queries", "artifacts"),
    ),
    ModuleManifest(
        "knowledge", "Knowledge", "1.2.0", ">=1.2,<2.0", "Notes, archive, and casebook.",
        status="enabled", capabilities=("commands", "queries", "events"),
    ),
    ModuleManifest(
        "finance", "Finance Subsystem", "1.0.0", ">=1.2,<2.0",
        "Independent ledger, budget, cash-flow, savings, and reporting subsystem.",
        status="enabled",
        capabilities=("ledger", "budget", "cash-flow", "savings", "reports", "migration"),
        privacy_class="sensitive",
    ),
    ModuleManifest(
        "documents", "Documents", "1.2.0", ">=1.2,<2.0", "Document integrity and references.",
        status="enabled", capabilities=("commands", "queries", "content-integrity"),
    ),
    ModuleManifest(
        "dashboard", "Dashboard", "1.2.0", ">=1.2,<2.0", "Current operating projection.",
        status="enabled", capabilities=("projection",),
    ),
    ModuleManifest(
        "analytics", "Analytics", "1.2.0", ">=1.2,<2.0", "Read-only pattern summaries.",
        status="enabled", capabilities=("projection",),
    ),
    ModuleManifest(
        "review", "Review", "1.2.0", ">=1.2,<2.0", "Human review queues.",
        status="enabled", capabilities=("projection", "commands"),
    ),
    ModuleManifest(
        "ai_briefing", "AI Briefing", "1.2.0", ">=1.2,<2.0", "Source-attributed draft analysis.",
        status="enabled", capabilities=("projection", "draft-only"),
        permissions=("explicit-ai-request",),
    ),
    ModuleManifest(
        "module_manager", "Module Manager", "1.2.0", ">=1.2,<2.0", "Module lifecycle and health.",
        status="enabled", capabilities=("lifecycle", "diagnostics"),
    ),
    ModuleManifest(
        "settings", "Settings/Admin", "1.2.0", ">=1.2,<2.0", "Owner and Hub administration.",
        status="enabled", capabilities=("configuration", "backup", "migration"),
    ),
)

V13_STABLE_MANIFESTS = V12_STABLE_MANIFESTS + (
    ModuleManifest(
        "health", "Health Subsystem", "1.0.0", ">=1.3,<2.0",
        "Independent weight, body composition, checkup, sleep, exercise, nutrition, trend, goal, and reporting subsystem.",
        status="enabled",
        capabilities=("weight", "body-composition", "health-checkup", "sleep", "exercise",
                      "nutrition", "trend", "goal", "health-report", "migration"),
        privacy_class="sensitive",
    ),
)

V14_STABLE_MANIFESTS = V13_STABLE_MANIFESTS + (
    ModuleManifest(
        "housing", "Housing Subsystem", "1.0.0", ">=1.4,<2.0",
        "Independent candidate, scoring, comparison, reporting, and migration subsystem.",
        status="enabled",
        capabilities=("candidate-crud", "scoring", "comparison", "housing-report", "migration"),
        privacy_class="sensitive",
    ),
)

V15_STABLE_MANIFESTS = V14_STABLE_MANIFESTS + (
    ModuleManifest(
        "vehicle", "Vehicle Subsystem", "1.0.0", ">=1.5,<2.0",
        "Independent vehicle profiles, odometer, maintenance, energy-cost, and reporting subsystem.",
        status="enabled",
        capabilities=("vehicle-profile", "odometer", "maintenance",
                      "maintenance-schedule", "energy-cost", "vehicle-report"),
        privacy_class="sensitive",
    ),
)

V16_STABLE_MANIFESTS = V15_STABLE_MANIFESTS + (
    ModuleManifest(
        "food", "Food Subsystem", "1.0.0", ">=1.6,<2.0",
        "Independent ingredients, recipes, cooking, meals, nutrition summaries, and reporting subsystem.",
        status="enabled",
        capabilities=("ingredient-catalog", "recipe", "cooking-record",
                      "meal-record", "nutrition-summary", "food-report"),
        privacy_class="sensitive",
    ),
)

# v1.7 adds two Settings/Admin-owned Subsystems rather than new user Modules.
# The Module catalog therefore remains compatible with the v1.6 Stable set.
V17_STABLE_MANIFESTS = V16_STABLE_MANIFESTS

# Compatibility alias for the approved pre-release name.
V17_RELEASE_CANDIDATE_MANIFESTS = V17_STABLE_MANIFESTS

# Kept for callers that adopted the unreleased implementation-candidate name.
V2_STABLE_MANIFESTS = V12_STABLE_MANIFESTS
