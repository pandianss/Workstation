from __future__ import annotations
import streamlit as st
import pandas as pd
import datetime
from src.interface.streamlit.state.services import (
    get_mis_service, get_circular_service, get_doc_service, get_master_service
)
from src.application.services.communication_service import CommunicationService
from src.infrastructure.persistence.database import get_db_session
from src.interface.streamlit.components.primitives import render_action_bar, render_premium_metrics, render_data_table

def render() -> None:
    # 1. Branch Identity
    sol_id = st.session_state.get("sol", "3933") # Default for demo
    branch_name = st.session_state.get("branch_name", "Dindigul Main")
    
    render_action_bar(f"Branch Dashboard: {branch_name}", ["Branch: "+str(sol_id), "Real-time", "Connected"])
    
    tabs = st.tabs(["🏠 Overview", "📢 Circulars", "🏗️ Wizards", "💬 RO Coordination", "🛍️ Products"])

    # --- TAB: OVERVIEW ---
    with tabs[0]:
        mis_service = get_mis_service()
        data = mis_service.get_data()
        
        if not data.empty:
            # Filter for this branch
            br_data = data[data["SOL"] == int(sol_id)]
            if not br_data.empty:
                latest = br_data.sort_values("DATE").iloc[-1]
                st.markdown(f"#### 📊 {branch_name} Performance")
                render_premium_metrics({
                    "Total Deposits": f"₹ {latest['Total Deposits']:,.2f} Cr",
                    "Total Advances": f"₹ {latest['Total Advances']:,.2f} Cr",
                    "CASA Ratio": f"{(latest['CASA']/latest['Total Deposits']*100):.2f}%" if latest['Total Deposits'] > 0 else "0%",
                    "NPA %": f"{latest['NPA %']}%",
                })
                
                st.markdown("<br>", unsafe_allow_html=True)
                # Comparison with Region
                reg_avg = data[data["DATE"] == latest["DATE"]]["Total Deposits"].mean()
                st.caption(f"Branch Deposit: ₹{latest['Total Deposits']:.2f} Cr vs Regional Avg: ₹{reg_avg:.2f} Cr")

                # Trend Chart (Current FY)
                st.markdown("#### 📈 Branch Business Trend")
                from src.core.utils.financial_year import get_fy_start
                fy_start = pd.to_datetime(get_fy_start(datetime.date.today()))
                br_hist = br_data[br_data["DATE"] >= fy_start].groupby("DATE")[["Total Deposits", "Total Advances"]].sum().reset_index()
                from src.interface.streamlit.components.primitives import render_chart_container
                render_chart_container(br_hist, "DATE", ["Total Deposits", "Total Advances"], f"{branch_name} Growth (Current FY)")
            else:
                st.warning(f"No MIS data found for SOL {sol_id}.")

    # --- TAB: CIRCULARS ---
    with tabs[1]:
        circ_service = get_circular_service()
        doc_service = get_doc_service()
        all_circs = circ_service.get_all()
        
        st.markdown("### 📢 Regional Notifications")
        if not all_circs:
            st.info("No active circulars found.")
        else:
            for i, c in enumerate(all_circs):
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**{c.get('subject', 'Circular')}**")
                    c1.caption(f"Ref: {c.get('ref_no')} | Date: {c.get('date')}")
                    if c2.button("Prepare PDF", key=f"br_prep_{i}"):
                        st.session_state[f"br_pdf_{i}"] = doc_service.generate_circular_pdf(c)
                    if f"br_pdf_{i}" in st.session_state:
                        c2.download_button("📥 Download", data=st.session_state[f"br_pdf_{i}"], file_name=f"Circular_{i}.pdf", key=f"br_dl_{i}")

    # --- TAB: WIZARDS ---
    with tabs[2]:
        st.markdown("### 🛠️ Approved Branch Wizards")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="glass-panel" style="padding: 20px;">
                    <h4>✉️ High Value DD</h4>
                    <p style="font-size: 0.85rem;">Required for reporting DDs above ₹ 5 Lakhs.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open DD Wizard", use_container_width=True):
                st.session_state["branch_wiz"] = "high_value_dd"
                st.rerun()

        with col2:
            st.markdown("""
                <div class="glass-panel" style="padding: 20px;">
                    <h4>📄 Office Note Generator</h4>
                    <p style="font-size: 0.85rem;">Standard template for internal approvals.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Office Note Wizard", use_container_width=True):
                st.session_state["branch_wiz"] = "office_note"
                st.rerun()
        
        # Sub-render wizards if selected
        if st.session_state.get("branch_wiz") == "high_value_dd":
            st.divider()
            from src.interface.streamlit.pages.operational_wizards import render_high_value_dd_wizard
            render_high_value_dd_wizard()
        elif st.session_state.get("branch_wiz") == "office_note":
            st.divider()
            from src.interface.streamlit.pages.execution import render_office_note_tab
            render_office_note_tab(doc_service, get_master_service)

    # --- TAB: COMS (RO COORDINATION) ---
    with tabs[3]:
        st.markdown("### 💬 Regional Office Coordination")
        st.caption("Communicate requests directly to Regional Office departments.")
        
        with get_db_session() as session:
            com_svc = CommunicationService(session)
            
            # 1. Raise New Request
            with st.expander("➕ Raise New Request / Inquiry"):
                with st.form("br_com_form"):
                    dept_list = ["IT", "OPERATIONS", "PLANNING", "ADVANCES", "HRM", "GENERAL ADMIN"]
                    target_dept = st.selectbox("Select RO Department", dept_list)
                    subj = st.text_input("Subject")
                    msg = st.text_area("Detailed Message")
                    priority = st.select_slider("Priority", ["LOW", "NORMAL", "HIGH", "URGENT"], value="NORMAL")
                    
                    if st.form_submit_button("Submit to RO"):
                        com_svc.create_request(
                            sender_unit=str(sol_id),
                            sender_name=st.session_state.get("username", "Branch Manager"),
                            receiver_dept=target_dept,
                            subject=subj,
                            message=msg,
                            priority=priority
                        )
                        st.success("Request sent to Regional Office!")
                        st.rerun()

            # 2. View History
            st.markdown("#### 📜 Request History")
            requests = com_svc.get_requests_from_unit(str(sol_id))
            if not requests:
                st.info("No previous requests found.")
            else:
                for r in requests:
                    status_color = {"PENDING": "gray", "IN_PROGRESS": "blue", "RESOLVED": "green", "CLOSED": "red"}.get(r.status, "black")
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        c1.markdown(f"**{r.subject}** (To: {r.receiver_dept})")
                        c1.caption(f"Status: :{status_color}[{r.status}] | Sent: {r.created_at.strftime('%d.%m.%Y')}")
                        c1.write(f"_{r.message}_")
                        
                        if r.response_message:
                            st.markdown(f"""
                                <div style="background: #f0fdf4; padding: 10px; border-radius: 8px; border: 1px solid #bbf7d0; margin-top: 10px;">
                                    <strong>RO Response:</strong> {r.response_message}
                                    <div style="font-size: 0.75rem; color: #166534; margin-top: 5px;">
                                        By {r.responded_by} on {r.responded_at.strftime('%d.%m.%Y %H:%M')}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

    # --- TAB: PRODUCTS ---
    with tabs[4]:
        st.markdown("### 🛍️ Product Catalog")
        products = [
            {"name": "Home Loan Plus", "cat": "Retail", "desc": "Reduced ROI for Senior Citizens.", "icon": "🏠"},
            {"name": "MSME Vidyut", "cat": "MSME", "desc": "Fast track credit for green energy units.", "icon": "⚡"},
            {"name": "Gold Overdraft", "cat": "Agri", "desc": "Instant liquidity against gold ornaments.", "icon": "👑"},
        ]
        
        for p in products:
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                c1.markdown(f"<div style='font-size: 3rem;'>{p['icon']}</div>", unsafe_allow_html=True)
                c2.markdown(f"**{p['name']}** ({p['cat']})")
                c2.write(p['desc'])
                c2.button("Download Brochure", key=f"brochure_{p['name']}")
