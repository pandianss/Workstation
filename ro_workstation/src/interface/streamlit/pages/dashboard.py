from __future__ import annotations

import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

from src.application.services.guardian_service import GuardianService
from src.application.services.task_service import TaskService
from src.application.services.circular_service import CircularService
from src.application.services.document import DocumentService
from src.application.services.returns_service import ReturnsService
from src.application.use_cases.mis.service import MISAnalyticsService
from src.interface.streamlit.components.primitives import (
    render_action_bar, render_data_table, render_premium_metrics, 
    render_section_divider, render_info_banner
)
from src.interface.streamlit.state.services import (
    get_task_service, get_guardian_service, get_returns_service, 
    get_search_service, get_circular_service, get_doc_service_v3
)

def render() -> None:
    username = st.session_state.get("username", "")
    task_service = get_task_service()
    guardian_service = get_guardian_service()
    returns_service = get_returns_service()
    mis_service = MISAnalyticsService()
    
    # 1. DATA AGGREGATION
    tasks_summary = task_service.get_task_summary(username)
    mis_df = mis_service.get_data()
    snapshot = mis_service.build_snapshot(None) if not mis_df.empty else None
    
    # Header Section
    st.markdown('<h1 class="text-gold" style="margin-bottom:0;">Regional Command Center</h1>', unsafe_allow_html=True)
    render_action_bar("Strategic Oversight & Operations", ["V3.0 Stable", "Live Analytics", "Guardian Active"])

    # 2. EXECUTIVE PULSE (KPIs)
    if snapshot:
        kpis = snapshot.kpis
        from src.core.utils.number_utils import format_crore
        render_premium_metrics({
            "Advances": format_crore(kpis['Total Advances']),
            "Deposits": format_crore(kpis['Total Deposits']),
            "CD Ratio": f"{kpis['CD Ratio']:.1f}%",
            "NPA": f"{kpis['NPA']:.2f}%",
            "Open Tasks": tasks_summary["open"],
            "Alerts": len(guardian_service.list_followups())
        })
    else:
        render_premium_metrics({
            "Open Tasks": tasks_summary["open"],
            "Overdue": tasks_summary["overdue"],
            "Pending Returns": len([r for r in returns_service.get_all() if r["status"] == "Pending"]),
            "Guardian Alerts": len(guardian_service.list_followups()),
        })

    render_section_divider()

    # 3. MAIN DASHBOARD LAYOUT
    col_main, col_side = st.columns([2.2, 1])

    with col_main:
        # A. Performance Trend (Compact Sparkline)
        if snapshot and not pd.DataFrame(snapshot.history_rows).empty:
            with st.container(border=True):
                st.markdown("#### 📈 Regional Growth Velocity")
                hist = pd.DataFrame(snapshot.history_rows)
                hist["DATE"] = pd.to_datetime(hist["DATE"])
                trend = hist.groupby("DATE", as_index=False)[["TOTAL ADVANCES", "TOTAL DEPOSITS"]].sum()
                fig = px.line(trend, x="DATE", y=["TOTAL ADVANCES", "TOTAL DEPOSITS"], 
                            template="plotly_dark", height=180, color_discrete_sequence=["#3b82f6", "#10b981"])
                fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # B. Active Action Queue (Priority Tasks)
        st.markdown('<div class="text-gold" style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">⚡ Priority Action Queue</div>', unsafe_allow_html=True)
        task_frame = pd.DataFrame(tasks_summary["tasks"])
        if not task_frame.empty:
            # Show only top priority tasks in dashboard for density
            display_tasks = task_frame.sort_values("priority").head(8)
            render_data_table(display_tasks[["title", "priority", "status", "due_date"]], "Critical Tasks", "dash_tasks.xlsx")
        else:
            st.info("Your action queue is empty. Operational peace achieved.")

        # C. Global Search (Floating style)
        with st.expander("🔍 Deep Registry Search", expanded=False):
            query = st.text_input("Search workstation...", placeholder="Staff, Units, or Circulars...", key="dash_global_search")
            if query:
                search_service = get_search_service()
                results = pd.DataFrame(search_service.search(query, username))
                if not results.empty:
                    render_data_table(results, "Search Matches", "search.xlsx")

        # D. Recent Circulars (Compact Row)
        st.markdown('<div class="text-gold" style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 0.5rem;">📢 Latest Regional Directives</div>', unsafe_allow_html=True)
        circ_service = get_circular_service()
        all_circs = circ_service.get_all()
        if all_circs:
            for i, c in enumerate(all_circs[:3]):
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1.5])
                    with c1:
                        st.markdown(f"**{c.get('subject', 'Circular')}**")
                        st.caption(f"{c.get('ref_no')} | {c.get('date')}")
                    with c2:
                        if st.button("📄 View", key=f"dash_circ_{i}", use_container_width=True):
                            with st.spinner(""):
                                pdf = get_doc_service_v3().generate_circular_pdf(c)
                                st.download_button("📥 Save", data=pdf, file_name=f"Circular_{i}.pdf", key=f"dl_circ_{i}", use_container_width=True)

    with col_side:
        # 1. Operational Guard (Guardian & Returns)
        st.markdown("#### 🛡️ Operational Guard")
        t_guard1, t_guard2 = st.tabs(["Alerts", "Returns"])
        
        with t_guard1:
            alerts = guardian_service.as_frame()
            if not alerts.empty:
                for _, row in alerts.head(4).iterrows():
                    st.markdown(f"""
                        <div class="glass-panel" style="margin-bottom: 6px; padding: 10px; border-left: 3px solid #ef4444; background: #1e293b55;">
                            <div style="font-weight: 600; font-size: 0.85rem;">{row.get('BRANCH', 'Alert')}</div>
                            <div style="font-size: 0.75rem; opacity: 0.8;">{row.get('REMARKS', '')[:45]}...</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No critical alerts.")

        with t_guard2:
            pending = [r for r in returns_service.get_all() if r["status"] == "Pending"][:4]
            if pending:
                for r in pending:
                    st.markdown(f"""
                        <div class="glass-panel" style="margin-bottom: 6px; padding: 10px; border-left: 3px solid #10b981; background: #1e293b55;">
                            <div style="font-weight: 600; font-size: 0.85rem;">{r.get('title', 'Return')}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">Due: {r.get('due_date', '')}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("All returns filed.")

        # 2. Regional Celebrations (Combined Anniversary & Birthday)
        st.markdown("<br>#### 🎊 Milestone Radar", unsafe_allow_html=True)
        from src.application.services.anniversary_service import AnniversaryService
        anniv_svc = AnniversaryService()
        
        br_events = anniv_svc.get_upcoming_anniversaries(days=10)
        st_events = anniv_svc.get_staff_celebrations(days=10)
        
        if not br_events and not st_events:
            st.info("No events in the 10-day radar.")
        else:
            # Combine and sort by days_to_go
            all_events = []
            for b in br_events: all_events.append({"type": "BRANCH", "name": b["name"], "days": b["days_to_go"], "val": f"{b['years']}Y", "date": b["anniversary_date"]})
            for s in st_events: all_events.append({"type": s["type"], "name": s["name"], "days": s["days_to_go"], "val": s["type"][:1], "date": s["event_date"]})
            
            all_events.sort(key=lambda x: x["days"])
            
            for event in all_events[:6]:
                icon = "🏦" if event["type"] == "BRANCH" else ("🎂" if event["type"] == "BIRTHDAY" else "🎖️")
                color = "#3b82f6" if event["type"] == "BRANCH" else "#f59e0b"
                days_txt = "TODAY" if event["days"] == 0 else f"In {event['days']}d"
                
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px; padding: 8px; border-radius: 8px; border: 1px solid #ffffff11; background: #ffffff05;">
                        <div style="font-size: 1.2rem;">{icon}</div>
                        <div style="flex-grow: 1;">
                            <div style="font-size: 0.85rem; font-weight: 600;">{event['name']}</div>
                            <div style="font-size: 0.7rem; color: #94a3b8;">{event['date'].strftime('%d %b')} | {event['val']}</div>
                        </div>
                        <div style="font-size: 0.7rem; font-weight: 700; color: {color};">{days_txt}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Footer Quick Actions
    st.divider()
    st.caption("Regional Office Cockpit V3.0 | Auto-synced with MIS Repository")
