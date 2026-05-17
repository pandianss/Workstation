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
    master_service = get_master_service()
    
    data = mis_service.get_data()
    units_df = master_service.get_units_frame()
    depts_df = master_service.get_departments_frame()
    
    if not data.empty:
        latest_date = data["DATE"].max()
        latest_data = data[data["DATE"] == latest_date]
        
        # 2. Key Regional Metrics
        st.markdown("### 📊 Regional Business Snapshot")
        from src.core.utils.number_utils import format_indian_number
        render_premium_metrics({
            "Total Deposits": f"₹ {format_indian_number(latest_data['TOTAL DEPOSITS'].sum())} Cr",
            "Total Advances": f"₹ {format_indian_number(latest_data['ADV'].sum())} Cr",
            "CD Ratio": f"{latest_data['CD RATIO'].mean():.2f}%",
            "Low Cost (CASA)": f"₹ {format_indian_number(latest_data['CASA'].sum())} Cr",
        })

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Growth Trends
        st.markdown("### 📈 Performance Trajectory")
        from src.core.utils.financial_year import get_fy_start
        fy_start = pd.to_datetime(get_fy_start(datetime.date.today()))
        hist = data[data["DATE"] >= fy_start].groupby("DATE")[["TOTAL DEPOSITS", "ADV"]].sum().reset_index()
        render_chart_container(hist, "DATE", ["TOTAL DEPOSITS", "ADV"], "Regional Business Growth (Current FY)")

    # 4. District Coverage & Network
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📍 Regional Network")
        st.markdown("""
            Our region covers **Dindigul** and surrounding areas with a robust network of branches.
            We are committed to financial inclusion across all tiers.
        """)
        
        # Fetch active branch counts per district dynamically
        if not units_df.empty:
            active_units = units_df[units_df["Active"] == True].copy()
            active_units["District"] = active_units["District"].astype(str).str.title().str.strip()
            district_counts = active_units.groupby("District")["Code"].count().to_dict()
        else:
            district_counts = {}

        if district_counts:
            cols = st.columns(len(district_counts))
            for i, (dist, count) in enumerate(sorted(district_counts.items())):
                cols[i].markdown(f"**{dist}**\n\n{count} Branches")
        else:
            st.info("No active units registered in the directory.")

    with col2:
        st.markdown("### 🏛️ Organization")
        
        # Fetch leadership and department details dynamically
        rm_details = master_service.get_branch_manager("3933")
        rm_name = rm_details.get("name", "The Regional Manager")
        rm_desig = rm_details.get("designation", "Regional Manager")
        
        active_depts = depts_df[depts_df["Active"] == True] if not depts_df.empty else []
        dept_count = len(active_depts)
        
        st.markdown(f"""
            <div class="glass-panel" style="padding: 20px; border-left: 4px solid #10b981;">
                <div style="font-weight: 700; color: #1e3a8a;">{rm_name}</div>
                <div style="font-size: 0.9rem; opacity: 0.8; color: #1f2937; font-weight: 500;">{rm_desig}</div>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid rgba(0,0,0,0.1);">
                <div style="font-weight: 600;">Operational Hub</div>
                <div style="font-size: 0.8rem; opacity: 0.9; color: #374151;">{dept_count} Active Specialized Departments</div>
            </div>
        """, unsafe_allow_html=True)

    # 5. Public Interactive Branch Finder
    st.divider()
    st.markdown("### 🔍 Regional Branch Directory")
    st.caption("Instantly find location details, opening dates, and designated unit authorities.")
    
    search_query = st.text_input("Search by Branch Name, SOL Code, or District", placeholder="e.g. Dindigul, 3933, Palani", key="guest_search_query")
    
    if search_query:
        query = search_query.lower().strip()
        if not units_df.empty:
            match_df = units_df[
                units_df["Code"].astype(str).str.lower().str.contains(query) |
                units_df["Name"].str.lower().str.contains(query) |
                units_df["District"].astype(str).str.lower().str.contains(query)
            ]
        else:
            match_df = pd.DataFrame()
        
        if not match_df.empty:
            for _, row in match_df.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1.2, 2, 1.8])
                    with c1:
                        st.markdown(f"##### 🏦 SOL {row['Code']}")
                        status_label = "🟢 Active" if row["Active"] else "🔴 Closed"
                        st.caption(f"Status: {status_label}")
                    with c2:
                        st.markdown(f"**{row['Name']}**")
                        st.caption(f"📍 District: {row['District']} | Group: {row['Population Group']}")
                        if pd.notna(row["Open Date"]):
                            try:
                                open_date_str = row["Open Date"].strftime("%d-%b-%Y")
                            except:
                                open_date_str = str(row["Open Date"])
                            st.caption(f"🗓️ Open Date: {open_date_str}")
                    with c3:
                        st.markdown(f"👤 **Head:** {row['Head']}")
                        st.markdown(f"👥 **2nd Line:** {row['2nd Line']}")
        else:
            st.warning("No branches match your search query.")
    else:
        st.info("Use the search bar above to look up branch profiles within our regional network.")

    # 6. Recent Public Announcements & Notices
    st.divider()
    st.markdown("### 📢 Announcements & Notices")
    
    from src.application.services.circular_service import CircularService
    try:
        circ_service = CircularService()
        all_circulars = circ_service.list_circulars()
    except Exception:
        all_circulars = []
        
    if all_circulars:
        # Sort circulars by date (newest first)
        try:
            sorted_circs = sorted(all_circulars, key=lambda x: pd.to_datetime(x.get("date"), errors="coerce"), reverse=True)[:3]
        except Exception:
            sorted_circs = all_circulars[:3]
            
        circ_cols = st.columns(3)
        for i, circ in enumerate(sorted_circs):
            with circ_cols[i]:
                with st.container(border=True):
                    st.markdown(f"📄 **{circ.get('number', 'RO Notice')}**")
                    st.caption(f"Issued: {circ.get('date', 'N/A')} | Category: {circ.get('category', 'General')}")
                    st.markdown(f"**{circ.get('title', '')}**")
    else:
        st.info("No recent regional announcements have been published.")

    # 7. Recent Achievements (Premium Layout)
    st.divider()
    st.markdown("### 🏆 Regional Achievements")
    achievements = [
        {"title": "CASA Excellence Award", "desc": "Ranked #1 in Zone for CASA growth in Q3."},
        {"title": "Digital Onboarding", "desc": "100% Mobile Banking registration in 15 rural branches."},
        {"title": "MSME Support", "desc": "₹ 50Cr sanctioned to local textile units in Vedasandur."},
    ]
    
    cols = st.columns(3)
    for i, ach in enumerate(achievements):
        cols[i].markdown(f"""
            <div class="glass-panel" style="padding: 15px; height: 100%; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; background: rgba(255,255,255,0.02);">
                <div style="font-size: 1.5rem; margin-bottom: 10px;">🌟</div>
                <div style="font-weight: 700; color: #1e3a8a; margin-bottom: 6px;">{ach['title']}</div>
                <div style="font-size: 0.85rem; opacity: 0.8; color: #374151; font-weight: 500;">{ach['desc']}</div>
            </div>
        """, unsafe_allow_html=True)
