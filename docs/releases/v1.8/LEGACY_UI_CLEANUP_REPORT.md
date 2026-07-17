# Legacy UI Cleanup Report

Active Streamlit notices that labeled the application as v1.2 compatibility mode were generalized to current compatibility language. The sidebar now displays `v1.8 Stable`; database migration, backup, restore, and current-schema messages use current release-neutral or v1.8 Stable wording.

Compatibility module aliases, historical docs, stored contract versions, and report-format strings were retained because they are executable backward-compatibility boundaries rather than obsolete UI notices. No necessary migration or data-protection warning was removed.
