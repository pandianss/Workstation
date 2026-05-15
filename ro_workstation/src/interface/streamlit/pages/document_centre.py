import streamlit as st
import datetime
import pandas as pd
from src.interface.streamlit.components.primitives import render_action_bar
from src.application.services.master_service import MasterService
from src.core.document.engine import DocumentEngine
from src.application.services.document.performance import PerformanceGenerator
from src.application.services.document.operational import OperationalGenerator
from src.application.services.document.milestones import MilestoneGenerator
from src.application.services.document.statutory import StatutoryGenerator

def render():
    
    render_action_bar("Document Command Centre", ["Unified Engine", "Centralized Archive", "Audit Ready"])
    
    # Initialize Services
    master_service = MasterService()
    engine = DocumentEngine()
    
    perf_gen = PerformanceGenerator(engine)
    ops_gen = OperationalGenerator(engine)
    milestone_gen = MilestoneGenerator(engine)
    stat_gen = StatutoryGenerator(engine)
    
    # Dashboard Layout
    st.markdown("### 🏛️ Regional Documentation Hub")
    st.caption("Centralized command centre for all statutory, performance, and operational document generation.")
    
    tabs = st.tabs([
        "📈 Business & Performance", 
        "🛠️ Operations & Admin", 
        "⚖️ Statutory & Returns", 
        "🎉 Celebrations & Recognition"
    ])
    
    with tabs[0]:
        render_performance_section(perf_gen, master_service)
        
    with tabs[1]:
        render_operations_section(ops_gen, master_service)
        
    with tabs[2]:
        render_statutory_section(stat_gen, master_service)
        
    with tabs[3]:
        render_celebrations_section(milestone_gen, master_service)

def render_performance_section(gen, master_service):
    st.subheader("Business & Performance Documentation")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 📬 Performance Letters")
        st.write("Generate mass appreciation and explanation letters based on monthly MIS performance.")
        if st.button("Open Performance Letter Generator", key="btn_perf", use_container_width=True):
            st.session_state["requested_page"] = "Letter Generator"
            st.rerun()
            
    with col2:
        st.info("### 🎯 Budget Communication")
        st.write("Draft and distribute formal annual budget targets to all units in the region.")
        if st.button("Open Budget Communicator", key="btn_budget", use_container_width=True):
            # Redirecting to same page but could have specific logic here
            st.session_state["requested_page"] = "Letter Generator"
            st.rerun()

def render_operations_section(gen, master_service):
    st.subheader("Operations & Administrative Logic")
    
    cols = st.columns(3)
    
    with cols[0]:
        with st.container(border=True):
            st.markdown("#### 📝 Office Notes")
            st.caption("Standardized trilingual internal notes for departmental approvals.")
            if st.button("New Office Note", use_container_width=True, key="btn_new_note"):
                st.session_state["requested_page"] = "Office Note Generator"
                st.rerun()
            if st.button("View Note Archive", use_container_width=True, key="btn_note_archive"):
                st.session_state["requested_page"] = "Office Note Hub"
                st.rerun()
                
    with cols[1]:
        with st.container(border=True):
            st.markdown("#### 📜 Circulars")
            st.caption("Draft and publish regional circulars with auto-sequencing.")
            if st.button("Manage Circulars", use_container_width=True):
                st.session_state["requested_page"] = "Office Note Generator"
                st.rerun()
                
    with cols[2]:
        with st.container(border=True):
            st.markdown("#### 🚗 Visit Reports")
            st.caption("Generate formal observation letters and monthly visit returns.")
            if st.button("Visit Portal", use_container_width=True):
                st.session_state["requested_page"] = "Branch Visits"
                st.rerun()

def render_statutory_section(gen, master_service):
    st.subheader("Statutory Returns & Compliance")
    
    cols = st.columns(2)
    
    with cols[0]:
        with st.container(border=True):
            st.markdown("#### 🏦 DICGC Certification")
            st.caption("Generate Certificate of Confirmation and Form DI-01 for insurance compliance.")
            if st.button("DICGC Portal", use_container_width=True):
                st.session_state["requested_page"] = "DICGC Return"
                st.rerun()
                
    with cols[1]:
        with st.container(border=True):
            st.markdown("#### 🧙 Operational Wizards")
            st.caption("Multi-step tools for RBI Proforma, Waiver Requests, and Expense Approvals.")
            if st.button("Open Wizards", use_container_width=True):
                st.session_state["requested_page"] = "Operations"
                st.rerun()

def render_celebrations_section(gen, master_service):
    st.subheader("Celebrations & Recognition")
    
    cols = st.columns(2)
    
    with cols[0]:
        with st.container(border=True):
            st.markdown("#### 🎂 Staff Milestones")
            st.caption("Automated posters for Birthdays and Retirements.")
            if st.button("Anniversary Portal", use_container_width=True):
                st.session_state["requested_page"] = "Anniversary Portal"
                st.rerun()
                
    with cols[1]:
        with st.container(border=True):
            st.markdown("#### 🎖️ Ad-hoc Recognition")
            st.caption("Premium appreciation certificates and professional ad-hoc letters.")
            if st.button("Recognition Tools", use_container_width=True):
                st.session_state["requested_page"] = "Letter Generator"
                st.rerun()

if __name__ == "__main__":
    render()
