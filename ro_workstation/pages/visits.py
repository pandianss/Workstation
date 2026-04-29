import streamlit as st

from modules.llm.client import LLMClient
from modules.ui.mock_data import visits_df
from modules.utils.page_helpers import render_generation_result, render_page_header


render_page_header(
    "Branch Visit Manager",
    "Plan visits, capture on-site observations quickly, and convert notes into a formal follow-up report.",
)

visits = visits_df()
tabs = st.tabs(["Schedule", "Observation Capture", "Visit Report", "History"])

with tabs[0]:
    with st.form("schedule_visit"):
        left, right = st.columns(2)
        with left:
            branch = st.selectbox("Select Branch", ["Pune Main", "Andheri", "Thane", "Kothrud"])
            visit_date = st.date_input("Visit Date")
        with right:
            officer = st.text_input("Visiting Officer")
            purpose = st.text_input("Visit Purpose")
        if st.form_submit_button("Schedule Visit"):
            st.success(f"Visit scheduled for {branch} on {visit_date} for {officer or 'assigned officer'}.")

with tabs[1]:
    st.text_area("Key Observations", help="Capture bullets while on site")
    st.text_area("Positives")
    st.text_area("Concerns / Irregularities")
    st.button("Save Observation Draft")

with tabs[2]:
    raw_notes = st.text_area("Paste raw notes here")
    if st.button("Generate Formal Report"):
        with st.spinner("Drafting report..."):
            llm = LLMClient()
            report = llm.generate(
                f"Convert these raw notes into a formal branch visit report: {raw_notes}",
                "You are an RO Officer writing a formal visit report.",
            )
            render_generation_result("Formal Report", report, "visit_report.txt")

with tabs[3]:
    st.dataframe(visits, use_container_width=True, hide_index=True)
