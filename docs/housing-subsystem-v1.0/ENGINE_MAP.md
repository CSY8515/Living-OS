# Housing Subsystem v1.0 Engine Map

| Engine | Responsibility |
|---|---|
| Candidate | Validated create, get, list, update, and delete |
| Scoring | Legacy-compatible deductions, score, grade, and total monthly cost |
| Comparison | Stable rank by score, monthly cost, commute, and name |
| Housing Report | Candidate, cost, grade, status, ranking, and next-action summaries |
| Migration | Read-only dry run and explicit transactional legacy JSON adoption |
| Storage | Lazy SQLite schema, transactions, integrity health, export snapshot |
| Validation | Text, integer, boolean, and status boundary validation |

No engine is a supported external import.
