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

    if "due_date" in df.columns:
        df = df.sort_values(by=["due_date", "priority"], ascending=[True, True], na_position="last")

    st.markdown(
        f"""
        <div class="glass-panel" style="margin-bottom: 0.9rem;">
            <div class="table-toolbar">
                <div>
                    <div class="section-title"><strong>Task queue</strong></div>
                    <div class="table-count">{len(df)} task(s) match the current filters.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        df[["title", "priority", "due_date", "status", "dept", "description"]],
        use_container_width=True,
        height=400,
        hide_index=True,
        column_config={
            "title": st.column_config.TextColumn("Task", width="medium"),
            "priority": st.column_config.TextColumn("Priority", width="small"),
            "due_date": st.column_config.DateColumn("Due", format="DD MMM YYYY"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "dept": st.column_config.TextColumn("Department", width="small"),
            "description": st.column_config.TextColumn("Description", width="large"),
        },
    )
