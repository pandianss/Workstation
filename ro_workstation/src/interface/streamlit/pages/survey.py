import streamlit as st
import datetime
import pandas as pd
from src.application.services.survey_service import SurveyService
from src.interface.streamlit.components.primitives import render_action_bar

def get_survey_service():
    return SurveyService()

def render() -> None:
    survey_service = get_survey_service()
    render_action_bar("Branch Opening Survey", ["Viability Study", "Market Analysis", "Logistics"])
    
    st.info("📊 This module calculates branch viability based on working days, cost of deposits, and projected growth.")
    
    tabs = st.tabs(["New Survey Report", "Recent Surveys"])
    
    with tabs[0]:
        with st.form("survey_form"):
            st.markdown("### 1. General & Market Info")
            c1, c2, c3 = st.columns(3)
            with c1:
                region = st.text_input("Region", value="Dindigul")
                loc_name = st.text_input("Proposed Location Name")
            with c2:
                report_date = st.date_input("Report Date")
                app_type = st.selectbox("Application Type", ["New Place", "Change Location"])
            with c3:
                population = st.text_input("Area Population")
                bank_dist = st.text_input("Dist to nearest Bank")

            st.markdown("---")
            st.markdown("### 2. Viability Projections (Calculators)")
            st.caption("Inputs in thousands (₹ 000s) as per standard bank reporting.")
            
            c4, c5, c6 = st.columns(3)
            with c4:
                dep_growth = st.number_input("Growth/Day (Deposits)", min_value=0.0, step=0.1, help="Expected daily incremental deposit")
                cost_of_dep = st.number_input("Cost of Deposit (%)", min_value=0.0, max_value=20.0, value=6.0)
            with c5:
                adv_growth = st.number_input("Growth/Day (Advances)", min_value=0.0, step=0.1)
                yield_on_adv = st.number_input("Yield on Advances (%)", min_value=0.0, max_value=25.0, value=10.0)
            with c6:
                monthly_rent = st.number_input("Est. Monthly Rent", min_value=0.0, step=1.0)
                manual_holidays = st.number_input("Manual Holidays", min_value=0, max_value=30, value=0, help="Holidays in year excluding Sundays/2nd&4th Saturdays")

            st.markdown("### 3. Additional Financials")
            c7, c8 = st.columns(2)
            with c7:
                st.markdown("**Expenditure Items**")
                est_charges = st.number_input("Est. Charges (Annual)", min_value=0.0)
                stat_misc = st.number_input("Stationery & Misc (Annual)", min_value=0.0)
                int_borrowed = st.number_input("Interest Borrowed (Annual)", min_value=0.0)
            with c8:
                st.markdown("**Income Items**")
                commission = st.number_input("Commission (Annual)", min_value=0.0)
                exchange = st.number_input("Exchange (Annual)", min_value=0.0)
                int_lent = st.number_input("Interest on Lent Funds", min_value=0.0)

            submitted = st.form_submit_button("Calculate & Save Survey")
            
            if submitted:
                data = {
                    "region": region,
                    "location": loc_name,
                    "date": report_date.isoformat(),
                    "population": population,
                    "depositGrowth": dep_growth,
                    "cost_of_dep": cost_of_dep,
                    "advanceGrowth": adv_growth,
                    "yield_on_adv": yield_on_adv,
                    "monthlyRent": monthly_rent,
                    "manualHolidays": manual_holidays,
                    "estCharges": est_charges,
                    "stationeryMisc": stat_misc,
                    "interestBorrowed": int_borrowed,
                    "commission": commission,
                    "exchange": exchange,
                    "interestLent": int_lent
                }
                
                # Perform calculation
                results = survey_service.calculate_viability(data)
                data.update(results)
                
                survey_service.save_survey(data)
                st.success("Survey Report saved successfully!")
                
                # Display Results
                st.markdown("### Viability Results")
                r1, r2, r3 = st.columns(3)
                r1.metric("Working Days", f"{results['workingDays']} Days")
                r2.metric("Total Expenditure", f"₹{results['totalExpenditure']:.2f}")
                r3.metric("Total Income", f"₹{results['totalIncome']:.2f}")
                
                p_color = "normal" if results['cumulativeProfit'] >= 0 else "inverse"
                st.metric("Cumulative Profit/Loss", f"₹{results['cumulativeProfit']:.2f}", delta_color=p_color)

    with tabs[1]:
        st.subheader("Historical Survey Reports")
        all_surveys = survey_service.get_all()
        if all_surveys:
            df = pd.DataFrame(all_surveys)
            cols = ["id", "location", "date", "workingDays", "cumulativeProfit"]
            st.dataframe(df[cols], use_container_width=True, hide_index=True)
        else:
            st.info("No survey reports found.")
