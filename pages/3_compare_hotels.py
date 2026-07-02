import html
import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import (
    get_areas,
    get_hotels_by_area,
    get_hotel_by_name,
    recommend_better_hotel,
    risk_badge
)


st.set_page_config(
    page_title="Compare Hotels",
    page_icon="⚖️",
    layout="wide"
)


def load_compare_css():
    st.markdown("""
    <style>
        .compare-intro-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.2rem 1.35rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .compare-intro-title {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.35rem;
        }

        .compare-intro-text {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .picker-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 1rem;
        }

        .picker-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.5rem;
        }

        div[data-baseweb="select"] > div {
            border-radius: 16px !important;
            border: 1px solid #D8CDBE !important;
            background: rgba(255, 255, 255, 0.96) !important;
            min-height: 3rem;
        }

        .recommendation-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 28px;
            padding: 1.2rem 1.35rem;
            box-shadow: var(--shadow-card);
            margin: 1rem 0;
        }

        .recommendation-label {
            color: #9B4325;
            font-size: 0.76rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .recommendation-text {
            color: var(--text-main);
            font-size: 1.15rem;
            font-weight: 850;
            line-height: 1.45;
        }

        .hotel-compare-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .hotel-card-title {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.045em;
            line-height: 1.15;
            margin-bottom: 0.35rem;
        }

        .hotel-card-meta {
            color: #64748B;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 0.85rem;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.45rem 0.78rem;
            font-size: 0.84rem;
            font-weight: 850;
            margin-bottom: 0.85rem;
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

        .quick-stat-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin-bottom: 1rem;
        }

        .quick-stat {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.7rem 0.75rem;
        }

        .quick-stat-label {
            color: #7C6F64;
            font-size: 0.72rem;
            font-weight: 900;
            margin-bottom: 0.22rem;
        }

        .quick-stat-value {
            color: var(--text-main);
            font-size: 1.05rem;
            font-weight: 950;
        }

        .sentiment-row {
            margin-bottom: 0.62rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.84rem;
            font-weight: 850;
            margin-bottom: 0.22rem;
        }

        .bar-track {
            width: 100%;
            height: 8px;
            background: #E8DDD0;
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-positive {
            height: 8px;
            background: #2F855A;
            border-radius: 999px;
        }

        .bar-neutral {
            height: 8px;
            background: #D99A25;
            border-radius: 999px;
        }

        .bar-negative {
            height: 8px;
            background: #C24136;
            border-radius: 999px;
        }

        .compare-info-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.65rem;
            margin-top: 1rem;
        }

        .compare-info-item {
            border-top: 1px solid #EFE3D8;
            padding-top: 0.65rem;
        }

        .compare-info-label {
            color: #7C6F64;
            font-size: 0.73rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.16rem;
        }

        .compare-info-value {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 800;
            line-height: 1.4;
        }

        .comparison-table-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-top: 0.6rem;
        }

        .section-title {
            color: var(--text-main);
            font-size: 1.25rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin: 1.2rem 0 0.55rem 0;
        }

        @media (max-width: 900px) {
            .quick-stat-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def escape(value):
    return html.escape(str(value))


def safe_get(hotel, key, default="Not stated"):
    value = hotel.get(key, default)

    if value is None or value == "":
        return default

    return value


def get_review_count(hotel):
    return hotel.get("review_count", hotel.get("total_reviews", 0))


def risk_class_name(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return "risk-low"

    if risk == "high":
        return "risk-high"

    return "risk-medium"


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


def render_hotel_compare_card(hotel):
    risk_level = safe_get(hotel, "risk_level", "Medium")

    card_html = (
        '<div class="hotel-compare-card">'
        f'<div class="hotel-card-title">{escape(safe_get(hotel, "hotel"))}</div>'
        f'<div class="hotel-card-meta">{escape(safe_get(hotel, "area"))} · {escape(safe_get(hotel, "price_level"))}</div>'
        f'<span class="risk-chip {risk_class_name(risk_level)}">{escape(risk_badge(risk_level))}</span>'

        '<div class="quick-stat-row">'
        '<div class="quick-stat">'
        '<div class="quick-stat-label">Reviews</div>'
        f'<div class="quick-stat-value">{escape(get_review_count(hotel))}</div>'
        '</div>'
        '<div class="quick-stat">'
        '<div class="quick-stat-label">Positive</div>'
        f'<div class="quick-stat-value">{escape(safe_get(hotel, "positive_pct", 0))}%</div>'
        '</div>'
        '<div class="quick-stat">'
        '<div class="quick-stat-label">Negative</div>'
        f'<div class="quick-stat-value">{escape(safe_get(hotel, "negative_pct", 0))}%</div>'
        '</div>'
        '</div>'

        + build_sentiment_bar("Positive", safe_get(hotel, "positive_pct", 0), "bar-positive")
        + build_sentiment_bar("Neutral", safe_get(hotel, "neutral_pct", 0), "bar-neutral")
        + build_sentiment_bar("Negative", safe_get(hotel, "negative_pct", 0), "bar-negative")

        '<div class="compare-info-list">'
        '<div class="compare-info-item">'
        '<div class="compare-info-label">What looks good</div>'
        f'<div class="compare-info-value">{escape(safe_get(hotel, "main_strength"))}</div>'
        '</div>'

        '<div class="compare-info-item">'
        '<div class="compare-info-label">What to check</div>'
        f'<div class="compare-info-value">{escape(safe_get(hotel, "main_risk"))}</div>'
        '</div>'

        '<div class="compare-info-item">'
        '<div class="compare-info-label">Best for</div>'
        f'<div class="compare-info-value">{escape(safe_get(hotel, "best_traveller_type"))}</div>'
        '</div>'

        '<div class="compare-info-item">'
        '<div class="compare-info-label">Suitability score</div>'
        f'<div class="compare-info-value">{escape(safe_get(hotel, "suitability_score", 0))}/100</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def build_comparison_table(hotel_a, hotel_b):
    return pd.DataFrame({
        "Criteria": [
            "Area",
            "Reviews",
            "Positive %",
            "Neutral %",
            "Negative %",
            "What looks good",
            "What to check",
            "Risk Level",
            "Best Traveller Type",
            "Suitability Score",
            "Price Level"
        ],
        safe_get(hotel_a, "hotel"): [
            safe_get(hotel_a, "area"),
            get_review_count(hotel_a),
            f"{safe_get(hotel_a, 'positive_pct', 0)}%",
            f"{safe_get(hotel_a, 'neutral_pct', 0)}%",
            f"{safe_get(hotel_a, 'negative_pct', 0)}%",
            safe_get(hotel_a, "main_strength"),
            safe_get(hotel_a, "main_risk"),
            safe_get(hotel_a, "risk_level"),
            safe_get(hotel_a, "best_traveller_type"),
            safe_get(hotel_a, "suitability_score", 0),
            safe_get(hotel_a, "price_level")
        ],
        safe_get(hotel_b, "hotel"): [
            safe_get(hotel_b, "area"),
            get_review_count(hotel_b),
            f"{safe_get(hotel_b, 'positive_pct', 0)}%",
            f"{safe_get(hotel_b, 'neutral_pct', 0)}%",
            f"{safe_get(hotel_b, 'negative_pct', 0)}%",
            safe_get(hotel_b, "main_strength"),
            safe_get(hotel_b, "main_risk"),
            safe_get(hotel_b, "risk_level"),
            safe_get(hotel_b, "best_traveller_type"),
            safe_get(hotel_b, "suitability_score", 0),
            safe_get(hotel_b, "price_level")
        ]
    })


load_css()
load_compare_css()
render_topbar()

render_page_header(
    "Compare Hotels",
    "Compare two hotels from the same area before making a booking decision."
)

st.markdown(
    '<div class="compare-intro-card">'
    '<div class="compare-intro-title">Choose two hotels to compare</div>'
    '<div class="compare-intro-text">Select an area first, then compare two hotels side by side using review sentiment, booking concern, suitability, and traveller type.</div>'
    '</div>',
    unsafe_allow_html=True
)

areas = get_areas()

if not areas:
    st.warning("No area data is available.")
    render_footer()
    st.stop()

st.markdown('<div class="picker-card"><div class="picker-label">Step 1 · Select area</div>', unsafe_allow_html=True)
selected_area = st.selectbox(
    "Select Area",
    areas,
    key="compare_area",
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

hotels_in_area = get_hotels_by_area(selected_area)
hotel_options = [hotel["hotel"] for hotel in hotels_in_area]

if len(hotel_options) < 2:
    st.warning("This area does not have enough hotels for comparison.")
else:
    st.markdown('<div class="picker-card"><div class="picker-label">Step 2 · Select two hotels</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        hotel_a_name = st.selectbox(
            "Select Hotel A",
            hotel_options,
            key="hotel_a"
        )

    available_hotel_b_options = [hotel for hotel in hotel_options if hotel != hotel_a_name]

    with col2:
        hotel_b_name = st.selectbox(
            "Select Hotel B",
            available_hotel_b_options,
            key="hotel_b"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    hotel_a = get_hotel_by_name(hotel_a_name)
    hotel_b = get_hotel_by_name(hotel_b_name)

    if hotel_a is None or hotel_b is None:
        st.error("Hotel data could not be loaded. Please check your dataset.")
    else:
        recommendation = recommend_better_hotel(hotel_a, hotel_b)

        st.markdown(
            '<div class="recommendation-card">'
            '<div class="recommendation-label">Quick recommendation</div>'
            f'<div class="recommendation-text">{escape(recommendation)}</div>'
            '</div>',
            unsafe_allow_html=True
        )

        compare_col1, compare_col2 = st.columns(2, gap="large")

        with compare_col1:
            render_hotel_compare_card(hotel_a)

        with compare_col2:
            render_hotel_compare_card(hotel_b)

        st.markdown('<div class="section-title">Detailed comparison</div>', unsafe_allow_html=True)

        comparison_df = build_comparison_table(hotel_a, hotel_b)

        st.markdown('<div class="comparison-table-card">', unsafe_allow_html=True)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

render_footer()