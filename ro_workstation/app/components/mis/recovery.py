import streamlit as st
import plotly.express as px

def render_recovery(df, branch_df=None):
    if branch_df is None:
        branch_df = df
    st.markdown("### Recovery Tracker")
    
    if df.empty:
        st.info("No recovery data available.")
        return
        
    q1 = df['Rec Q1'].sum().round(2) if 'Rec Q1' in df.columns else 0
    q2 = df['Rec Q2'].sum().round(2) if 'Rec Q2' in df.columns else 0
    q3 = df['Rec Q3'].sum().round(2) if 'Rec Q3' in df.columns else 0
    q4 = df['Rec Q4'].sum().round(2) if 'Rec Q4' in df.columns else 0
    
    total = q1 + q2 + q3 + q4
    st.metric("Total Recovery", f"₹ {total:,.2f}")
    
    data = {
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Recovery": [q1, q2, q3, q4]
    }
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(data, x="Quarter", y="Recovery", title="Recovery by Quarter", color="Quarter")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        if 'SOL' in branch_df.columns:
            branch_rec = branch_df.groupby('SOL')['Total Recovery'].sum().round(2).reset_index()
            branch_rec = branch_rec.sort_values(by='Total Recovery', ascending=False).head(10)
            
            fig2 = px.bar(branch_rec, x="Total Recovery", y="SOL", orientation='h', 
                          title="Top 10 Branches by Recovery")
            fig2.update_yaxes(type='category')
            st.plotly_chart(fig2, use_container_width=True)
