# Living OS Version

Workspace version: Living OS v1.7 Stable

Stable verification date: 2026-07-17

Production version: Living OS v1.7 Stable

Status: official v1.7 Stable commit, GitHub Release, Release Notes, Streamlit production deployment, Stable Verification, and Archive are complete. v1.8 work has not started.

Production URL: [https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/](https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/)

Architecture: Living OS is the Module layer; its runtime implements Subsystem → Engine → Function below `subsystems/`.

Database Foundation: Database and Database Management are independent peer Subsystems under Settings/Admin. The app exposes the v1.7 Stable management surface; real user database migration is explicit and never runs on startup.

All public behavior and data contracts on the v1.1 stable baseline are retained. Code, docs, compilation, unit, integration, architecture, and Streamlit smoke verification are complete.

## Installed official subsystem

Finance Subsystem v1.0.0 is enabled and compatible with Living OS `>=1.2,<2.0`. Implementation and regression verification are complete. Legacy data migration remains an explicit operator action and never runs automatically.

Health Subsystem v1.0.0 is enabled in the v1.3 manifest and compatible with Living OS `>=1.3,<2.0`. All required engines, isolated tests, full regression, and docs are complete. Real Health migration remains an explicit owner action and has not run.

Housing Subsystem v1.0.0 is enabled only in the new v1.4 manifest and compatible with Living OS `>=1.4,<2.0`. It preserves legacy Housing scoring and data, uses isolated lazy storage, and requires explicit dry-run-first migration. No real Housing migration has run.

Vehicle Subsystem v1.0.0 is enabled only in the new v1.5 manifest and compatible with Living OS `>=1.5,<2.0`. It provides isolated profiles, odometer, maintenance, schedule, energy-cost, and report capabilities. No legacy Vehicle source or migration exists.

Food Subsystem v1.0.0 is enabled only in the v1.6 manifest and compatible with Living OS `>=1.6,<2.0`. It provides isolated ingredients, recipes, cooking, meals, explicit nutrition summaries, and Food reports. No legacy Food source or migration exists. Food does not access Health or Finance.
