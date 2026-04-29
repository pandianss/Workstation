import streamlit as st
import plotly.express as px

def render_asset_quality(df, branch_df=None):
    if branch_df is None:
        branch_df = df
        
    st.markdown("### Asset Quality")
    
    if df.empty or 'NPA' not in df.columns:
        st.info("No NPA data available.")
        return
        
    total_npa = df['NPA'].sum().round(2)
    st.metric("Total NPA", f"₹ {total_npa:,.2f}")
    
    if 'SOL' in branch_df.columns:
        npa_by_branch = branch_df.groupby('SOL')['NPA'].sum().round(2).reset_index()
        npa_by_branch = npa_by_branch.sort_values(by='NPA', ascending=False).head(10)
        
        fig = px.bar(npa_by_branch, x='SOL', y='NPA', title="Top 10 Branches by NPA", 
                     text='NPA', color='NPA', color_continuous_scale='Reds')
        
        # Format the x-axis to be discrete string if SOL is numeric
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### High NPA Branches Alert (NPA % > 5%)")
        branch_pct = branch_df.groupby('SOL').agg({'NPA': 'sum', 'Total Advances': 'sum'}).round(2).reset_index()
        branch_pct['NPA %'] = (branch_pct['NPA'] / branch_pct['Total Advances'] * 100).round(2)
        high_npa = branch_pct[branch_pct['NPA %'] > 5.0].sort_values(by='NPA %', ascending=False)
        
        if not high_npa.empty:
            st.dataframe(high_npa[['SOL', 'NPA %', 'NPA']], use_container_width=True, hide_index=True)
        else:
            st.success("No branches exceed the 5% NPA threshold.")
