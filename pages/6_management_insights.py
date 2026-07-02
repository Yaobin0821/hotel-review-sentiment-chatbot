import html
from urllib.parse import quote

import pandas as pd
import streamlit as st

from styles import load_css, render_topbar, render_footer
from utils import (
    get_areas,
    get_hotels_by_area,
    get_hotel_by_name,
    get_complaint_df,
    risk_badge
)


st.set_page_config(
    page_title="Management Insights",
    page_icon="🛠️",
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


def get_selected_hotel(hotels):
    hotel_names = [hotel["hotel"] for hotel in hotels]

    if not hotel_names:
        return None

    selected_hotel = get_query_value("hotel", hotel_names[0])

    if selected_hotel not in hotel_names:
        selected_hotel = hotel_names[0]

    return selected_hotel


def priority_rank(priority_level):
    priority = str(priority_level).lower()

    if priority == "high":
        return 1

    if priority == "medium":
        return 2

    if priority == "low":
        return 3

    return 4


def derive_priority(count, max_count):
    if max_count <= 0:
        return "Low"

    ratio = count / max_count

    if ratio >= 0.7:
        return "High"

    if ratio >= 0.35:
        return "Medium"

    return "Low"


def normalize_priority(row, max_count):
    priority = str(row.get("Priority Level", "")).strip().title()

    if priority in ["High", "Medium", "Low"]:
        return priority

    count = safe_number(row.get("Complaint Count", 0))
    return derive_priority(count, max_count)


def priority_class(priority_level):
    priority = str(priority_level).lower()

    if priority == "high":
        return "priority-high"

    if priority == "medium":
        return "priority-medium"

    return "priority-low"


def risk_class_name(risk_level):
    risk = str(risk_level).lower()

    if risk == "low":
        return "risk-low"

    if risk == "high":
        return "risk-high"

    return "risk-medium"


def get_issue_impact(issue):
    issue_lower = str(issue).lower()

    if "clean" in issue_lower or "hygiene" in issue_lower:
        return "May affect guest comfort, room freshness, bathroom condition, and trust in the hotel."

    if "room" in issue_lower or "noise" in issue_lower or "comfort" in issue_lower:
        return "May affect sleep quality, rest experience, and overall room satisfaction."

    if "breakfast" in issue_lower or "food" in issue_lower:
        return "May affect guest value perception, morning convenience, and dining satisfaction."

    if "check-in" in issue_lower or "booking" in issue_lower or "payment" in issue_lower:
        return "May affect arrival experience, waiting time, booking confidence, and payment clarity."

    if "facility" in issue_lower or "maintenance" in issue_lower:
        return "May affect guest convenience if room facilities or hotel equipment are not working properly."

    if "service" in issue_lower or "staff" in issue_lower:
        return "May affect guest satisfaction, complaint handling, and the feeling of being supported."

    if "parking" in issue_lower or "transport" in issue_lower or "access" in issue_lower:
        return "May affect convenience, especially for guests travelling with cars or luggage."

    if "overall" in issue_lower or "experience" in issue_lower:
        return "This is a broad signal that guests are commenting on the overall stay experience."

    return "This issue may affect the guest experience and should be reviewed by management."


def get_action_steps(issue, suggested_action):
    issue_lower = str(issue).lower()

    if "clean" in issue_lower or "hygiene" in issue_lower:
        return [
            "Review housekeeping checklist and room inspection standards.",
            "Increase bathroom and bedding quality checks before guest check-in.",
            "Monitor recent cleanliness-related reviews weekly."
        ]

    if "room" in issue_lower or "noise" in issue_lower or "comfort" in issue_lower:
        return [
            "Inspect air-conditioning, lighting, bedding, and room facilities regularly.",
            "Identify rooms with repeated noise or comfort complaints.",
            "Prioritise maintenance for rooms mentioned repeatedly in reviews."
        ]

    if "breakfast" in issue_lower or "food" in issue_lower:
        return [
            "Review breakfast quality, variety, and serving consistency.",
            "Track repeated food-related complaints from guest reviews.",
            "Adjust menu or service flow based on recurring feedback."
        ]

    if "check-in" in issue_lower or "booking" in issue_lower or "payment" in issue_lower:
        return [
            "Review front desk workflow during peak check-in hours.",
            "Improve booking confirmation and payment communication.",
            "Train staff to handle arrival and payment issues more clearly."
        ]

    if "facility" in issue_lower or "maintenance" in issue_lower:
        return [
            "Create a recurring facility maintenance checklist.",
            "Respond faster to repeated room or facility defect reports.",
            "Track maintenance-related review patterns by room or facility type."
        ]

    if "service" in issue_lower or "staff" in issue_lower:
        return [
            "Review staff response time and complaint handling process.",
            "Provide refresher training for guest communication.",
            "Monitor service-related review trends after improvement actions."
        ]

    if "overall" in issue_lower or "experience" in issue_lower:
        return [
            "Review the full guest journey from booking to check-out.",
            "Identify which review topics are affecting overall satisfaction.",
            "Prioritise improvements that appear repeatedly across multiple reviews."
        ]

    if suggested_action and suggested_action != "Not stated":
        return [
            str(suggested_action),
            "Monitor whether this issue continues to appear in recent reviews.",
            "Review this area again after implementing improvement actions."
        ]

    return [
        "Review recent guest comments related to this issue.",
        "Identify the operational process connected to the complaint.",
        "Track whether the issue improves over time."
    ]


def prepare_management_df(complaint_df):
    if complaint_df is None or complaint_df.empty:
        return pd.DataFrame(columns=[
            "Complaint Area",
            "Complaint Count",
            "Priority Level",
            "Suggested Improvement Action"
        ])

    df = complaint_df.copy()

    if "Complaint Count" not in df.columns:
        df["Complaint Count"] = 0

    if "Complaint Area" not in df.columns:
        df["Complaint Area"] = "Other"

    if "Suggested Improvement Action" not in df.columns:
        df["Suggested Improvement Action"] = "Review recent guest reviews for this issue."

    max_count = safe_number(df["Complaint Count"].max(), 0)

    df["Priority Level"] = df.apply(
        lambda row: normalize_priority(row, max_count),
        axis=1
    )

    df["Complaint Count"] = df["Complaint Count"].apply(
        lambda x: int(safe_number(x, 0))
    )

    df["Priority Rank"] = df["Priority Level"].apply(priority_rank)

    df = df.sort_values(
        by=["Priority Rank", "Complaint Count"],
        ascending=[True, False]
    )

    df = df.drop(columns=["Priority Rank"])

    return df


def get_management_summary(hotel, management_df):
    if management_df.empty:
        top_issue = "No repeated issue found"
        high_priority_count = 0
    else:
        top_issue = management_df.iloc[0]["Complaint Area"]
        high_priority_count = len(
            management_df[management_df["Priority Level"].str.lower() == "high"]
        )

    negative_pct = safe_get(hotel, "negative_pct", 0)
    risk_level = safe_get(hotel, "risk_level", "Medium")

    if high_priority_count > 0 or str(risk_level).lower() == "high":
        urgency = "Immediate attention"
    elif safe_number(negative_pct, 0) >= 15:
        urgency = "Needs monitoring"
    else:
        urgency = "Maintain standards"

    return {
        "top_issue": top_issue,
        "high_priority_count": high_priority_count,
        "urgency": urgency
    }


def load_management_css():
    st.markdown("""
    <style>
        .mgmt-header {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem 1.45rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .mgmt-badge {
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

        .mgmt-title {
            color: var(--text-main);
            font-size: clamp(2rem, 4vw, 2.9rem);
            font-weight: 950;
            letter-spacing: -0.07em;
            line-height: 1.05;
            margin-bottom: 0.25rem;
        }

        .mgmt-subtitle {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .access-card {
            max-width: 620px;
            margin: 1rem auto 1.2rem auto;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.2rem;
            box-shadow: var(--shadow-card);
        }

        .access-title {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.25rem;
        }

        .access-desc {
            color: #64748B;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 0.9rem;
        }

        .access-note {
            background: #FFF8EF;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.8rem;
            color: #7C6F64;
            font-size: 0.82rem;
            line-height: 1.45;
            margin-top: 0.8rem;
        }

        .management-mode-bar {
            background: #EAF7F0;
            border: 1px solid #BFE3CF;
            color: #216E46;
            border-radius: 18px;
            padding: 0.75rem 0.9rem;
            font-size: 0.86rem;
            font-weight: 850;
            margin-bottom: 0.85rem;
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

        .choice-chip,
        .hotel-chip {
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

        .choice-chip:hover,
        .hotel-chip:hover {
            background: #FFF4E8;
            border-color: var(--brand);
            transform: translateY(-1px);
        }

        .choice-chip.active,
        .hotel-chip.active {
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-color: transparent;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.18);
        }

        .hotel-chip-row {
            display: flex;
            gap: 0.45rem;
            overflow-x: auto;
            padding-bottom: 0.2rem;
        }

        .hotel-chip {
            flex: 0 0 auto;
            max-width: 330px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .summary-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 26px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.9rem;
        }

        .summary-label {
            color: #9B4325;
            font-size: 0.72rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .summary-text {
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 850;
            line-height: 1.45;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-bottom: 0.9rem;
        }

        .metric-card,
        .mgmt-card,
        .table-section {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.85rem;
        }

        .metric-label {
            color: #7C6F64;
            font-size: 0.68rem;
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        .metric-value {
            color: var(--text-main);
            font-size: 1.04rem;
            font-weight: 950;
            line-height: 1.25;
        }

        .metric-sub {
            color: #64748B;
            font-size: 0.76rem;
            font-weight: 750;
            margin-top: 0.25rem;
            line-height: 1.35;
        }

        .card-title {
            color: var(--text-main);
            font-size: 1.16rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.2rem;
        }

        .card-desc {
            color: #64748B;
            font-size: 0.82rem;
            line-height: 1.4;
            margin-bottom: 0.85rem;
        }

        .priority-list {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }

        .priority-item,
        .action-card {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
            margin-bottom: 0.6rem;
        }

        .priority-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.65rem;
            margin-bottom: 0.35rem;
        }

        .priority-title,
        .action-title {
            color: var(--text-main);
            font-size: 0.96rem;
            font-weight: 950;
            line-height: 1.3;
        }

        .priority-impact {
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.4;
            margin-top: 0.2rem;
        }

        .priority-badge,
        .risk-chip {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border-radius: 999px;
            padding: 0.38rem 0.68rem;
            font-size: 0.74rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .priority-high,
        .risk-high {
            background: #FFF0EE;
            color: #A33A2F;
            border: 1px solid #F4C7BF;
        }

        .priority-medium,
        .risk-medium {
            background: #FFF4D6;
            color: #8A5A12;
            border: 1px solid #E6C879;
        }

        .priority-low,
        .risk-low {
            background: #EAF7F0;
            color: #216E46;
            border: 1px solid #BFE3CF;
        }

        .action-list {
            margin: 0;
            padding-left: 1.1rem;
            color: #64748B;
            font-size: 0.8rem;
            line-height: 1.45;
        }

        .action-list li {
            margin-bottom: 0.25rem;
        }

        @media (max-width: 1000px) {
            .metric-grid {
                grid-template-columns: 1fr;
            }

            .priority-top {
                flex-direction: column;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    render_html("""
    <div class="mgmt-header">
        <div class="mgmt-badge">For hotel management</div>
        <div class="mgmt-title">Management Insights</div>
        <div class="mgmt-subtitle">
            Convert aggregated guest review complaints into improvement priorities and suggested management actions.
        </div>
    </div>
    """)


def require_management_access():
    access_code = st.secrets.get("MANAGEMENT_ACCESS_CODE", "staff123")

    if st.session_state.get("management_access_granted", False):
        return

    render_html("""
    <div class="access-card">
        <div class="access-title">Staff Access Required</div>
        <div class="access-desc">
            This page is designed for hotel management users only. Enter the management access code to view improvement priorities and action plans.
        </div>
        <div class="access-note">
            Prototype note: This system does not include a full login system. A simple access code is used to separate management-facing features from traveller-facing pages.
        </div>
    </div>
    """)

    entered_code = st.text_input(
        "Management access code",
        type="password",
        placeholder="Enter staff access code"
    )

    if st.button("Enter Management Portal", use_container_width=True):
        if entered_code == access_code:
            st.session_state["management_access_granted"] = True
            st.rerun()
        else:
            st.error("Incorrect access code. Please try again.")

    render_footer()
    st.stop()


def render_management_mode_bar():
    col1, col2 = st.columns([0.78, 0.22], gap="medium")

    with col1:
        render_html("""
        <div class="management-mode-bar">
            Management mode is active. This page is separated from the public traveller pages.
        </div>
        """)

    with col2:
        if st.button("Exit Management Mode", use_container_width=True):
            st.session_state["management_access_granted"] = False
            st.rerun()


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


def render_hotel_choices(hotels, selected_area, selected_hotel):
    chips_html = ""

    for hotel in hotels:
        hotel_name = safe_get(hotel, "hotel")
        active_class = "active" if hotel_name == selected_hotel else ""

        area_url = quote(selected_area, safe="")
        hotel_url = quote(hotel_name, safe="")

        chips_html += (
            f'<a class="hotel-chip {active_class}" '
            f'href="?area={area_url}&hotel={hotel_url}" '
            f'target="_self">{escape(hotel_name)}</a>'
        )

    render_html(f"""
    <div class="choice-card">
        <div class="section-label">Choose hotel</div>
        <div class="hotel-chip-row">{chips_html}</div>
    </div>
    """)


def render_management_summary(hotel, management_df):
    summary = get_management_summary(hotel, management_df)
    hotel_name = safe_get(hotel, "hotel")

    render_html(f"""
    <div class="summary-card">
        <div class="summary-label">Hotel improvement summary</div>
        <div class="summary-text">
            For {escape(hotel_name)}, the main improvement focus is
            <b>{escape(summary["top_issue"])}</b>. Current urgency level:
            <b>{escape(summary["urgency"])}</b>.
        </div>
    </div>
    """)


def render_metrics(hotel, management_df):
    summary = get_management_summary(hotel, management_df)
    risk_level = safe_get(hotel, "risk_level", "Medium")
    risk_class = risk_class_name(risk_level)

    render_html(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Risk level</div>
            <div class="metric-value">
                <span class="risk-chip {risk_class}">{escape(risk_badge(risk_level))}</span>
            </div>
            <div class="metric-sub">Based on aggregated review signals</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Negative reviews</div>
            <div class="metric-value">{escape(safe_get(hotel, "negative_pct", 0))}%</div>
            <div class="metric-sub">Share of reviews with negative sentiment</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Top issue</div>
            <div class="metric-value">{escape(summary["top_issue"])}</div>
            <div class="metric-sub">Most important repeated complaint area</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">High priority items</div>
            <div class="metric-value">{escape(summary["high_priority_count"])}</div>
            <div class="metric-sub">Issues requiring stronger management attention</div>
        </div>
    </div>
    """)


def render_priority_areas(management_df):
    if management_df.empty:
        render_html("""
        <div class="mgmt-card">
            <div class="card-title">Priority improvement areas</div>
            <div class="card-desc">No repeated complaint pattern was found for this hotel.</div>
        </div>
        """)
        return

    rows_html = ""

    for _, row in management_df.head(6).iterrows():
        issue = row["Complaint Area"]
        priority = row["Priority Level"]
        count = row["Complaint Count"]
        priority_cls = priority_class(priority)
        impact = get_issue_impact(issue)

        rows_html += f"""
        <div class="priority-item">
            <div class="priority-top">
                <div>
                    <div class="priority-title">{escape(issue)}</div>
                    <div class="priority-impact">{escape(impact)}</div>
                </div>
                <span class="priority-badge {priority_cls}">{escape(priority)} priority</span>
            </div>
            <div class="metric-sub">{escape(count)} related complaint signal(s)</div>
        </div>
        """

    render_html(f"""
    <div class="mgmt-card">
        <div class="card-title">Priority improvement areas</div>
        <div class="card-desc">
            These are the main complaint areas management should review first.
        </div>
        <div class="priority-list">
            {rows_html}
        </div>
    </div>
    """)


def render_action_plan(management_df):
    if management_df.empty:
        render_html("""
        <div class="mgmt-card">
            <div class="card-title">Recommended action plan</div>
            <div class="card-desc">No action plan is available because no repeated complaint pattern was found.</div>
        </div>
        """)
        return

    action_html = ""

    for _, row in management_df.head(3).iterrows():
        issue = row["Complaint Area"]
        suggested_action = row.get("Suggested Improvement Action", "Not stated")
        steps = get_action_steps(issue, suggested_action)

        steps_html = ""

        for step in steps:
            steps_html += f"<li>{escape(step)}</li>"

        action_html += f"""
        <div class="action-card">
            <div class="action-title">{escape(issue)}</div>
            <ul class="action-list">
                {steps_html}
            </ul>
        </div>
        """

    render_html(f"""
    <div class="mgmt-card">
        <div class="card-title">Recommended action plan</div>
        <div class="card-desc">
            Suggested operational actions based on the highest priority complaint areas.
        </div>
        {action_html}
    </div>
    """)


def render_review_signal_summary(hotel):
    render_html(f"""
    <div class="mgmt-card">
        <div class="card-title">Review signal summary</div>
        <div class="card-desc">
            A quick view of the hotel's overall review condition.
        </div>

        <div class="action-card">
            <div class="action-title">Sentiment distribution</div>
            <ul class="action-list">
                <li>Positive reviews: {escape(safe_get(hotel, "positive_pct", 0))}%</li>
                <li>Neutral reviews: {escape(safe_get(hotel, "neutral_pct", 0))}%</li>
                <li>Negative reviews: {escape(safe_get(hotel, "negative_pct", 0))}%</li>
            </ul>
        </div>

        <div class="action-card">
            <div class="action-title">Key review signals</div>
            <ul class="action-list">
                <li>Main strength: {escape(safe_get(hotel, "main_strength"))}</li>
                <li>Main risk: {escape(safe_get(hotel, "main_risk"))}</li>
                <li>Total reviews analysed: {escape(get_review_count(hotel))}</li>
            </ul>
        </div>
    </div>
    """)


def render_management_table(management_df, hotel_name):
    if management_df.empty:
        return

    table_df = management_df[[
        "Complaint Area",
        "Complaint Count",
        "Priority Level",
        "Suggested Improvement Action"
    ]].copy()

    render_html("""
    <div class="table-section">
        <div class="card-title">Detailed improvement table</div>
        <div class="card-desc">
            A structured management view of complaint areas, priority levels, and suggested improvement actions.
        </div>
    </div>
    """)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = table_df.to_csv(index=False).encode("utf-8")

    safe_filename = (
        hotel_name
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    st.download_button(
        label="Download improvement report CSV",
        data=csv_data,
        file_name=f"{safe_filename}_improvement_report.csv",
        mime="text/csv",
        use_container_width=True
    )


load_css()
load_management_css()
render_topbar()
render_header()

require_management_access()
render_management_mode_bar()

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

selected_hotel_name = get_selected_hotel(hotels)

render_area_choices(areas, selected_area)
render_hotel_choices(hotels, selected_area, selected_hotel_name)

hotel = get_hotel_by_name(selected_hotel_name)

if hotel is None:
    st.error("Hotel data could not be loaded. Please check your dataset.")
    render_footer()
    st.stop()

complaint_df = get_complaint_df(hotel)
management_df = prepare_management_df(complaint_df)

render_management_summary(hotel, management_df)
render_metrics(hotel, management_df)

main_col, side_col = st.columns([1.25, 0.85], gap="large")

with main_col:
    render_priority_areas(management_df)

with side_col:
    render_action_plan(management_df)
    render_review_signal_summary(hotel)

render_management_table(management_df, selected_hotel_name)

render_footer()