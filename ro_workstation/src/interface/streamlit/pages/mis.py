from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.application.use_cases.mis.service import MISAnalyticsService
from src.core.utils.financial_year import get_fy_start
from src.domain.schemas.mis import MISFilter
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_premium_metrics, render_chart_container


    # 1. Base Data Load
    df = service.get_data()
    if df.empty:
        st.error("No MIS data found. Please upload .xlsx files to the `data/mis/` folder.")
        return

    render_action_bar("Regional MIS Analytics", ["Market Share", "Budget Tracking", "NPA Surveillance"])
    
    # 2. Global Filters
    dates = sorted(df["DATE"].dt.date.unique())
    sols = sorted(df["SOL"].dropna().astype(int).unique().tolist())
    
    col_d, col_b = st.columns(2)
    with col_d:
        selected_date = st.selectbox("Reporting Date", dates, index=len(dates) - 1)
    with col_b:
        selected_sols = st.multiselect("Branch Focus", sols, default=[])

    # 3. Dynamic Snapshot Generation
    snapshot = service.build_snapshot(MISFilter(selected_date=selected_date, sols=selected_sols))
    if not snapshot:
        st.warning("No data found for this selection.")
        return

    # Glassmorphic KPI Row
    render_premium_metrics(snapshot.kpis)
    
    st.markdown("<br>", unsafe_allow_html=True)

    frame = pd.DataFrame(snapshot.rows)
    # Filter for numeric columns that aren't IDs or Dates
    excluded_cols = {"SOL", "DATE", "SNO", "ID", "YEAR", "MONTH", "CD RATIO", "NPA %"}
    metric_options = [c for c in frame.columns if frame[c].dtype in ['float64', 'int64'] and c.upper() not in excluded_cols]
    
    # Advanced Performance Tracking
    with st.expander("📈 Advanced Budget Gap Analysis", expanded=True):
        metric_to_track = st.selectbox("Select Parameter to Analyze", sorted(metric_options), index=sorted(metric_options).index("Total Advances") if "Total Advances" in metric_options else 0)
        perf = service.get_performance_metrics(selected_date, metric_to_track, sols=selected_sols)
        
        def format_cr(val):
            """Formats Lacs to Crores if large enough."""
            if abs(val) >= 100: # If more than 100 Lacs, show in Crores? 
                # Actually Bank ROs usually use Lacs for specific parameters, but Cr for Total.
                # Let's stick to Lacs but with comma separators, or Cr if > 1000 Lacs (10 Cr).
                if abs(val) >= 1000:
                    return f"{val/100:.2f} Cr"
            return f"{val:,.1f} L"

        if perf:
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #10b981;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">FY GROWTH</div>
                        <div style="font-size: 1.8rem; font-weight: 700;">{format_cr(perf['fy_growth'])}</div>
                        <div style="color: #10b981; font-weight: 600;">↑ {perf['fy_growth_pct']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col2:
                gap = perf['gap_current_month']
                gap_color = "#ef4444" if gap > 0 else "#10b981"
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid {gap_color};">
                        <div style="font-size: 0.8rem; color: #94a3b8;">MONTHLY GAP</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: {gap_color};">{format_cr(gap)}</div>
                        <div style="font-size: 0.8rem;">Target: {format_cr(perf['targets']['month'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col3:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #3b82f6;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">ANNUAL GAP</div>
                        <div style="font-size: 1.8rem; font-weight: 700;">{format_cr(perf['gap_fy'])}</div>
                        <div style="font-size: 0.8rem;">Target: {format_cr(perf['targets']['fy'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Visualization Layer
    col_chart, col_table = st.columns([1.5, 1])
    
    history = pd.DataFrame(snapshot.history_rows)
    if not history.empty:
        history["DATE"] = pd.to_datetime(history["DATE"])
        fy_start = pd.to_datetime(get_fy_start(selected_date))
        # Filter for current FY by default
        history = history[history["DATE"] >= fy_start]

    with col_chart:
        if not history.empty:
            st.markdown("#### 📊 Dynamic Business Trend (Current FY)")
            # Multi-line chart: Advances vs Deposits
            trend = history.groupby("DATE", as_index=False)[["Total Advances", "Total Deposits"]].sum()
            fig = px.line(trend, x="DATE", y=["Total Advances", "Total Deposits"], 
                         template="plotly_dark", color_discrete_sequence=["#3b82f6", "#10b981"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title=None)
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### 🏢 Branch Hierarchy")
        frame = pd.DataFrame(snapshot.rows)
        if not frame.empty:
            st.dataframe(frame[["SOL", "Total Advances", "Total Deposits", "NPA %"]].sort_values("Total Advances", ascending=False), 
                         hide_index=True, use_container_width=True)
            
    # Full Data View
    with st.expander("📋 Detailed MIS Inventory"):
        render_data_table(frame, "Complete Snapshot", f"mis_snapshot_{snapshot.selected_date}.xlsx")
