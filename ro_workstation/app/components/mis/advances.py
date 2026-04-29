import streamlit as st
import plotly.express as px

def render_advances(df):
    st.markdown("### Advances Portfolio")
    
    if df.empty:
        st.info("No data available.")
        return
        
    agri = df['CORE AGRI'].sum().round(2) if 'CORE AGRI' in df.columns else 0
    gold = df['GOLD'].sum().round(2) if 'GOLD' in df.columns else 0
    msme = df['MSME'].sum().round(2) if 'MSME' in df.columns else 0
    retail = df['CORE RETAIL'].sum().round(2) if 'CORE RETAIL' in df.columns else 0
    
    data = {
        "Category": ["Core Agri", "Gold", "MSME", "Core Retail"],
        "Amount": [agri, gold, msme, retail]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(data, names="Category", values="Amount", title="Advances Composition", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("#### Portfolio Drill-Down")
        drill_down = st.selectbox("Select Portfolio", ["Core Agri", "Gold", "MSME", "Core Retail"])
        
        if drill_down == "Core Agri":
            cols = ['KCC', 'SHG', 'Govt Spon', 'Oth Schematic']
        elif drill_down == "Gold":
            cols = ['RETAIL JL', 'AGRI JL']
        elif drill_down == "MSME":
            cols = ['MUDRA']
        else:
            cols = ['HOUSING', 'VEHICLE', 'PERSONAL', 'MORTGAGE', 'EDUCATION', 'LIQUIRENT', 'OTHER RETAIL']
            
        drill_data = []
        for c in cols:
            val = df[c].sum().round(2) if c in df.columns else 0
            drill_data.append({"Sub-Component": c, "Amount": val})
            
        fig2 = px.bar(drill_data, x="Sub-Component", y="Amount", title=f"{drill_down} Breakdown")
        st.plotly_chart(fig2, use_container_width=True)
