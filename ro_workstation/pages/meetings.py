import streamlit as st

from modules.llm.client import LLMClient
from modules.utils.page_helpers import DEPARTMENT_OPTIONS, render_generation_result, render_page_header


render_page_header(
    "Meeting Manager",
    "Set up meetings, prepare agenda ownership, and turn rough notes into structured minutes without bouncing between tools.",
)

tabs = st.tabs(["Schedule", "Agenda Builder", "Minutes Generator"])

with tabs[0]:
    left, right = st.columns(2)
    with left:
        st.selectbox("Meeting Type", ["Weekly HOD", "Quarterly Performance Review", "Monthly RO Review", "Ad hoc"])
        st.date_input("Meeting Date")
    with right:
        st.text_input("Chairperson")
        st.text_input("Venue / Link")
    st.button("Create Meeting")

with tabs[1]:
    agenda_owner, agenda_item = st.columns([1, 2])
    with agenda_owner:
        st.selectbox("Responsible Dept", DEPARTMENT_OPTIONS)
    with agenda_item:
        st.text_input("Agenda Item")
    st.text_area("Expected discussion points")
    st.button("Add Agenda Item")

with tabs[2]:
    bullets = st.text_area("Paste raw meeting notes")
    if st.button("Generate Minutes"):
        with st.spinner("Generating formal minutes..."):
            llm = LLMClient()
            mins = llm.generate(
                f"Draft formal meeting minutes from these notes: {bullets}. Format: Agenda -> Discussion -> Decision -> Action Points.",
                "You are the Regional Manager's secretary.",
            )
            render_generation_result("Meeting Minutes", mins, "meeting_minutes.txt")
