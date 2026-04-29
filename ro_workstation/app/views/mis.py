import streamlit as st
import pandas as pd
from app.services.mis_service import load_mis_data
from app.components.mis.overview import render_overview
from app.components.mis.advances import render_advances
from app.components.mis.deposits import render_deposits
from app.components.mis.asset_quality import render_asset_quality
from app.components.mis.cash import render_cash
from app.components.mis.recovery import render_recovery
from app.components.mis.profit import render_profit
from app.components.mis.trends import render_trends
from app.services.report_service import generate_mis_report

def render_mis_dashboard():
    master_df = load_mis_data()
    
    if master_df.empty:
        st.error("No MIS data found in the `mis/` directory. Please load daily .xlsx files.")
        return
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Performance Filters")
    
    # Date Filter
    dates = sorted(master_df['DATE'].dropna().dt.date.unique())
    if not dates:
        st.error("No valid dates found in data.")
        return
        
    selected_date = st.sidebar.selectbox("Select Date", dates, index=len(dates)-1)
    
    # SOL Filter
    sols = sorted(master_df['SOL'].dropna().unique().tolist())
    selected_sols = st.sidebar.multiselect("Select Branch (SOL)", sols, default=[])
    
    # MIS Views Menu
    st.sidebar.markdown("### MIS Views")
    view = st.sidebar.radio("Go to", [
        "Overview", "Advances", "Deposits", 
        "Asset Quality", "Cash", "Recovery", 
        "Profit", "Trends"
    ])
    
    # Filter Data
    base_filtered_df = master_df[master_df['DATE'].dt.date == selected_date].copy()
    base_historical_df = master_df.copy()
    
    if selected_sols:
        global_df = base_filtered_df[base_filtered_df['SOL'].isin(selected_sols)]
        branch_df = global_df
        global_hist_df = base_historical_df[base_historical_df['SOL'].isin(selected_sols)]
    else:
        global_df = base_filtered_df[base_filtered_df['SOL'] == 3933]
        branch_df = base_filtered_df[base_filtered_df['SOL'] != 3933]
        global_hist_df = base_historical_df[base_historical_df['SOL'] == 3933]

    st.sidebar.markdown("---")
    report_pdf = generate_mis_report(
        global_df if not global_df.empty else branch_df, 
        str(selected_date), 
        ", ".join([str(s) for s in selected_sols]) if selected_sols else "All Branches (Regional Aggregate)"
    )
    
    st.sidebar.download_button(
        label="📥 Download PDF Report",
        data=report_pdf,
        file_name=f"MIS_Report_{selected_date}.pdf",
        mime="application/pdf"
    )

    st.markdown(f"## {view}")
    
    # Routing
    if view == "Overview":
        render_overview(global_df)
    elif view == "Advances":
        render_advances(global_df)
    elif view == "Deposits":
        render_deposits(global_df)
    elif view == "Asset Quality":
        render_asset_quality(global_df, branch_df)
    elif view == "Cash":
        render_cash(global_df, branch_df)
    elif view == "Recovery":
        render_recovery(global_df, branch_df)
    elif view == "Profit":
        render_profit(global_df, branch_df)
    elif view == "Trends":
        render_trends(global_hist_df)
