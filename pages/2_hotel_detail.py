import streamlit as st
import html
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import (
    get_hotel_names,
    get_hotel_by_name,
    get_sentiment_df,
    sentiment_label_style,
    risk_badge
)

st.set_page_config(
    page_title="Hotel Detail",
    page_icon="🏨",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Hotel Detail",
    "View full sentiment summary, risk alerts, traveller suitability, and review examples."
)

default_hotel = st.session_state.get("selected_hotel", get_hotel_names()[0])

hotel_name = st.selectbox(
    "Select Hotel",
    get_hotel_names(),
    index=get_hotel_names().index(default_hotel) if default_hotel in get_hotel_names() else 0
)

hotel = get_hotel_by_name(hotel_name)

if hotel:
    st.markdown(f"## {hotel['hotel']}")
    st.write(hotel["description"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reviews", hotel["total_reviews"])
    c2.metric("Positive", f"{hotel['positive_pct']}%")
    c3.metric("Neutral", f"{hotel['neutral_pct']}%")
    c4.metric("Negative", f"{hotel['negative_pct']}%")

    st.markdown("### Sentiment Distribution")
    sentiment_df = get_sentiment_df(hotel)
    st.bar_chart(sentiment_df.set_index("Sentiment"))

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### Risk Alerts")

        for alert in hotel["risk_alerts"]:
            st.markdown(f"""
            <div class="warning-box">
                ⚠️ {alert}
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("### Traveller Suitability")

        st.markdown(f"""
        <div class="good-box">
            <b>Best for:</b> {hotel["best_traveller_type"]}<br>
            <b>Suitability Score:</b> {hotel["suitability_score"]}/100<br>
            <b>Risk Level:</b> {risk_badge(hotel["risk_level"])}
        </div>
        """, unsafe_allow_html=True)

        for item in hotel["suitability"]:
            st.markdown(f'<span class="tag">{item}</span>', unsafe_allow_html=True)

    st.markdown("### Review List")

    for sentiment, review in hotel["reviews"]:
        if sentiment == "Positive":
            box_class = "good-box"
        elif sentiment == "Negative":
            box_class = "bad-box"
        else:
            box_class = "warning-box"

        st.markdown(f"""
        <div class="{box_class}">
            <b>{sentiment_label_style(sentiment)}</b><br>
            {html.escape(review)}
        </div>
        """, unsafe_allow_html=True)

render_footer()
