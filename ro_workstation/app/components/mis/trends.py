import streamlit as st
import plotly.express as px

def render_trends(master_df):
    st.markdown("### Historical Trends")
    
    if master_df.empty or 'DATE' not in master_df.columns:
        st.info("Insufficient historical data for trend analysis.")
        return
        
    metrics = ["Total Advances", "Total Deposits", "CD Ratio", "NPA %", "Total Cash", "PL"]
    selected_metric = st.selectbox("Select Metric", metrics)
    
    # We aggregate by date across all branches (or the currently filtered branch if filtered prior to calling)
    trend_df = master_df.groupby('DATE')[selected_metric].sum().round(2).reset_index()
    
    # If CD Ratio or NPA %, we need to recalculate correctly, summing percentages is wrong.
    if selected_metric in ["CD Ratio", "NPA %"]:
        if selected_metric == "CD Ratio":
            agg_df = master_df.groupby('DATE').agg({'Total Advances': 'sum', 'Total Deposits': 'sum'}).reset_index()
            import numpy as np
            trend_df['CD Ratio'] = np.where(agg_df['Total Deposits'] > 0, (agg_df['Total Advances'] / agg_df['Total Deposits'] * 100), 0)
        else:
            agg_df = master_df.groupby('DATE').agg({'NPA': 'sum', 'Total Advances': 'sum'}).reset_index()
            import numpy as np
            trend_df['NPA %'] = np.where(agg_df['Total Advances'] > 0, (agg_df['NPA'] / agg_df['Total Advances'] * 100), 0)
            
    fig = px.line(trend_df, x="DATE", y=selected_metric, markers=True, title=f"{selected_metric} Trend Over Time")
    st.plotly_chart(fig, use_container_width=True)
