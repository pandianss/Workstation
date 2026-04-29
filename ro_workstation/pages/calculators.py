import streamlit as st

from modules.utils.page_helpers import render_page_header


render_page_header(
    "Calculator Suite",
    "Keep frequent operational calculations in one place with clearer input flow and direct interpretations.",
)

tabs = st.tabs(["EMI", "NPA Provision", "PSL / ANBC", "Interest Subvention"])

with tabs[0]:
    with st.form("emi_form"):
        principal = st.number_input("Principal Amount", min_value=0.0, value=1000000.0, step=50000.0)
        rate = st.number_input("Interest Rate (Annual %)", min_value=0.0, value=8.5, step=0.1)
        tenure = st.number_input("Tenure (Years)", min_value=1, value=15, step=1)
        submitted = st.form_submit_button("Calculate EMI")
    if submitted:
        monthly_rate = (rate / 12) / 100
        months = tenure * 12
        emi = (principal * monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        st.success(f"Monthly EMI: Rs {emi:,.2f}")

with tabs[1]:
    asset_class = st.selectbox(
        "Asset Classification",
        ["Substandard", "Doubtful D1 (< 1 yr)", "Doubtful D2 (1-3 yr)", "Doubtful D3 (> 3 yr)", "Loss"],
    )
    outstanding = st.number_input("Outstanding Balance (Rs)", min_value=0.0, value=500000.0, step=25000.0)
    if st.button("Calculate Provision"):
        rates = {
            "Substandard": 0.15,
            "Doubtful D1 (< 1 yr)": 0.25,
            "Doubtful D2 (1-3 yr)": 0.40,
            "Doubtful D3 (> 3 yr)": 1.0,
            "Loss": 1.0,
        }
        provision = outstanding * rates[asset_class]
        st.success(f"Required Provision: Rs {provision:,.2f} ({rates[asset_class] * 100:.0f}%)")

with tabs[2]:
    anbc = st.number_input("Adjusted Net Bank Credit (ANBC)", min_value=0.0, value=100000000.0, step=500000.0)
    agriculture = st.number_input("Agriculture Lending", min_value=0.0, value=15000000.0, step=500000.0)
    if st.button("Check Agriculture Sub-target"):
        target = anbc * 0.18
        current_pct = (agriculture / anbc * 100) if anbc else 0
        if agriculture >= target:
            st.success(f"Target achieved at {current_pct:.1f}% against the 18% requirement.")
        else:
            st.error(f"Shortfall remains. Current: {current_pct:.1f}% | Required value: Rs {target:,.2f}")

with tabs[3]:
    st.info("Use this area for crop loan interest subvention claim calculation once the claim format is finalized.")
