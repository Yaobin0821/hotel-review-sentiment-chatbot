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
    page_title="Booking Insights",
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


def concern_frequency_label(count, max_count):
    if max_count <= 0:
        return "Review signal"

    ratio = count / max_count

    if ratio >= 0.7:
        return "Mentioned often"

    if ratio >= 0.35:
        return "Common concern"

    return "Occasional concern"


def concern_frequency_class(count, max_count):
    if max_count <= 0:
        return "concern-low"

    ratio = count / max_count

    if ratio >= 0.7:
        return "concern-high"

    if ratio >= 0.35:
        return "concern-medium"

    return "concern-low"


def get_concern_meaning(concern):
    concern_lower = str(concern).lower()

    if "clean" in concern_lower or "hygiene" in concern_lower:
        return "May affect comfort, room freshness, bathroom condition, or overall stay confidence."

    if "room" in concern_lower or "noise" in concern_lower or "comfort" in concern_lower:
        return "May affect sleep quality, room comfort, and how relaxed the stay feels."

    if "breakfast" in concern_lower or "food" in concern_lower:
        return "May affect morning convenience, food satisfaction, and value for money."

    if "check-in" in concern_lower or "booking" in concern_lower or "payment" in concern_lower:
        return "May affect arrival experience, waiting time, payment clarity, or booking smoothness."

    if "parking" in concern_lower or "access" in concern_lower or "transport" in concern_lower:
        return "May affect how easy it is to reach the hotel or move around the area."

    if "service" in concern_lower or "staff" in concern_lower:
        return "May affect how helpful, responsive, and comfortable the guest experience feels."

    if "facility" in concern_lower or "maintenance" in concern_lower:
        return "May affect convenience if hotel facilities are not working well."

    if "price" in concern_lower or "value" in concern_lower:
        return "May affect whether the stay feels worth the money paid."

    if "overall" in concern_lower or "experience" in concern_lower:
        return "Shows that guests mention general stay experience, so recent reviews should be checked carefully."

    return "Check recent reviews to understand how this issue may affect your stay."


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
                        "Check recent guest reviews for this issue before booking."
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


def get_common_positive_signal(hotels):
    strengths = []

    for hotel in hotels:
        strength = safe_get(hotel, "main_strength", "")

        if strength and strength != "Not stated":
            strengths.append(strength)

    if not strengths:
        return "No clear positive pattern found"

    counter = Counter(strengths)
    return counter.most_common(1)[0][0]


def get_area_warning(complaint_df):
    if complaint_df.empty:
        return "No repeated concern found"

    return complaint_df.iloc[0]["Complaint Area"]


