from __future__ import annotations

import pandas as pd
import streamlit as st

from src.application.services.guardian_service import GuardianService
from src.application.services.operation_service import OperationService
from src.application.services.task_service import TaskService
from src.application.use_cases.global_search import GlobalSearchService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_filter_panel, render_premium_metrics


def render() -> None:
    username = st.session_state.get("username", "")
    task_service = TaskService()
    guardian_service = GuardianService()
    operation_service = OperationService()
    search_service = GlobalSearchService()

    summary = task_service.get_task_summary(username)
    
    # Premium Action Bar
    render_action_bar("Executive Dashboard", ["Real-time", "Bi-lingual", "Glassmorphic"])
    
    # Glassmorphic KPI Row
    render_premium_metrics({
        "Open Tasks": summary["open"],
        "Overdue": summary["overdue"],
        "Recent Syncs": len(operation_service.get_operation_history(limit=5)),
        "Guardian Alerts": len(guardian_service.list_followups()),
    })

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Integrated Search & Focus Area
    col_search, col_stats = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("Unified Search", placeholder="🔎 Search staff, branches, tasks, or MIS references...", key="global_search_input")
        if query:
            results = pd.DataFrame(search_service.search(query, username))
            if results.empty:
                st.info("No matching records found in the workstation index.")
            else:
                render_data_table(results, "Deep Search Results", "global_search_results.xlsx")
        
        task_frame = pd.DataFrame(summary["tasks"])
        if not task_frame.empty:
            st.markdown("#### ⚡ Active Workload Queue")
            render_data_table(task_frame, "Pending Actions", "task_queue.xlsx")

    with col_stats:
        st.markdown("#### 🛡️ Guardian Insights")
        followups = guardian_service.as_frame()
        if not followups.empty:
            for _, row in followups.head(5).iterrows():
                st.markdown(f"""
                    <div class="glass-panel" style="margin-bottom: 8px; padding: 12px; border-left: 4px solid #3b82f6;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">{row.get('DATE', '')}</div>
                        <div style="font-weight: 600; font-size: 0.9rem;">{row.get('BRANCH', 'Alert')}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{row.get('REMARKS', '')[:60]}...</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active follow-ups detected.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ Operational Flow")
        operations = operation_service.get_operation_history(limit=5)
        if not operations.empty:
            st.dataframe(operations, hide_index=True, use_container_width=True)
