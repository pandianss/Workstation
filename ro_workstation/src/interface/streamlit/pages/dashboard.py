from __future__ import annotations

import pandas as pd
import streamlit as st

from src.application.services.guardian_service import GuardianService
from src.application.services.task_service import TaskService
from src.application.services.circular_service import CircularService
from src.application.services.document_service import DocumentService
from src.application.services.returns_service import ReturnsService
from src.application.use_cases.global_search import GlobalSearchService
import datetime
from src.interface.streamlit.components.primitives import (
    render_action_bar, render_data_table, render_filter_panel, 
    render_premium_metrics, render_section_divider, render_info_banner
)


from src.interface.streamlit.state.services import (
    get_task_service, get_guardian_service, get_returns_service, 
    get_search_service, get_circular_service, get_doc_service_v2
)

def render() -> None:
    username = st.session_state.get("username", "")
    task_service = get_task_service()
    guardian_service = get_guardian_service()
    returns_service = get_returns_service()
    search_service = get_search_service()

    summary = task_service.get_task_summary(username)
    
    # Premium Action Bar
    st.markdown('<h1 class="text-gold">Executive Command Center</h1>', unsafe_allow_html=True)
    render_action_bar("Strategic Regional Oversight", ["Real-time", "Bi-lingual", "Luxury Edition"])
    
    # Glassmorphic KPI Row
    render_premium_metrics({
        "Open Tasks": summary["open"],
        "Overdue": summary["overdue"],
        "Pending Returns": len([r for r in returns_service.get_all() if r["status"] == "Pending"]),
        "Guardian Alerts": len(guardian_service.list_followups()),
    })

    render_section_divider()
    
    # Integrated Search & Focus Area
    col_search, col_stats = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("Unified Search", placeholder="🔎 Search staff, units, tasks, or MIS references...", key="global_search_input")
        if query:
            results = pd.DataFrame(search_service.search(query, username))
            if results.empty:
                st.info("No matching records found in the workstation index.")
            else:
                render_data_table(results, "Deep Search Results", "global_search_results.xlsx")
        
        task_frame = pd.DataFrame(summary["tasks"])
        if not task_frame.empty:
            st.markdown('<div class="text-gold" style="font-size: 1.2rem; margin-bottom: 0.5rem;">⚡ Active Action Queue</div>', unsafe_allow_html=True)
            render_data_table(task_frame, "Pending Responsibilities", "task_queue.xlsx")

    with col_stats:
        st.markdown("#### 🛡️ Guardian Insights")
        followups = guardian_service.as_frame()
        if not followups.empty:
            for _, row in followups.head(5).iterrows():
                st.markdown(f"""
                    <div class="glass-panel" style="margin-bottom: 8px; padding: 12px; border-left: 4px solid #3b82f6;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">{row.get('DATE', '')}</div>
                        <div style="font-weight: 600; font-size: 0.9rem;">{row.get('BRANCH', 'Alert')}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{row.get('REMARKS', '')[:60]}...</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active follow-ups detected.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📅 Upcoming Returns")
        returns = [r for r in returns_service.get_all() if r["status"] == "Pending"][:3]
        if returns:
            for r in returns:
                st.markdown(f"""
                    <div class="glass-panel" style="margin-bottom: 8px; padding: 12px; border-left: 4px solid #10b981;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">Due: {r.get('due_date', '')}</div>
                        <div style="font-weight: 600; font-size: 0.9rem;">{r.get('title', 'Return')}</div>
                        <div style="font-size: 0.7rem; text-transform: uppercase;">{r.get('frequency', '')}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No pending returns.")

        # --- Branch Anniversaries Section ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🎈 Upcoming Anniversaries")
        from src.application.services.anniversary_service import AnniversaryService
        anniv_svc = AnniversaryService()
        upcoming_anniv = anniv_svc.get_upcoming_anniversaries(days=15)
        
        if upcoming_anniv:
            for anniv in upcoming_anniv:
                days_txt = "TODAY" if anniv["days_to_go"] == 0 else f"IN {anniv['days_to_go']} DAYS"
                render_info_banner(
                    title=f"{anniv['name']} - {anniv['years']} Year Anniversary",
                    message=f"Celebrate this milestone on {anniv['anniversary_date'].strftime('%d %B')}. Status: {days_txt}",
                    icon="🎊"
                )
                
                # Small action buttons for anniversary
                c1, c2 = st.columns(2)
                if c1.button("🎨 Poster", key=f"post_{anniv['sol']}", use_container_width=True):
                    with st.spinner("Generating..."):
                        html = get_doc_service_v2().generate_anniversary_poster_html(anniv["name"], anniv["years"], anniv["open_date"].strftime("%d.%m.%Y"))
                        st.session_state[f"anniv_post_html_{anniv['sol']}"] = html
                
                if c2.button("📝 Note", key=f"note_{anniv['sol']}", use_container_width=True):
                    with st.spinner("Preparing..."):
                        pdf = get_doc_service_v2().generate_pdf_anniversary(anniv["name"], anniv["sol"], anniv["years"], anniv["open_date"].strftime("%d.%m.%Y"))
                        st.session_state[f"anniv_note_{anniv['sol']}"] = pdf
                
                # Render the interactive poster preview if generated
                if f"anniv_post_html_{anniv['sol']}" in st.session_state:
                    with st.expander("👁️ Poster Preview & Image Download", expanded=True):
                        st.components.v1.html(st.session_state[f"anniv_post_html_{anniv['sol']}"], height=800, scrolling=True)
                        st.info("💡 Use the blue button inside the preview above to download the high-res PNG.")
                if f"anniv_note_{anniv['sol']}" in st.session_state:
                    st.download_button("📥 Download Note", data=st.session_state[f"anniv_note_{anniv['sol']}"], file_name=f"Note_{anniv['name']}.pdf", key=f"dl_note_{anniv['sol']}", use_container_width=True)

        else:
            st.info("No branch anniversaries in the next 15 days.")

        # --- Staff Milestones Section ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🌟 Staff Milestones")
        staff_events = anniv_svc.get_staff_celebrations(days=15)
        
        if staff_events:
            for event in staff_events:
                days_txt = "TODAY" if event["days_to_go"] == 0 else f"IN {event['days_to_go']} DAYS"
                icon = "🎂" if event["type"] == "BIRTHDAY" else "🎖️"
                title_prefix = "Birthday" if event["type"] == "BIRTHDAY" else "Retirement"
                
                render_info_banner(
                    title=f"{title_prefix}: {event['name']}",
                    message=f"{event['designation']} ({event['sol']}) | {event['event_date'].strftime('%d %B')}. Status: {days_txt}",
                    icon=icon
                )
                
                # Poster generation for staff
                if st.button(f"🎨 Generate {title_prefix} Poster", key=f"staff_post_{event['roll']}_{event['type']}", use_container_width=True):
                    with st.spinner("Crafting..."):
                        if event["type"] == "BIRTHDAY":
                            html = get_doc_service_v2().generate_staff_birthday_html(event['name'], event['designation'], f"Branch {event['sol']}")
                        else:
                            html = get_doc_service_v2().generate_staff_retirement_html(event['name'], event['designation'])
                        st.session_state[f"staff_post_html_{event['roll']}_{event['type']}"] = html
                
                if f"staff_post_html_{event['roll']}_{event['type']}" in st.session_state:
                    with st.expander(f"👁️ {title_prefix} Preview", expanded=True):
                        st.components.v1.html(st.session_state[f"staff_post_html_{event['roll']}_{event['type']}"], height=800, scrolling=True)
                        st.info("💡 Use the blue button inside the preview above to download.")
        else:
            st.info("No staff birthdays or retirements in the next 15 days.")

    # 4. Regional Circulars (Visible to All)
    st.divider()
    st.markdown("### 📢 Regional Circulars & Notifications")
    circ_service = CircularService()
    doc_service = DocumentService()
    all_circs = circ_service.get_all()
    
    if all_circs:
        # Show top 3 most recent
        for i, c in enumerate(all_circs[:3]):
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    is_new = False
                    try:
                        c_date_str = c.get('date', '')
                        p_date = datetime.datetime.fromisoformat(c_date_str) if 'T' in c_date_str else datetime.datetime.strptime(c_date_str, "%Y-%m-%d")
                        if (datetime.datetime.now() - p_date).days <= 7:
                            is_new = True
                    except: pass
                    
                    subject = c.get("subject") or c.get("title") or "Circular"
                    if is_new:
                        st.markdown(f"**🆕 {subject}**")
                    else:
                        st.markdown(f"**{subject}**")
                    st.caption(f"{c.get('ref_no') or c.get('number')} | {c.get('date')}")
                with c2:
                    if st.button("📄 Prepare", key=f"dash_prep_{i}", use_container_width=True):
                        with st.spinner("Generating..."):
                            pdf_bytes = doc_service.generate_circular_pdf(c)
                            st.session_state[f"dash_pdf_{i}"] = pdf_bytes
                    
                    if f"dash_pdf_{i}" in st.session_state:
                        st.download_button("📥 Download", data=st.session_state[f"dash_pdf_{i}"], file_name=f"Circular_{i}.pdf", key=f"dash_dl_{i}", use_container_width=True)
        
        if len(all_circs) > 3:
            if st.button("View All Circulars"):
                st.session_state["page"] = "Document Center" # Or whatever the page name is in router
                st.rerun()
    else:
        st.info("No active circulars to display.")
