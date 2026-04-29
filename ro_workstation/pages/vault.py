import streamlit as st

from modules.ui.mock_data import vault_docs
from modules.utils.page_helpers import DEPARTMENT_OPTIONS, render_page_header


user = render_page_header(
    "Document Vault",
    "Search submitted returns, notes, and reference material without leaving the workstation.",
)

docs = vault_docs()
tabs = st.tabs(["Search", "Version History"])

with tabs[0]:
    filter_1, filter_2, filter_3 = st.columns(3)
    default_dept_index = DEPARTMENT_OPTIONS.index(user["department"]) if user["department"] in DEPARTMENT_OPTIONS else 0
    dept_filter = filter_1.selectbox("Department", DEPARTMENT_OPTIONS, index=default_dept_index)
    doc_type = filter_2.selectbox("Document Type", ["ALL", "Returns", "Office Notes", "Circulars", "Letters"])
    search_query = filter_3.text_input("Keywords")

    filtered = docs.copy()
    if dept_filter != "ALL":
        filtered = filtered[filtered["Department"].isin([dept_filter, "ALL"])]
    if doc_type != "ALL":
        filtered = filtered[filtered["Type"] == doc_type]
    if search_query.strip():
        filtered = filtered[filtered["Title"].str.contains(search_query, case=False)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("Version History")
    doc_id = st.selectbox("Document ID", docs["Doc ID"].tolist())
    if doc_id == "DOC-891":
        st.write("Version 1: Initial draft (2026-04-10)")
        st.write("Version 2: Revised after RM comments (2026-04-11)")
        st.write("Version 3: Final submitted copy (2026-04-12) [Immutable]")
    else:
        st.info("Detailed version history is available for selected formal documents only.")
