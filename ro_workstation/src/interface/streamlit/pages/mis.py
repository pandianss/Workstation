from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import datetime

from src.application.use_cases.mis.service import MISAnalyticsService
from src.core.utils.financial_year import get_fy_start
from src.domain.schemas.mis import MISFilter
from src.infrastructure.persistence.database import get_db_session
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_premium_metrics, render_chart_container
from src.application.services.milestone_service import MilestoneService
from src.application.services.performance_letter_service import PerformanceLetterService
from src.application.services.master_service import MasterService
from src.application.services.graphic_service import GraphicService
from src.core.paths import project_path

def render() -> None:
    service = MISAnalyticsService()
    letter_service = PerformanceLetterService()
    # 1. Page Title
    render_action_bar("Regional MIS Analytics", ["Market Share", "Budget Tracking", "NPA Surveillance"])
    
    # ─── DATA INGESTION HUB ──────────────────────────────────────────────
    with st.expander("🛠️ Data Maintenance Hub", expanded=False):
        st.caption("Upload source files to update regional database.")
        
        up_col1, up_col2 = st.columns(2)
        with up_col1:
            # MIS Data Ingestion
            mis_file = st.file_uploader("📊 MIS Performance (.xlsx)", type=["xlsx"])
            if mis_file:
                mis_dir = project_path("data", "mis")
                mis_dir.mkdir(parents=True, exist_ok=True)
                with open(mis_dir / mis_file.name, "wb") as f:
                    f.write(mis_file.getbuffer())
                st.success(f"MIS File '{mis_file.name}' uploaded! Processing...")
                service.sync_database() # Trigger DB sync
                st.rerun()

            # Budget Data Ingestion
            budget_file = st.file_uploader("🎯 Budget Targets (.csv)", type=["csv"])
            if budget_file:
                target_path = project_path("files", "Budget3.csv")
                with open(target_path, "wb") as f:
                    f.write(budget_file.getbuffer())
                st.success("Budget3.csv updated! Syncing targets...")
                letter_service.budget_repo.sync_if_needed()
                st.rerun()

        with up_col2:
            # Staff Data Ingestion
            staff_file = st.file_uploader("👥 Staff Registry (.csv)", type=["csv"])
            if staff_file:
                target_path = project_path("files", "Staff.csv")
                with open(target_path, "wb") as f:
                    f.write(staff_file.getbuffer())
                MasterService().sync_staff_from_csv()
                st.success("Staff Registry updated with history preservation!")
                st.rerun()

            # Branch Data Ingestion
            branch_file = st.file_uploader("🏢 Branch Master (.csv)", type=["csv"])
            if branch_file:
                target_path = project_path("files", "branches.csv")
                with open(target_path, "wb") as f:
                    f.write(branch_file.getbuffer())
                MasterService().sync_units_from_csv()
                st.success("Branch Master updated and database synchronized!")
                st.rerun()
    
    # ─── BASE DATA LOAD ────────────────────────────────────────────────────
    df = service.get_data()
    if df.empty:
        st.error("No MIS data found. Please use the Maintenance Hub above to upload MIS files.")
        return
    
    # 2. Global Filters
    dates = sorted(df["DATE"].dt.date.unique())
    sols = sorted(df["SOL"].dropna().astype(int).unique().tolist())
    
    # SOL to Branch Name Mapping
    from src.infrastructure.persistence.master_repository import MasterRepository
    repo = MasterRepository()
    units = repo.get_by_category("UNIT")
    unit_map = {int(u.code): f"{u.code} - {u.name_en}" for u in units if u.code.isdigit()}
    
    col_d, col_b = st.columns(2)
    with col_d:
        selected_date = st.selectbox("Reporting Date", dates, index=len(dates) - 1)
    with col_b:
        selected_sols = st.multiselect(
            "Unit Focus", 
            options=sols, 
            default=[],
            format_func=lambda x: unit_map.get(x, f"SOL {x}")
        )

    # 3. Dynamic Snapshot Generation
    snapshot = service.build_snapshot(MISFilter(selected_date=selected_date, sols=selected_sols))
    if not snapshot:
        st.warning("No data found for this selection.")
        return

    # Glassmorphic KPI Row
    render_premium_metrics(snapshot.kpis)
    
    st.markdown("<br>", unsafe_allow_html=True)

    frame = pd.DataFrame(snapshot.rows)
    # Filter for numeric columns that aren't IDs or Dates
    excluded_cols = {"SOL", "DATE", "SNO", "ID", "YEAR", "MONTH", "CD RATIO", "NPA %"}
    metric_options = [c for c in frame.columns if frame[c].dtype in ['float64', 'int64'] and c.upper() not in excluded_cols]
    
    # Advanced Performance Tracking
    with st.expander("📈 Advanced Budget Gap Analysis", expanded=True):
        metric_to_track = st.selectbox("Select Parameter to Analyze", sorted(metric_options), index=sorted(metric_options).index("TOTAL ADVANCES") if "TOTAL ADVANCES" in metric_options else 0)
        perf = service.get_performance_metrics(selected_date, metric_to_track, sols=selected_sols)
        
        def format_cr(val):
            """Formats Lacs to Crores as per bank standards."""
            return f"{val/100:,.2f} Cr"

        if perf:
            st.markdown("### 🎯 Executive Budget Gap Summary")
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #10b981; background: #0f172a; border-radius: 12px; padding: 20px;">
                        <div style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.1rem; font-weight: 700; text-transform: uppercase;">FY GROWTH</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 12px 0;">{format_cr(perf['fy_growth'])}</div>
                        <div style="color: #10b981; font-weight: 700; font-size: 1rem;">↑ {perf['fy_growth_pct']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col2:
                gap = perf['gap_current_month']
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #ef4444; background: #0f172a; border-radius: 12px; padding: 20px;">
                        <div style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.1rem; font-weight: 700; text-transform: uppercase;">MONTHLY GAP</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: #ef4444; margin: 12px 0;">{format_cr(gap)}</div>
                        <div style="font-size: 0.9rem; color: #f8fafc; font-weight: 600;">Target: {format_cr(perf['targets']['month'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col3:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #ffffff; background: #0f172a; border-radius: 12px; padding: 20px;">
                        <div style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.1rem; font-weight: 700; text-transform: uppercase;">ANNUAL GAP</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 12px 0;">{format_cr(perf['gap_fy'])}</div>
                        <div style="font-size: 0.9rem; color: #f8fafc; font-weight: 600;">Target: {format_cr(perf['targets']['fy'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Visualization Layer
    tabs = st.tabs(["📊 Business Trends", "🏦 Advances Portfolio", "🏆 Milestones Record", "📬 Budget Communication"])
    
    with tabs[0]:
        col_chart, col_table = st.columns([1.5, 1])
        
        history = pd.DataFrame(snapshot.history_rows)
        if not history.empty:
            history["DATE"] = pd.to_datetime(history["DATE"])
            fy_start = pd.to_datetime(get_fy_start(selected_date))
            # Filter for current FY by default
            history = history[history["DATE"] >= fy_start]

        with col_chart:
            if not history.empty:
                st.markdown("#### 📈 Dynamic Business Trend (Current FY)")
                # Multi-line chart: Advances vs Deposits
                trend = history.groupby("DATE", as_index=False)[["TOTAL ADVANCES", "TOTAL DEPOSITS"]].sum()
                fig = px.line(trend, x="DATE", y=["TOTAL ADVANCES", "TOTAL DEPOSITS"], 
                            template="plotly_dark", color_discrete_sequence=["#3b82f6", "#10b981"])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title=None)
                st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("#### 🏢 Unit Hierarchy")
            frame = pd.DataFrame(snapshot.rows)
            if not frame.empty:
                # Add Branch Name column for display
                frame["Branch"] = frame["SOL"].map(lambda x: unit_map.get(int(x), f"SOL {x}") if pd.notnull(x) else "Unknown")
                st.dataframe(frame[["Branch", "TOTAL ADVANCES", "TOTAL DEPOSITS", "NPA %"]].sort_values("TOTAL ADVANCES", ascending=False), 
                             hide_index=True, use_container_width=True)
            
    with tabs[1]:
        from src.application.services.advances_service import AdvancesService
        adv_service = AdvancesService()
        st.subheader("🏦 Advances Portfolio Risk Analysis")
        
        # 1. Selection and Persistence Logic
        avail_dates = adv_service.get_available_dates()
        col_sel, col_up = st.columns([1, 1.5])
        
        with col_sel:
            selected_report_dt = st.selectbox(
                "Select Saved Report", 
                options=avail_dates, 
                format_func=lambda x: x.strftime('%d-%b-%Y'),
                help="Select a previously uploaded and processed portfolio report."
            )

        with col_up:
            uploaded_adv = st.file_uploader("Upload New Advances File", type=["xlsx", "xls", "csv"], key="mis_adv_upload")
        
        adv_df = pd.DataFrame()
        
        if uploaded_adv:
            with st.spinner("Processing & Saving portfolio..."):
                # Process the new data
                adv_df = adv_service.process_data(uploaded_adv)
                # Persist to database
                saved_date = adv_service.save_to_db(adv_df)
                st.success(f"Successfully processed and saved report for {saved_date.strftime('%d-%b-%Y')}")
                # Set as current view
                selected_report_dt = saved_date
        elif selected_report_dt:
            with st.spinner("Loading stored report..."):
                adv_df = adv_service.get_stored_data(selected_report_dt)
                # Normalize column names for the stats engine (since DB stores them lowercase/standardized)
                # But our stats engine expects uppercase normalized names from process_data.
                # Actually, AdvancesRepository stores them with specific lowercase names.
                # Let's map them back to the expected names for the stats engine.
                reverse_mapping = {
                    'branch_code': 'BRANCH_CODE',
                    'ac_name': 'AC_NAME',
                    'foracid': 'FORACID',
                    'schm_code': 'SCHM_CODE',
                    'gl_sub_cd': 'GL_SUB_CD',
                    'open_dt': 'OPEN_DT_NORM',
                    'limit_cr': 'LIMIT_CR',
                    'balance_cr': 'BALANCE_CR',
                    'risk_category': 'RISK_CATEGORY',
                    'l1_category': 'L1_CATEGORY',
                    'l2_sector': 'L2_SECTOR',
                    'l3_scheme': 'L3_SCHEME',
                    'priority_type': 'PRIORITY_TYPE'
                }
                adv_df.rename(columns=reverse_mapping, inplace=True)
                # Ensure date column is datetime
                adv_df['OPEN_DT_NORM'] = pd.to_datetime(adv_df['OPEN_DT_NORM'])
                # Add report_dt for stats extraction
                adv_df['REPORT_DT'] = selected_report_dt.strftime('%Y%m%d')

        if not adv_df.empty:
            stats = adv_service.get_summary_stats(adv_df)
            
            # Metric Row (Glassmorphic)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Accounts", f"{stats['total_count']:,}")
            m2.metric("Portfolio", f"₹{stats['total_balance_cr']:.2f} Cr")
            m3.metric("NPA", f"₹{stats.get('risk_summary', {}).get('NPA', {}).get('sum', 0):.2f} Cr")
            m4.metric("SMA-2", f"₹{stats.get('risk_summary', {}).get('SMA-2', {}).get('sum', 0):.2f} Cr")

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Sanctions Overview (Temporal)
            s_vals = stats.get('sanctions', {})
            st.markdown("#### 🚀 Sanction Momentum")
            s1, s2, s3 = st.columns(3)
            s1.metric("Month", f"₹{s_vals.get('month', 0):.2f} Cr")
            s2.metric("Quarter", f"₹{s_vals.get('quarter', 0):.2f} Cr")
            s3.metric("FY Total", f"₹{s_vals.get('fy', 0):.2f} Cr")

            # Granular Breakup
            with st.expander("📊 Detailed Sanction Breakup by Category & Scheme", expanded=True):
                breakup = stats.get('sanction_breakup', {})
                breakup_data = []
                for grp, vals in breakup.items():
                    breakup_data.append({
                        'Category': vals['category'],
                        'Subdivision': vals['subdivision'],
                        'Mth Cnt': vals['month_count'],
                        'Mth (Cr)': vals['month_amt'],
                        'Qtr Cnt': vals['quarter_count'],
                        'Qtr (Cr)': vals['quarter_amt'],
                        'FY Cnt': vals['fy_count'],
                        'FY (Cr)': vals['fy_amt']
                    })
                
                b_df = pd.DataFrame(breakup_data)
                if not b_df.empty:
                    # Sort by Category then FY Total
                    b_df = b_df.sort_values(['Category', 'FY (Cr)'], ascending=[True, False])
                    st.table(b_df.style.format({
                        'Mth (Cr)': '{:,.2f}',
                        'Qtr (Cr)': '{:,.2f}',
                        'FY (Cr)': '{:,.2f}',
                        'Mth Cnt': '{:,}',
                        'Qtr Cnt': '{:,}',
                        'FY Cnt': '{:,}'
                    }))
                    
                    # Download Branch-wise reports
                    st.markdown("---")
                    st.markdown("##### 📥 Download Branch-wise Analysis")
                    d_col1, d_col2, d_col3 = st.columns(3)
                    
                    with d_col1:
                        m_report = adv_service.generate_branch_wise_sanction_report(adv_df, selected_report_dt, period='month')
                        if m_report:
                            st.download_button(
                                label="This Month",
                                data=m_report,
                                file_name=f"Sanctions_MTD_{selected_report_dt.strftime('%b_%Y')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    with d_col2:
                        pm_report = adv_service.generate_branch_wise_sanction_report(adv_df, selected_report_dt, period='prev_month')
                        if pm_report:
                            st.download_button(
                                label="Prev Month",
                                data=pm_report,
                                file_name=f"Sanctions_PrevMth_{selected_report_dt.strftime('%b_%Y')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    with d_col3:
                        fy_report = adv_service.generate_branch_wise_sanction_report(adv_df, selected_report_dt, period='fy')
                        if fy_report:
                            st.download_button(
                                label="Full FY",
                                data=fy_report,
                                file_name=f"Sanctions_FY_{selected_report_dt.strftime('%Y')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Category Distribution")
                cat_df = pd.DataFrame(list(stats['by_category'].items()), columns=['Category', 'Balance (Cr)'])
                fig_cat = px.pie(cat_df, values='Balance (Cr)', names='Category', hole=.4, template="plotly_dark")
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col_b:
                st.markdown("#### Asset Quality Mix")
                risk_df = pd.DataFrame([{'Risk': k, 'Balance': v['sum']} for k, v in stats['risk_summary'].items()])
                fig_risk = px.bar(risk_df, x='Risk', y='Balance', template="plotly_dark", color='Risk')
                st.plotly_chart(fig_risk, use_container_width=True)

            st.markdown("#### Sector Breakdown")
            sector_df = pd.DataFrame([{'Sector': k, 'Count': v['count'], 'Balance (Cr)': v['sum']} for k, v in stats['by_sector'].items()])
            st.dataframe(sector_df.sort_values('Balance (Cr)', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("Please upload an Advances file to begin analysis.")

    with tabs[2]:
        col_title, col_pdf = st.columns([3, 1])
        with col_title:
            st.subheader("🏆 Business Milestones Record")
        with col_pdf:
            from src.application.services.document_service import DocumentService
            doc_service = DocumentService()
            
            # Prepare summary for PDF (Count by Parameter)
            params_avail = MilestoneService.PARAMETERS
            summary_data = []
            milestone_list = snapshot.milestones or []
            
            for p in params_avail:
                p_milestones = [m for m in milestone_list if m["parameter"] == p]
                count_50 = sum(1 for m in p_milestones if m["value"] >= 50)
                count_100 = sum(1 for m in p_milestones if m["value"] >= 100)
                count_150 = sum(1 for m in p_milestones if m["value"] >= 150)
                count_200 = sum(1 for m in p_milestones if m["value"] >= 200)
                
                summary_data.append({
                    "Parameter": p,
                    "50Cr+": count_50,
                    "100Cr+": count_100,
                    "150Cr+": count_150,
                    "200Cr+": count_200,
                    "Total Milestones": len(p_milestones)
                })
            
            if st.button("📄 Prepare PDF Report", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_bytes = doc_service.generate_milestones_pdf(
                        snapshot.milestones, 
                        summary_data, 
                        str(snapshot.selected_date)
                    )
                    st.session_state["milestone_pdf"] = pdf_bytes
            
            if "milestone_pdf" in st.session_state:
                st.download_button(
                    "📥 Download Report",
                    data=st.session_state["milestone_pdf"],
                    file_name=f"Milestone_Report_{snapshot.selected_date}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        st.info("Tracks branches that have crossed 50Cr, 100Cr, 150Cr, 200Cr, 250Cr... milestones.")
        
        # Monthly Breakthroughs Section
        if snapshot.milestone_breakthroughs:
            with st.container(border=True):
                col_bt, col_btn = st.columns([3, 1.5])
                with col_bt:
                    st.markdown("#### 🌟 Monthly Breakthroughs")
                    st.caption("Branches that crossed a NEW 50Cr-increment threshold since last month end.")
                with col_btn:
                    if st.button("✅ Finalize & Generate Letters", use_container_width=True):
                        with st.spinner("Saving breakthroughs and preparing letters..."):
                            with get_db_session() as session:
                                ms_srv = MilestoneService(session)
                                saved_count = ms_srv.save_achievements(snapshot.milestone_breakthroughs)
                                st.success(f"Successfully recorded {saved_count} new breakthroughs!")
                            
                            # Generate letters and posters
                            graphic_srv = GraphicService()
                            
                            import io, zipfile
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w") as zf:
                                for i, b in enumerate(snapshot.milestone_breakthroughs):
                                    # PDF Letter
                                    pdf = doc_service.generate_performance_appreciation(b)
                                    pdf_name = f"Appreciation_{b['branch_name'].replace(' ', '_')}_{b['parameter']}.pdf"
                                    zf.writestr(f"Letters/{pdf_name}", pdf)
                                    
                                    # Social Media Poster
                                    img_bytes = graphic_srv.generate_milestone_poster(b)
                                    img_name = f"Poster_{b['branch_name'].replace(' ', '_')}_{b['parameter']}.png"
                                    zf.writestr(f"Posters/{img_name}", img_bytes)
                            
                            st.session_state["breakthrough_zip"] = zip_buffer.getvalue()

                    if "breakthrough_zip" in st.session_state:
                        st.download_button(
                            "📥 Download Appreciation Kit",
                            data=st.session_state["breakthrough_zip"],
                            file_name=f"Recognition_Kit_{snapshot.selected_date}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )

                b_df = pd.DataFrame(snapshot.milestone_breakthroughs)
                cols_to_show = ["branch_name", "parameter", "previous_value", "value", "milestone"]
                b_display = b_df[cols_to_show].copy()
                b_display["previous_value"] = b_display["previous_value"].map(lambda x: f"{x:.2f}")
                b_display["value"] = b_display["value"].map(lambda x: f"{x:.2f}")

                p_dt = b_df["prev_date"].iloc[0].strftime("%d-%b") if "prev_date" in b_df.columns and not b_df.empty else "Prev"
                c_dt = b_df["date"].iloc[0].strftime("%d-%b") if "date" in b_df.columns and not b_df.empty else "Curr"
                b_display.columns = ["Branch", "Parameter", f"Value {p_dt} (Cr)", f"Value {c_dt} (Cr)", "New Milestone"]
                st.table(b_display)
        
        if snapshot.milestones:
            m_df_raw = pd.DataFrame(snapshot.milestones)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                selected_param = st.multiselect("Filter Parameters", params_avail, default=[])
            with col_f2:
                levels_avail = sorted(m_df_raw["milestone"].unique())
                selected_levels = st.multiselect("Filter Milestones", levels_avail, default=[])

            filtered_df = m_df_raw.copy()
            if selected_param:
                filtered_df = filtered_df[filtered_df["parameter"].isin(selected_param)]
            if selected_levels:
                filtered_df = filtered_df[filtered_df["milestone"].isin(selected_levels)]

            if not filtered_df.empty:
                st.markdown(f"#### Milestones Inventory")
                display_df = filtered_df[["sol", "branch_name", "parameter", "value", "milestone"]].copy()
                display_df.columns = ["SOL", "Branch", "Parameter", "Value (Cr)", "Milestone"]
                display_df["Value (Cr)"] = display_df["Value (Cr)"].map(lambda x: f"{x:.2f}")
                st.dataframe(display_df.sort_values(["Milestone", "Value (Cr)"], ascending=False), hide_index=True, use_container_width=True)
            
            st.divider()
            st.markdown("#### Achievement Heatmap (Parameter vs Level)")
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df.sort_values("Total Milestones", ascending=False), hide_index=True, use_container_width=True)

    with tabs[3]:
        letter_service = PerformanceLetterService()
        
        st.subheader("📬 Regional Communication Center")
        
        # --- Section 1: Budget Communication ---
        st.markdown("### 🎯 Annual Budget Communication")
        
        status = letter_service.budget_repo.get_sync_status()
        st.caption(f"🛡️ **Data Maintenance:** Last synced on {status['last_sync']} | FYs available: {', '.join(status['fy_ranges'])}")
        
        st.info("Generate formal budget communication letters for all parameters defined in the registry.")
        
        # FY & Communication Date
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            selected_fy = st.selectbox("Target Fiscal Year", options=status["fy_ranges"], index=len(status["fy_ranges"])-1 if status["fy_ranges"] else 0)
        with fcol2:
            comm_date = st.date_input("Date of Communication", value=datetime.date.today())
        
        # Convert selected_fy (e.g. "2026-27") to a date (2026-04-01) for target retrieval
        try:
            fy_start_year = int(selected_fy.split("-")[0])
            fy_ref_date = datetime.date(fy_start_year, 4, 1)
        except:
            fy_ref_date = selected_date
            
        exec_list = MasterService().get_ro_executives()
        exec_options = {e["roll"]: e["name"] for e in exec_list}
        selected_sig_roll = st.selectbox("Signing Authority (Budget)", options=list(exec_options.keys()), format_func=lambda x: exec_options[x], key="budget_sig")
        
        if st.button("🚀 Generate Budget Letters (ZIP)", use_container_width=True):
            budget_data = letter_service.get_budget_communication_data(fy_ref_date)
            if not budget_data:
                st.error(f"No budget data found for {selected_fy}.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(pct, msg):
                    try:
                        progress_bar.progress(pct)
                        status_text.text(msg)
                        return True
                    except: return False
                
                signatory_profile = letter_service.doc_service._resolve_staff_profile(selected_sig_roll)
                formatted_comm_date = comm_date.strftime("%d.%m.%Y")
                zip_bytes = letter_service.generate_budget_zip(
                    budget_data, 
                    signatory_profile, 
                    progress_callback=update_progress,
                    comm_date=formatted_comm_date
                )
                
                progress_bar.empty()
                status_text.empty()
                if zip_bytes:
                    st.success(f"Generated budget letters for {len(budget_data)} branches!")
                    st.download_button("📥 Download Budget Letters ZIP", data=zip_bytes, file_name=f"Budget_Communication_{selected_fy}.zip", mime="application/zip", use_container_width=True)

        st.divider()
        
        # --- Section 2: Performance Letters ---
        perf_header_col1, perf_header_col2 = st.columns([3, 1])
        with perf_header_col1:
            st.markdown("### 📈 Monthly Performance Communication")
            st.caption("Generate mass appreciation and explanation letters based on budget performance.")
        
        with perf_header_col2:
            # Group available dates by Month-Year for selection
            month_options = {}
            for d in reversed(dates):
                m_key = d.strftime("%B %Y")
                if m_key not in month_options:
                    month_options[m_key] = d # Keep the latest date for that month
            
            # Default to the month of the globally selected date
            current_m_key = selected_date.strftime("%B %Y")
            default_idx = list(month_options.keys()).index(current_m_key) if current_m_key in month_options else 0
            
            selected_perf_month_key = st.selectbox("Target Month", options=list(month_options.keys()), index=default_idx, key="perf_month_picker")
            perf_date = month_options[selected_perf_month_key]

        performance_data = letter_service.get_branch_performance(perf_date)
        
        if performance_data:
            with st.expander("📝 Review Monthly Performance Status", expanded=False):
                for p in performance_data:
                    all_achievements = []
                    all_declines = []
                    for g_data in p.get("groups", {}).values():
                        all_achievements.extend(g_data.get("achievements", []))
                        all_declines.extend(g_data.get("declines", []))

                    status_col, name_col, details_col = st.columns([1, 2, 4])
                    with status_col:
                        if all_achievements and not all_declines: st.success("EXCELLENT")
                        elif all_achievements and all_declines: st.warning("MIXED")
                        else: st.error("ACTION REQ")
                    with name_col: st.markdown(f"**{p['branch_name']}** ({p['sol']})")
                    with details_col:
                        ach_tags = [f"{a['parameter']} ({a['pct']:.0f}%)" for a in all_achievements[:3]]
                        dec_tags = [f"{a['parameter']} ({a['pct']:.0f}%)" for a in all_declines[:3]]
                        if ach_tags: st.markdown(f"✅ {', '.join(ach_tags)}")
                        if dec_tags: st.markdown(f"⚠️ {', '.join(dec_tags)}")

            selected_sig_roll_perf = st.selectbox("Signing Authority (Performance)", options=list(exec_options.keys()), format_func=lambda x: exec_options[x], key="perf_sig")
            selected_signatory = next((e for e in exec_list if e["roll"] == selected_sig_roll_perf), None)

            if st.button("📦 Generate All Performance Letters (ZIP)", use_container_width=True):
                if not selected_signatory: st.error("Please select a signatory.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def update_progress_perf(pct, msg):
                        progress_bar.progress(pct)
                        status_text.text(msg)
                    
                    zip_data = letter_service.generate_letters_zip(
                        performance_data, 
                        signatory=selected_signatory,
                        progress_callback=update_progress_perf
                    )
                    
                    progress_bar.empty()
                    status_text.empty()
                    st.success(f"Generated performance letters for {len(performance_data)} branches!")
                    st.download_button("📥 Download Performance Kit", data=zip_data, file_name=f"Performance_Letters_{snapshot.selected_date}.zip", mime="application/zip", use_container_width=True)
        else:
            st.info("No performance data available.")

    # Full Data View
    with st.expander("📋 Detailed MIS Inventory"):
        render_data_table(frame, "Complete Snapshot", f"mis_snapshot_{snapshot.selected_date}.xlsx")
