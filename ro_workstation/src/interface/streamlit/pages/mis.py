from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.application.use_cases.mis.service import MISAnalyticsService
from src.core.utils.financial_year import get_fy_start
from src.domain.schemas.mis import MISFilter
from src.infrastructure.persistence.database import get_db_session
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table, render_premium_metrics, render_chart_container
from src.application.services.milestone_service import MilestoneService
from src.application.services.performance_letter_service import PerformanceLetterService

def render() -> None:
    service = MISAnalyticsService()
    # 1. Base Data Load
    df = service.get_data()
    if df.empty:
        st.error("No MIS data found. Please upload .xlsx files to the `data/mis/` folder.")
        return

    render_action_bar("Regional MIS Analytics", ["Market Share", "Budget Tracking", "NPA Surveillance"])
    
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
        metric_to_track = st.selectbox("Select Parameter to Analyze", sorted(metric_options), index=sorted(metric_options).index("Total Advances") if "Total Advances" in metric_options else 0)
        perf = service.get_performance_metrics(selected_date, metric_to_track, sols=selected_sols)
        
        def format_cr(val):
            """Formats Lacs to Crores if large enough."""
            if abs(val) >= 100: # If more than 100 Lacs, show in Crores? 
                # Actually Bank ROs usually use Lacs for specific parameters, but Cr for Total.
                # Let's stick to Lacs but with comma separators, or Cr if > 1000 Lacs (10 Cr).
                if abs(val) >= 1000:
                    return f"{val/100:.2f} Cr"
            return f"{val:,.1f} L"

        if perf:
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #10b981;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">FY GROWTH</div>
                        <div style="font-size: 1.8rem; font-weight: 700;">{format_cr(perf['fy_growth'])}</div>
                        <div style="color: #10b981; font-weight: 600;">↑ {perf['fy_growth_pct']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col2:
                gap = perf['gap_current_month']
                gap_color = "#ef4444" if gap > 0 else "#10b981"
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid {gap_color};">
                        <div style="font-size: 0.8rem; color: #94a3b8;">MONTHLY GAP</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: {gap_color};">{format_cr(gap)}</div>
                        <div style="font-size: 0.8rem;">Target: {format_cr(perf['targets']['month'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with p_col3:
                st.markdown(f"""
                    <div class="glass-panel" style="border-top: 4px solid #3b82f6;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">ANNUAL GAP</div>
                        <div style="font-size: 1.8rem; font-weight: 700;">{format_cr(perf['gap_fy'])}</div>
                        <div style="font-size: 0.8rem;">Target: {format_cr(perf['targets']['fy'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Visualization Layer
    tabs = st.tabs(["📊 Business Trends", "🏦 Advances Portfolio", "🏆 Milestones Record"])
    
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
                trend = history.groupby("DATE", as_index=False)[["Total Advances", "Total Deposits"]].sum()
                fig = px.line(trend, x="DATE", y=["Total Advances", "Total Deposits"], 
                            template="plotly_dark", color_discrete_sequence=["#3b82f6", "#10b981"])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title=None)
                st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("#### 🏢 Unit Hierarchy")
            frame = pd.DataFrame(snapshot.rows)
            if not frame.empty:
                # Add Branch Name column for display
                frame["Branch"] = frame["SOL"].map(lambda x: unit_map.get(int(x), f"SOL {x}") if pd.notnull(x) else "Unknown")
                st.dataframe(frame[["Branch", "Total Advances", "Total Deposits", "NPA %"]].sort_values("Total Advances", ascending=False), 
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
                    file_name=f"Milestones_Record_{snapshot.selected_date}.pdf",
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
                            from src.application.services.graphic_service import GraphicService
                            graphic_srv = GraphicService()
                            
                            import io, zipfile
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w") as zf:
                                for i, b in enumerate(snapshot.milestone_breakthroughs):
                                    # PDF Letter
                                    pdf = doc_service.generate_appreciation_letter(b)
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
                b_display.columns = ["Branch", "Parameter", "Prev Val (Cr)", "Curr Val (Cr)", "New Milestone"]
                # Rounding
                for col in ["Prev Val (Cr)", "Curr Val (Cr)"]:
                    b_display[col] = b_display[col].map(lambda x: f"{x:.2f}")
                
                st.table(b_display)
        
        if snapshot.milestones:
            m_df_raw = pd.DataFrame(snapshot.milestones)
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                selected_param = st.multiselect("Filter Parameters", params_avail, default=[])
            with col_f2:
                levels_avail = sorted(m_df_raw["milestone"].unique())
                selected_levels = st.multiselect("Filter Milestones", levels_avail, default=[])

            # Apply filters
            filtered_df = m_df_raw.copy()
            if selected_param:
                filtered_df = filtered_df[filtered_df["parameter"].isin(selected_param)]
            if selected_levels:
                filtered_df = filtered_df[filtered_df["milestone"].isin(selected_levels)]

            if not filtered_df.empty:
                st.markdown(f"#### Milestones Inventory")
                
                # Format for display
                display_df = filtered_df[["sol", "branch_name", "parameter", "value", "milestone"]].copy()
                display_df.columns = ["SOL", "Branch", "Parameter", "Value (Cr)", "Milestone"]
                display_df["Value (Cr)"] = display_df["Value (Cr)"].map(lambda x: f"{x:.2f}")
                
                st.dataframe(display_df.sort_values(["Milestone", "Value (Cr)"], ascending=False), hide_index=True, use_container_width=True)
            else:
                st.info("No branches matching the selection have reached milestones.")
            
            # Global Milestones Summary Chart
            st.divider()
            st.markdown("#### Achievement Heatmap (Parameter vs Level)")
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df.sort_values("Total Milestones", ascending=False), hide_index=True, use_container_width=True)

        else:
            st.warning("Milestone data not available.")

        st.divider()
        st.subheader("📬 Performance Communication Center")
        st.caption("Generate mass appreciation and explanation letters based on budget performance.")
        
        perf_service = PerformanceLetterService()
        performance_data = perf_service.get_branch_performance(snapshot.selected_date)
        
        if performance_data:
            with st.expander("📝 Review Monthly Performance Status", expanded=False):
                for p in performance_data:
                    status_col, name_col, details_col = st.columns([1, 2, 4])
                    with status_col:
                        if p["achievements"] and not p["declines"]:
                            st.success("EXCELLENT")
                        elif p["achievements"] and p["declines"]:
                            st.warning("MIXED")
                        else:
                            st.error("ACTION REQ")
                    with name_col:
                        st.markdown(f"**{p['branch_name']}** ({p['sol']})")
                    with details_col:
                        ach_tags = [f"{a['parameter']} ({a['pct']:.0f}%)" for a in p["achievements"]]
                        dec_tags = [f"{a['parameter']} ({a['pct']:.0f}%)" for a in p["declines"]]
                        if ach_tags: st.markdown(f"✅ {', '.join(ach_tags)}")
                        if dec_tags: st.markdown(f"⚠️ {', '.join(dec_tags)}")

            if st.button("📦 Generate All Performance Letters (ZIP)", use_container_width=True):
                with st.spinner("Preparing bulk letters..."):
                    zip_data = perf_service.generate_letters_zip(performance_data)
                    st.download_button(
                        "📥 Download Performance Kit",
                        data=zip_data,
                        file_name=f"Performance_Letters_{snapshot.selected_date}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
        else:
            st.info("No performance data available for this date.")

    # Full Data View
    with st.expander("📋 Detailed MIS Inventory"):
        render_data_table(frame, "Complete Snapshot", f"mis_snapshot_{snapshot.selected_date}.xlsx")
