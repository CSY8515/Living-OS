# Module catalog configuration

The executable v1.5 manifest catalog is declared by `subsystems/operations/engines/catalog.py` and remains available through `modules.catalog`. This directory is reserved for validated serialized manifests if package discovery is introduced later.

Finance Subsystem v1.0 is registered as module finance with sensitive privacy classification and capabilities for ledger, budget, cash flow, savings, reports, and migration.

Health, Housing, and Vehicle Subsystem v1.0 are registered as isolated sensitive modules in their version-specific manifests. Vehicle capabilities are profiles, odometer history, maintenance, maintenance schedules, energy costs, and deterministic reports. Older manifest constants remain unchanged for compatibility.
