import streamlit as st
import plotly.express as px

def render_cash(df, branch_df=None):
    if branch_df is None:
        branch_df = df
    st.markdown("### Cash Management")
    
    if df.empty or 'Total Cash' not in df.columns:
        st.info("No cash data available.")
        return
        
    total_cash = df['Total Cash'].sum().round(2)
    total_crl = df['CRL'].sum().round(2) if 'CRL' in df.columns else 0
    net_position = round(total_cash - total_crl, 2)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cash", f"₹ {total_cash:,.2f}")
    col2.metric("Total CRL", f"₹ {total_crl:,.2f}")
    col3.metric("Net Position", f"₹ {net_position:,.2f}", 
                delta=f"{net_position:,.2f}", delta_color="inverse")
    
    if 'SOL' in branch_df.columns:
        st.markdown("#### Branch-wise Cash vs CRL")
        cash_df = branch_df.groupby('SOL').agg({'Total Cash': 'sum', 'Cash vs CRL': 'sum'}).round(2).reset_index()
        cash_df = cash_df.sort_values(by='Cash vs CRL', ascending=False)
        
        fig = px.bar(cash_df, x='SOL', y='Cash vs CRL', 
                     title="Cash Excess / Shortfall by Branch",
                     color='Cash vs CRL', 
                     color_continuous_scale=px.colors.diverging.RdYlGn)
                     
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)
