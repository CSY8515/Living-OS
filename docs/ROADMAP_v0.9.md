# Living OS v0.9 Roadmap

## Version

- Target version: Living OS v0.9
- Baseline: Living OS v0.8 Stable
- Release theme: First OpenAI API Integration
- Historical status: Implemented and released as the v1.0 baseline

## Objectives

- Add the first optional OpenAI API integration without changing the approved local, single-user, modular Streamlit architecture.
- Let the user configure an API key securely on the local machine and test the connection manually.
- Add read-only AI analysis for Daily Logs and Decisions.
- Generate AI report drafts that remain in memory until the user explicitly chooses to save them.
- Make every AI request user-initiated and every data-changing action separately user-approved.
- Preserve all v0.8 pages, behavior, storage interfaces, and JSON/JSONL schemas.

## Safety and Approval Contract

- AI is an assistant only. It does not make decisions for the user.
- No AI request runs automatically on page load, navigation, record creation, or report generation.
- The user must select the source and press an explicit analysis or draft-generation button before data is sent to OpenAI.
- AI output is displayed as an untrusted, read-only suggestion or draft.
- AI output never automatically modifies, deletes, appends, restores, archives, or saves Living OS data.
- Saving an AI-generated report draft requires a separate explicit user action using the existing report-save boundary.
- Recommendations have no automatic apply action. The user may manually copy or use them outside the AI panel.
- Requests are foreground-only. No queue, scheduler, retry worker, background process, notification, or automation is introduced.
- The UI must clearly state what selected Living OS content will be sent to OpenAI before the request is made.

## Approved-Scope Proposal

### OpenAI API Configuration

- Add an AI configuration section to the existing Settings page; do not add authentication or accounts.
- Support an explicitly entered API key and an optional `OPENAI_API_KEY` environment variable fallback.
- Allow selection from a small configured model list, with a conservative default documented at implementation time.
- Keep model selection and non-secret AI preferences outside existing user-data schemas. No existing settings key may be added or changed without separate approval.
- Show whether AI is configured without displaying the full API key.

### Secure Local API Key Management

- Never store the API key in `state/settings.json`, any project JSON/JSONL file, reports, logs, source code, browser-visible query parameters, or Git-tracked files.
- Use the operating system credential store through a narrowly scoped local credential adapter when the user explicitly chooses to save the key locally.
- Permit session-only use without persistence.
- Mask key input and any displayed credential fingerprint.
- Provide explicit Save credential and Remove credential controls with confirmation-quality labeling.
- Never include the key in exception messages, telemetry, generated reports, or test fixtures.
- Fail safely when the operating system credential store is unavailable; session-only entry and environment-variable configuration remain available.

### AI Connection Test

- Add a user-triggered Test Connection control in Settings.
- Perform the smallest practical OpenAI request and display a sanitized success or failure result.
- Do not write application data or persist AI output during the test.
- Handle missing credentials, invalid credentials, permission errors, rate limits, timeouts, unavailable networks, and malformed responses without crashing the app.

### AI Analysis Panel

- Add one new `AI Analysis` page to the existing navigation while preserving all nine v0.8 pages.
- Keep the panel read-only and foreground-only.
- Provide a clear configured/not-configured state and link the user conceptually to Settings.
- Show selected source records, request status, generated output, limitations, and an explicit statement that the result has not been saved.
- Keep generated output only in Streamlit session state unless the user separately approves an available save action.

### AI-Powered Daily Log Analysis

- Let the user select one existing Daily Log record.
- Show the exact selected record fields that will be sent before analysis.
- On explicit request, generate a concise summary, observed themes, possible patterns, questions for reflection, and read-only recommendations.
- Treat missing or malformed optional fields safely.
- Do not edit the source Daily Log or add fields to `data/daily_logs.json`.

### AI-Powered Decision Analysis

- Let the user select one existing Decision record.
- Show the exact selected record fields that will be sent before analysis.
- On explicit request, identify assumptions, tradeoffs, risks, missing information, and questions for review.
- Label recommendations as suggestions, not decisions or instructions.
- Do not change decision status, append a JSONL record, or modify `logs/decision_log.jsonl`.

### AI Report Draft Generation

