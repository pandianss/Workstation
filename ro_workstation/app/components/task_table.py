import streamlit as st
import pandas as pd

def render_task_table(tasks, filters):
    if not tasks:
        st.info("No tasks available.")
        return

    df = pd.DataFrame(tasks)

    # --- Apply Filters ---
    if filters["status"] != "All":
        df = df[df["status"] == filters["status"]]

    if filters["priority"] != "All":
        df = df[df["priority"] == filters["priority"]]

    if filters["search"]:
        df = df[df.apply(
            lambda row: filters["search"].lower() in str(row).lower(),
            axis=1
        )]

    if df.empty:
        st.warning("No tasks match the selected filters.")
        return

    # --- Display ---
    st.dataframe(
        df[["title", "priority", "due_date", "status", "dept", "description"]],
        use_container_width=True,
        height=400,
        hide_index=True
    )
