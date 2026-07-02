import html
import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import (
    get_hotel_names,
    get_hotel_by_name,
    get_complaint_df,
    get_hotel_reviews,
    risk_badge
)


st.set_page_config(
    page_title="Hotel Detail",
    page_icon="🏨",
    layout="wide"
)


def load_hotel_detail_css():
    st.markdown("""
    <style>
        .detail-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .hotel-title {
            font-size: 2rem;
            font-weight: 950;
            color: var(--text-main);
            letter-spacing: -0.055em;
            line-height: 1.1;
            margin-bottom: 0.45rem;
        }

        .hotel-meta {
            color: #64748B;
            font-size: 0.98rem;
            line-height: 1.55;
            margin-bottom: 0.9rem;
        }

        .quick-note {
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
            border-radius: 20px;
            padding: 1rem 1.05rem;
            color: var(--text-main);
            font-size: 0.98rem;
            line-height: 1.6;
            font-weight: 650;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 1rem;
        }

        .metric-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.03em;
        }

        .metric-help {
            color: #64748B;
            font-size: 0.82rem;
            margin-top: 0.28rem;
            line-height: 1.35;
        }

        .sentiment-box {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .section-title-custom {
            font-size: 1.2rem;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -0.04em;
            margin-bottom: 0.75rem;
        }

        .sentiment-row {
            margin-bottom: 0.8rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.9rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }

        .bar-track {
            width: 100%;
            height: 10px;
            background: #E8DDD0;
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-positive {
            height: 10px;
            background: #2F855A;
            border-radius: 999px;
        }

        .bar-neutral {
            height: 10px;
            background: #D99A25;
            border-radius: 999px;
        }

        .bar-negative {
            height: 10px;
            background: #C24136;
            border-radius: 999px;
        }

        .info-box {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.15rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 1rem;
            min-height: 175px;
        }

        .info-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.35rem;
        }

        .info-title {
            color: var(--text-main);
            font-size: 1.1rem;
            font-weight: 900;
            margin-bottom: 0.45rem;
        }

        .info-text {
            color: #334155;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.48rem 0.82rem;
            font-size: 0.86rem;
            font-weight: 850;
            margin-top: 0.5rem;
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

        .review-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 6px 16px rgba(74, 55, 40, 0.04);
        }

        .review-sentiment {
            font-size: 0.82rem;
            font-weight: 900;
            margin-bottom: 0.35rem;
        }

        .review-text {
            color: #334155;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .positive-text {
            color: #216E46;
        }

        .neutral-text {
            color: #8A5A12;
        }

        .negative-text {
            color: #A33A2F;
        }

        div[data-baseweb="select"] > div {
            border-radius: 16px !important;
            border: 1px solid #D8CDBE !important;
            background: rgba(255, 255, 255, 0.95) !important;
            min-height: 3rem;
        }

        .empty-note {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
            border-radius: 18px;
            padding: 1rem;
            line-height: 1.5;
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


def render_metric_card(label, value, help_text):
    html_block = (
        '<div class="metric-card">'
        f'<div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(value)}</div>'
        f'<div class="metric-help">{escape(help_text)}</div>'
        '</div>'
    )

    st.markdown(html_block, unsafe_allow_html=True)


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


def render_sentiment_distribution(hotel):
    sentiment_html = (
        '<div class="sentiment-box">'
        '<div class="section-title-custom">Guest review feeling</div>'
        + build_sentiment_bar("Positive", hotel.get("positive_pct", 0), "bar-positive")
        + build_sentiment_bar("Neutral", hotel.get("neutral_pct", 0), "bar-neutral")
        + build_sentiment_bar("Negative", hotel.get("negative_pct", 0), "bar-negative")
        + '</div>'
    )

    st.markdown(sentiment_html, unsafe_allow_html=True)


def render_info_box(label, title, text):
    html_block = (
        '<div class="info-box">'
        f'<div class="info-label">{escape(label)}</div>'
        f'<div class="info-title">{escape(title)}</div>'
        f'<div class="info-text">{escape(text)}</div>'
        '</div>'
    )

    st.markdown(html_block, unsafe_allow_html=True)


def render_review_card(sentiment, review):
    sentiment_lower = str(sentiment).lower()

    if sentiment_lower == "positive":
        sentiment_class = "positive-text"
        label = "🟢 Positive review"
    elif sentiment_lower == "negative":
        sentiment_class = "negative-text"
        label = "🔴 Negative review"
    else:
        sentiment_class = "neutral-text"
        label = "🟡 Neutral review"

    html_block = (
        '<div class="review-card">'
        f'<div class="review-sentiment {sentiment_class}">{escape(label)}</div>'
        f'<div class="review-text">{escape(review)}</div>'
        '</div>'
    )

    st.markdown(html_block, unsafe_allow_html=True)


def get_review_text_column(reviews_df):
    for column in ["Original_Review", "Translated_Review", "Review", "BERT_Text"]:
        if column in reviews_df.columns:
            return column

    return None


load_css()
load_hotel_detail_css()
render_topbar()

render_page_header(
    "Hotel Detail",
    "View a clearer summary of one hotel's review profile, strengths, concerns, and sample reviews."
)

hotel_names = get_hotel_names()

if not hotel_names:
    st.markdown(
        '<div class="empty-note">No hotel data is available. Please check your dataset file.</div>',
        unsafe_allow_html=True
    )
    render_footer()
    st.stop()

default_hotel = st.session_state.get("selected_hotel", hotel_names[0])

if default_hotel not in hotel_names:
    default_hotel = hotel_names[0]

hotel_name = st.selectbox(
    "Select Hotel",
    hotel_names,
    index=hotel_names.index(default_hotel)
)

hotel = get_hotel_by_name(hotel_name)

if hotel:
    st.markdown(
        (
            '<div class="detail-card">'
            f'<div class="hotel-title">{escape(hotel.get("hotel", hotel_name))}</div>'
            f'<div class="hotel-meta">{escape(hotel.get("area", ""))} · {escape(hotel.get("hotel_address", "Address not stated"))}</div>'
            f'<div class="quick-note">{escape(hotel.get("description", ""))}</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card(
            "Total Reviews",
            hotel.get("review_count", 0),
            "Reviews available in the dataset."
        )

    with c2:
        render_metric_card(
            "Positive",
            f'{hotel.get("positive_pct", 0)}%',
            "Positive review share."
        )

    with c3:
        render_metric_card(
            "Neutral",
            f'{hotel.get("neutral_pct", 0)}%',
            "Neutral review share."
        )

    with c4:
        render_metric_card(
            "Negative",
            f'{hotel.get("negative_pct", 0)}%',
            "Negative review share."
        )

    render_sentiment_distribution(hotel)

    left_col, right_col = st.columns(2)

    with left_col:
        render_info_box(
            "Main strength",
            hotel.get("main_strength", "Not clearly stated"),
            "This is the most common positive area found from guest reviews."
        )

        render_info_box(
            "Main thing to check",
            hotel.get("main_risk", "No major repeated concern"),
            "Travellers should pay attention to this area before booking."
        )

    with right_col:
        risk_level = hotel.get("risk_level", "Medium")
        risk_html = (
            '<div class="info-box">'
            '<div class="info-label">Booking concern</div>'
            f'<div class="info-title">{escape(risk_badge(risk_level))}</div>'
            f'<span class="risk-chip {risk_class_name(risk_level)}">{escape(risk_badge(risk_level))}</span>'
            '<div class="info-text" style="margin-top:0.8rem;">This shows how much caution the hotel reviews suggest.</div>'
            '</div>'
        )
        st.markdown(risk_html, unsafe_allow_html=True)

        render_info_box(
            "Best for",
            hotel.get("best_traveller_type", "General travellers"),
            f'Suitability score: {hotel.get("suitability_score", 0)}/100'
        )

    st.markdown("### Common improvement areas")

    complaint_df = get_complaint_df(hotel)

    if complaint_df.empty:
        st.markdown(
            '<div class="empty-note">No repeated complaint area was found for this hotel.</div>',
            unsafe_allow_html=True
        )
    else:
        st.dataframe(complaint_df, use_container_width=True, hide_index=True)

    st.markdown("### Sample reviews")

    reviews_df = get_hotel_reviews(hotel_name, limit=8)
    review_text_column = get_review_text_column(reviews_df)

    if reviews_df.empty or review_text_column is None:
        st.markdown(
            '<div class="empty-note">No sample review is available for this hotel.</div>',
            unsafe_allow_html=True
        )
    else:
        for _, row in reviews_df.iterrows():
            render_review_card(
                sentiment=row.get("sentiment", "neutral"),
                review=row.get(review_text_column, "")
            )

render_footer()