import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import get_hotel_names, get_hotel_by_name, get_complaint_df

st.set_page_config(
    page_title="Improvement Insights",
    page_icon="📊",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Improvement Insights",
    "View common complaint areas and suggested improvement actions for a selected hotel."
)

hotel_name = st.selectbox("Select Hotel", get_hotel_names(), key="insight_hotel")
hotel = get_hotel_by_name(hotel_name)

if hotel:
    st.markdown(f"## {hotel['hotel']}")

    complaint_df = get_complaint_df(hotel)

    c1, c2, c3 = st.columns(3)
    c1.metric("Main Risk", hotel["main_risk"])
    c2.metric("Risk Level", hotel["risk_level"])
    c3.metric("Negative Reviews", f"{hotel['negative_pct']}%")

    st.markdown("### Most Common Complaint Areas")
    st.bar_chart(complaint_df.set_index("Complaint Area")[["Complaint Count"]])

    st.markdown("### Priority Table")
    st.dataframe(complaint_df, use_container_width=True)

    st.markdown("### Suggested Improvement Focus")

    top_issue = complaint_df.iloc[0]

    if top_issue["Priority Level"] == "High":
        st.error(
            f"Highest priority area: {top_issue['Complaint Area']}. "
            f"Suggested action: {top_issue['Suggested Improvement Action']}"
        )
    elif top_issue["Priority Level"] == "Medium":
        st.warning(
            f"Medium priority area: {top_issue['Complaint Area']}. "
            f"Suggested action: {top_issue['Suggested Improvement Action']}"
        )
    else:
        st.success(
            f"Current complaint level is low. Continue monitoring {top_issue['Complaint Area']}."
        )

render_footer()
