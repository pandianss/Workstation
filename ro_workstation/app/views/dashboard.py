import streamlit as st
from app.services.task_service import get_task_summary
from app.components.metrics import render_metrics
from app.components.task_table import render_task_table
from app.components.filters import render_task_filters
from app.components.anniversary import render_anniversary_alerts


def render_dashboard():
    st.markdown("## Dashboard")
    st.markdown(
        """
        <div class="glass-panel">
            <div class="section-title"><strong>Daily visibility</strong></div>
            <div class="section-kicker">
                Track open work, spot pressure points early, and move from overview to action without scanning clutter.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_anniversary_alerts()

    summary = get_task_summary()

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    render_metrics(summary)

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="filter-shell">
            <div class="section-title"><strong>Task filters</strong></div>
            <div class="section-kicker">Refine the queue by status, urgency, or a free-text search.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filters = render_task_filters()

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)

    render_task_table(summary["tasks"], filters)
