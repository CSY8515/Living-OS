# Legacy UI Cleanup Report

Active Streamlit notices that labeled the application as v1.2 compatibility mode were generalized to current compatibility language. The sidebar now displays `v1.8 Development`, and the database-current message uses the v1.8 development baseline.

Compatibility module aliases, historical docs, stored contract versions, and report-format strings were retained because they are executable backward-compatibility boundaries rather than obsolete UI notices. No necessary migration or data-protection warning was removed.
