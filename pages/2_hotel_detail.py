import html
import streamlit as st
from urllib.parse import quote
from styles import load_css, render_topbar, render_footer
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
        .compact-title-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.2rem 1.35rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.9rem;
        }

        .compact-kicker {
            display: inline-flex;
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            padding: 0.32rem 0.68rem;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.6rem;
        }

        .compact-title {
            font-size: clamp(1.8rem, 4vw, 2.7rem);
            font-weight: 950;
            color: var(--text-main);
            letter-spacing: -0.065em;
            line-height: 1.05;
            margin-bottom: 0.35rem;
        }

        .compact-desc {
            color: #64748B;
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .hotel-picker-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 0.95rem 1rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 0.9rem;
        }

        .hotel-picker-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.55rem;
        }

        .hotel-picker-row {
            display: flex;
            gap: 0.55rem;
            overflow-x: auto;
            padding-bottom: 0.2rem;
        }

        .hotel-picker-row::-webkit-scrollbar {
            height: 7px;
        }

        .hotel-picker-row::-webkit-scrollbar-track {
            background: #F1E8DC;
            border-radius: 999px;
        }

        .hotel-picker-row::-webkit-scrollbar-thumb {
            background: #D8C2AD;
            border-radius: 999px;
        }

        .hotel-option {
            flex: 0 0 auto;
            display: inline-flex;
            align-items: center;
            text-decoration: none !important;
            background: #FFFDF8;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 999px;
            padding: 0.58rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 800;
            box-shadow: 0 6px 16px rgba(74, 55, 40, 0.04);
            transition: all 0.16s ease;
            max-width: 285px;
        }

        .hotel-option:hover {
            background: #FFF4E8;
            border-color: var(--brand);
            transform: translateY(-1px);
        }

        .hotel-option.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.20);
        }

        .hotel-option-name {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .main-summary-card {
            background: rgba(255, 255, 255, 0.93);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.95rem;
        }

        .hotel-title {
            color: var(--text-main);
            font-size: 1.65rem;
            font-weight: 950;
            letter-spacing: -0.055em;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }

        .hotel-meta {
            color: #64748B;
            font-size: 0.92rem;
            line-height: 1.5;
            margin-bottom: 0.8rem;
        }

        .quick-note {
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
            border-radius: 18px;
            padding: 0.85rem 0.9rem;
            color: #334155;
            font-size: 0.92rem;
            line-height: 1.55;
            margin-bottom: 0.9rem;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.55rem;
        }

        .stat-item {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.75rem 0.8rem;
        }

        .stat-label {
            color: #7C6F64;
            font-size: 0.75rem;
            font-weight: 850;
            margin-bottom: 0.25rem;
        }

        .stat-value {
            color: var(--text-main);
            font-size: 1.2rem;
            font-weight: 950;
            letter-spacing: -0.03em;
        }

        .side-card {
            background: rgba(255, 255, 255, 0.93);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.95rem;
        }

        .side-title {
            color: var(--text-main);
            font-size: 1.15rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.75rem;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.48rem 0.82rem;
            font-size: 0.86rem;
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

        .insight-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.55rem;
        }

        .insight-item {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.72rem 0.8rem;
        }

        .insight-label {
            color: #7C6F64;
            font-size: 0.75rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.2rem;
        }

        .insight-value {
            color: #172033;
            font-size: 0.92rem;
            font-weight: 750;
            line-height: 1.4;
        }

        .sentiment-box {
            background: rgba(255, 255, 255, 0.93);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.95rem;
        }

        .sentiment-title {
            color: var(--text-main);
            font-size: 1.05rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.75rem;
        }

        .sentiment-row {
            margin-bottom: 0.68rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.86rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
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

        .detail-tabs-note {
            background: rgba(255, 255, 255, 0.82);
            border: 1px dashed #D8CDBE;
            border-radius: 18px;
            padding: 0.75rem 0.85rem;
            color: #7C6F64;
            font-size: 0.88rem;
            line-height: 1.45;
            margin-bottom: 0.75rem;
        }

        .review-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.85rem;
            margin-bottom: 0.65rem;
            box-shadow: 0 6px 14px rgba(74, 55, 40, 0.035);
        }

        .review-sentiment {
            font-size: 0.8rem;
            font-weight: 900;
            margin-bottom: 0.25rem;
        }

        .review-text {
            color: #334155;
            font-size: 0.9rem;
            line-height: 1.5;
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

        .empty-note {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
            border-radius: 18px;
            padding: 0.9rem;
            line-height: 1.5;
        }

        @media (max-width: 900px) {
            .stat-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
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


def get_selected_hotel_from_url(hotel_names, default_hotel):
    selected_hotel = st.query_params.get("hotel", default_hotel)

    if isinstance(selected_hotel, list):
        selected_hotel = selected_hotel[0]

    if selected_hotel not in hotel_names:
        selected_hotel = default_hotel

    return selected_hotel


def render_hotel_picker(hotel_names, selected_hotel):
    hotel_options_html = ""

    for hotel in hotel_names:
        active_class = "active" if hotel == selected_hotel else ""
        hotel_url = quote(hotel, safe="")

        hotel_options_html += (
            f'<a class="hotel-option {active_class}" href="?hotel={hotel_url}" target="_self">'
            f'<span class="hotel-option-name">{escape(hotel)}</span>'
            f'</a>'
        )

    picker_html = (
        '<div class="hotel-picker-card">'
        '<div class="hotel-picker-label">Choose hotel</div>'
        '<div class="hotel-picker-row">'
        f'{hotel_options_html}'
        '</div>'
        '</div>'
    )

    st.markdown(picker_html, unsafe_allow_html=True)


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
        '<div class="sentiment-title">Guest review feeling</div>'
        + build_sentiment_bar("Positive", hotel.get("positive_pct", 0), "bar-positive")
        + build_sentiment_bar("Neutral", hotel.get("neutral_pct", 0), "bar-neutral")
        + build_sentiment_bar("Negative", hotel.get("negative_pct", 0), "bar-negative")
        + '</div>'
    )

    st.markdown(sentiment_html, unsafe_allow_html=True)


def render_main_summary(hotel, hotel_name):
    summary_html = (
        '<div class="main-summary-card">'
        f'<div class="hotel-title">{escape(hotel.get("hotel", hotel_name))}</div>'
        f'<div class="hotel-meta">{escape(hotel.get("area", ""))} · {escape(hotel.get("hotel_address", "Address not stated"))}</div>'
        f'<div class="quick-note">{escape(hotel.get("description", ""))}</div>'
        '<div class="stat-grid">'
        '<div class="stat-item">'
        '<div class="stat-label">Reviews</div>'
        f'<div class="stat-value">{escape(hotel.get("review_count", 0))}</div>'
        '</div>'
        '<div class="stat-item">'
        '<div class="stat-label">Positive</div>'
        f'<div class="stat-value">{escape(hotel.get("positive_pct", 0))}%</div>'
        '</div>'
        '<div class="stat-item">'
        '<div class="stat-label">Neutral</div>'
        f'<div class="stat-value">{escape(hotel.get("neutral_pct", 0))}%</div>'
        '</div>'
        '<div class="stat-item">'
        '<div class="stat-label">Negative</div>'
        f'<div class="stat-value">{escape(hotel.get("negative_pct", 0))}%</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(summary_html, unsafe_allow_html=True)


def render_booking_snapshot(hotel):
    risk_level = hotel.get("risk_level", "Medium")

    snapshot_html = (
        '<div class="side-card">'
        '<div class="side-title">Booking snapshot</div>'
        f'<span class="risk-chip {risk_class_name(risk_level)}">{escape(risk_badge(risk_level))}</span>'
        '<div class="insight-grid">'
        '<div class="insight-item">'
        '<div class="insight-label">Main strength</div>'
        f'<div class="insight-value">{escape(hotel.get("main_strength", "Not clearly stated"))}</div>'
        '</div>'
        '<div class="insight-item">'
        '<div class="insight-label">Main thing to check</div>'
        f'<div class="insight-value">{escape(hotel.get("main_risk", "No major repeated concern"))}</div>'
        '</div>'
        '<div class="insight-item">'
        '<div class="insight-label">Best for</div>'
        f'<div class="insight-value">{escape(hotel.get("best_traveller_type", "General travellers"))}</div>'
        '</div>'
        '<div class="insight-item">'
        '<div class="insight-label">Suitability score</div>'
        f'<div class="insight-value">{escape(hotel.get("suitability_score", 0))}/100</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(snapshot_html, unsafe_allow_html=True)


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

    review_html = (
        '<div class="review-card">'
        f'<div class="review-sentiment {sentiment_class}">{escape(label)}</div>'
        f'<div class="review-text">{escape(review)}</div>'
        '</div>'
    )

    st.markdown(review_html, unsafe_allow_html=True)


def get_review_text_column(reviews_df):
    for column in ["Original_Review", "Translated_Review", "Review", "BERT_Text"]:
        if column in reviews_df.columns:
            return column

    return None


load_css()
load_hotel_detail_css()
render_topbar()

st.markdown(
    '<div class="compact-title-card">'
    '<div class="compact-kicker">Hotel review profile</div>'
    '<div class="compact-title">Hotel Detail</div>'
    '<div class="compact-desc">View one hotel\'s review summary, booking concern, strengths, improvement areas, and sample reviews.</div>'
    '</div>',
    unsafe_allow_html=True
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

hotel_name = get_selected_hotel_from_url(hotel_names, default_hotel)
st.session_state.selected_hotel = hotel_name

render_hotel_picker(hotel_names, hotel_name)

hotel = get_hotel_by_name(hotel_name)

if hotel:
    left_col, right_col = st.columns([1.2, 0.8], gap="large")

    with left_col:
        render_main_summary(hotel, hotel_name)
        render_sentiment_distribution(hotel)

    with right_col:
        render_booking_snapshot(hotel)

    tab1, tab2 = st.tabs(["Common improvement areas", "Sample reviews"])

    with tab1:
        st.markdown(
            '<div class="detail-tabs-note">These are the most repeated improvement areas found from the hotel reviews.</div>',
            unsafe_allow_html=True
        )

        complaint_df = get_complaint_df(hotel)

        if complaint_df.empty:
            st.markdown(
                '<div class="empty-note">No repeated complaint area was found for this hotel.</div>',
                unsafe_allow_html=True
            )
        else:
            st.dataframe(complaint_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown(
            '<div class="detail-tabs-note">Sample reviews are shown for quick understanding. Travellers should compare more than one review.</div>',
            unsafe_allow_html=True
        )

        reviews_df = get_hotel_reviews(hotel_name, limit=5)
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