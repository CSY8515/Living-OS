# Living OS Version

Current version: Living OS v1.2 Stable

Release date: 2026-07-15

Status: production release. The repository is ready for the v1.2 tag, GitHub Release, and Streamlit Community Cloud deployment.

Architecture: Living OS is the Module layer; its runtime implements Subsystem → Engine → Function below `subsystems/`.

All public behavior and data contracts on the v1.1 stable baseline are retained. Code, docs, compilation, unit, integration, architecture, and Streamlit smoke verification are complete.

## Installed official subsystem

Finance Subsystem v1.0.0 is enabled and compatible with Living OS `>=1.2,<2.0`. Implementation and regression verification are complete. Legacy data migration remains an explicit operator action and never runs automatically.