import html
from urllib.parse import quote

import streamlit as st

from styles import load_css, render_topbar, render_footer
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


def clean_html(markup):
    return "\n".join(
        line.strip()
        for line in str(markup).splitlines()
        if line.strip()
    )


def render_html(markup):
    st.markdown(clean_html(markup), unsafe_allow_html=True)


def escape(value):
    return html.escape(str(value))


def safe_get(hotel, key, default="Not stated"):
    value = hotel.get(key, default)

    if value is None or value == "":
        return default

    return value


def safe_pct(value):
    try:
        return float(value)
    except Exception:
        return 0


def get_review_count(hotel):
    return hotel.get("review_count", hotel.get("total_reviews", 0))


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


def get_selected_area(areas):
    selected_area = get_query_value("area", areas[0])

    if selected_area not in areas:
        selected_area = areas[0]

    return selected_area


def get_other_hotel_choice(hotel_options, selected_hotel):
    for hotel_name in hotel_options:
        if hotel_name != selected_hotel:
            return hotel_name

    return selected_hotel


def get_selected_hotels(hotel_options):
    hotel_a = get_query_value("hotel_a", hotel_options[0])

    if hotel_a not in hotel_options:
        hotel_a = hotel_options[0]

    hotel_b_options = [hotel for hotel in hotel_options if hotel != hotel_a]

    if not hotel_b_options:
        return hotel_a, None

    hotel_b = get_query_value("hotel_b", hotel_b_options[0])

    if hotel_b not in hotel_b_options:
        hotel_b = hotel_b_options[0]

    return hotel_a, hotel_b


def get_better_positive_label(hotel_a, hotel_b):
    a_positive = safe_pct(safe_get(hotel_a, "positive_pct", 0))
    b_positive = safe_pct(safe_get(hotel_b, "positive_pct", 0))

    if a_positive > b_positive:
        return safe_get(hotel_a, "hotel")

    if b_positive > a_positive:
        return safe_get(hotel_b, "hotel")

    return "Similar"


def get_better_negative_label(hotel_a, hotel_b):
    a_negative = safe_pct(safe_get(hotel_a, "negative_pct", 0))
    b_negative = safe_pct(safe_get(hotel_b, "negative_pct", 0))

    if a_negative < b_negative:
        return safe_get(hotel_a, "hotel")

    if b_negative < a_negative:
        return safe_get(hotel_b, "hotel")

    return "Similar"


def get_better_score_label(hotel_a, hotel_b):
    a_score = safe_pct(safe_get(hotel_a, "suitability_score", 0))
    b_score = safe_pct(safe_get(hotel_b, "suitability_score", 0))

    if a_score > b_score:
        return safe_get(hotel_a, "hotel")

    if b_score > a_score:
        return safe_get(hotel_b, "hotel")

    return "Similar"


