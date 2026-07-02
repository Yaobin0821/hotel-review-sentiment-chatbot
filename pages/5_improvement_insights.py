import html
from urllib.parse import quote

import pandas as pd
import streamlit as st

from styles import load_css, render_topbar, render_footer
from utils import (
    get_areas,
    get_hotels_by_area,
    get_complaint_df,
    risk_badge
)


st.set_page_config(
    page_title="Travel Insights",
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


def risk_score(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return 1

    if risk == "medium":
        return 2

    if risk == "high":
        return 3

    return 2


def risk_class_name(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return "risk-low"

    if risk == "high":
        return "risk-high"

    return "risk-medium"


def concern_frequency_label(count, max_count):
    if max_count <= 0:
        return "Review signal"

    percentage = count / max_count

    if percentage >= 0.7:
        return "Mentioned often"

    if percentage >= 0.35:
        return "Common concern"

    return "Occasional concern"


def concern_frequency_class(count, max_count):
    if max_count <= 0:
        return "concern-low"

    percentage = count / max_count

    if percentage >= 0.7:
        return "concern-high"

    if percentage >= 0.35:
        return "concern-medium"

    return "concern-low"


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

        .area-note {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 24px;
            padding: 0.95rem 1.05rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .area-note-title {
            color: var(--text-main);
            font-size: 1.08rem;
            font-weight: 950;
            letter-spacing: -0.035em;
            margin-bottom: 0.22rem;
        }

        .area-note-text {
            color: #64748B;
            font-size: 0.88rem;
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
            grid-template-columns: 1.05fr 0.95fr;
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

        .hotel-rank-card {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.8rem;
            margin-bottom: 0.55rem;
        }

        .hotel-rank-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .hotel-rank-name {
            color: var(--text-main);
            font-size: 0.95rem;
            font-weight: 950;
            line-height: 1.3;
        }

        .hotel-rank-meta {
            color: #64748B;
            font-size: 0.78rem;
            font-weight: 750;
            margin-top: 0.15rem;
        }

        .risk-chip {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border-radius: 999px;
            padding: 0.38rem 0.68rem;
            font-size: 0.76rem;
            font-weight: 850;
            white-space: nowrap;
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

        .quick-note {
            background: #FFF8EF;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.8rem;
            color: var(--text-main);
            font-size: 0.88rem;
            font-weight: 750;
            line-height: 1.5;
            margin-bottom: 0.85rem;
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
        <div class="insights-badge">Traveller insights</div>
        <div class="insights-title">Travel Insights</div>
        <div class="insights-subtitle">
            Understand common hotel review patterns before booking. This page focuses on what travellers should check, not hotel management reports.
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


def get_area_snapshot(hotels, complaint_df):
    safest_hotel = min(
        hotels,
        key=lambda h: (
            risk_score(safe_get(h, "risk_level")),
            -safe_number(safe_get(h, "positive_pct", 0))
        )
    )

    most_positive_hotel = max(
        hotels,
        key=lambda h: safe_number(safe_get(h, "positive_pct", 0))
    )

    if complaint_df.empty:
        top_concern = "No repeated concern found"
    else:
        top_concern = complaint_df.iloc[0]["Complaint Area"]

    return safest_hotel, most_positive_hotel, top_concern


def render_area_note(selected_area, hotels):
    render_html(f"""
    <div class="area-note">
        <div class="area-note-title">{escape(selected_area)} travel review overview</div>
        <div class="area-note-text">
            Based on the available hotel reviews, this area has {len(hotels)} hotel option(s) in the dataset.
            Use the summary below to quickly understand which hotel looks safer and what issues travellers should check before booking.
        </div>
    </div>
    """)


def render_snapshot(selected_area, hotels, complaint_df):
    safest_hotel, most_positive_hotel, top_concern = get_area_snapshot(hotels, complaint_df)

    render_html(f"""
    <div class="snapshot-grid">
        <div class="snapshot-card">
            <div class="snapshot-label">Safest-looking option</div>
            <div class="snapshot-value">{escape(safe_get(safest_hotel, "hotel"))}</div>
            <div class="snapshot-sub">{escape(safe_get(safest_hotel, "risk_level"))} booking concern</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Most positive reviews</div>
            <div class="snapshot-value">{escape(safe_get(most_positive_hotel, "hotel"))}</div>
            <div class="snapshot-sub">{escape(safe_get(most_positive_hotel, "positive_pct", 0))}% positive</div>
        </div>

        <div class="snapshot-card">
            <div class="snapshot-label">Main thing to check</div>
            <div class="snapshot-value">{escape(top_concern)}</div>
            <div class="snapshot-sub">A repeated topic found in guest reviews</div>
        </div>
    </div>
    """)


def render_common_concerns(complaint_df):
    if complaint_df.empty:
        render_html("""
        <div class="insight-card">
            <div class="card-title">Most repeated concerns in this area</div>
            <div class="card-desc">No repeated complaint pattern was found for this area.</div>
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
                    This issue appears in guest review patterns. Check recent reviews before booking.
                </div>
            </div>
            <div class="concern-badge {label_class}">{escape(label)}</div>
        </div>
        """

    render_html(f"""
    <div class="insight-card">
        <div class="card-title">Most repeated concerns in this area</div>
        <div class="card-desc">
            These are common issues mentioned by guests. The labels show how often the issue appears compared with other concerns in this area.
        </div>
        {rows_html}
    </div>
    """)


def render_hotels_to_consider(hotels):
    ranked_hotels = sorted(
        hotels,
        key=lambda h: (
            risk_score(safe_get(h, "risk_level")),
            -safe_number(safe_get(h, "positive_pct", 0)),
            safe_number(safe_get(h, "negative_pct", 0))
        )
    )

    cards_html = ""

    for hotel in ranked_hotels[:4]:
        risk_level = safe_get(hotel, "risk_level")
        risk_class = risk_class_name(risk_level)

        cards_html += f"""
        <div class="hotel-rank-card">
            <div class="hotel-rank-top">
                <div>
                    <div class="hotel-rank-name">{escape(safe_get(hotel, "hotel"))}</div>
                    <div class="hotel-rank-meta">
                        {escape(safe_get(hotel, "area"))} · {escape(get_review_count(hotel))} reviews
                    </div>
                </div>
                <span class="risk-chip {risk_class}">{escape(risk_badge(risk_level))}</span>
            </div>
            <div class="quick-note">
                {escape(safe_get(hotel, "positive_pct", 0))}% positive reviews.
                Guests often mention <b>{escape(safe_get(hotel, "main_strength"))}</b>.
                Check <b>{escape(safe_get(hotel, "main_risk"))}</b> before booking.
            </div>
        </div>
        """

    render_html(f"""
    <div class="insight-card">
        <div class="card-title">Hotels worth checking first</div>
        <div class="card-desc">
            These hotels are ranked by lower booking concern and stronger positive review signals.
        </div>
        {cards_html}
    </div>
    """)


def render_booking_checklist(complaint_df):
    if complaint_df.empty:
        checklist_html = """
        <div class="checklist-item">
            <div class="checklist-title">Compare more than one review</div>
            <div class="checklist-text">
                No repeated concern was found, but one review should not decide everything. Read a few recent reviews before booking.
            </div>
        </div>
        """
    else:
        checklist_html = ""

        for _, row in complaint_df.head(4).iterrows():
            concern = row["Complaint Area"]

            checklist_html += f"""
            <div class="checklist-item">
                <div class="checklist-title">Check {escape(concern)}</div>
                <div class="checklist-text">
                    Look for recent reviews mentioning this issue. If many guests mention the same thing,
                    compare another hotel before deciding.
                </div>
            </div>
            """

    render_html(f"""
    <div class="checklist-section">
        <div class="card-title">Before booking checklist</div>
        <div class="card-desc">
            Use this as a quick reminder when reading hotel reviews.
        </div>

        <div class="checklist-grid">
            {checklist_html}

            <div class="checklist-item">
                <div class="checklist-title">Compare at least two hotels</div>
                <div class="checklist-text">
                    A hotel can still be suitable even if it has some concerns. Compare risk level, positive reviews, and repeated complaint areas.
                </div>
            </div>

            <div class="checklist-item">
                <div class="checklist-title">Focus on repeated patterns</div>
                <div class="checklist-text">
                    One bad comment may not represent the whole hotel. Repeated concerns are more useful for booking decisions.
                </div>
            </div>
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
render_area_note(selected_area, hotels)
render_snapshot(selected_area, hotels, complaint_df)

left_col, right_col = st.columns([1.05, 0.95], gap="large")

with left_col:
    render_common_concerns(complaint_df)

with right_col:
    render_hotels_to_consider(hotels)

render_booking_checklist(complaint_df)

render_footer()