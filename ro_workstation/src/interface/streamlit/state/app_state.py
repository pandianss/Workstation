from __future__ import annotations

import streamlit as st


def ensure_app_state() -> None:
    st.session_state.setdefault("active_page", "Dashboard")
    st.session_state.setdefault("notifications_open", True)
    st.session_state.setdefault("global_search_query", "")
