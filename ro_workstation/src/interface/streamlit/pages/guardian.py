from __future__ import annotations

import pandas as pd
import streamlit as st

from src.application.services.admin_service import AdminService
from src.application.services.guardian_service import GuardianService
from src.application.services.task_service import TaskService
from src.domain.schemas.task import TaskCreate
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    admin_service = AdminService()
    guardian_service = GuardianService()
    task_service = TaskService()
    render_action_bar("Guardian", ["Field follow-ups", "Regional requests", "Activity feed"])

    user = admin_service.get_user(st.session_state.get("username", ""))
    followups = guardian_service.list_followups(go_username=st.session_state.get("username", ""))
    if followups:
        render_data_table(pd.DataFrame(item.model_dump() for item in followups), "My follow-up activity", "guardian_activity.xlsx")

    assigned_sols = user.assigned_branches if user else []
    st.caption(f"Assigned branches: {', '.join(assigned_sols) if assigned_sols else 'None'}")
    with st.form("guardian_followup_form"):
        sol = st.text_input("Branch SOL")
        details = st.text_area("Observations")
        target_user = st.text_input("Assign follow-up to officer (optional)")
        priority = st.select_slider("Priority", options=["P4", "P3", "P2", "P1"], value="P3")
        submit = st.form_submit_button("Record Follow-up")
    if submit and sol and details:
        guardian_service.record_followup(st.session_state.get("username", ""), sol, details)
        if target_user.strip():
            task_service.create_task(
                TaskCreate(
                    title=f"Guardian Request for {sol}",
                    dept=st.session_state.get("user_dept", "ALL"),
                    assigned_to=target_user.strip(),
                    description=details,
                    priority=priority,
                )
            )
        st.success("Guardian activity saved.")