- Add an optional AI draft mode to the existing Reports page without removing deterministic v0.8 report generation.
- The user selects the existing report range and explicitly requests an AI draft based on the same read-only Daily Log and Decision inputs.
- Display the AI result as an editable/copyable draft marked `Not saved`.
- Do not save the draft automatically.
- Saving requires a distinct explicit Save AI Draft action and uses the existing Markdown report and report-index interfaces without changing their schemas.
- A failed AI request must not affect deterministic report preview or saving.

### Read-Only AI Recommendations

- Recommendations appear only inside the generated analysis or draft.
- No Apply, auto-update, auto-archive, auto-create, status-change, or rule-creation behavior is included.
- The UI reminds the user to verify AI output before manual use.

## Proposed Module Responsibilities

### AI Service Module

Planned file: `modules/ai_service.py`

- Isolate OpenAI client creation and request execution from Streamlit rendering.
- Resolve credentials without exposing them to other modules.
- Sanitize errors and normalize responses.
- Accept explicit prompt/input values and return text only.
- Contain no Living OS data-write calls.

### AI Credential Module

Planned file: `modules/ai_credentials.py`

- Isolate session, environment-variable, and operating-system credential-store access.
- Store no credential in repository files.
- Provide masked configuration status, explicit save, and explicit removal operations.

### AI Analysis Module

Planned file: `modules/ai_analysis.py`

- Render the AI Analysis page.
- Load existing Daily Logs and Decisions through their current read interfaces.
- Build minimal, source-specific request payloads only after user selection.
- Hold AI results in session state and render them read-only.
- Contain no Living OS data-write calls.

## Architecture Impact

- The existing `app.py` Streamlit shell remains the entry point.
- The existing module-per-feature structure remains in place.
- JSON and JSONL remain the persistence formats for Living OS user data.
- Existing storage functions and record schemas remain unchanged.
- One optional, synchronous external integration is added behind `modules/ai_service.py`.
- The operating system credential store is used only for the API secret and is not a new Living OS data store.
- AI output flows only to the UI/session state, except when a user separately approves saving a report through the existing report system.
- No database, server, authentication layer, service daemon, background worker, or repository restructuring is introduced.

## Files Expected to Change

### New application files

- `modules/ai_service.py`
- `modules/ai_credentials.py`
- `modules/ai_analysis.py`

### Existing application files

- `app.py` — register the AI Analysis page and update the visible version.
- `modules/settings.py` — add AI credential/configuration UI without changing `state/settings.json`.
- `modules/report_system.py` — add optional in-memory AI draft generation and explicit save control; preserve deterministic reports.
- `modules/storage.py` — update the default version label only; no storage shape or user-record changes.
- `modules/dashboard.py` — update the displayed version only.
- `requirements.txt` — add narrowly pinned OpenAI client and operating-system credential-store dependencies.
- `state/settings.json` — version value only; no key or schema change.

### Verification files

- `tests/test_v09.py` — isolated tests with mocked OpenAI and credential-store boundaries.
- Existing v0.8 tests remain and must continue to pass unchanged unless a version-label assertion requires the approved v0.9 update.

### Documentation files

- `README.md`
- `ROADMAP.md`
- `KNOWN_ISSUES.md`
- `CHANGELOG.md`
- `docs/ROADMAP_v0.9.md`

### Files and schemas not expected to change

- `data/daily_logs.json` and its schema.
- `logs/decision_log.jsonl` and its schema.
- `data/archive.json` and its schema.
- `reports/report_index.json` and its schema.
- `config/module_registry.json` and its schema.
- Finance and Housing compatibility assets.

## Compatibility Risks and Mitigations

- **Missing or incompatible optional dependencies:** keep imports localized and show a safe unavailable state rather than breaking non-AI pages.
- **Credential leakage:** prohibit project-file storage, mask UI values, sanitize errors, and test that secrets never appear in output.
- **Network, API, quota, or model failure:** catch and classify errors; retain all existing local functionality and data unchanged.
- **API/client changes:** isolate the SDK behind one service module and pin compatible dependency ranges.
- **Accidental data transmission:** send only the selected record and display the selected source content before the explicit request.
- **Accidental persistence:** keep results in session state and test that analysis calls do not invoke JSON, JSONL, report, archive, or settings writers.
- **Duplicate report saves:** disable implicit saving and require a separate user click for each saved draft.
- **Large or malformed records:** validate types, cap request size conservatively, and show clear truncation or validation messages.
- **Prompt injection inside user records:** treat record text as quoted source material, constrain the system instruction, and label all output untrusted.
- **Regression to v0.8 behavior:** retain deterministic report generation and all current pages, then run existing regression and manual smoke tests.
- **Platform credential-store differences:** cover unavailable-store behavior and retain session-only/environment-variable fallback without storing plaintext.

