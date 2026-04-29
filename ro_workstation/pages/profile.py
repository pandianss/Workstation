import streamlit as st

from modules.tasks.engine import get_tasks_for_user
from modules.utils.page_helpers import render_page_header
from modules.ui.theme import render_callout


user = render_page_header(
    "Profile & Settings",
    "Review your role context, keep your default working preferences handy, and generate a clean handover summary when responsibilities shift.",
)

tasks = get_tasks_for_user(user["username"])
open_tasks = [task for task in tasks if task.status == "OPEN"]
preference_state = st.session_state.setdefault(
    "preferences",
    {"email_notifications": True, "export_format": "PDF"},
)

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Profile Role", user["role"])
metric_2.metric("Department", user["department"])
metric_3.metric("Open Tasks", len(open_tasks))

render_callout(
    "Handover readiness",
    "Use the handover tab after clearing obvious task noise so the outgoing summary stays useful for the next officer.",
)

tabs = st.tabs(["My Profile", "Preferences", "Charge Handover Report"])

with tabs[0]:
    st.subheader("My Profile")
    st.write(f"**Name**: {user['name']}")
    st.write(f"**Role**: {user['role']}")
    st.write(f"**Department**: {user['department']}")
    st.write(f"**Username**: {user['username']}")

with tabs[1]:
    st.subheader("System Preferences")
    email_notifications = st.checkbox(
        "Receive Email Notifications",
        value=preference_state["email_notifications"],
    )
    export_format = st.selectbox(
        "Default Export Format",
        ["PDF", "Excel", "Word"],
        index=["PDF", "Excel", "Word"].index(preference_state["export_format"]),
    )
    if st.button("Save Preferences"):
        preference_state["email_notifications"] = email_notifications
        preference_state["export_format"] = export_format
        st.success("Preferences saved for this session.")

with tabs[2]:
    st.subheader("Charge Handover Report")
    st.write("Generate a concise summary of pending tasks and current work context for the incoming officer.")
    if st.button("Generate Handover Report"):
        with st.spinner("Compiling handover report..."):
            report = "\n".join(
                [
                    f"Handover Report for {user['name']} ({user['department']})",
                    "",
                    f"Open tasks: {len(open_tasks)}",
                    "",
                    *[
                        f"- {task.title} | Priority: {task.priority} | Due: {task.due_date or 'No due date'}"
                        for task in open_tasks
                    ],
                ]
            )
            st.success("Handover report generated successfully.")
            st.text_area("Handover Summary", report, height=280)
            st.download_button(
                "Download Summary",
                report,
                "Handover_Report.txt",
                mime="text/plain",
            )
