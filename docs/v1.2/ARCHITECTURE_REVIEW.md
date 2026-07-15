# v1.2 Architecture Review

Baseline: clean v1.1 stabilization commit; 44/44 tests passed. Runtime was split across app/, core/, modules/, and shared/, while docs/tests carried unreleased v2.0 terminology.

Issues: functions outside Subsystems, canonical imports through public paths, proposed structure differing from files, and inconsistent product labels.

Decision: Foundation, Operations, Insight, Experience, and Compatibility. This minimizes coupling while retaining all behavior and data contracts.
