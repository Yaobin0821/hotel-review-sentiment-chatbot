import html
from collections import Counter
from urllib.parse import quote

import pandas as pd
import streamlit as st

from styles import load_css, render_topbar, render_footer
from utils import (
    get_areas,
    get_hotels_by_area,
    get_complaint_df
)


st.set_page_config(
    page_title="Area Review Insights",
    page_icon="📊",
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


def safe_get(data, key, default="Not stated"):
    value = data.get(key, default)

    if value is None or value == "":
        return default

    return value


def safe_number(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def get_review_count(hotel):
    return hotel.get("review_count", hotel.get("total_reviews", 0))


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


def get_pattern_level(count, max_count):
    if max_count <= 0:
        return "light"

    ratio = count / max_count

    if ratio >= 0.7:
        return "strong"

    if ratio >= 0.35:
        return "common"

    return "light"


def get_positive_badge(count, max_count):
    level = get_pattern_level(count, max_count)

    if level == "strong":
        return "Strong praise", "positive-strong"

    if level == "common":
        return "Common praise", "positive-common"

    return "Light praise", "positive-light"


def get_complaint_badge(count, max_count):
    level = get_pattern_level(count, max_count)

    if level == "strong":
        return "Strong concern", "complaint-strong"

    if level == "common":
        return "Common concern", "complaint-common"

    return "Light concern", "complaint-light"


def get_match_badge(count, max_count):
    level = get_pattern_level(count, max_count)

    if level == "strong":
        return "Strong match", "match-strong"

    if level == "common":
        return "Common match", "match-common"

    return "Light match", "match-light"


def weighted_average(hotels, key):
    total_weight = 0
    total_value = 0

    for hotel in hotels:
        review_count = safe_number(get_review_count(hotel), 1)

        if review_count <= 0:
            review_count = 1

        value = safe_number(safe_get(hotel, key, 0), 0)

        total_value += value * review_count
        total_weight += review_count

    if total_weight == 0:
        return 0

    return round(total_value / total_weight, 1)


def get_area_tone(hotels):
    positive_avg = weighted_average(hotels, "positive_pct")
    negative_avg = weighted_average(hotels, "negative_pct")

    if positive_avg >= 70 and negative_avg <= 15:
        tone = "Mostly positive"
        description = "Reviews in this area generally lean positive."

    elif negative_avg >= 25:
        tone = "Mixed"
        description = "This area has stronger negative review signals, so hotel choice matters more."

    else:
        tone = "Balanced"
        description = "Reviews in this area are not one-sided."

    return {
        "tone": tone,
        "description": description,
        "positive_avg": positive_avg,
        "negative_avg": negative_avg
    }


def get_area_complaints(hotels):
    all_complaints = []

    for hotel in hotels:
        try:
            complaint_df = get_complaint_df(hotel)

            if complaint_df is None or complaint_df.empty:
                continue

            for _, row in complaint_df.iterrows():
                all_complaints.append({
                    "Complaint Area": row.get("Complaint Area", "Other"),
                    "Complaint Count": safe_number(row.get("Complaint Count", 0)),
                    "Suggested Improvement Action": row.get(
                        "Suggested Improvement Action",
                        "Check recent guest reviews for this issue."
                    )
                })

        except Exception:
            continue

    if not all_complaints:
        return pd.DataFrame(columns=[
            "Complaint Area",
            "Complaint Count",
            "Suggested Improvement Action"
        ])

    complaint_df = pd.DataFrame(all_complaints)

    grouped_df = (
        complaint_df
        .groupby("Complaint Area", as_index=False)
        .agg({
            "Complaint Count": "sum",
            "Suggested Improvement Action": "first"
        })
        .sort_values("Complaint Count", ascending=False)
    )

    return grouped_df


def get_common_hotel_field_patterns(hotels, field_name, limit=6):
    values = []

    for hotel in hotels:
        value = safe_get(hotel, field_name, "")

        if value and value != "Not stated":
            values.append(value)

    if not values:
        return []

    counter = Counter(values)
    return counter.most_common(limit)


def get_top_pattern(patterns, default_value):
    if not patterns:
        return default_value

    return patterns[0][0]


def get_top_concern(complaint_df):
    if complaint_df.empty:
        return "No repeated concern found"

    return complaint_df.iloc[0]["Complaint Area"]


def get_area_takeaway(selected_area, hotels, complaint_df):
    tone_info = get_area_tone(hotels)

    positive_patterns = get_common_hotel_field_patterns(
        hotels,
        "main_strength",
        5
    )

    traveller_patterns = get_common_hotel_field_patterns(
        hotels,
        "best_traveller_type",
        5
    )

    top_positive = get_top_pattern(
        positive_patterns,
        "no clear positive pattern"
    )

    top_traveller = get_top_pattern(
        traveller_patterns,
        "general travellers"
    )

    top_concern = get_top_concern(complaint_df)

    if top_concern == "No repeated concern found":
        return (
            f"In {selected_area}, the available reviews are {tone_info['tone'].lower()} overall. "
            f"The most visible positive signal is {top_positive}, and the area appears suitable for {top_traveller}."
        )

    return (
        f"In {selected_area}, the available reviews are {tone_info['tone'].lower()} overall. "
        f"Guests often highlight {top_positive}, while the most repeated concern is {top_concern}. "
        f"This area appears most relevant for {top_traveller}."
    )


def get_concern_meaning(concern):
    concern_lower = str(concern).lower()

    if "clean" in concern_lower or "hygiene" in concern_lower:
        return "This usually relates to room freshness, bathroom condition, or overall comfort confidence."

    if "room" in concern_lower or "noise" in concern_lower or "comfort" in concern_lower:
        return "This usually affects sleep quality, room comfort, and how relaxing the stay feels."

    if "breakfast" in concern_lower or "food" in concern_lower:
        return "This usually affects morning convenience, food satisfaction, and perceived value."

    if "check-in" in concern_lower or "booking" in concern_lower or "payment" in concern_lower:
        return "This usually affects arrival experience, waiting time, or booking smoothness."

    if "parking" in concern_lower or "transport" in concern_lower or "access" in concern_lower:
        return "This usually affects convenience when reaching the hotel or moving around the area."

    if "service" in concern_lower or "staff" in concern_lower:
        return "This usually affects how supported, welcomed, and comfortable guests feel."

    if "facility" in concern_lower or "maintenance" in concern_lower:
        return "This usually affects convenience when hotel facilities are not working well."

    if "price" in concern_lower or "value" in concern_lower:
        return "This usually affects whether guests feel the stay was worth the money paid."

    if "overall" in concern_lower or "experience" in concern_lower:
        return "This is a broad review signal about the general stay experience."

    return "This is a repeated review topic that may affect the stay experience."


def load_insights_css():
    st.markdown("""
    <style>
        .insights-header {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem 1.45rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .insights-badge {
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

        .insights-title {
            color: var(--text-main);
            font-size: clamp(2rem, 4vw, 2.9rem);
            font-weight: 950;
            letter-spacing: -0.07em;
            line-height: 1.05;
            margin-bottom: 0.25rem;
        }

        .insights-subtitle {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .choice-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .section-label {
            color: #7C6F64;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.45rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.48rem;
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

        .takeaway-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 26px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.9rem;
        }

        .takeaway-label {
            color: #9B4325;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .takeaway-text {
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 850;
            line-height: 1.45;
        }

        .snapshot-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-bottom: 0.9rem;
        }

        .snapshot-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 0.95rem;
            box-shadow: var(--shadow-card);
        }

        .snapshot-label {
            color: #7C6F64;
            font-size: 0.68rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        .snapshot-value {
            color: var(--text-main);
            font-size: 1.02rem;
            font-weight: 950;
            line-height: 1.25;
        }

        .snapshot-sub {
            color: #64748B;
            font-size: 0.76rem;
            font-weight: 750;
            margin-top: 0.25rem;
            line-height: 1.35;
        }

        .pattern-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.75rem;
        }

        .card-title {
            color: var(--text-main);
            font-size: 1.12rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.2rem;
        }

        .card-desc {
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.4;
            margin-bottom: 0.75rem;
        }

        .pattern-list {
            display: flex;
            flex-direction: column;
            gap: 0.48rem;
        }

        .pattern-row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.5rem;
            align-items: center;
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.62rem 0.68rem;
        }

        .pattern-name {
            color: var(--text-main);
            font-size: 0.9rem;
            font-weight: 900;
            line-height: 1.28;
        }

        .pattern-badge {
            border-radius: 999px;
            padding: 0.38rem 0.55rem;
            font-size: 0.68rem;
            font-weight: 900;
            text-align: center;
            white-space: nowrap;
        }

        .positive-strong {
            background: #EAF7F0;
            color: #216E46;
            border: 1px solid #BFE3CF;
        }

        .positive-common {
            background: #F0FAF4;
            color: #2E7D52;
            border: 1px solid #CAEAD8;
        }

        .positive-light {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
        }

        .complaint-strong {
            background: #FFF0EE;
            color: #A33A2F;
            border: 1px solid #F4C7BF;
        }

        .complaint-common {
            background: #FFF4D6;
            color: #8A5A12;
            border: 1px solid #E6C879;
        }

        .complaint-light {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
        }

        .match-strong {
            background: #EEF2FF;
            color: #3B4B9A;
            border: 1px solid #C7D2FE;
        }

        .match-common {
            background: #F5F3FF;
            color: #5B3A9A;
            border: 1px solid #DDD6FE;
        }

        .match-light {
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px solid #E5D8CA;
        }

        .meaning-section {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .meaning-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 0.75rem;
        }

        .meaning-card {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
        }

        .meaning-title {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 950;
            margin-bottom: 0.22rem;
        }

        .meaning-text {
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.4;
        }

        @media (max-width: 1000px) {
            .snapshot-grid,
            .meaning-grid {
                grid-template-columns: 1fr;
            }

            .pattern-row {
                grid-template-columns: 1fr;
            }

            .pattern-badge {
                width: fit-content;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    render_html("""
    <div class="insights-header">
        <div class="insights-badge">Area review patterns</div>
        <div class="insights-title">Area Review Insights</div>
        <div class="insights-subtitle">
            See what hotel reviews in this area usually talk about. This page shows area-level patterns, not a direct hotel comparison.
        </div>
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

    render_html(f"""
    <div class="choice-card">
        <div class="section-label">Choose area</div>
        <div class="chip-row">{chips_html}</div>
    </div>
    """)


def render_takeaway(selected_area, hotels, complaint_df):
    takeaway = get_area_takeaway(selected_area, hotels, complaint_df)

    render_html(f"""
    <div class="takeaway-card">
        <div class="takeaway-label">Area takeaway</div>
        <div class="takeaway-text">{escape(takeaway)}</div>
    </div>
    """)


def render_snapshot(selected_area, hotels, complaint_df):
    tone_info = get_area_tone(hotels)

    positive_patterns = get_common_hotel_field_patterns(
        hotels,
        "main_strength",
        5
    )

    traveller_patterns = get_common_hotel_field_patterns(
        hotels,
        "best_traveller_type",
        5
    )

    top_positive = get_top_pattern(
        positive_patterns,
        "No clear positive pattern"
    )

    top_traveller = get_top_pattern(
        traveller_patterns,
        "General travellers"
    )

    top_concern = get_top_concern(complaint_df)

    render_html(f"""
    <div class="snapshot-grid">
        <div class="snapshot-card">
            <div class="snapshot-label">Selected area</div>
            <div class="snapshot-value">{escape(selected_area)}</div>
            <div class="snapshot-sub">{len(hotels)} hotel option(s) in this dataset</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Overall review tone</div>
            <div class="snapshot-value">{escape(tone_info["tone"])}</div>
            <div class="snapshot-sub">{escape(tone_info["positive_avg"])}% positive · {escape(tone_info["negative_avg"])}% negative</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Most praised topic</div>
            <div class="snapshot-value">{escape(top_positive)}</div>
            <div class="snapshot-sub">Appears most often in hotel summaries</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Most repeated concern</div>
            <div class="snapshot-value">{escape(top_concern)}</div>
            <div class="snapshot-sub">A repeated topic in review patterns</div>
        </div>
    </div>
    """)


def render_positive_patterns(hotels):
    patterns = get_common_hotel_field_patterns(
        hotels,
        "main_strength",
        6
    )

    if not patterns:
        render_html("""
        <div class="pattern-card">
            <div class="card-title">What guests usually praise</div>
            <div class="card-desc">No repeated positive pattern was found for this area.</div>
        </div>
        """)
        return

    max_count = max(count for _, count in patterns)
    rows_html = ""

    for name, count in patterns:
        label, label_class = get_positive_badge(count, max_count)

        rows_html += f"""
        <div class="pattern-row">
            <div class="pattern-name">{escape(name)}</div>
            <div class="pattern-badge {label_class}">{escape(label)}</div>
        </div>
        """

    render_html(f"""
    <div class="pattern-card">
        <div class="card-title">What guests usually praise</div>
        <div class="card-desc">Positive topics that appear across hotels in this area.</div>
        <div class="pattern-list">
            {rows_html}
        </div>
    </div>
    """)


def render_complaint_patterns(complaint_df):
    if complaint_df.empty:
        render_html("""
        <div class="pattern-card">
            <div class="card-title">What guests complain about</div>
            <div class="card-desc">No repeated concern pattern was found for this area.</div>
        </div>
        """)
        return

    top_df = complaint_df.head(6)
    max_count = safe_number(top_df["Complaint Count"].max(), 0)
    rows_html = ""

    for _, row in top_df.iterrows():
        concern = row["Complaint Area"]
        count = safe_number(row["Complaint Count"], 0)

        label, label_class = get_complaint_badge(count, max_count)

        rows_html += f"""
        <div class="pattern-row">
            <div class="pattern-name">{escape(concern)}</div>
            <div class="pattern-badge {label_class}">{escape(label)}</div>
        </div>
        """

    render_html(f"""
    <div class="pattern-card">
        <div class="card-title">What guests complain about</div>
        <div class="card-desc">Repeated concern topics found in this area.</div>
        <div class="pattern-list">
            {rows_html}
        </div>
    </div>
    """)


def render_traveller_pattern(hotels):
    patterns = get_common_hotel_field_patterns(
        hotels,
        "best_traveller_type",
        5
    )

    if not patterns:
        render_html("""
        <div class="pattern-card">
            <div class="card-title">Who this area suits</div>
            <div class="card-desc">No clear traveller suitability pattern was found for this area.</div>
        </div>
        """)
        return

    max_count = max(count for _, count in patterns)
    rows_html = ""

    for name, count in patterns:
        label, label_class = get_match_badge(count, max_count)

        rows_html += f"""
        <div class="pattern-row">
            <div class="pattern-name">{escape(name)}</div>
            <div class="pattern-badge {label_class}">{escape(label)}</div>
        </div>
        """

    render_html(f"""
    <div class="pattern-card">
        <div class="card-title">Who this area suits</div>
        <div class="card-desc">Traveller types commonly matched with hotels here.</div>
        <div class="pattern-list">
            {rows_html}
        </div>
    </div>
    """)


def render_concern_meanings(complaint_df):
    if complaint_df.empty:
        return

    meaning_html = ""

    for _, row in complaint_df.head(4).iterrows():
        concern = row["Complaint Area"]
        meaning = get_concern_meaning(concern)

        meaning_html += f"""
        <div class="meaning-card">
            <div class="meaning-title">{escape(concern)}</div>
            <div class="meaning-text">{escape(meaning)}</div>
        </div>
        """

    render_html(f"""
    <div class="meaning-section">
        <div class="card-title">What the concern patterns mean</div>
        <div class="card-desc">
            These explanations help users understand how repeated review topics may affect the stay experience.
        </div>

        <div class="meaning-grid">
            {meaning_html}
        </div>
    </div>
    """)


load_css()
load_insights_css()
render_topbar()
render_header()

areas = get_areas()

if not areas:
    st.warning("No area data is available.")
    render_footer()
    st.stop()

selected_area = get_selected_area(areas)
hotels = get_hotels_by_area(selected_area)

if not hotels:
    st.warning("No hotel data is available for this area.")
    render_footer()
    st.stop()

complaint_df = get_area_complaints(hotels)

render_area_choices(areas, selected_area)
render_takeaway(selected_area, hotels, complaint_df)
render_snapshot(selected_area, hotels, complaint_df)

main_pattern_col, side_pattern_col = st.columns(
    [1.35, 0.85],
    gap="large"
)

with main_pattern_col:
    render_complaint_patterns(complaint_df)

with side_pattern_col:
    render_positive_patterns(hotels)
    render_traveller_pattern(hotels)

render_concern_meanings(complaint_df)

render_footer()