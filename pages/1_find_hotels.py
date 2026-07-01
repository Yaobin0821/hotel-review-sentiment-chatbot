import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import get_areas, get_hotels_by_area, risk_css_class, risk_badge

st.set_page_config(
    page_title="Find Hotels",
    page_icon="🏠",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Home / Find Hotels",
    "Browse hotels by area and quickly understand each hotel's review-based strengths and risks."
)

st.subheader("Find Hotels by Area")
st.write("Select an area to discover hotels with sentiment summary, main strength, main risk, and best traveller type.")

selected_area = st.selectbox("Select Area", get_areas())

hotels = get_hotels_by_area(selected_area)

st.markdown("### Recommended Hotels in This Area")

cols = st.columns(2)

for index, hotel in enumerate(hotels):
    with cols[index % 2]:
        risk_class = risk_css_class(hotel["risk_level"])

        st.markdown(f"""
        <div class="hotel-card">
            <h3>{hotel["hotel"]}</h3>
            <p class="small-text">{hotel["area"]} • {hotel["price_level"]}</p>
            <p><b>Sentiment Summary</b></p>
            <p>🟢 Positive: {hotel["positive_pct"]}%<br>
            🟡 Neutral: {hotel["neutral_pct"]}%<br>
            🔴 Negative: {hotel["negative_pct"]}%</p>
            <p><b>Main Strength:</b> {hotel["main_strength"]}</p>
            <p><b>Main Risk:</b> {hotel["main_risk"]}</p>
            <p><b>Best Traveller Type:</b><br>{hotel["best_traveller_type"]}</p>
            <p><span class="{risk_class}">{risk_badge(hotel["risk_level"])}</span></p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Details", key=f"view_{hotel['hotel']}"):
            st.session_state.selected_hotel = hotel["hotel"]
            st.switch_page("pages/2_hotel_detail.py")

render_footer()
