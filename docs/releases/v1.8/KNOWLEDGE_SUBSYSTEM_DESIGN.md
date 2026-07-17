# Knowledge Subsystem Design

Knowledge is an independent data-owning Subsystem (`SUB-KNOWLEDGE`, v1.0.0). Its contract contains record ID, title, content, summary, category, tags, source, lifecycle status, importance, timestamps, archive timestamp, and metadata.

The model validates required values, statuses (`NEW`, `REVIEW`, `ORGANIZED`, `ACTIVE`, `ARCHIVED`), importance 1–5, tags, and metadata. The repository provides create, read, update, archive, filtered list, and text search. Its private schema is stored under `data/knowledge/knowledge.sqlite3` only after first write or approved management initialization.

The management projection reports totals, lifecycle/category counts, recent changes, archived records, adapter health, registry state, and execution success/failure counts. Shared execution records are best-effort and cannot roll back successful domain writes.
