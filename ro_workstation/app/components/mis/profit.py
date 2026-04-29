import streamlit as st
import plotly.express as px

def render_profit(df, branch_df=None):
    if branch_df is None:
        branch_df = df
    st.markdown("### Profit & Loss")
    
    if df.empty or 'PL' not in df.columns:
        st.info("No P&L data available.")
        return
        
    total_pl = df['PL'].sum().round(2)
    st.metric("Total P&L", f"₹ {total_pl:,.2f}")
    
    if 'SOL' in branch_df.columns:
        branch_pl = branch_df.groupby('SOL')['PL'].sum().round(2).reset_index()
        branch_pl = branch_pl.sort_values(by='PL', ascending=False)
        
        fig = px.bar(branch_pl, x='SOL', y='PL', 
                     title="Profit & Loss by Branch",
                     color='PL',
                     color_continuous_scale=px.colors.diverging.RdYlGn)
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top 5 Profitable Branches")
            st.dataframe(branch_pl.head(5), hide_index=True, use_container_width=True)
            
        with col2:
            st.markdown("#### Bottom 5 Branches")
            st.dataframe(branch_pl.tail(5).sort_values(by='PL'), hide_index=True, use_container_width=True)