## Test Plan

### Automated tests

- Run the complete existing v0.8 regression suite.
- Test credential resolution precedence without using real credentials.
- Test save/remove credential adapter behavior with a mocked operating-system credential store.
- Assert API keys are never written to repository files or included in sanitized messages.
- Test connection success and sanitized failures for missing key, invalid key, timeout, rate limit, permission, network, and malformed response cases.
- Test Daily Log and Decision request builders with valid, empty, missing, malformed, oversized, and Unicode content.
- Assert analysis is not called until the explicit action function is invoked.
- Assert AI analysis performs no calls to Living OS write functions.
- Test report draft generation remains in memory before approval.
- Assert report files and `report_index.json` change only after the explicit save action.
- Test deterministic v0.8 report generation still works when AI is unconfigured or failing.
- Test all visible/generated version labels expected for v0.9.

### Manual verification

- Start the app with no API key and smoke-test all ten pages.
- Confirm every v0.8 page and feature remains available and functional.
- Test session-only, environment-variable, and explicit operating-system credential-store configuration paths.
- Confirm the full key is never displayed after entry.
- Test connection success and common failure states.
- Inspect the pre-request disclosure for Daily Log, Decision, and Report flows.
- Confirm no request occurs on load, navigation, selection, or ordinary report preview.
- Generate each AI output and verify it is marked unsaved/read-only as applicable.
- Confirm closing or refreshing the session does not silently save AI output.
- Save one AI report draft explicitly and verify the existing Markdown/index formats remain compatible.
- Compare hashes or diffs of JSON/JSONL user-data files before and after all read-only AI operations.
- Run with the network unavailable and confirm all local functionality remains usable.

## Acceptance Criteria

- All nine v0.8 pages and features remain available, with AI Analysis added as the tenth page.
- Existing JSON and JSONL schemas are byte-for-byte structurally compatible and require no migration.
- No API key is stored in the repository or any Living OS JSON/JSONL file.
- The user can use a session-only key, an environment-provided key, or explicitly save a key to the local operating-system credential store.
- The connection test runs only when the user requests it and never writes Living OS data.
- Daily Log and Decision analysis run only for an explicitly selected record and explicit button press.
- Recommendations remain read-only and cannot automatically change records.
- AI report drafts are not saved until a separate explicit save action.
- AI/network failures do not break existing pages, deterministic reports, or local data access.
- No authentication, notification, automation, background task, or autonomous AI behavior is introduced.
- Automated tests and manual smoke checks pass.
- Documentation and version labels accurately describe the approved v0.9 implementation.

## Out of Scope

- Automatic analysis, summarization, classification, recommendation, or report generation.
- Automatic modification, deletion, saving, archiving, status changes, or Living Rule creation.
- Multi-record bulk analysis beyond the explicitly selected report range.
- Conversation memory, chat history, embeddings, vector databases, retrieval systems, agents, tools/function calling, or fine-tuning.
- Streaming responses unless separately approved during implementation planning.
- Sending Archive, Finance, Housing, settings, backups, or unrelated files to OpenAI.
- Storing AI analysis history in JSON, JSONL, Markdown, or a database.
- Authentication, accounts, roles, permissions, or cloud secret storage.
- Notifications, reminders, schedules, polling, retries in the background, or automation.
- Database migration or changes to existing JSON/JSONL schemas.
- Changes to the approved application architecture or repository structure.
- Expansion-module implementation.
- Cloud deployment, telemetry, analytics collection, commit, push, tag, release, or publishing actions.

## Approval Gate

Historical note: implementation proceeded only after explicit approval. v1.0 Stable preserves this safety and compatibility contract.
