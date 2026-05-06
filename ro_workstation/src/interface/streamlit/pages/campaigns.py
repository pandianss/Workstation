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
        active = [(i, c) for i, c in enumerate(campaigns) if c["status"] == "Active"]
        if not active:
            st.info("No active campaigns currently running.")
        else:
            for i, c in active:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"### {c['name']}")
                    c1.caption(f"Period: {c['start_date']} to {c['end_date']}")
                    c1.write(f"**Target Metric:** {c['target_metric']} | **Target Value:** {c['target_value']}")
                    
                    if c2.button("Complete", key=f"comp_{i}", use_container_width=True):
                        service.update_campaign(i, {"status": "Completed"})
                        st.rerun()
                    
                    with st.expander("📝 Edit Details"):
                        with st.form(f"edit_form_{i}"):
                            new_name = st.text_input("Name", value=c['name'])
                            new_metric = st.selectbox("Metric", ["CASA", "GOLD", "TOTAL ADVANCES", "RETAIL", "MSME", "DIGITAL"], index=["CASA", "GOLD", "TOTAL ADVANCES", "RETAIL", "MSME", "DIGITAL"].index(c['target_metric'].upper() if c['target_metric'].upper() in ["CASA", "GOLD", "TOTAL ADVANCES", "RETAIL", "MSME", "DIGITAL"] else 0))
                            new_target = st.number_input("Target", value=float(c['target_value']))
                            if st.form_submit_button("Update Campaign"):
                                service.update_campaign(i, {"name": new_name, "target_metric": new_metric, "target_value": new_target})
                                st.success("Updated.")
                                st.rerun()

                    if c2.button("Delete", key=f"del_{i}", use_container_width=True, type="secondary"):
                        service.delete_campaign(i)
                        st.rerun()

    with tabs[1]:
        completed = [(i, c) for i, c in enumerate(campaigns) if c["status"] == "Completed"]
        if not completed:
            st.info("No archived campaigns.")
        else:
            df = pd.DataFrame([c for i, c in completed])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### 🛠️ Archive Management")
            selected_name = st.selectbox("Select Campaign to Manage", options=[c["name"] for i, c in completed])
            if selected_name:
                idx, camp = next((i, c) for i, c in completed if c["name"] == selected_name)
                col1, col2 = st.columns(2)
                if col1.button("🗑️ Delete Permanently", use_container_width=True, key="del_arch"):
                    service.delete_campaign(idx)
                    st.success("Deleted.")
                    st.rerun()
                if col2.button("♻️ Reactivate", use_container_width=True, key="reac_arch"):
                    service.update_campaign(idx, {"status": "Active"})
                    st.success("Reactivated.")
                    st.rerun()

    with tabs[2]:
        with st.form("launch_campaign"):
            name = st.text_input("Campaign Name")
            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")
            
            metric = st.selectbox("Target Metric", ["CASA", "GOLD", "TOTAL ADVANCES", "RETAIL", "MSME", "DIGITAL"])
            target = st.number_input("Target Value (Cr)", min_value=0.0)
            
            if st.form_submit_button("Launch Campaign"):
                service.add_campaign(name, str(start), str(end), metric, target)
                st.success("Campaign launched successfully!")
                st.rerun()
