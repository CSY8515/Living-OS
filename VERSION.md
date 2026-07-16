# Living OS Version

Workspace version: Living OS v1.3 Stable

Stable verification date: 2026-07-16

Production version: Living OS v1.3 Stable

Status: official v1.3 Stable GitHub Release and Streamlit production deployment are complete and verified.

Production URL: [https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/](https://living-os-h5uinmvmjpvv6m8phat28a.streamlit.app/)

Architecture: Living OS is the Module layer; its runtime implements Subsystem → Engine → Function below `subsystems/`.

All public behavior and data contracts on the v1.1 stable baseline are retained. Code, docs, compilation, unit, integration, architecture, and Streamlit smoke verification are complete.

## Installed official subsystem

Finance Subsystem v1.0.0 is enabled and compatible with Living OS `>=1.2,<2.0`. Implementation and regression verification are complete. Legacy data migration remains an explicit operator action and never runs automatically.

Health Subsystem v1.0.0 is enabled in the v1.3 manifest and compatible with Living OS `>=1.3,<2.0`. All required engines, isolated tests, full regression, and docs are complete. Real Health migration remains an explicit owner action and has not run.
