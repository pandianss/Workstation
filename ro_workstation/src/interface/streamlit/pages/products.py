from __future__ import annotations

import streamlit as st
import pandas as pd
from src.application.services.product_service import ProductService
from src.interface.streamlit.components.primitives import render_action_bar, render_premium_metrics


def render() -> None:
    service = ProductService()
    render_action_bar("Bank Products", ["Loan Schemes", "Deposit Products", "ROI Tracker"])
    
    products = service.list_products()
    
    st.markdown("### Active Lending Schemes")
    cols = st.columns(3)
    for i, product in enumerate(products):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="glass-card">
                    <div style="font-weight: 800; font-size: 1.1rem; color: #3b82f6;">{product['name']}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 12px;">{product['category']}</div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>ROI: <strong>{product['interest']}</strong></span>
                        <span>Max: <strong>{product['tenure']}</strong></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Add New Product Scheme"):
        with st.form("add_product"):
            name = st.text_input("Scheme Name")
            cat = st.selectbox("Category", ["Retail", "MSME", "Agri", "Deposits"])
            roi = st.text_input("Interest Rate (%)")
            tenure = st.text_input("Max Tenure")
            if st.form_submit_button("Publish Product"):
                service.add_product({"name": name, "category": cat, "interest": roi, "tenure": tenure})
                st.success("Product published to regional workstation.")
                st.rerun()
