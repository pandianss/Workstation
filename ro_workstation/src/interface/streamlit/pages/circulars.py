from __future__ import annotations

import streamlit as st
import pandas as pd
from src.application.services.circular_service import CircularService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    service = CircularService()
    render_action_bar("RO Circulars", ["Internal Policy", "Searchable Archive", "Admin Upload"])
    
    tabs = st.tabs(["Browse Circulars", "Upload New"])
    
    with tabs[0]:
        category = st.selectbox("Category", ["All", "Operations", "Retail", "HR", "IT", "Recovery"])
        filter_cat = None if category == "All" else category
        circulars = service.list_circulars(category=filter_cat)
        
        if circulars:
            render_data_table(pd.DataFrame(circulars), f"{category} Circulars", "circular_list.xlsx")
        else:
            st.info("No circulars found in this category.")
            
    with tabs[1]:
        with st.form("upload_circular"):
            title = st.text_input("Circular Title")
            number = st.text_input("Circular Number (e.g., RO/OPR/2026/01)")
            cat = st.selectbox("Category", ["Operations", "Retail", "HR", "IT", "Recovery"], key="up_cat")
            date = st.date_input("Date of Issue")
            file = st.file_uploader("Upload PDF")
            submit = st.form_submit_button("Archive Circular")
            
            if submit and file:
                service.add_circular(title, number, cat, date.strftime("%Y-%m-%d"), file.name)
                st.success("Circular archived successfully!")
