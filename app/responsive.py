from __future__ import annotations


def apply_responsive_layout() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root { --living-content: 1180px; }
        .block-container { max-width: var(--living-content); padding-top: 1.5rem; }
        [data-testid="stMetric"] { min-height: 7rem; }
        .living-status { padding: .65rem .85rem; border-radius: .65rem; background: rgba(49, 130, 206, .10); }
        @media (max-width: 900px) {
          .block-container { padding: 1rem 1.1rem 4rem; }
          [data-testid="stHorizontalBlock"] { gap: .55rem; }
        }
        @media (max-width: 640px) {
          .block-container { padding: .75rem .75rem 5rem; }
          h1 { font-size: 1.75rem !important; }
          h2 { font-size: 1.35rem !important; }
          [data-testid="stMetric"] { min-height: auto; }
          .stButton button { min-height: 2.75rem; width: 100%; }
          [data-testid="stFileUploader"] { width: 100%; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
