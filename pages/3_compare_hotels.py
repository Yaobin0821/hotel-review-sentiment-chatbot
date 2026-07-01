import streamlit as st
import pandas as pd
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import get_areas, get_hotel_names, get_hotel_by_name, recommend_better_hotel

st.set_page_config(
    page_title="Compare Hotels",
    page_icon="⚖️",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Compare Hotels",
    "Compare two hotels from the same area before making a booking decision."
)

selected_area = st.selectbox("Select Area", get_areas(), key="compare_area")
hotel_options = get_hotel_names(selected_area)

if len(hotel_options) < 2:
    st.warning("This area does not have enough hotels for comparison.")
else:
    col1, col2 = st.columns(2)

    with col1:
        hotel_a_name = st.selectbox("Select Hotel A", hotel_options, key="hotel_a")

    with col2:
        hotel_b_name = st.selectbox("Select Hotel B", hotel_options, key="hotel_b")

    hotel_a = get_hotel_by_name(hotel_a_name)
    hotel_b = get_hotel_by_name(hotel_b_name)

    if hotel_a_name == hotel_b_name:
        st.warning("Please select two different hotels.")
    else:
        comparison_df = pd.DataFrame({
            "Criteria": [
                "Area",
                "Total Reviews",
                "Positive %",
                "Neutral %",
                "Negative %",
                "Main Strength",
                "Main Risk",
                "Risk Level",
                "Best Traveller Type",
                "Suitability Score",
                "Price Level"
            ],
            hotel_a["hotel"]: [
                hotel_a["area"],
                hotel_a["total_reviews"],
                f"{hotel_a['positive_pct']}%",
                f"{hotel_a['neutral_pct']}%",
                f"{hotel_a['negative_pct']}%",
                hotel_a["main_strength"],
                hotel_a["main_risk"],
                hotel_a["risk_level"],
                hotel_a["best_traveller_type"],
                hotel_a["suitability_score"],
                hotel_a["price_level"]
            ],
            hotel_b["hotel"]: [
                hotel_b["area"],
                hotel_b["total_reviews"],
                f"{hotel_b['positive_pct']}%",
                f"{hotel_b['neutral_pct']}%",
                f"{hotel_b['negative_pct']}%",
                hotel_b["main_strength"],
                hotel_b["main_risk"],
                hotel_b["risk_level"],
                hotel_b["best_traveller_type"],
                hotel_b["suitability_score"],
                hotel_b["price_level"]
            ]
        })

        st.markdown("### Comparison Table")
        st.dataframe(comparison_df, use_container_width=True)

        st.markdown("### Sentiment Comparison")
        chart_df = pd.DataFrame({
            "Hotel": [hotel_a["hotel"], hotel_b["hotel"]],
            "Positive": [hotel_a["positive_pct"], hotel_b["positive_pct"]],
            "Neutral": [hotel_a["neutral_pct"], hotel_b["neutral_pct"]],
            "Negative": [hotel_a["negative_pct"], hotel_b["negative_pct"]]
        })
        st.bar_chart(chart_df.set_index("Hotel"))

        st.markdown("### Recommendation")
        recommendation = recommend_better_hotel(hotel_a, hotel_b)
        st.success(recommendation)

render_footer()
