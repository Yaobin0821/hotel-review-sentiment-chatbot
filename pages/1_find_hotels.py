import html
import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import get_areas, get_hotels_by_area


st.set_page_config(
    page_title="Find Hotels",
    page_icon="🏠",
    layout="wide"
)


def load_find_hotels_css():
    st.markdown("""
    <style>
        .find-intro-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.35rem 1.45rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1.2rem;
        }

        .find-intro-title {
            font-size: 1.35rem;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -0.04em;
            margin-bottom: 0.4rem;
        }

        .find-intro-text {
            color: #64748B;
            font-size: 0.98rem;
            line-height: 1.6;
            max-width: 820px;
        }

        .area-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 8px 22px rgba(74, 55, 40, 0.05);
            margin-bottom: 0.75rem;
        }

        .area-label {
            font-size: 0.82rem;
            font-weight: 850;
            color: #7C6F64;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.25rem;
        }

        .area-title {
            font-size: 1.1rem;
            font-weight: 850;
            color: var(--text-main);
        }

        div[data-testid="stSelectbox"] label {
            color: var(--text-main);
            font-weight: 800;
        }

        div[data-baseweb="select"] > div {
            border-radius: 16px !important;
            border: 1px solid #D8CDBE !important;
            background: rgba(255, 255, 255, 0.95) !important;
            min-height: 3rem;
        }

        .section-heading-row {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
            margin-top: 1.4rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .section-heading {
            font-size: 1.55rem;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -0.045em;
            margin-bottom: 0.2rem;
        }

        .section-sub {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .area-pill {
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            padding: 0.45rem 0.78rem;
            font-size: 0.84rem;
            font-weight: 850;
        }

        .hotel-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            min-height: 620px;
            margin-bottom: 0.75rem;
            box-sizing: border-box;
            transition: transform 0.16s ease, box-shadow 0.16s ease;
        }

        .hotel-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 38px rgba(74, 55, 40, 0.12);
        }

        .hotel-top {
            display: flex;
            justify-content: space-between;
            gap: 0.8rem;
            align-items: flex-start;
            margin-bottom: 0.85rem;
        }

        .hotel-name {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.045em;
            line-height: 1.12;
            margin-bottom: 0.35rem;
        }

        .hotel-meta {
            color: #64748B;
            font-size: 0.9rem;
            font-weight: 650;
        }

        .hotel-icon {
            width: 46px;
            height: 46px;
            min-width: 46px;
            border-radius: 17px;
            background: #FFF4E8;
            border: 1px solid #F2CBAE;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
        }

        .recommendation-box {
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
            border-radius: 18px;
            padding: 0.85rem 0.9rem;
            margin-bottom: 0.95rem;
        }

        .recommendation-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.25rem;
        }

        .recommendation-text {
            color: var(--text-main);
            font-size: 0.95rem;
            font-weight: 750;
            line-height: 1.45;
        }

        .sentiment-title {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 850;
            margin-bottom: 0.65rem;
        }

        .sentiment-row {
            margin-bottom: 0.72rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.88rem;
            font-weight: 750;
            margin-bottom: 0.28rem;
        }

        .bar-track {
            width: 100%;
            height: 9px;
            background: #E8DDD0;
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-positive {
            height: 9px;
            background: #2F855A;
            border-radius: 999px;
        }

        .bar-neutral {
            height: 9px;
            background: #D99A25;
            border-radius: 999px;
        }

        .bar-negative {
            height: 9px;
            background: #C24136;
            border-radius: 999px;
        }

        .hotel-info-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.65rem;
            margin-top: 1rem;
        }

        .info-item {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.75rem 0.85rem;
        }

        .info-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.2rem;
        }

        .info-value {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 750;
            line-height: 1.4;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.74rem;
            font-size: 0.84rem;
            font-weight: 850;
            margin-top: 0.9rem;
        }

        .risk-low {
            background: #EAF7F0;
            color: #216E46;
            border: 1px solid #BFE3CF;
        }

        .risk-medium {
            background: #FFF4D6;
            color: #8A5A12;
            border: 1px solid #E6C879;
        }

        .risk-high {
            background: #FFF0EE;
            color: #A33A2F;
            border: 1px solid #F4C7BF;
        }

        .button-space {
            margin-top: 0.2rem;
            margin-bottom: 1rem;
        }

        div[data-testid="stButton"] button {
            width: 100%;
            border-radius: 16px !important;
            height: 3rem !important;
            font-weight: 850 !important;
        }

        .empty-hotels {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.3rem;
            color: #64748B;
            box-shadow: var(--shadow-card);
        }

        @media (max-width: 900px) {
            .hotel-card {
                min-height: auto;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def escape(value):
    return html.escape(str(value))


def risk_class_name(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return "risk-low"

    if risk == "high":
        return "risk-high"

    return "risk-medium"


def risk_label(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return "Low booking concern"

    if risk == "high":
        return "High booking concern"

    return "Some booking concern"


def build_hotel_recommendation(hotel):
    positive = hotel["positive_pct"]
    negative = hotel["negative_pct"]
    main_strength = hotel["main_strength"]
    main_risk = hotel["main_risk"]

    if positive >= 65 and negative <= 15:
        return f"Good option to consider, especially for travellers who care about {main_strength.lower()}."

    if negative >= 25:
        return f"Compare carefully because guests often mention {main_risk.lower()} as a concern."

    return f"Worth considering, but check whether {main_risk.lower()} matters to your trip."


def build_sentiment_bar(label, value, css_class):
    return (
        '<div class="sentiment-row">'
        '<div class="sentiment-line">'
        f'<span>{escape(label)}</span>'
        f'<span>{escape(value)}%</span>'
        '</div>'
        '<div class="bar-track">'
        f'<div class="{css_class}" style="width: {escape(value)}%;"></div>'
        '</div>'
        '</div>'
    )


def build_hotel_card_html(hotel):
    hotel_name = escape(hotel["hotel"])
    area = escape(hotel["area"])
    price = escape(hotel["price_level"])
    recommendation = escape(build_hotel_recommendation(hotel))
    main_strength = escape(hotel["main_strength"])
    main_risk = escape(hotel["main_risk"])
    best_traveller_type = escape(hotel["best_traveller_type"])
    risk_class = risk_class_name(hotel["risk_level"])
    risk_text = escape(risk_label(hotel["risk_level"]))

    positive = hotel["positive_pct"]
    neutral = hotel["neutral_pct"]
    negative = hotel["negative_pct"]

    sentiment_html = (
        build_sentiment_bar("Positive", positive, "bar-positive")
        + build_sentiment_bar("Neutral", neutral, "bar-neutral")
        + build_sentiment_bar("Negative", negative, "bar-negative")
    )

    card_html = (
        '<div class="hotel-card">'
        '<div class="hotel-top">'
        '<div>'
        f'<div class="hotel-name">{hotel_name}</div>'
        f'<div class="hotel-meta">{area} · {price}</div>'
        '</div>'
        '<div class="hotel-icon">🏨</div>'
        '</div>'

        '<div class="recommendation-box">'
        '<div class="recommendation-label">Quick booking note</div>'
        f'<div class="recommendation-text">{recommendation}</div>'
        '</div>'

        '<div class="sentiment-title">Guest review feeling</div>'
        f'{sentiment_html}'

        '<div class="hotel-info-grid">'
        '<div class="info-item">'
        '<div class="info-label">Main strength</div>'
        f'<div class="info-value">{main_strength}</div>'
        '</div>'

        '<div class="info-item">'
        '<div class="info-label">Main thing to check</div>'
        f'<div class="info-value">{main_risk}</div>'
        '</div>'

        '<div class="info-item">'
        '<div class="info-label">Best for</div>'
        f'<div class="info-value">{best_traveller_type}</div>'
        '</div>'
        '</div>'

        f'<span class="risk-chip {risk_class}">{risk_text}</span>'
        '</div>'
    )

    return card_html


def render_hotel_card(hotel):
    st.markdown(build_hotel_card_html(hotel), unsafe_allow_html=True)


load_css()
load_find_hotels_css()
render_topbar()

render_page_header(
    "Find Hotels",
    "Browse hotels by area and quickly understand each hotel's strengths, concerns, and traveller suitability."
)

st.markdown(
    """
    <div class="find-intro-card">
        <div class="find-intro-title">Choose an area first</div>
        <div class="find-intro-text">
            Select where you plan to stay. StayWise KL will show hotels in that area with a simple review-based summary,
            including what guests like, what to check, and who the hotel may suit best.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="area-card">
        <div class="area-label">Area filter</div>
        <div class="area-title">Where are you planning to stay?</div>
    </div>
    """,
    unsafe_allow_html=True
)

selected_area = st.selectbox(
    "Select Area",
    get_areas(),
    label_visibility="collapsed"
)

hotels = get_hotels_by_area(selected_area)

st.markdown(
    f"""
    <div class="section-heading-row">
        <div>
            <div class="section-heading">Recommended hotels</div>
            <div class="section-sub">Review-based hotel options in the selected area.</div>
        </div>
        <div class="area-pill">{escape(selected_area)}</div>
    </div>
    """,
    unsafe_allow_html=True
)

if not hotels:
    st.markdown(
        """
        <div class="empty-hotels">
            No hotels are available for this area yet.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    cols = st.columns(2)

    for index, hotel in enumerate(hotels):
        with cols[index % 2]:
            render_hotel_card(hotel)

            st.markdown('<div class="button-space"></div>', unsafe_allow_html=True)

            if st.button("View Details", key=f"view_{hotel['hotel']}"):
                st.session_state.selected_hotel = hotel["hotel"]
                st.switch_page("pages/2_hotel_detail.py")

render_footer()