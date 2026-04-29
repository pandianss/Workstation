import datetime

import streamlit as st

from app.services.anniversary_service import (
    get_congratulations_message,
    get_upcoming_anniversaries,
)
from app.services.report_service import generate_ro_anniversary_letter


def render_anniversary_alerts():
    upcoming = get_upcoming_anniversaries(days=30)

    if not upcoming:
        return

    st.markdown("### Branch Anniversaries and Campaigns")

    todays = [item for item in upcoming if item["is_today"]]
    if todays:
        st.balloons()

    for item in todays:
        st.success(get_congratulations_message(item))
        letter_pdf = generate_ro_anniversary_letter(item)
        st.download_button(
            label=f"Download RO congratulatory letter for {item['name']}",
            data=letter_pdf,
            file_name=f"RO_Letter_{item['code']}_{item['anniversary_date'].year}.pdf",
            mime="application/pdf",
            key=f"dl_{item['code']}",
        )

    future = [item for item in upcoming if not item["is_today"]]
    if not future:
        return

    for item in future:
        if item["is_campaign_period"]:
            st.info(
                f"**{item['name']}** ({item['code']}) is in its **Special Business Fortnight** drive. "
                f"Foundation Day: {item['anniversary_date'].strftime('%d %B')}."
            )
            col1, col2 = st.columns([3, 1])
            col1.write(
                f"The **{item['name']}** branch is currently running special campaigns leading up to its "
                f"**{item['years']}th Anniversary**."
            )

            letter_pdf = generate_ro_anniversary_letter(item)
            col2.download_button(
                label="RO Letter",
                data=letter_pdf,
                file_name=f"RO_Letter_{item['code']}.pdf",
                mime="application/pdf",
                key=f"cp_{item['code']}",
            )

    with st.expander("Other Upcoming Anniversaries", expanded=False):
        for item in [entry for entry in future if not entry["is_campaign_period"]]:
            days_left = (item["anniversary_date"] - datetime.date.today()).days
            st.write(
                f"**{item['anniversary_date'].strftime('%d %B')}**: **{item['name']}** "
                f"({item['years']} Years), in {days_left} days."
            )
