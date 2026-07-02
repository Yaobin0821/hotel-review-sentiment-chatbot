import html
import streamlit as st
from urllib.parse import quote
from styles import load_css, render_topbar, render_footer
from utils import (
    get_areas,
    get_hotels_by_area,
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
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem 1.4rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.9rem;
        }

        .compact-kicker {
            display: inline-flex;
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            padding: 0.34rem 0.72rem;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.65rem;
        }

        .compact-title {
            font-size: clamp(1.9rem, 4vw, 2.8rem);
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

        .picker-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 0.95rem 1rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 0.9rem;
        }

        .picker-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.55rem;
        }

        .area-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.6rem;
        }

        .area-option {
            display: block;
            text-decoration: none !important;
            background: #FFFDF8;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.75rem 0.85rem;
            box-shadow: 0 6px 16px rgba(74, 55, 40, 0.04);
            transition: all 0.16s ease;
        }

        .area-option:hover {
            background: #FFF4E8;
            border-color: var(--brand);
            transform: translateY(-1px);
        }

        .area-option.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.20);
        }

        .area-option-name {
            font-size: 0.92rem;
            font-weight: 900;
            margin-bottom: 0.18rem;
        }

        .area-option-note {
            font-size: 0.78rem;
            opacity: 0.78;
            font-weight: 650;
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
            flex-direction: column;
            justify-content: center;
            text-decoration: none !important;
            background: #FFFDF8;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.65rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 800;
            box-shadow: 0 6px 16px rgba(74, 55, 40, 0.04);
            transition: all 0.16s ease;
            width: 260px;
            min-height: 70px;
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
            margin-bottom: 0.2rem;
        }

        .hotel-option-meta {
            font-size: 0.76rem;
            opacity: 0.78;
            font-weight: 650;
        }

        .overview-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.95rem;
            min-height: 530px;
            box-sizing: border-box;
        }

        .hotel-title {
            color: var(--text-main);
            font-size: clamp(1.45rem, 3vw, 1.95rem);
            font-weight: 950;
            letter-spacing: -0.055em;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }

        .hotel-meta {
            color: #64748B;
            font-size: 0.92rem;
            line-height: 1.5;
            margin-bottom: 0.85rem;
        }

        .booking-note {
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
            border-radius: 20px;
            padding: 0.9rem 1rem;
            color: #334155;
            font-size: 0.94rem;
            line-height: 1.55;
            margin-bottom: 1rem;
        }

        .quick-line {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-bottom: 1rem;
        }

        .quick-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            color: #3F342B;
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            font-size: 0.84rem;
            font-weight: 850;
        }

        .section-small-title {
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 950;
            letter-spacing: -0.035em;
            margin-bottom: 0.7rem;
        }

        .sentiment-row {
            margin-bottom: 0.68rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.86rem;
            font-weight: 850;
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

        .advice-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.95rem;
            min-height: 530px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }

        .advice-title {
            color: var(--text-main);
            font-size: 1.2rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.8rem;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.48rem 0.82rem;
            font-size: 0.86rem;
            font-weight: 850;
            margin-bottom: 0.95rem;
            width: fit-content;
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

        .advice-list {
            display: grid;
            grid-template-columns: 1fr;
            gap: 0.9rem;
        }

        .advice-item {
            padding-bottom: 0.7rem;
            border-bottom: 1px solid #EFE3D8;
        }

        .advice-item:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .advice-label {
            color: #7C6F64;
            font-size: 0.73rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.18rem;
        }

        .advice-value {
            color: var(--text-main);
            font-size: 0.98rem;
            font-weight: 850;
            line-height: 1.4;
        }

        .custom-tab-row {
            display: flex;
            gap: 0.45rem;
            border-bottom: 1px solid #D8CDBE;
            margin-top: 0.35rem;
            margin-bottom: 1rem;
        }

        .custom-tab {
            text-decoration: none !important;
            color: #64748B !important;
            padding: 0.7rem 0.95rem;
            font-size: 0.92rem;
            font-weight: 800;
            border-bottom: 2px solid transparent;
        }

        .custom-tab:hover {
            color: var(--brand-dark) !important;
        }

        .custom-tab.active {
            color: var(--brand-dark) !important;
            border-bottom: 2px solid var(--brand);
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

        .review-filter-row {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 0.9rem;
        }

        .review-filter-option {
            display: inline-flex;
            align-items: center;
            text-decoration: none !important;
            background: #FFFDF8;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 999px;
            padding: 0.48rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 850;
            box-shadow: 0 5px 14px rgba(74, 55, 40, 0.04);
            transition: all 0.16s ease;
        }

        .review-filter-option:hover {
            background: #FFF4E8;
            border-color: var(--brand);
            transform: translateY(-1px);
        }

        .review-filter-option.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.18);
        }

        .review-count-note {
            color: #7C6F64;
            font-size: 0.86rem;
            font-weight: 700;
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
            .area-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .overview-card,
            .advice-card {
                min-height: auto;
            }
        }

        @media (max-width: 520px) {
            .area-grid {
                grid-template-columns: 1fr;
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


def get_query_value(key, default_value):
    value = st.query_params.get(key, default_value)

    if isinstance(value, list):
        value = value[0]

    return value


def get_default_area_from_session(areas):
    selected_hotel = st.session_state.get("selected_hotel")

    if selected_hotel:
        hotel = get_hotel_by_name(selected_hotel)

        if hotel and hotel.get("area") in areas:
            return hotel.get("area")

    return areas[0]


def get_selected_area(areas):
    default_area = get_default_area_from_session(areas)
    selected_area = get_query_value("area", default_area)

    if selected_area not in areas:
        selected_area = default_area

    return selected_area


def get_selected_hotel(hotels, selected_area):
    hotel_names = [hotel["hotel"] for hotel in hotels]

    if not hotel_names:
        return None

    default_hotel = hotel_names[0]

    session_hotel = st.session_state.get("selected_hotel")

    if session_hotel in hotel_names:
        default_hotel = session_hotel

    selected_hotel = get_query_value("hotel", default_hotel)

    if selected_hotel not in hotel_names:
        selected_hotel = default_hotel

    st.session_state.selected_hotel = selected_hotel
    st.session_state.selected_area = selected_area

    return selected_hotel


def get_selected_section():
    selected_section = get_query_value("section", "improvements")

    if selected_section not in ["improvements", "reviews"]:
        selected_section = "improvements"

    return selected_section


def get_selected_review_type():
    selected_review_type = get_query_value("review_type", "All")

    if selected_review_type not in ["All", "Positive", "Neutral", "Negative"]:
        selected_review_type = "All"

    return selected_review_type


def get_booking_advice_text(hotel):
    risk_level = hotel.get("risk_level", "Medium")
    positive_pct = hotel.get("positive_pct", 0)
    negative_pct = hotel.get("negative_pct", 0)
    main_risk = hotel.get("main_risk", "the repeated concerns")

    if risk_level == "Low" and positive_pct >= 70:
        return (
            "Looks good to consider. Most reviews are positive, but it is still useful "
            f"to check comments about {main_risk.lower()} before booking."
        )

    if risk_level == "High":
        return (
            "Compare carefully before booking. This hotel has stronger concern signals, "
            f"especially around {main_risk.lower()}."
        )

    if negative_pct >= 15:
        return (
            "Worth considering, but read some negative reviews first. The hotel has good points, "
            f"but travellers should check {main_risk.lower()}."
        )

    return (
        "Generally suitable for consideration. Reviews are fairly balanced, so travellers should "
        "compare more reviews before making a final booking decision."
    )


def render_area_picker(areas, selected_area):
    area_notes = {
        "Bukit Jalil": "Events & stadium area",
        "KLCC": "City centre stay",
        "Petaling Jaya": "Shopping & business",
        "Sunway": "Family & theme park"
    }

    area_options_html = ""

    for area in areas:
        active_class = "active" if area == selected_area else ""
        area_url = quote(area, safe="")

        area_options_html += (
            f'<a class="area-option {active_class}" href="?area={area_url}" target="_self">'
            f'<div class="area-option-name">{escape(area)}</div>'
            f'<div class="area-option-note">{escape(area_notes.get(area, "Hotel area"))}</div>'
            f'</a>'
        )

    st.markdown(
        '<div class="picker-card">'
        '<div class="picker-label">Step 1 · Choose area</div>'
        '<div class="area-grid">'
        f'{area_options_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_hotel_picker(hotels, selected_area, selected_hotel):
    hotel_options_html = ""

    for hotel in hotels:
        hotel_name = hotel["hotel"]
        active_class = "active" if hotel_name == selected_hotel else ""
        area_url = quote(selected_area, safe="")
        hotel_url = quote(hotel_name, safe="")
        meta_text = f'{hotel.get("positive_pct", 0)}% positive · {risk_badge(hotel.get("risk_level", "Medium"))}'

        hotel_options_html += (
            f'<a class="hotel-option {active_class}" href="?area={area_url}&hotel={hotel_url}" target="_self">'
            f'<span class="hotel-option-name">{escape(hotel_name)}</span>'
            f'<span class="hotel-option-meta">{escape(meta_text)}</span>'
            f'</a>'
        )

    st.markdown(
        '<div class="picker-card">'
        '<div class="picker-label">Step 2 · Choose hotel in this area</div>'
        '<div class="hotel-picker-row">'
        f'{hotel_options_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


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


def render_hotel_overview(hotel, hotel_name):
    advice_text = get_booking_advice_text(hotel)

    overview_html = (
        '<div class="overview-card">'
        f'<div class="hotel-title">{escape(hotel.get("hotel", hotel_name))}</div>'
        f'<div class="hotel-meta">{escape(hotel.get("area", ""))} · {escape(hotel.get("hotel_address", "Address not stated"))}</div>'
        f'<div class="booking-note"><b>Booking advice:</b> {escape(advice_text)}</div>'

        '<div class="quick-line">'
        f'<span class="quick-chip">📝 {escape(hotel.get("review_count", 0))} reviews</span>'
        f'<span class="quick-chip">🟢 {escape(hotel.get("positive_pct", 0))}% positive</span>'
        f'<span class="quick-chip">🔴 {escape(hotel.get("negative_pct", 0))}% negative</span>'
        f'<span class="quick-chip">{escape(risk_badge(hotel.get("risk_level", "Medium")))}</span>'
        '</div>'

        '<div class="section-small-title">Review summary</div>'
        + build_sentiment_bar("Positive", hotel.get("positive_pct", 0), "bar-positive")
        + build_sentiment_bar("Neutral", hotel.get("neutral_pct", 0), "bar-neutral")
        + build_sentiment_bar("Negative", hotel.get("negative_pct", 0), "bar-negative")
        + '</div>'
    )

    st.markdown(overview_html, unsafe_allow_html=True)


def render_booking_advice(hotel):
    risk_level = hotel.get("risk_level", "Medium")

    advice_html = (
        '<div class="advice-card">'
        '<div class="advice-title">At a glance</div>'
        f'<span class="risk-chip {risk_class_name(risk_level)}">{escape(risk_badge(risk_level))}</span>'
        '<div class="advice-list">'

        '<div class="advice-item">'
        '<div class="advice-label">Best for this hotel</div>'
        f'<div class="advice-value">{escape(hotel.get("best_traveller_type", "General travellers"))}</div>'
        '</div>'

        '<div class="advice-item">'
        '<div class="advice-label">What looks good</div>'
        f'<div class="advice-value">{escape(hotel.get("main_strength", "Not clearly stated"))}</div>'
        '</div>'

        '<div class="advice-item">'
        '<div class="advice-label">What to check</div>'
        f'<div class="advice-value">{escape(hotel.get("main_risk", "No major repeated concern"))}</div>'
        '</div>'

        '<div class="advice-item">'
        '<div class="advice-label">Suitability score</div>'
        f'<div class="advice-value">{escape(hotel.get("suitability_score", 0))}/100</div>'
        '</div>'

        '</div>'
        '</div>'
    )

    st.markdown(advice_html, unsafe_allow_html=True)


def render_detail_section_tabs(selected_area, selected_hotel, selected_section, selected_review_type):
    area_url = quote(selected_area, safe="")
    hotel_url = quote(selected_hotel, safe="")
    review_type_url = quote(selected_review_type, safe="")

    improvements_active = "active" if selected_section == "improvements" else ""
    reviews_active = "active" if selected_section == "reviews" else ""

    tabs_html = (
        '<div id="detail-section"></div>'
        '<div class="custom-tab-row">'
        f'<a class="custom-tab {improvements_active}" '
        f'href="?area={area_url}&hotel={hotel_url}&section=improvements#detail-section" target="_self">'
        'Common concerns'
        '</a>'
        f'<a class="custom-tab {reviews_active}" '
        f'href="?area={area_url}&hotel={hotel_url}&section=reviews&review_type={review_type_url}#detail-section" target="_self">'
        'Sample reviews'
        '</a>'
        '</div>'
    )

    st.markdown(tabs_html, unsafe_allow_html=True)


def render_review_filter(selected_area, selected_hotel, selected_review_type):
    filter_options = ["All", "Positive", "Neutral", "Negative"]

    filter_html = '<div class="review-filter-row">'

    for option in filter_options:
        active_class = "active" if option == selected_review_type else ""
        area_url = quote(selected_area, safe="")
        hotel_url = quote(selected_hotel, safe="")
        review_type_url = quote(option, safe="")

        filter_html += (
            f'<a class="review-filter-option {active_class}" '
            f'href="?area={area_url}&hotel={hotel_url}&section=reviews&review_type={review_type_url}#detail-section" '
            f'target="_self">{escape(option)}</a>'
        )

    filter_html += '</div>'

    st.markdown(filter_html, unsafe_allow_html=True)


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
    '<div class="compact-desc">First choose an area, then select a hotel to view its review summary and booking concern.</div>'
    '</div>',
    unsafe_allow_html=True
)

areas = get_areas()

if not areas:
    st.markdown(
        '<div class="empty-note">No area data is available. Please check your dataset file.</div>',
        unsafe_allow_html=True
    )
    render_footer()
    st.stop()

selected_area = get_selected_area(areas)
render_area_picker(areas, selected_area)

hotels = get_hotels_by_area(selected_area)

if not hotels:
    st.markdown(
        '<div class="empty-note">No hotels are available for this area.</div>',
        unsafe_allow_html=True
    )
    render_footer()
    st.stop()

selected_hotel = get_selected_hotel(hotels, selected_area)
render_hotel_picker(hotels, selected_area, selected_hotel)

hotel = get_hotel_by_name(selected_hotel)

if hotel:
    left_col, right_col = st.columns([1.45, 0.75], gap="large")

    with left_col:
        render_hotel_overview(hotel, selected_hotel)

    with right_col:
        render_booking_advice(hotel)

    selected_section = get_selected_section()
    selected_review_type = get_selected_review_type()

    render_detail_section_tabs(
        selected_area=selected_area,
        selected_hotel=selected_hotel,
        selected_section=selected_section,
        selected_review_type=selected_review_type
    )

    if selected_section == "improvements":
        st.markdown(
            '<div class="detail-tabs-note">These are the most repeated concerns found from this hotel\'s reviews.</div>',
            unsafe_allow_html=True
        )

        complaint_df = get_complaint_df(hotel)

        if complaint_df.empty:
            st.markdown(
                '<div class="empty-note">No repeated concern was found for this hotel.</div>',
                unsafe_allow_html=True
            )
        else:
            st.dataframe(complaint_df, use_container_width=True, hide_index=True)

    else:
        render_review_filter(
            selected_area=selected_area,
            selected_hotel=selected_hotel,
            selected_review_type=selected_review_type
        )

        reviews_df = get_hotel_reviews(selected_hotel, limit=300)
        review_text_column = get_review_text_column(reviews_df)

        if reviews_df.empty or review_text_column is None:
            st.markdown(
                '<div class="empty-note">No sample review is available for this hotel.</div>',
                unsafe_allow_html=True
            )
        else:
            if selected_review_type == "All":
                positive_reviews_df = reviews_df[
                    reviews_df["sentiment"].astype(str).str.lower() == "positive"
                ].head(5)

                neutral_reviews_df = reviews_df[
                    reviews_df["sentiment"].astype(str).str.lower() == "neutral"
                ].head(5)

                negative_reviews_df = reviews_df[
                    reviews_df["sentiment"].astype(str).str.lower() == "negative"
                ].head(5)

                total_shown = (
                    len(positive_reviews_df)
                    + len(neutral_reviews_df)
                    + len(negative_reviews_df)
                )

                if total_shown == 0:
                    st.markdown(
                        '<div class="empty-note">No sample review is available for this hotel.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="review-count-note">Showing {total_shown} mixed review(s): '
                        f'{len(positive_reviews_df)} positive, '
                        f'{len(neutral_reviews_df)} neutral, '
                        f'{len(negative_reviews_df)} negative.</div>',
                        unsafe_allow_html=True
                    )

                    for _, row in positive_reviews_df.iterrows():
                        render_review_card(
                            sentiment=row.get("sentiment", "positive"),
                            review=row.get(review_text_column, "")
                        )

                    for _, row in neutral_reviews_df.iterrows():
                        render_review_card(
                            sentiment=row.get("sentiment", "neutral"),
                            review=row.get(review_text_column, "")
                        )

                    for _, row in negative_reviews_df.iterrows():
                        render_review_card(
                            sentiment=row.get("sentiment", "negative"),
                            review=row.get(review_text_column, "")
                        )

            else:
                filtered_reviews_df = reviews_df[
                    reviews_df["sentiment"].astype(str).str.lower() == selected_review_type.lower()
                ]

                if filtered_reviews_df.empty:
                    st.markdown(
                        f'<div class="empty-note">No {selected_review_type.lower()} review is available for this hotel.</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="review-count-note">Showing {min(15, len(filtered_reviews_df))} {selected_review_type.lower()} review(s).</div>',
                        unsafe_allow_html=True
                    )

                    for _, row in filtered_reviews_df.head(15).iterrows():
                        render_review_card(
                            sentiment=row.get("sentiment", "neutral"),
                            review=row.get(review_text_column, "")
                        )

render_footer()