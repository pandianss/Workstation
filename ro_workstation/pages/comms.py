import streamlit as st

from modules.llm.client import LLMClient
from modules.ui.mock_data import notice_board
from modules.ui.theme import render_callout
from modules.utils.page_helpers import render_generation_result, render_page_header


render_page_header(
    "Staff Communications Hub",
    "Handle urgent staff communication from one screen: what is live, what needs drafting, and what has already gone out.",
)

tabs = st.tabs(["Live Notices", "Draft Notice", "Archive"])

with tabs[0]:
    st.subheader("What Staff Will See")
    for label, message in notice_board():
        render_callout(label, message)

with tabs[1]:
    st.subheader("AI-Assisted Notice Drafting")
    topic = st.text_input("Notice Topic")
    audience = st.selectbox("Audience", ["All staff", "Department heads", "Branch managers", "Field officers"])
    points = st.text_area("Key points to convey")
    if st.button("Draft Notice"):
        with st.spinner("Drafting notice..."):
            llm = LLMClient()
            notice = llm.generate(
                f"Draft an internal notice on {topic}. Audience: {audience}. Points: {points}",
                "You are the RO Admin writing a clear, professional notice to internal staff.",
            )
            render_generation_result("Drafted Notice", notice, "staff_notice.txt")

with tabs[2]:
    st.subheader("Archive")
    st.dataframe(
        {
            "Issued On": ["2026-04-21", "2026-04-16", "2026-04-11"],
            "Topic": ["Q4 Compliance Update", "BC Activity Review", "CBS Maintenance Window"],
            "Audience": ["All staff", "Department heads", "All staff"],
        },
        use_container_width=True,
        hide_index=True,
    )