def load_compare_css():
    st.markdown("""
    <style>
        .compare-header {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem 1.45rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .compare-badge {
            display: inline-flex;
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            padding: 0.32rem 0.72rem;
            font-size: 0.76rem;
            font-weight: 850;
            margin-bottom: 0.55rem;
        }

        .compare-title {
            color: var(--text-main);
            font-size: clamp(2rem, 4vw, 2.9rem);
            font-weight: 950;
            letter-spacing: -0.07em;
            line-height: 1.05;
            margin-bottom: 0.25rem;
        }

        .compare-subtitle {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .selection-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem 1.05rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .selection-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }

        .selection-title {
            color: var(--text-main);
            font-size: 1.1rem;
            font-weight: 950;
            letter-spacing: -0.04em;
        }

        .selector-label {
            color: #7C6F64;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.42rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.48rem;
            margin-bottom: 0.9rem;
        }

        .choice-chip {
            display: inline-flex;
            align-items: center;
            text-decoration: none !important;
            background: #FFFDF8;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 999px;
            padding: 0.5rem 0.82rem;
            font-size: 0.84rem;
            font-weight: 850;
            box-shadow: 0 5px 14px rgba(74, 55, 40, 0.04);
            transition: all 0.16s ease;
        }

        .choice-chip:hover {
            background: #FFF4E8;
            border-color: var(--brand);
            transform: translateY(-1px);
        }

        .choice-chip.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.18);
        }

        .hotel-choice-grid {
            display: grid;
            grid-template-columns: 1fr 44px 1fr;
            gap: 0.8rem;
            align-items: start;
        }

        .hotel-choice-box {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 20px;
            padding: 0.85rem;
        }

        .vs-pill {
            align-self: center;
            justify-self: center;
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.78rem;
            font-weight: 950;
        }

        .hotel-chip-row {
            display: flex;
            gap: 0.45rem;
            overflow-x: auto;
            padding-bottom: 0.15rem;
        }

        .hotel-chip-row::-webkit-scrollbar {
            height: 6px;
        }

        .hotel-chip-row::-webkit-scrollbar-track {
            background: #F1E8DC;
            border-radius: 999px;
        }

        .hotel-chip-row::-webkit-scrollbar-thumb {
            background: #D8C2AD;
            border-radius: 999px;
        }

        .hotel-chip {
            flex: 0 0 auto;
            display: inline-flex;
            align-items: center;
            text-decoration: none !important;
            background: white;
            color: var(--text-main) !important;
            border: 1px solid #EAD7C6;
            border-radius: 999px;
            padding: 0.52rem 0.82rem;
            font-size: 0.82rem;
            font-weight: 850;
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            box-shadow: 0 4px 12px rgba(74, 55, 40, 0.035);
        }

        .hotel-chip:hover {
            background: #FFF4E8;
            border-color: var(--brand);
        }

        .hotel-chip.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.18);
        }

        .recommendation-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 24px;
            padding: 0.95rem 1.1rem;
            box-shadow: var(--shadow-card);
            margin: 0.85rem 0;
        }

        .recommendation-label {
            color: #9B4325;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.22rem;
        }

        .recommendation-text {
            color: var(--text-main);
            font-size: 0.98rem;
            font-weight: 850;
            line-height: 1.42;
        }

        .hotel-compare-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1.05rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.75rem;
        }

        .hotel-card-title {
            color: var(--text-main);
            font-size: 1.15rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            line-height: 1.15;
            margin-bottom: 0.22rem;
        }

        .hotel-card-meta {
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.42;
            margin-bottom: 0.65rem;
        }

        .top-line {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-bottom: 0.75rem;
        }

        .risk-chip,
        .stat-chip {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border-radius: 999px;
            padding: 0.38rem 0.68rem;
            font-size: 0.78rem;
            font-weight: 850;
        }

        .stat-chip {
            background: #FFFDF8;
            color: #3F342B;
            border: 1px solid #EAD7C6;
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

        .sentiment-row {
            margin-bottom: 0.45rem;
        }

        .sentiment-line {
            display: flex;
            justify-content: space-between;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.18rem;
        }

        .bar-track {
            width: 100%;
            height: 7px;
            background: #E8DDD0;
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-positive {
            height: 7px;
            background: #2F855A;
            border-radius: 999px;
        }

        .bar-neutral {
            height: 7px;
            background: #D99A25;
            border-radius: 999px;
        }

        .bar-negative {
            height: 7px;
            background: #C24136;
            border-radius: 999px;
        }

        .compare-info-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.48rem;
            margin-top: 0.7rem;
        }

        .compare-info-item {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 15px;
            padding: 0.58rem 0.62rem;
        }

        .compare-info-label {
            color: #7C6F64;
            font-size: 0.65rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.12rem;
        }

        .compare-info-value {
            color: var(--text-main);
            font-size: 0.82rem;
            font-weight: 800;
            line-height: 1.32;
        }

        .traveller-summary-section {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-top: 0.85rem;
            margin-bottom: 1rem;
        }

        .traveller-summary-title {
            color: var(--text-main);
            font-size: 1.18rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.15rem;
        }

        .traveller-summary-desc {
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.4;
            margin-bottom: 0.8rem;
        }

        .summary-row {
            display: grid;
            grid-template-columns: 180px 1fr 1fr 120px;
            gap: 0.5rem;
            align-items: center;
            padding: 0.55rem 0;
            border-top: 1px solid #EFE3D8;
        }

        .summary-row:first-of-type {
            border-top: none;
        }

        .summary-topic {
            color: #7C6F64;
            font-size: 0.74rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            line-height: 1.25;
        }

        .summary-value-box {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 14px;
            padding: 0.58rem 0.65rem;
            min-height: auto;
        }

        .summary-hotel-name {
            color: #64748B;
            font-size: 0.68rem;
            font-weight: 850;
            margin-bottom: 0.18rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .summary-value {
            color: var(--text-main);
            font-size: 0.84rem;
            font-weight: 900;
            line-height: 1.3;
        }

        .summary-better {
            display: flex;
            align-items: center;
            justify-content: center;
            background: #EAF7F0;
            color: #216E46;
            border: 1px solid #BFE3CF;
            border-radius: 14px;
            padding: 0.55rem;
            font-size: 0.72rem;
            font-weight: 900;
            text-align: center;
            line-height: 1.25;
            min-height: 48px;
        }

        .summary-better.neutral {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
        }

        @media (max-width: 1000px) {
            .summary-row {
                grid-template-columns: 1fr;
                gap: 0.45rem;
            }

            .summary-better {
                justify-content: flex-start;
                min-height: auto;
            }
        }

        @media (max-width: 900px) {
            .hotel-choice-grid {
                grid-template-columns: 1fr;
            }

            .vs-pill {
                width: auto;
                height: auto;
                padding: 0.4rem 0.7rem;
            }

            .compare-info-list {
                grid-template-columns: 1fr;
            }

            .selection-top {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def build_sentiment_bar(label, value, css_class):
    value_number = safe_pct(value)

    return clean_html(f"""
    <div class="sentiment-row">
        <div class="sentiment-line">
            <span>{escape(label)}</span>
            <span>{escape(value)}%</span>
        </div>
        <div class="bar-track">
            <div class="{css_class}" style="width: {value_number}%;"></div>
        </div>
    </div>
    """)


def render_header():
    render_html("""
    <div class="compare-header">
        <div class="compare-badge">Travel decision support</div>
        <div class="compare-title">Compare Hotels</div>
        <div class="compare-subtitle">Choose two hotels and quickly see which one looks safer, stronger, and more suitable.</div>
    </div>
    """)


def render_area_choices(areas, selected_area):
    chips_html = ""

    for area in areas:
        active_class = "active" if area == selected_area else ""
        area_url = quote(area, safe="")

        chips_html += (
            f'<a class="choice-chip {active_class}" '
            f'href="?area={area_url}" target="_self">{escape(area)}</a>'
        )

    return clean_html(f"""
    <div class="selector-label">Area</div>
    <div class="chip-row">{chips_html}</div>
    """)


def build_hotel_choice_chips(hotel_options, selected_area, selected_hotel, other_hotel, target):
    chips_html = ""

    for hotel_name in hotel_options:
        if hotel_name == other_hotel:
            continue

        active_class = "active" if hotel_name == selected_hotel else ""

        new_hotel_a = hotel_name if target == "hotel_a" else other_hotel
        new_hotel_b = hotel_name if target == "hotel_b" else other_hotel

        if new_hotel_a == new_hotel_b:
            new_hotel_b = get_other_hotel_choice(hotel_options, new_hotel_a)

        area_url = quote(selected_area, safe="")
        hotel_a_url = quote(new_hotel_a, safe="")
        hotel_b_url = quote(new_hotel_b, safe="")

        chips_html += (
            f'<a class="hotel-chip {active_class}" '
            f'href="?area={area_url}&hotel_a={hotel_a_url}&hotel_b={hotel_b_url}" '
            f'target="_self">{escape(hotel_name)}</a>'
        )

    return chips_html


def render_selection_panel(areas, hotel_options, selected_area, hotel_a_name, hotel_b_name):
    area_html = render_area_choices(areas, selected_area)

    hotel_a_chips = build_hotel_choice_chips(
        hotel_options=hotel_options,
        selected_area=selected_area,
        selected_hotel=hotel_a_name,
        other_hotel=hotel_b_name,
        target="hotel_a"
    )

    hotel_b_chips = build_hotel_choice_chips(
        hotel_options=hotel_options,
        selected_area=selected_area,
        selected_hotel=hotel_b_name,
        other_hotel=hotel_a_name,
        target="hotel_b"
    )

    render_html(f"""
    <div class="selection-card">
        <div class="selection-top">
            <div class="selection-title">Pick hotels to compare</div>
        </div>

        {area_html}

        <div class="hotel-choice-grid">
            <div class="hotel-choice-box">
                <div class="selector-label">Hotel A</div>
                <div class="hotel-chip-row">{hotel_a_chips}</div>
            </div>

            <div class="vs-pill">VS</div>

            <div class="hotel-choice-box">
                <div class="selector-label">Hotel B</div>
                <div class="hotel-chip-row">{hotel_b_chips}</div>
            </div>
        </div>
    </div>
    """)


def render_hotel_compare_card(hotel):
    risk_level = safe_get(hotel, "risk_level", "Medium")

    sentiment_html = (
        build_sentiment_bar("Positive", safe_get(hotel, "positive_pct", 0), "bar-positive")
        + build_sentiment_bar("Neutral", safe_get(hotel, "neutral_pct", 0), "bar-neutral")
        + build_sentiment_bar("Negative", safe_get(hotel, "negative_pct", 0), "bar-negative")
    )

    card_html = clean_html(f"""
    <div class="hotel-compare-card">
        <div class="hotel-card-title">{escape(safe_get(hotel, "hotel"))}</div>
        <div class="hotel-card-meta">{escape(safe_get(hotel, "area"))} · {escape(get_review_count(hotel))} reviews</div>

        <div class="top-line">
            <span class="risk-chip {risk_class_name(risk_level)}">{escape(risk_badge(risk_level))}</span>
            <span class="stat-chip">🟢 {escape(safe_get(hotel, "positive_pct", 0))}% positive</span>
            <span class="stat-chip">🔴 {escape(safe_get(hotel, "negative_pct", 0))}% negative</span>
        </div>

        {sentiment_html}

        <div class="compare-info-list">
            <div class="compare-info-item">
                <div class="compare-info-label">Looks good</div>
                <div class="compare-info-value">{escape(safe_get(hotel, "main_strength"))}</div>
            </div>

            <div class="compare-info-item">
                <div class="compare-info-label">Check first</div>
                <div class="compare-info-value">{escape(safe_get(hotel, "main_risk"))}</div>
            </div>

            <div class="compare-info-item">
                <div class="compare-info-label">Best for</div>
                <div class="compare-info-value">{escape(safe_get(hotel, "best_traveller_type"))}</div>
            </div>

            <div class="compare-info-item">
                <div class="compare-info-label">Score</div>
                <div class="compare-info-value">{escape(safe_get(hotel, "suitability_score", 0))}/100</div>
            </div>
        </div>
    </div>
    """)

    render_html(card_html)


def render_summary_row(topic, hotel_a, hotel_b, value_a, value_b, better_label):
    hotel_a_name = safe_get(hotel_a, "hotel")
    hotel_b_name = safe_get(hotel_b, "hotel")

    better_class = "neutral" if better_label == "Similar" else ""

    if better_label == "Similar":
        better_text = "Similar"
    elif better_label == hotel_a_name:
        better_text = "Better: Hotel A"
    elif better_label == hotel_b_name:
        better_text = "Better: Hotel B"
    else:
        better_text = "Better"

    render_html(f"""
    <div class="summary-row">
        <div class="summary-topic">
            {escape(topic)}
        </div>

        <div class="summary-value-box">
            <div class="summary-hotel-name">{escape(hotel_a_name)}</div>
            <div class="summary-value">{escape(value_a)}</div>
        </div>

        <div class="summary-value-box">
            <div class="summary-hotel-name">{escape(hotel_b_name)}</div>
            <div class="summary-value">{escape(value_b)}</div>
        </div>

        <div class="summary-better {better_class}">
            {escape(better_text)}
        </div>
    </div>
    """)


def render_traveller_summary(hotel_a, hotel_b):
    better_positive = get_better_positive_label(hotel_a, hotel_b)
    better_negative = get_better_negative_label(hotel_a, hotel_b)
    better_score = get_better_score_label(hotel_a, hotel_b)

    render_html("""
    <div class="traveller-summary-section">
        <div class="traveller-summary-title">Traveller comparison summary</div>
        <div class="traveller-summary-desc">
            A compact side-by-side view of the most important booking signals.
        </div>
    """)

    render_summary_row(
        topic="Guest feeling",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=f"{safe_get(hotel_a, 'positive_pct', 0)}% positive",
        value_b=f"{safe_get(hotel_b, 'positive_pct', 0)}% positive",
        better_label=better_positive
    )

    render_summary_row(
        topic="Booking concern",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=f"{safe_get(hotel_a, 'negative_pct', 0)}% negative · {safe_get(hotel_a, 'risk_level')}",
        value_b=f"{safe_get(hotel_b, 'negative_pct', 0)}% negative · {safe_get(hotel_b, 'risk_level')}",
        better_label=better_negative
    )

    render_summary_row(
        topic="Looks good",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=safe_get(hotel_a, "main_strength"),
        value_b=safe_get(hotel_b, "main_strength"),
        better_label="Similar"
    )

    render_summary_row(
        topic="Check first",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=safe_get(hotel_a, "main_risk"),
        value_b=safe_get(hotel_b, "main_risk"),
        better_label="Similar"
    )

    render_summary_row(
        topic="Best for",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=safe_get(hotel_a, "best_traveller_type"),
        value_b=safe_get(hotel_b, "best_traveller_type"),
        better_label="Similar"
    )

    render_summary_row(
        topic="Score",
        hotel_a=hotel_a,
        hotel_b=hotel_b,
        value_a=f"{safe_get(hotel_a, 'suitability_score', 0)}/100",
        value_b=f"{safe_get(hotel_b, 'suitability_score', 0)}/100",
        better_label=better_score
    )

    render_html("</div>")


def get_recommendation_text(hotel_a, hotel_b):
    try:
        recommendation = recommend_better_hotel(hotel_a, hotel_b)
        return str(recommendation).replace("**", "")
    except Exception:
        a_score = float(safe_get(hotel_a, "suitability_score", 0))
        b_score = float(safe_get(hotel_b, "suitability_score", 0))

        if a_score > b_score:
            return f"{safe_get(hotel_a, 'hotel')} looks more suitable based on the current review summary."
        elif b_score > a_score:
            return f"{safe_get(hotel_b, 'hotel')} looks more suitable based on the current review summary."
        else:
            return "Both hotels look similar. Compare the main risk and sample reviews before deciding."


load_css()
load_compare_css()
render_topbar()
render_header()

areas = get_areas()

if not areas:
    st.warning("No area data is available.")
    render_footer()
    st.stop()

selected_area = get_selected_area(areas)

hotels_in_area = get_hotels_by_area(selected_area)
hotel_options = [hotel["hotel"] for hotel in hotels_in_area]

if len(hotel_options) < 2:
    st.warning("This area does not have enough hotels for comparison.")
    render_footer()
    st.stop()

hotel_a_name, hotel_b_name = get_selected_hotels(hotel_options)

render_selection_panel(
    areas=areas,
    hotel_options=hotel_options,
    selected_area=selected_area,
    hotel_a_name=hotel_a_name,
    hotel_b_name=hotel_b_name
)

hotel_a = get_hotel_by_name(hotel_a_name)
hotel_b = get_hotel_by_name(hotel_b_name)

if hotel_a is None or hotel_b is None:
    st.error("Hotel data could not be loaded. Please check your dataset.")
else:
    recommendation = get_recommendation_text(hotel_a, hotel_b)

    render_html(f"""
    <div class="recommendation-card">
        <div class="recommendation-label">Quick recommendation</div>
        <div class="recommendation-text">{escape(recommendation)}</div>
    </div>
    """)

    compare_col1, compare_col2 = st.columns(2, gap="large")

    with compare_col1:
        render_hotel_compare_card(hotel_a)

    with compare_col2:
        render_hotel_compare_card(hotel_b)

    render_traveller_summary(hotel_a, hotel_b)

render_footer()