from __future__ import annotations

import datetime
import pandas as pd
import streamlit as st

from src.application.services.survey_service import SurveyService
from src.interface.streamlit.components.primitives import render_action_bar, render_data_table

@st.cache_resource
def get_survey_service():
    return SurveyService()

def render() -> None:
    service = get_survey_service()
    render_action_bar("Survey & Research Management", ["Viability Study", "Branch Feedback", "Compliance"])
    
    tabs = st.tabs(["📋 Active Surveys", "🏢 Unit Viability Study", "📊 Survey Reports", "🚀 Deploy New Survey"])

    # 1. Active Surveys
    with tabs[0]:
        st.subheader("Active Regional Surveys")
        surveys = service.list_surveys()
        if surveys:
            for survey in surveys:
                with st.container():
                    st.markdown(f"""
                        <div class="glass-panel" style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-weight: 700; font-size: 1.1rem;">{survey['title']}</div>
                                    <div style="font-size: 0.8rem; color: #94a3b8;">Deadline: {survey['deadline']}</div>
                                </div>
                                <span class="status-pill status-low">{survey['status']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Open Survey Form", key=f"sv_active_{survey['title']}"):
                        st.info(f"Opening survey: {survey.get('url', 'N/A')}")
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No active surveys found.")

    # 2. Unit Viability Study
    with tabs[1]:
        st.subheader("New Unit Viability Calculator")
        st.info("Calculate projected profitability for new branches or location changes.")
        
        with st.form("viability_form"):
            st.markdown("#### Market & Logistics")
            c1, c2, c3 = st.columns(3)
            with c1:
                loc_name = st.text_input("Proposed Location")
                population = st.text_input("Area Population")
            with c2:
                report_date = st.date_input("Report Date")
                app_type = st.selectbox("Application Type", ["New Place", "Change Location"])
            with c3:
                bank_dist = st.text_input("Dist to nearest Bank")
            
            st.markdown("#### Projections (₹ 000s)")
            c4, c5, c6 = st.columns(3)
            with c4:
                dep_growth = st.number_input("Daily Deposit Growth", min_value=0.0, step=0.1)
                cost_of_dep = st.number_input("Cost of Deposit (%)", value=6.0)
            with c5:
                adv_growth = st.number_input("Daily Advance Growth", min_value=0.0, step=0.1)
                yield_on_adv = st.number_input("Yield on Advances (%)", value=10.0)
            with c6:
                monthly_rent = st.number_input("Est. Monthly Rent", step=1.0)
                manual_holidays = st.number_input("Manual Holidays", min_value=0, value=0)

            if st.form_submit_button("Calculate Viability"):
                data = {
                    "location": loc_name,
                    "date": report_date.isoformat(),
                    "population": population,
                    "depositGrowth": dep_growth,
                    "cost_of_dep": cost_of_dep,
                    "advanceGrowth": adv_growth,
                    "yield_on_adv": yield_on_adv,
                    "monthlyRent": monthly_rent,
                    "manualHolidays": manual_holidays
                }
                results = service.calculate_viability(data)
                data.update(results)
                service.save_survey(data)
                st.success("Analysis saved.")
                
                r1, r2, r3 = st.columns(3)
                r1.metric("Working Days", f"{results['workingDays']}")
                r2.metric("Total Income", f"₹{results['totalIncome']:.2f}")
                r3.metric("Total Exp", f"₹{results['totalExpenditure']:.2f}")
                
                p_color = "normal" if results['cumulativeProfit'] >= 0 else "inverse"
                st.metric("Proj. Profit/Loss", f"₹{results['cumulativeProfit']:.2f}", delta_color=p_color)

    # 3. Survey Reports
    with tabs[2]:
        st.subheader("Historical Viability Reports")
        all_surveys = service.get_all()
        if all_surveys:
            df = pd.DataFrame(all_surveys)
            render_data_table(df, "Viability Archive", "viability_reports.xlsx")
        else:
            st.info("No reports found.")

    # 4. Deploy New Survey
    with tabs[3]:
        st.subheader("Deploy Regional Survey")
        st.caption("Push a new survey link to all branches in the Dindigul region.")
        with st.form("deploy_survey_form"):
            title = st.text_input("Survey Title", placeholder="e.g., Staff Wellness Survey Q2")
            deadline = st.date_input("Deadline")
            form_url = st.text_input("Form URL (e.g., MS Forms)")
            if st.form_submit_button("Deploy to Network"):
                service.create_survey({
                    "title": title,
                    "deadline": deadline.strftime("%Y-%m-%d"),
                    "status": "Open",
                    "url": form_url
                })
                st.success("Survey deployed successfully.")
                st.rerun()
