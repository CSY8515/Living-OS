# Known Issues

## Living OS v1.0 Stable

### Local storage

- Living OS remains a local, single-user Streamlit application using JSON and JSONL files.
- Concurrent writers are not supported, and performance is not designed for very large datasets.
- Read paths fail safely for missing or malformed content, but Living OS does not automatically repair source files.
- A save against malformed Daily Log, Archive, Settings, or Module Registry JSON is rejected to protect the existing file.
- Decision JSONL readers skip malformed or non-object lines; source content is not rewritten automatically.

### Dates and reports

- Bounded date filters exclude records whose existing date fields are missing or malformed.
- Report ordering uses each accessible report file's local modification time.
- A report file that becomes inaccessible or disappears during discovery is ignored.

### Backup and restore

- Backups cover configured Living OS data targets, not a full filesystem snapshot or arbitrary attachments.
- Restore accepts recognized targets only and validates their JSON/JSONL content before writing.
- Rollback after an operating-system write failure is best effort; external filesystem failure can prevent restoration of an original file.

### Optional OpenAI integration

- AI requires a user-provided API key, network access, access to a configured model, and available quota; API use may incur charges.
- Only user-selected displayed content is sent after an explicit action.
- AI output may be inaccurate and remains untrusted.
- Daily Log and Decision analysis is session-only. AI report drafts remain session-only unless saved through a separate explicit save action.
- Operating-system credential storage availability depends on local platform configuration.
- Model availability may vary by OpenAI account and can change independently of Living OS.

### Intentionally excluded

- Database storage and multi-user access
- Authentication, accounts, roles, and permissions
- Notifications, reminders, scheduling, and background automation
- Autonomous AI writes or decisions
- Agents, embeddings, vector databases, and fine-tuning
- Automatic data repair and expansion-module implementation

## Historical compatibility notes

v1.0 preserves the v0.9 optional OpenAI workflow, the v0.8 reliability improvements, the v0.7 Review Workspace, and all earlier local JSON/JSONL data shapes. Finance and Housing source assets remain available for backward compatibility but are not current navigation pages.
