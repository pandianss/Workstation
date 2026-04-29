import streamlit as st

from modules.ui.mock_data import vendors_df
from modules.utils.page_helpers import render_page_header


render_page_header(
    "Vendor & Empanelment Register",
    "Review empanelled vendors, see renewal risk, and capture performance feedback in one place.",
)

vendors = vendors_df()
tabs = st.tabs(["Directory", "Renewal Alerts", "Performance Rating"])

with tabs[0]:
    left, right = st.columns(2)
    with left:
        category = st.selectbox("Category", ["ALL"] + sorted(vendors["Category"].unique().tolist()))
    with right:
        district = st.selectbox("District", ["ALL"] + sorted(vendors["District"].unique().tolist()))
    filtered = vendors.copy()
    if category != "ALL":
        filtered = filtered[filtered["Category"] == category]
    if district != "ALL":
        filtered = filtered[filtered["District"] == district]
    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tabs[1]:
    st.warning("Desai & Co. (Chartered Accountants) empanelment expires in 60 days.")
    st.warning("Axis Security Services empanelment expires in 120 days.")
    st.button("Draft Renewal Reminder")

with tabs[2]:
    vendor = st.selectbox("Select Vendor", vendors["Name"].tolist())
    rating = st.slider("Rating", 1, 5, 3)
    remarks = st.text_area("Remarks")
    blacklist = st.checkbox("Recommend for blacklisting")
    if st.button("Submit Rating"):
        outcome = "flagged for escalation" if blacklist else "recorded"
        st.success(f"Rating for {vendor} has been {outcome}.")
