from __future__ import annotations

import streamlit as st
import pandas as pd
from src.interface.streamlit.components.primitives import render_action_bar


def render() -> None:
    render_action_bar("Branch-RO Coordination", ["Internal Messaging", "Clarifications", "Regional Broadcasts"])
    
    st.markdown("### 📢 Regional Broadcast Feed")
    st.markdown("""
        <div class="glass-panel" style="border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
            <div style="font-weight: 700; color: #3b82f6;">URGENT: Quarterly Closing Instructions</div>
            <div style="font-size: 0.8rem; opacity: 0.8;">Posted 2 hours ago by Operations Dept</div>
            <p style="margin-top: 8px;">All branches to ensure recovery entries are pushed before 4 PM today.</p>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["Branch Queries", "RO Instructions", "Post Broadcast"])
    
    with tabs[0]:
        st.info("Incoming queries from branches will appear here for resolution.")
        # Placeholder for query tracking
        st.dataframe(pd.DataFrame({
            "Branch": ["Dindigul Main", "Palani", "Oddanchatram"],
            "Subject": ["Gold Loan Sanction", "ATM Hardware issue", "Staff Leave"],
            "Received": ["10:00 AM", "10:30 AM", "11:15 AM"],
            "Status": ["Pending", "Assigned", "Resolved"]
        }), use_container_width=True)

    with tabs[2]:
        with st.form("broadcast"):
            subj = st.text_input("Broadcast Subject")
            msg = st.text_area("Message Content")
            target = st.multiselect("Target Branches", ["All Branches", "Dindigul Cluster", "Palani Cluster"])
            if st.form_submit_button("Send Broadcast"):
                st.success("Broadcast sent to selected branches.")
