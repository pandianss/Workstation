import streamlit as st
import pandas as pd
import datetime
import textwrap
from src.application.services.campaign_service import CampaignService
from src.interface.streamlit.components.primitives import render_action_bar
from src.interface.streamlit.state.services import get_doc_service_v4

def get_metric_icon(metric: str) -> str:
    """Returns SVG path data for metrics."""
    icons = {
        "CASA": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
        "GOLD": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"></circle><path d="M18.09 10.37A6 6 0 1 1 10.34 18.1"></path><path d="M7 6h1v4"></path><path d="M17.31 15.9l.84 2.16"></path></svg>',
        "RETAIL": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>',
        "DIGITAL": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>',
        "INSURANCE": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        "MUTUAL FUNDS": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>',
        "SOCIAL SECURITY": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
        "DEFAULT": '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
    }
    return icons.get(metric.upper(), icons["DEFAULT"])

def render() -> None:
    service = CampaignService()
    doc_service = get_doc_service_v4()
    render_action_bar("Regional Campaigns", ["Strategic Drives", "Performance Command", "Publicity"])
    
    # 🏆 Hero Banner
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 40px; border-radius: 24px; color: white; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(212,175,55,0.05); border-radius: 50%; blur: 80px;"></div>
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 900; letter-spacing: -1px;">Campaign Command Center</h1>
            <p style="opacity: 0.7; font-size: 1.2rem; margin-top: 10px;">Driving Regional Excellence through Strategic Performance Hubs</p>
        </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📢 Active Missions", "📁 Command Archive", "➕ Strategic Launch"])

    campaigns = service.get_all()

    with tabs[0]:
        active = [(i, c) for i, c in enumerate(campaigns) if c["status"] == "Active"]
        if not active:
            st.info("No active strategic missions currently in progress.")
        else:
            cols = st.columns(2)
            for idx, (i, c) in enumerate(active):
                with cols[idx % 2]:
                    # Calculate Progress (Mock for now, can be linked to MIS)
                    days_left = (datetime.datetime.strptime(c["end_date"], "%Y-%m-%d").date() - datetime.date.today()).days
                    urgency_color = "#ef4444" if days_left < 7 else "#3b82f6"
                    metric_icon = get_metric_icon(c['target_metric'])
                    
                    card_html = textwrap.dedent(f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: white; border-radius: 16px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="background: rgba(59, 130, 246, 0.1); color: #2563eb; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                        {metric_icon.replace('width="24"', 'width="18"').replace('height="24"', 'height="18"')}
                                    </div>
                                    <span style="background: #eff6ff; color: #1d4ed8; padding: 4px 10px; border-radius: 100px; font-weight: 700; font-size: 11px; text-transform: uppercase;">{c['target_metric']}</span>
                                </div>
                                <span style="color: {urgency_color}; font-weight: 700; font-size: 12px;">{max(0, days_left)} DAYS REMAINING</span>
                            </div>
                            <h3 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: #1e293b;">{c['name']}</h3>
                            <div style="margin-top: 20px;">
                                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
                                    <span style="color: #64748b;">Target: {c['target_value']} Cr</span>
                                    <span style="font-weight: 700; color: #1e293b;">65%</span>
                                </div>
                                <div style="width: 100%; height: 8px; background: #f1f5f9; border-radius: 100px; overflow: hidden;">
                                    <div style="width: 65%; height: 100%; background: linear-gradient(90deg, #3b82f6, #2563eb);"></div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; border-top: 1px dashed #e2e8f0; padding-top: 10px; display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8;">
                                <span>START: {c['start_date']}</span>
                                <span>END: {c['end_date']}</span>
                            </div>
                        </div>
                    """)
                    st.components.v1.html(card_html, height=200)
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("🎨 Poster", key=f"post_{i}"):
                        with st.spinner("Rendering..."):
                            html = doc_service.generate_campaign_poster_html(i)
                            st.session_state[f"camp_post_html_{i}"] = html
                    
                    if st.session_state.get(f"camp_post_html_{i}"):
                        with st.expander("👁️ Preview & Download Poster", expanded=True):
                            st.components.v1.html(st.session_state[f"camp_post_html_{i}"], height=800, scrolling=True)
                            if st.button("❌ Close Preview", key=f"close_{i}"):
                                del st.session_state[f"camp_post_html_{i}"]
                                st.rerun()
                    
                    if c2.button("✅ Finish", key=f"comp_{i}"):
                        service.update_campaign(i, {"status": "Completed"})
                        st.rerun()
                        
                    if c3.button("⚙️ Edit", key=f"edit_{i}"):
                        st.session_state[f"edit_camp_{i}"] = True

                    if st.session_state.get(f"edit_camp_{i}"):
                        with st.form(f"f_edit_{i}"):
                            new_name = st.text_input("Name", value=c['name'])
                            new_target = st.number_input("Target (Cr)", value=float(c['target_value']))
                            if st.form_submit_button("Save"):
                                service.update_campaign(i, {"name": new_name, "target_value": new_target})
                                del st.session_state[f"edit_camp_{i}"]
                                st.rerun()

    with tabs[1]:
        completed = [(i, c) for i, c in enumerate(campaigns) if c["status"] == "Completed"]
        if not completed:
            st.info("No archived strategic missions.")
        else:
            df = pd.DataFrame([c for i, c in completed])
            st.dataframe(df[["name", "target_metric", "target_value", "start_date", "end_date"]], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            selected_name = st.selectbox("Select Mission to Archive/Reactivate", options=[c["name"] for i, c in completed])
            if selected_name:
                idx, camp = next((i, c) for i, c in completed if c["name"] == selected_name)
                col1, col2 = st.columns(2)
                if col1.button("🗑️ Purge Records", use_container_width=True):
                    service.delete_campaign(idx)
                    st.rerun()
                if col2.button("♻️ Reactivate Mission", use_container_width=True):
                    service.update_campaign(idx, {"status": "Active"})
                    st.rerun()

    with tabs[2]:
        st.markdown("### 🚀 Launch Strategic Mission")
        st.caption("Define your regional objectives and intelligently allocate targets to branches.")
        
        from src.infrastructure.persistence.master_repository import MasterRepository
        repo = MasterRepository()
        branches = repo.get_by_category("UNIT")
        branches = sorted(branches, key=lambda x: x.name_en)

        with st.form("launch_campaign", border=True):
            name = st.text_input("Mission Name", placeholder="e.g., Gold Loan Carnival June 2026")
            col1, col2 = st.columns(2)
            start = col1.date_input("Start Date")
            end = col2.date_input("End Date")
            
            m1, m2 = st.columns([2, 1])
            metric = m1.selectbox("Key Performance Indicator (KPI)", [
                "CASA", "GOLD", "RETAIL", "MSME", "AGRI", "DIGITAL", "JEWEL LOAN",
                "INSURANCE", "MUTUAL FUNDS", "SOCIAL SECURITY", "CREDIT CARDS"
            ])
            total_target = m2.number_input("Regional Target (Cr)", min_value=0.0, format="%.2f")
            
            st.markdown("---")
            st.markdown("#### 🏛️ Branch Target Allocation")
            st.caption("Branch targets can be set as 'Stretch Goals' that exceed the overall regional benchmark.")
            
            # Using selectbox for better state reliability
            alloc_mode = st.selectbox("Allocation Mode", 
                ["Absolute by Category", "Weighted (by Population)", "Equal Distribution"],
                index=0
            )
            
            branch_targets = {}
            
            if alloc_mode == "Absolute by Category":
                st.markdown("##### Set Absolute Targets by Category (Cr)")
                c1, c2, c3 = st.columns(3)
                t_urban = c1.number_input("URBAN", value=1.0, min_value=0.0, format="%.2f", key="abs_u")
                t_semi = c2.number_input("SEMI URBAN", value=0.5, min_value=0.0, format="%.2f", key="abs_s")
                t_rural = c3.number_input("RURAL", value=0.2, min_value=0.0, format="%.2f", key="abs_r")
                
                for b in branches:
                    group = (b.metadata or {}).get("populationGroup", "RURAL").upper()
                    if "URBAN" in group and "SEMI" not in group: val = t_urban
                    elif "SEMI" in group: val = t_semi
                    else: val = t_rural
                    branch_targets[b.code] = val
                
                total_abs = sum(branch_targets.values())
                st.success(f"Absolute allocation: **{total_abs:.2f} Cr** across all branches.")

            elif alloc_mode == "Weighted (by Population)":
                stretch_factor = st.slider("Stretch Factor", 1.0, 3.0, 1.2, key="stretch_w")
                adjusted_target = total_target * stretch_factor
                weights = {"METRO": 2.0, "URBAN": 1.5, "SEMI URBAN": 1.0, "RURAL": 0.7}
                total_weight = sum(weights.get((b.metadata or {}).get("populationGroup", "RURAL").upper(), 1.0) for b in branches)
                base_unit = adjusted_target / total_weight if total_weight > 0 else 0
                st.info(f"Weighted stretch allocation complete. (Total: {adjusted_target:.2f} Cr)")
                for b in branches:
                    group = (b.metadata or {}).get("populationGroup", "RURAL").upper()
                    branch_targets[b.code] = base_unit * weights.get(group, 1.0)
            
            else: # Equal Distribution
                stretch_factor = st.slider("Stretch Factor", 1.0, 3.0, 1.2, key="stretch_e")
                adjusted_target = total_target * stretch_factor
                avg = adjusted_target / len(branches) if branches else 0
                st.info(f"Each branch will be assigned **{avg:.4f} Cr** (Total: {adjusted_target:.2f} Cr)")
                branch_targets = {b.code: avg for b in branches}

            if st.form_submit_button("🚀 LAUNCH STRATEGIC MISSION", use_container_width=True):
                if not name:
                    st.error("Mission Name is mandatory.")
                elif total_target <= 0:
                    st.error("Please set a valid Regional Target.")
                else:
                    service.add_campaign(name, str(start), str(end), metric, total_target, branch_targets)
                    st.success(f"Strategic Mission '{name}' launched successfully! Branch targets have been allocated.")
                    st.rerun()
