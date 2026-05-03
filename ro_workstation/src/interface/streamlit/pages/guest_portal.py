from __future__ import annotations
import streamlit as st
import pandas as pd
import datetime
from src.interface.streamlit.state.services import get_mis_service, get_master_service
from src.interface.streamlit.components.primitives import render_premium_metrics, render_chart_container

def render() -> None:
    # 1. Premium Public Header
    st.markdown("""
        <section class="app-hero" style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 60px 40px; color: white; border-radius: 24px; margin-bottom: 40px;">
            <div class="app-hero__eyebrow" style="color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 2px;">Dindigul Regional Office</div>
            <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 16px;">Regional Business Portal</h1>
            <p style="font-size: 1.2rem; opacity: 0.9; max-width: 600px;">
                Transparency and Excellence in Banking. Overview of our regional performance, district coverage, and organizational growth.
            </p>
        </section>
    """, unsafe_allow_html=True)

    mis_service = get_mis_service()
    data = mis_service.get_data()
    
    if not data.empty:
        latest_date = data["DATE"].max()
        latest_data = data[data["DATE"] == latest_date]
        
        # 2. Key Regional Metrics
        st.markdown("### 📊 Regional Business Snapshot")
        render_premium_metrics({
            "Total Deposits": f"₹ {latest_data['Total Deposits'].sum():,.2f} Cr",
            "Total Advances": f"₹ {latest_data['Total Advances'].sum():,.2f} Cr",
            "CD Ratio": f"{latest_data['CD Ratio'].mean():.2f}%",
            "Low Cost (CASA)": f"{latest_data['CASA'].sum():,.2f} Cr",
        })

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Growth Trends
        st.markdown("### 📈 Performance Trajectory")
        from src.core.utils.financial_year import get_fy_start
        fy_start = pd.to_datetime(get_fy_start(datetime.date.today()))
        hist = data[data["DATE"] >= fy_start].groupby("DATE")[["Total Deposits", "Total Advances"]].sum().reset_index()
        render_chart_container(hist, "DATE", ["Total Deposits", "Total Advances"], "Regional Business Growth (Current FY)")

    # 4. District Coverage & Network
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📍 Regional Network")
        st.markdown("""
            Our region covers **Dindigul** and surrounding areas with a robust network of branches.
            We are committed to financial inclusion across all tiers.
        """)
        
        districts = {
            "Dindigul": "42 Branches",
            "Palani": "12 Branches",
            "Oddanchatram": "8 Branches",
            "Kodaikanal": "5 Branches",
            "Vedasandur": "6 Branches"
        }
        
        cols = st.columns(len(districts))
        for i, (dist, count) in enumerate(districts.items()):
            cols[i].markdown(f"**{dist}**\n\n{count}")

    with col2:
        st.markdown("### 🏛️ Organization")
        st.markdown("""
            <div class="glass-panel" style="padding: 20px; border-left: 4px solid #10b981;">
                <div style="font-weight: 700; color: #1e3a8a;">Regional Manager</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Head of Dindigul Region</div>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(0,0,0,0.1);">
                <div style="font-weight: 600;">Operational Hub</div>
                <div style="font-size: 0.8rem;">14 Specialized Departments</div>
            </div>
        """, unsafe_allow_html=True)

    # 5. Recent Achievements (Static for Demo)
    st.markdown("### 🏆 Regional Achievements")
    achievements = [
        {"title": "CASA Excellence Award", "desc": "Ranked #1 in Zone for CASA growth in Q3."},
        {"title": "Digital Onboarding", "desc": "100% Mobile Banking registration in 15 rural branches."},
        {"title": "MSME Support", "desc": "₹ 50Cr sanctioned to local textile units in Vedasandur."},
    ]
    
    cols = st.columns(3)
    for i, ach in enumerate(achievements):
        cols[i].markdown(f"""
            <div class="glass-panel" style="padding: 15px; height: 100%;">
                <div style="font-size: 1.5rem; margin-bottom: 10px;">🌟</div>
                <div style="font-weight: 700;">{ach['title']}</div>
                <div style="font-size: 0.85rem; opacity: 0.7;">{ach['desc']}</div>
            </div>
        """, unsafe_allow_html=True, help="Award Details")
