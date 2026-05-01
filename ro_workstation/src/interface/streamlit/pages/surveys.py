from __future__ import annotations

import streamlit as st
import pandas as pd
from src.application.services.survey_service import SurveyService
from src.interface.streamlit.components.primitives import render_action_bar


def render() -> None:
    service = SurveyService()
    render_action_bar("Regional Surveys", ["Branch Feedback", "Data Collection", "Policy Compliance"])
    
    surveys = service.list_surveys()
    
    st.markdown("### Active Regional Surveys")
    for survey in surveys:
        with st.container():
            st.markdown(f"""
                <div class="glass-panel" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 700; font-size: 1.1rem;">{survey['title']}</div>
                            <div style="font-size: 0.8rem; color: #94a3b8;">Deadline: {survey['deadline']}</div>
                        </div>
                        <span class="status-pill status-low">{survey['status']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Survey Form", key=f"sv_{survey['title']}"):
                st.info("Form would open here (e.g., Google Form or Internal Form).")
            st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Deploy New Branch Survey"):
        with st.form("new_survey"):
            title = st.text_input("Survey Title")
            deadline = st.date_input("Submission Deadline")
            form_url = st.text_input("Form URL (e.g., MS Forms/Google Forms)")
            if st.form_submit_button("Deploy to Network"):
                service.create_survey({
                    "title": title,
                    "deadline": deadline.strftime("%Y-%m-%d"),
                    "status": "Open",
                    "url": form_url
                })
                st.success("Survey notification sent to all branches.")
                st.rerun()
