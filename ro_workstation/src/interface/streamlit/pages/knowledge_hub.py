from __future__ import annotations

import streamlit as st
import pandas as pd
from src.application.services.hub_service import KnowledgeHubService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    service = KnowledgeHubService()
    render_action_bar("Knowledge Hub", ["Circulars", "Products", "Surveys"])
    
    tabs = st.tabs(["📄 RO Circulars", "🏦 Bank Products", "📝 Active Surveys"])
    
    with tabs[0]:
        category = st.selectbox("Category", ["All", "Operations", "Retail", "HR", "IT", "Recovery"])
        filter_cat = None if category == "All" else category
        circulars = service.list_circulars(category=filter_cat)
        if circulars:
            render_data_table(pd.DataFrame(circulars), f"{category} Archive", "circulars.xlsx")
        
    with tabs[1]:
        products = service.list_products()
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                st.markdown(f"""
                    <div class="glass-card">
                        <div style="font-weight: 800; font-size: 1.1rem; color: #3b82f6;">{product['name']}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">{product['category']} | {product['interest']}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

    with tabs[2]:
        surveys = service.list_surveys()
        for survey in surveys:
            st.markdown(f"""
                <div class="glass-panel" style="margin-bottom: 0.75rem;">
                    <strong>{survey['title']}</strong><br>
                    <small>Deadline: {survey['deadline']} | Status: {survey['status']}</small>
                </div>
            """, unsafe_allow_html=True)
