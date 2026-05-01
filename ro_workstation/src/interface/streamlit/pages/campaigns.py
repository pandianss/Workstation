from __future__ import annotations

import streamlit as st
import pandas as pd
from src.application.services.campaign_service import CampaignService
from src.application.use_cases.mis.service import MISAnalyticsService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table


def render() -> None:
    service = CampaignService()
    mis_service = MISAnalyticsService()
    render_action_bar("Business Campaigns", ["Performance Incentives", "Target Tracking", "Regional Drives"])
    
    campaigns = service.list_campaigns()
    
    for campaign in campaigns:
        with st.container():
            st.markdown(f"""
                <div class="glass-panel" style="margin-bottom: 1.5rem; border-left: 5px solid #10b981;">
                    <h3 style="margin-bottom: 4px;">{campaign['name']}</h3>
                    <div style="font-size: 0.85rem; color: #94a3b8;">{campaign['start_date']} to {campaign['end_date']} | Metric: {campaign['target_metric']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Simulated progress based on MIS data
            col1, col2 = st.columns([2, 1])
            with col1:
                # Mock actual progress for demo
                progress = 65 # percentage
                st.progress(progress / 100, text=f"Regional Progress: {progress}% of {campaign['target_value']}L Lacs")
            with col2:
                st.button("View Branch Rankings", key=f"rank_{campaign['name']}")
            st.markdown("<hr>", unsafe_allow_html=True)

    with st.expander("Launch New Campaign"):
        with st.form("new_campaign"):
            name = st.text_input("Campaign Name")
            metric = st.selectbox("MIS Target Metric", ["CASA", "Total Advances", "Gold", "MSME", "Recovery"])
            target = st.number_input("Regional Target (Lacs)", value=1000.0)
            dates = st.date_input("Campaign Period", [])
            if st.form_submit_button("Launch Regional Drive") and len(dates) == 2:
                service.create_campaign({
                    "name": name,
                    "target_metric": metric,
                    "target_value": target,
                    "start_date": dates[0].strftime("%Y-%m-%d"),
                    "end_date": dates[1].strftime("%Y-%m-%d"),
                    "status": "Active"
                })
                st.success("Campaign launched across all branches!")
                st.rerun()
