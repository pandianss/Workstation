from __future__ import annotations

from typing import Any
import io

import pandas as pd
import plotly.express as px
import streamlit as st


def render_status_badge(text: str) -> None:
    st.markdown(f'<span class="status-badge">{text}</span>', unsafe_allow_html=True)


def render_metric_cards(metrics: dict[str, str | int | float]) -> None:
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics.items()):
        column.metric(label, value)


def render_filter_panel(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="glass-panel">
            <div class="section-title"><strong>{title}</strong></div>
            <div class="section-kicker">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_bar(title: str, actions: list[str]) -> None:
    items = "".join([f"<span class='app-badge'>{action}</span>" for action in actions])
    st.markdown(
        f"""
        <div class="page-toolbar">
            <div>
                <div class="section-title"><strong>{title}</strong></div>
            </div>
            <div class="app-badges">{items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_table(frame: pd.DataFrame, title: str, export_name: str) -> None:
    st.markdown(
        f"""
        <div class="glass-panel" style="margin-bottom: 0.75rem;">
            <div class="section-title"><strong>{title}</strong></div>
            <div class="table-count">{len(frame)} row(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(frame, use_container_width=True, hide_index=True, height=420)
    buffer = io.BytesIO()
    frame.to_excel(buffer, index=False)
    st.download_button("Export to Excel", data=buffer.getvalue(), file_name=export_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def render_chart_container(frame: pd.DataFrame, x: str, y: str, title: str, kind: str = "line", color: str | None = None):
    if frame.empty:
        st.info("No data available.")
        return
    if kind == "bar":
        figure = px.bar(frame, x=x, y=y, color=color, title=title)
    elif kind == "pie":
        figure = px.pie(frame, names=x, values=y, title=title, hole=0.45)
    else:
        figure = px.line(frame, x=x, y=y, color=color, title=title, markers=True)
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(figure, use_container_width=True)


def render_premium_metrics(metrics: dict[str, Any]) -> None:
    """Renders glassmorphic metric cards for a premium feel."""
    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics.items()):
        with cols[i]:
            display_val = f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
            st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{display_val}</div>
                </div>
            """, unsafe_allow_html=True)
