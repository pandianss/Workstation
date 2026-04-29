import streamlit as st

def render_overview(df):
    st.markdown("### Executive Overview")
    
    if df.empty:
        st.info("No data available for the selected filters.")
        return
        
    # Aggregate data for KPIs
    total_advances = df['Total Advances'].sum().round(2)
    total_deposits = df['Total Deposits'].sum().round(2)
    
    cd_ratio = round((total_advances / total_deposits * 100), 2) if total_deposits > 0 else 0
    
    total_npa = df['NPA'].sum().round(2) if 'NPA' in df.columns else 0
    npa_pct = round((total_npa / total_advances * 100), 2) if total_advances > 0 else 0
    
    total_pl = df['PL'].sum().round(2) if 'PL' in df.columns else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Advances", f"₹ {total_advances:,.2f}")
    col2.metric("Total Deposits", f"₹ {total_deposits:,.2f}")
    col3.metric("CD Ratio", f"{cd_ratio:.2f} %")
    col4.metric("NPA %", f"{npa_pct:.2f} %")
    col5.metric("P&L", f"₹ {total_pl:,.2f}")
