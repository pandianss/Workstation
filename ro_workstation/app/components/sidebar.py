import streamlit as st
from app.services.task_service import get_task_summary


def render_sidebar():
    try:
        st.sidebar.image("app/assets/logo.svg", width=120)
    except Exception:
        pass

    st.sidebar.markdown("### RO Workstation")
    st.sidebar.caption("A focused workspace for daily control, execution, and insight.")

    summary = get_task_summary()

    st.sidebar.markdown("#### Live Status")
    st.sidebar.metric("Open Tasks", summary["open"])
    st.sidebar.metric("Overdue", summary["overdue"])

    st.sidebar.markdown("---")
    st.sidebar.caption("Move quickly between execution, monitoring, and management views.")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Operations", "Intelligence", "Performance MIS", "Admin"],
        label_visibility="collapsed",
    )

    return page
