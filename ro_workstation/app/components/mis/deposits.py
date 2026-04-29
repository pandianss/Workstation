import streamlit as st
import plotly.express as px

def render_deposits(df):
    st.markdown("### Deposit Profile")
    
    if df.empty:
        st.info("No data available.")
        return
        
    casa = df['CASA'].sum().round(2) if 'CASA' in df.columns else 0
    ret_td = df['Ret TD'].sum().round(2) if 'Ret TD' in df.columns else 0
    bulk = df['Bulk Dep'].sum().round(2) if 'Bulk Dep' in df.columns else 0
    
    total = round(casa + ret_td + bulk, 2)
    casa_pct = (casa / total * 100) if total > 0 else 0
    
    st.metric("CASA %", f"{casa_pct:.2f} %")
    
    data = {
        "Type": ["CASA", "Retail TD", "Bulk Deposits"],
        "Amount": [casa, ret_td, bulk]
    }
    
    fig = px.bar(data, x="Type", y="Amount", color="Type", title="Deposit Composition")
    st.plotly_chart(fig, use_container_width=True)
