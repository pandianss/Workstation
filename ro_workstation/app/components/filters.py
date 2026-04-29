import streamlit as st


def render_task_filters():
    col1, col2, col3 = st.columns(3)

    with col1:
        status = st.selectbox(
            "Status",
            ["All", "OPEN", "CLOSED"],
            help="Limit results to open or closed items.",
        )

    with col2:
        priority = st.selectbox(
            "Priority",
            ["All", "P1", "P2", "P3", "P4"],
            help="Use priority to surface the most urgent work first.",
        )

    with col3:
        search = st.text_input("Search", placeholder="Search by title, department, owner, or notes")

    return {
        "status": status,
        "priority": priority,
        "search": search.strip()
    }
