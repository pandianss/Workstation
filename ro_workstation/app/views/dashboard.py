import streamlit as st
from app.services.task_service import get_task_summary
from app.components.metrics import render_metrics
from app.components.task_table import render_task_table
from app.components.filters import render_task_filters
from app.components.anniversary import render_anniversary_alerts

def render_dashboard():
    st.markdown("## Dashboard")
    
    # --- Anniversary Alerts ---
    render_anniversary_alerts()

    summary = get_task_summary()

    # --- KPI Layer ---
    render_metrics(summary)

    st.markdown("---")

    # --- Filter Layer ---
    filters = render_task_filters()

    st.markdown("---")

    # --- Data Layer ---
    render_task_table(summary["tasks"], filters)
