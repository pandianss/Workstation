from __future__ import annotations
import streamlit as st
import pandas as pd
from src.application.services.campaign_service import CampaignService
from src.interface.streamlit.components.primitives import render_action_bar

def render() -> None:
    service = CampaignService()
    render_action_bar("Campaign Management", ["Regional Drives", "Performance Tracking", "Publicity"])
    
    tabs = st.tabs(["📢 Active Campaigns", "📁 History & Analytics", "➕ Launch New"])

    campaigns = service.get_all()

    with tabs[0]:
        active = [c for c in campaigns if c["status"] == "Active"]
        if not active:
            st.info("No active campaigns currently running.")
        else:
            for i, c in enumerate(active):
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"### {c['name']}")
                    c1.caption(f"Period: {c['start_date']} to {c['end_date']}")
                    c1.write(f"**Target Metric:** {c['target_metric']} | **Target Value:** {c['target_value']}")
                    
                    if c2.button("Complete", key=f"comp_{i}"):
                        idx = campaigns.index(c)
                        service.update_campaign(idx, {"status": "Completed"})
                        st.rerun()
                    if c2.button("Delete", key=f"del_{i}"):
                        idx = campaigns.index(c)
                        service.delete_campaign(idx)
                        st.rerun()

    with tabs[1]:
        completed = [c for c in campaigns if c["status"] == "Completed"]
        if not completed:
            st.info("No archived campaigns.")
        else:
            df = pd.DataFrame(completed)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[2]:
        with st.form("launch_campaign"):
            name = st.text_input("Campaign Name")
            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")
            
            metric = st.selectbox("Target Metric", ["CASA", "Gold", "Total Advances", "Retail", "MSME", "Digital"])
            target = st.number_input("Target Value (Cr)", min_value=0.0)
            
            if st.form_submit_button("Launch Campaign"):
                service.add_campaign(name, str(start), str(end), metric, target)
                st.success("Campaign launched successfully!")
                st.rerun()
