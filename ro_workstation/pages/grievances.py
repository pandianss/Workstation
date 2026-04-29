import streamlit as st

from modules.llm.client import LLMClient
from modules.ui.mock_data import complaints_df
from modules.utils.page_helpers import render_generation_result, render_page_header


render_page_header(
    "Grievance Tracker",
    "Watch complaint risk, see who owns each open item, and prepare consistent customer communication.",
)

complaints = complaints_df()
metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Open Complaints", len(complaints))
metric_2.metric("Critical Cases", len(complaints[complaints["Status"] == "Critical"]))
metric_3.metric("Average TAT Days", f"{complaints['TAT Days'].mean():.0f}")

tabs = st.tabs(["Open Complaints", "Resolution Letter"])

with tabs[0]:
    st.dataframe(complaints, use_container_width=True, hide_index=True)

with tabs[1]:
    complaint_id = st.selectbox("Complaint Reference", complaints["ID"].tolist())
    complaint_details = st.text_area("Complaint Summary")
    resolution_details = st.text_area("Resolution / Action Taken")
    if st.button("Draft Letter"):
        with st.spinner("Drafting professional response..."):
            llm = LLMClient()
            letter = llm.generate(
                f"Draft a resolution letter for complaint {complaint_id}. Complaint: {complaint_details}. Resolution: {resolution_details}",
                "You are a Customer Service Officer. Write a polite and formal bank response letter.",
            )
            render_generation_result("Resolution Letter", letter, "resolution_letter.txt")