def get_area_advice(selected_area, complaint_df):
    if complaint_df.empty:
        return (
            f"For {selected_area}, no strong repeated concern was found in the available review data. "
            "Still, travellers should compare several recent reviews before booking."
        )

    top_concern = complaint_df.iloc[0]["Complaint Area"]

    return (
        f"For {selected_area}, travellers should pay extra attention to reviews about "
        f"{top_concern}. If the same issue appears repeatedly in recent reviews, compare another hotel before booking."
    )


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

        .area-advice-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 24px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.9rem;
        }

        .area-advice-label {
            color: #9B4325;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .area-advice-text {
            color: var(--text-main);
            font-size: 0.98rem;
            font-weight: 850;
            line-height: 1.45;
        }

        .snapshot-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
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
            font-size: 0.7rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        .snapshot-value {
            color: var(--text-main);
            font-size: 1.05rem;
            font-weight: 950;
            line-height: 1.25;
        }

        .snapshot-sub {
            color: #64748B;
            font-size: 0.78rem;
            font-weight: 750;
            margin-top: 0.25rem;
            line-height: 1.35;
        }

        .main-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.9rem;
            margin-bottom: 0.9rem;
        }

        .insight-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
        }

        .card-title {
            color: var(--text-main);
            font-size: 1.18rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.2rem;
        }

        .card-desc {
            color: #64748B;
            font-size: 0.84rem;
            line-height: 1.4;
            margin-bottom: 0.85rem;
        }

        .concern-row {
            display: grid;
            grid-template-columns: 1fr 150px;
            gap: 0.65rem;
            align-items: center;
            padding: 0.68rem 0;
            border-top: 1px solid #EFE3D8;
        }

        .concern-row:first-of-type {
            border-top: none;
        }

        .concern-name {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 900;
            line-height: 1.35;
        }

        .concern-help {
            color: #64748B;
            font-size: 0.78rem;
            line-height: 1.35;
            margin-top: 0.15rem;
        }

        .concern-badge {
            border-radius: 999px;
            padding: 0.45rem 0.65rem;
            font-size: 0.76rem;
            font-weight: 900;
            text-align: center;
            white-space: nowrap;
        }

        .concern-high {
            background: #FFF0EE;
            color: #A33A2F;
            border: 1px solid #F4C7BF;
        }

        .concern-medium {
            background: #FFF4D6;
            color: #8A5A12;
            border: 1px solid #E6C879;
        }

        .concern-low {
            background: #EAF7F0;
            color: #216E46;
            border: 1px solid #BFE3CF;
        }

        .meaning-row {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
            margin-bottom: 0.55rem;
        }

        .meaning-title {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 950;
            margin-bottom: 0.18rem;
        }

        .meaning-text {
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.4;
        }

        .checklist-section {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 26px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .checklist-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 0.75rem;
        }

        .checklist-item {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
        }

        .checklist-title {
            color: var(--text-main);
            font-size: 0.92rem;
            font-weight: 950;
            margin-bottom: 0.22rem;
        }

        .checklist-text {
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.4;
        }

        @media (max-width: 1000px) {
            .snapshot-grid,
            .main-layout,
            .checklist-grid {
                grid-template-columns: 1fr;
            }

            .concern-row {
                grid-template-columns: 1fr;
            }

            .concern-badge {
                width: fit-content;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    render_html("""
    <div class="insights-header">
        <div class="insights-badge">Booking insights</div>
        <div class="insights-title">Booking Insights</div>
        <div class="insights-subtitle">
            See what travellers commonly mention in this area before choosing a hotel.
            This page helps you know what to check before booking.
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


def render_area_advice(selected_area, complaint_df):
    advice = get_area_advice(selected_area, complaint_df)

    render_html(f"""
    <div class="area-advice-card">
        <div class="area-advice-label">Area booking advice</div>
        <div class="area-advice-text">{escape(advice)}</div>
    </div>
    """)


def render_area_snapshot(selected_area, hotels, complaint_df):
    common_positive = get_common_positive_signal(hotels)
    main_warning = get_area_warning(complaint_df)

    render_html(f"""
    <div class="snapshot-grid">
        <div class="snapshot-card">
            <div class="snapshot-label">Selected area</div>
            <div class="snapshot-value">{escape(selected_area)}</div>
            <div class="snapshot-sub">{len(hotels)} hotel option(s) in this dataset</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Common positive signal</div>
            <div class="snapshot-value">{escape(common_positive)}</div>
            <div class="snapshot-sub">A strength mentioned in available hotel summaries</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Main thing to check</div>
            <div class="snapshot-value">{escape(main_warning)}</div>
            <div class="snapshot-sub">A repeated review topic in this area</div>
        </div>
    </div>
    """)


def render_common_concerns(complaint_df):
    if complaint_df.empty:
        render_html("""
        <div class="insight-card">
            <div class="card-title">Most repeated concerns in this area</div>
            <div class="card-desc">No repeated concern pattern was found for this area.</div>
        </div>
        """)
        return

    rows_html = ""
    top_df = complaint_df.head(6)
    max_count = safe_number(top_df["Complaint Count"].max(), 0)

    for _, row in top_df.iterrows():
        concern = row["Complaint Area"]
        count = safe_number(row["Complaint Count"], 0)
        label = concern_frequency_label(count, max_count)
        label_class = concern_frequency_class(count, max_count)

        rows_html += f"""
        <div class="concern-row">
            <div>
                <div class="concern-name">{escape(concern)}</div>
                <div class="concern-help">
                    This is a repeated review topic. Check recent reviews to see whether it still appears.
                </div>
            </div>
            <div class="concern-badge {label_class}">{escape(label)}</div>
        </div>
        """

    render_html(f"""
    <div class="insight-card">
        <div class="card-title">Most repeated concerns in this area</div>
        <div class="card-desc">
            These labels show how often each issue appears compared with other concerns in the same area.
        </div>
        {rows_html}
    </div>
    """)


def render_concern_meanings(complaint_df):
    if complaint_df.empty:
        render_html("""
        <div class="insight-card">
            <div class="card-title">What these concerns mean</div>
            <div class="card-desc">No concern explanation is available because no repeated pattern was found.</div>
        </div>
        """)
        return

    meaning_html = ""

    for _, row in complaint_df.head(5).iterrows():
        concern = row["Complaint Area"]
        meaning = get_concern_meaning(concern)

        meaning_html += f"""
        <div class="meaning-row">
            <div class="meaning-title">{escape(concern)}</div>
            <div class="meaning-text">{escape(meaning)}</div>
        </div>
        """

    render_html(f"""
    <div class="insight-card">
        <div class="card-title">What these concerns may mean for your stay</div>
        <div class="card-desc">
            A simple explanation of why these review topics may matter to travellers.
        </div>
        {meaning_html}
    </div>
    """)


def render_booking_checklist(complaint_df):
    checklist_html = ""

    if complaint_df.empty:
        checklist_html += """
        <div class="checklist-item">
            <div class="checklist-title">Read several recent reviews</div>
            <div class="checklist-text">
                No repeated concern was found, but one review should not decide everything.
            </div>
        </div>
        """
    else:
        for _, row in complaint_df.head(4).iterrows():
            concern = row["Complaint Area"]

            checklist_html += f"""
            <div class="checklist-item">
                <div class="checklist-title">Check {escape(concern)}</div>
                <div class="checklist-text">
                    Look for recent reviews mentioning this topic. If many guests mention the same issue,
                    compare another hotel before booking.
                </div>
            </div>
            """

    checklist_html += """
    <div class="checklist-item">
        <div class="checklist-title">Compare more than one hotel</div>
        <div class="checklist-text">
            A hotel can still be suitable even if it has some concerns. Compare repeated issues, positive signals, and suitability.
        </div>
    </div>

    <div class="checklist-item">
        <div class="checklist-title">Focus on repeated patterns</div>
        <div class="checklist-text">
            One negative review may not represent the whole hotel. Repeated comments are more useful for booking decisions.
        </div>
    </div>
    """

    render_html(f"""
    <div class="checklist-section">
        <div class="card-title">Before booking checklist</div>
        <div class="card-desc">
            Use this checklist when reading hotel reviews in this area.
        </div>

        <div class="checklist-grid">
            {checklist_html}
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
render_area_advice(selected_area, complaint_df)
render_area_snapshot(selected_area, hotels, complaint_df)

left_col, right_col = st.columns(2, gap="large")

with left_col:
    render_common_concerns(complaint_df)

with right_col:
    render_concern_meanings(complaint_df)

render_booking_checklist(complaint_df)

render_footer()