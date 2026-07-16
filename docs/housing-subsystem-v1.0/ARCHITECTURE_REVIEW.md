# Housing Subsystem v1.0 Architecture Review

Baseline: Living OS v1.3 Stable at commit `65ae166`; clean compile and 67/67 tests passed before implementation.

Decision: promote the preserved Housing candidate workflow into a new peer subsystem, not into Compatibility, Finance, or Health. The production pattern is one public facade, private engines, injected lazy storage, transactional writes, explicit migration, manifest registration, isolated tests, and Experience access through the facade only.

    Experience -> Housing public facade
    Housing facade -> private Housing engines
    Housing engine -> Housing engine / Python standard library

No Core schema or v1.3 data contract changes. Existing Housing compatibility code and JSON remain unchanged.
