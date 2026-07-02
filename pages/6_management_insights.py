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
    get_hotel_reviews,
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
    if data is None:
        return default

    if isinstance(data, dict):
        value = data.get(key, default)
    else:
        value = getattr(data, key, default)

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


def has_management_access():
    access_value = st.query_params.get("mgmt_access", "")

    if isinstance(access_value, list):
        access_value = access_value[0]

    if access_value == "1":
        st.session_state["management_access_granted"] = True

    return st.session_state.get("management_access_granted", False)


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


def get_selected_issue(management_df):
    if management_df is None or management_df.empty:
        return ""

    issues = management_df["Complaint Area"].astype(str).tolist()
    selected_issue = get_query_value("issue", issues[0])

    if selected_issue not in issues:
        selected_issue = issues[0]

    return selected_issue


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


def risk_text(risk_level):
    level = str(risk_level).title()
    return f"{level} Risk"


def get_issue_impact(issue):
    issue_lower = str(issue).lower()

    if "clean" in issue_lower or "hygiene" in issue_lower:
        return "May affect room cleanliness, bathroom condition, and guest trust."

    if "room" in issue_lower or "noise" in issue_lower or "comfort" in issue_lower:
        return "May affect sleep quality, comfort, and overall room satisfaction."

    if "breakfast" in issue_lower or "food" in issue_lower:
        return "May affect value perception and dining satisfaction."

    if "check-in" in issue_lower or "booking" in issue_lower or "payment" in issue_lower:
        return "May affect the arrival experience, waiting time, and booking confidence."

    if "facility" in issue_lower or "maintenance" in issue_lower:
        return "May affect convenience if hotel facilities are not functioning properly."

    if "service" in issue_lower or "staff" in issue_lower:
        return "May affect guest satisfaction and complaint handling quality."

    if "parking" in issue_lower or "transport" in issue_lower or "access" in issue_lower:
        return "May affect convenience, especially for guests travelling with luggage or cars."

    if "price" in issue_lower or "value" in issue_lower:
        return "May affect whether guests feel the hotel stay was worth the price."

    if "overall" in issue_lower or "experience" in issue_lower:
        return "This is a broad signal that overall guest satisfaction may be affected."

    return "This issue may affect the overall guest experience and should be reviewed."


def get_action_steps(issue, suggested_action):
    issue_lower = str(issue).lower()

    if "clean" in issue_lower or "hygiene" in issue_lower:
        return [
            "Review housekeeping checklist and room inspection standards.",
            "Increase checks for bathrooms, bedding, and room cleanliness before check-in.",
            "Track whether cleanliness complaints continue in recent reviews."
        ]

    if "room" in issue_lower or "noise" in issue_lower or "comfort" in issue_lower:
        return [
            "Inspect bedding, air-conditioning, lighting, and room condition regularly.",
            "Identify rooms with repeated comfort or noise complaints.",
            "Prioritise maintenance for rooms repeatedly mentioned in reviews."
        ]

    if "breakfast" in issue_lower or "food" in issue_lower:
        return [
            "Review breakfast quality, variety, and serving consistency.",
            "Track recurring food-related complaints.",
            "Improve service flow or menu choices based on guest feedback."
        ]

    if "check-in" in issue_lower or "booking" in issue_lower or "payment" in issue_lower:
        return [
            "Review front desk workflow during busy arrival periods.",
            "Improve booking confirmation and payment communication.",
            "Train staff to handle arrival and payment issues more clearly."
        ]

    if "facility" in issue_lower or "maintenance" in issue_lower:
        return [
            "Create a recurring facility maintenance checklist.",
            "Respond faster to room or facility defect reports.",
            "Track maintenance-related review trends over time."
        ]

    if "service" in issue_lower or "staff" in issue_lower:
        return [
            "Review staff response time and complaint handling process.",
            "Provide refresher training for guest communication.",
            "Monitor service-related review trends after changes are made."
        ]

    if "parking" in issue_lower or "transport" in issue_lower or "access" in issue_lower:
        return [
            "Provide clearer parking and transport information before arrival.",
            "Monitor repeated access-related complaints.",
            "Improve guidance for guests travelling by car or ride-hailing service."
        ]

    if "price" in issue_lower or "value" in issue_lower:
        return [
            "Review whether room condition and service quality match the price point.",
            "Highlight value-added services more clearly.",
            "Monitor value-for-money complaints after pricing or service changes."
        ]

    if "overall" in issue_lower or "experience" in issue_lower:
        return [
            "Review the full guest journey from booking to check-out.",
            "Identify which operational areas most affect satisfaction.",
            "Prioritise issues that appear repeatedly across reviews."
        ]

    if suggested_action and suggested_action != "Not stated":
        return [
            str(suggested_action),
            "Monitor whether this issue still appears in recent reviews.",
            "Review again after improvement actions are implemented."
        ]

    return [
        "Review recent guest comments related to this issue.",
        "Identify the operational process linked to the complaint.",
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


def get_review_field(review, possible_keys, default=""):
    if review is None:
        return default

    if isinstance(review, dict):
        for key in possible_keys:
            if key in review and review[key] not in [None, ""]:
                return str(review[key])
    else:
        for key in possible_keys:
            try:
                value = getattr(review, key)
                if value not in [None, ""]:
                    return str(value)
            except Exception:
                pass

    return default


def normalize_review_records(reviews):
    if reviews is None:
        return []

    if isinstance(reviews, pd.DataFrame):
        return reviews.to_dict("records")

    if isinstance(reviews, list):
        return reviews

    return []


def get_review_text(review):
    return get_review_field(
        review,
        [
            "Sentence",
            "sentence",
            "Review",
            "review",
            "Review Text",
            "review_text",
            "Original_Review",
            "Translated_Review",
            "Translated Sentence",
            "Translated_Review",
            "BERT_Text",
            "Text",
            "text"
        ],
        "No review text available."
    )


def get_review_sentiment(review):
    return get_review_field(
        review,
        [
            "Sentiment",
            "sentiment",
            "Predicted Sentiment",
            "predicted_sentiment"
        ],
        "Unknown"
    )


def get_review_source_label(review):
    source = get_review_field(
        review,
        [
            "Source",
            "source",
            "Platform",
            "platform"
        ],
        ""
    )

    if source:
        return source

    return "Guest review"


def normalize_text(value):
    return str(value).lower().replace("/", " ").replace("&", " and ").strip()


def get_issue_aliases(issue):
    issue_lower = normalize_text(issue)

    if "clean" in issue_lower or "hygiene" in issue_lower:
        return [
            "cleanliness",
            "hygiene",
            "cleanliness hygiene",
            "cleanliness hygiene risk",
            "clean",
            "dirty",
            "unclean",
            "bathroom",
            "toilet",
            "housekeeping",
            "smell",
            "stain"
        ]

    if "room comfort" in issue_lower or "noise" in issue_lower:
        return [
            "room comfort",
            "noise",
            "noise control",
            "room comfort noise control",
            "noisy",
            "soundproof",
            "sleep",
            "bed",
            "pillow",
            "air conditioning",
            "aircon",
            "room condition"
        ]

    if "room" in issue_lower and "facility" in issue_lower:
        return [
            "room facility",
            "facility maintenance",
            "room maintenance",
            "maintenance",
            "broken",
            "not working",
            "lift",
            "elevator",
            "wifi",
            "repair"
        ]

    if "breakfast" in issue_lower or "food" in issue_lower:
        return [
            "food",
            "breakfast",
            "food breakfast",
            "restaurant",
            "buffet",
            "meal",
            "dining",
            "menu"
        ]

    if "check" in issue_lower or "booking" in issue_lower or "payment" in issue_lower:
        return [
            "check in",
            "check-in",
            "check out",
            "checkout",
            "booking",
            "payment",
            "deposit",
            "front desk",
            "reception",
            "waiting",
            "queue"
        ]

    if "parking" in issue_lower or "access" in issue_lower or "transport" in issue_lower:
        return [
            "parking",
            "accessibility",
            "access",
            "transport",
            "car park",
            "location",
            "traffic",
            "grab",
            "taxi"
        ]

    if "service" in issue_lower or "staff" in issue_lower:
        return [
            "service",
            "staff",
            "front desk",
            "reception",
            "rude",
            "helpful",
            "friendly",
            "attitude"
        ]

    if "price" in issue_lower or "value" in issue_lower:
        return [
            "price",
            "value",
            "worth",
            "money",
            "expensive",
            "overpriced",
            "value for money"
        ]

    if "overall" in issue_lower or "experience" in issue_lower:
        return [
            "overall experience",
            "overall stay experience",
            "overall stay",
            "stay experience",
            "general experience",
            "experience",
            "disappointed",
            "not satisfied",
            "poor experience",
            "bad experience",
            "terrible experience"
        ]

    return [word for word in issue_lower.split() if len(word) > 2]


def get_review_metadata_blob(review):
    metadata_fields = [
        get_review_field(review, ["Complaint Area", "complaint_area"], ""),
        get_review_field(review, ["Improvement Area", "improvement_area"], ""),
        get_review_field(review, ["Hotel Improvement Insight", "hotel_improvement_insight"], ""),
        get_review_field(review, ["Risk Type(s)", "Risk Type", "risk_type", "risk_types"], ""),
        get_review_field(review, ["Aspect(s)", "Aspects", "aspect", "aspects"], ""),
        get_review_field(review, ["Reason / Notes", "Reason", "Notes", "notes"], ""),
    ]

    return normalize_text(" ".join(metadata_fields))


def get_review_text_blob(review):
    text_fields = [
        get_review_text(review),
        get_review_field(review, ["Reason / Notes", "Reason", "Notes", "notes"], ""),
    ]

    return normalize_text(" ".join(text_fields))


def contains_alias(blob, aliases):
    return any(normalize_text(alias) in blob for alias in aliases)


def review_matches_issue_by_metadata(issue, review):
    metadata_blob = get_review_metadata_blob(review)
    aliases = get_issue_aliases(issue)

    if not metadata_blob:
        return False

    return contains_alias(metadata_blob, aliases)


def review_matches_issue_by_text(issue, review):
    text_blob = get_review_text_blob(review)
    aliases = get_issue_aliases(issue)

    if not text_blob:
        return False

    return contains_alias(text_blob, aliases)


def get_sentiment_group(review):
    sentiment = normalize_text(get_review_sentiment(review))

    if "negative" in sentiment:
        return "negative"

    if "neutral" in sentiment:
        return "neutral"

    if "positive" in sentiment:
        return "positive"

    text_blob = get_review_text_blob(review)

    negative_words = [
        "bad",
        "poor",
        "dirty",
        "noisy",
        "disappointed",
        "problem",
        "issue",
        "complaint",
        "slow",
        "rude",
        "broken",
        "not working",
        "uncomfortable",
        "smell",
        "worst",
        "terrible",
        "not worth",
        "overpriced"
    ]

    if any(word in text_blob for word in negative_words):
        return "negative"

    return "unknown"


def dedupe_reviews(reviews):
    seen = set()
    unique_reviews = []

    for review in reviews:
        text = get_review_text(review).strip().lower()

        if not text:
            continue

        if text in seen:
            continue

        seen.add(text)
        unique_reviews.append(review)

    return unique_reviews


def get_issue_review_evidence(hotel_name, issue, expected_count=0):
    try:
        reviews = get_hotel_reviews(hotel_name, limit=800)
    except TypeError:
        reviews = get_hotel_reviews(hotel_name)
    except Exception:
        reviews = pd.DataFrame()

    records = normalize_review_records(reviews)

    metadata_negative = []
    metadata_neutral = []
    text_negative = []
    text_neutral = []
    hotel_negative_fallback = []

    for review in records:
        sentiment_group = get_sentiment_group(review)
        metadata_match = review_matches_issue_by_metadata(issue, review)
        text_match = review_matches_issue_by_text(issue, review)

        if metadata_match and sentiment_group == "negative":
            metadata_negative.append(review)
        elif metadata_match and sentiment_group == "neutral":
            metadata_neutral.append(review)
        elif text_match and sentiment_group == "negative":
            text_negative.append(review)
        elif text_match and sentiment_group == "neutral":
            text_neutral.append(review)
        elif sentiment_group == "negative":
            hotel_negative_fallback.append(review)

    combined_reviews = (
        metadata_negative
        + metadata_neutral
        + text_negative
        + text_neutral
    )

    if not combined_reviews:
        combined_reviews = hotel_negative_fallback

    combined_reviews = dedupe_reviews(combined_reviews)

    limit = int(expected_count) if expected_count and expected_count > 0 else 12
    limit = min(max(limit, 8), 35)

    return combined_reviews[:limit]


def truncate_text(text, max_chars=430):
    text = str(text).strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "..."


def load_management_css():
    st.markdown("""
    <style>
        .mgmt-header {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.25rem 1.45rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
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

        .access-info-card {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
            min-height: 100%;
        }

        .access-title {
            color: var(--text-main);
            font-size: 1.8rem;
            font-weight: 950;
            letter-spacing: -0.05em;
            margin-bottom: 0.4rem;
            line-height: 1.15;
        }

        .access-desc {
            color: #64748B;
            font-size: 0.98rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .access-list {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            margin-top: 0.7rem;
        }

        .access-list-item {
            background: #FFF8EF;
            border: 1px solid #EAD7C6;
            border-radius: 16px;
            padding: 0.8rem 0.9rem;
            color: #7C6F64;
            font-size: 0.88rem;
            line-height: 1.45;
            font-weight: 700;
        }

        .login-panel-card {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border: 1px solid #EAD7C6;
            border-radius: 28px;
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 0.8rem;
        }

        .login-panel-title {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 950;
            letter-spacing: -0.04em;
            margin-bottom: 0.3rem;
        }

        .login-panel-desc {
            color: #64748B;
            font-size: 0.92rem;
            line-height: 1.55;
        }

        .login-panel-label {
            color: #7C6F64;
            font-size: 0.72rem;
            font-weight: 950;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
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
        .table-section,
        .priority-section,
        .evidence-section,
        .action-section {
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

        .priority-row {
            display: grid;
            grid-template-columns: 1.2fr 150px 210px;
            gap: 0.75rem;
            align-items: center;
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
            margin-bottom: 0.55rem;
        }

        .priority-row.active {
            background: linear-gradient(135deg, #FFF8EF, #EEF7F1);
            border-color: #C7653A;
            box-shadow: 0 8px 22px rgba(155, 67, 37, 0.10);
        }

        .priority-title {
            color: var(--text-main);
            font-size: 0.98rem;
            font-weight: 950;
            line-height: 1.25;
        }

        .priority-impact {
            color: #64748B;
            font-size: 0.78rem;
            line-height: 1.35;
            margin-top: 0.18rem;
        }

        .priority-badge,
        .risk-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: fit-content;
            border-radius: 999px;
            padding: 0.38rem 0.68rem;
            font-size: 0.72rem;
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

        .signal-link {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            text-decoration: none !important;
            color: white !important;
            background: linear-gradient(135deg, #C7653A, #9B4325);
            border-radius: 999px;
            padding: 0.48rem 0.75rem;
            font-size: 0.76rem;
            font-weight: 900;
            box-shadow: 0 8px 18px rgba(155, 67, 37, 0.16);
            white-space: nowrap;
        }

        .signal-link:hover {
            filter: brightness(1.04);
            transform: translateY(-1px);
        }

        .evidence-header-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.8rem;
            margin-bottom: 0.75rem;
        }

        .evidence-pill {
            display: inline-flex;
            background: #EEF7F1;
            color: #216E46;
            border: 1px solid #BFE3CF;
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            font-size: 0.74rem;
            font-weight: 900;
            white-space: nowrap;
        }

        .evidence-card {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.82rem;
            margin-bottom: 0.55rem;
        }

        .evidence-top {
            display: flex;
            justify-content: space-between;
            gap: 0.65rem;
            margin-bottom: 0.35rem;
            align-items: center;
        }

        .evidence-title {
            color: var(--text-main);
            font-size: 0.86rem;
            font-weight: 950;
        }

        .sentiment-chip {
            display: inline-flex;
            border-radius: 999px;
            padding: 0.28rem 0.58rem;
            font-size: 0.68rem;
            font-weight: 900;
            color: #7C6F64;
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
        }

        .evidence-text {
            color: #475569;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        .action-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
        }

        .action-card {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            border-radius: 18px;
            padding: 0.85rem;
        }

        .action-number {
            display: inline-flex;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            align-items: center;
            justify-content: center;
            background: #FFF4E8;
            color: #9B4325;
            border: 1px solid #F2CBAE;
            font-size: 0.75rem;
            font-weight: 950;
            margin-bottom: 0.45rem;
        }

        .action-text {
            color: #475569;
            font-size: 0.82rem;
            line-height: 1.45;
            font-weight: 750;
        }

        div[data-testid="stTextInput"] > label {
            font-weight: 800 !important;
            color: #4B5563 !important;
        }

        div[data-testid="stTextInput"] > div > div {
            background: #FFFFFF !important;
            border: 1px solid #E2C9B7 !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 22px rgba(155, 67, 37, 0.06);
        }

        div[data-testid="stTextInput"] input {
            color: #1F2937 !important;
            font-size: 0.98rem !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            width: 100%;
            border-radius: 16px !important;
            border: none !important;
            color: white !important;
            background: linear-gradient(135deg, #C7653A, #9B4325) !important;
            font-weight: 850 !important;
            min-height: 50px !important;
            box-shadow: 0 10px 24px rgba(155, 67, 37, 0.20);
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            filter: brightness(1.03);
            transform: translateY(-1px);
        }

        @media (max-width: 1000px) {
            .metric-grid,
            .action-grid {
                grid-template-columns: 1fr;
            }

            .priority-row {
                grid-template-columns: 1fr;
            }

            .evidence-header-row {
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
            Convert aggregated guest review complaints into improvement priorities, review evidence, and suggested management actions.
        </div>
    </div>
    """)


def require_management_access():
    access_code = st.secrets.get("MANAGEMENT_ACCESS_CODE", "staff123")

    if has_management_access():
        return

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        render_html("""
        <div class="access-info-card">
            <div class="mgmt-badge">Staff only</div>
            <div class="access-title">Hotel Management Access</div>
            <div class="access-desc">
                This page is for hotel management users only. Use the access code to open the management dashboard and review hotel improvement priorities.
            </div>
            <div class="access-list">
                <div class="access-list-item">Review the most repeated guest complaint areas.</div>
                <div class="access-list-item">Click complaint signals to view supporting reviews.</div>
                <div class="access-list-item">Get suggested improvement actions for hotel operations.</div>
            </div>
        </div>
        """)

    with right_col:
        render_html("""
        <div class="login-panel-card">
            <div class="login-panel-label">Secure entry</div>
            <div class="login-panel-title">Enter management access code</div>
            <div class="login-panel-desc">
                Only authorised hotel management users should continue beyond this point.
            </div>
        </div>
        """)

        with st.form("management_access_form"):
            entered_code = st.text_input(
                "Access code",
                type="password",
                placeholder="Enter staff access code"
            )

            submit_clicked = st.form_submit_button(
                "Enter Management Portal",
                use_container_width=True
            )

            if submit_clicked:
                if entered_code == access_code:
                    st.session_state["management_access_granted"] = True
                    st.query_params["mgmt_access"] = "1"
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
            st.query_params.clear()
            st.rerun()


def render_area_choices(areas, selected_area):
    chips_html = ""

    for area in areas:
        active_class = "active" if area == selected_area else ""
        area_url = quote(area, safe="")

        chips_html += (
            f'<a class="choice-chip {active_class}" '
            f'href="?mgmt_access=1&area={area_url}" target="_self">{escape(area)}</a>'
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
            f'href="?mgmt_access=1&area={area_url}&hotel={hotel_url}" '
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
                <span class="risk-chip {risk_class}">{escape(risk_text(risk_level))}</span>
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
            <div class="metric-sub">Most repeated complaint area</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">High priority items</div>
            <div class="metric-value">{escape(summary["high_priority_count"])}</div>
            <div class="metric-sub">Issues needing stronger attention</div>
        </div>
    </div>
    """)


def render_priority_areas(management_df, selected_area, selected_hotel_name, selected_issue):
    if management_df.empty:
        render_html("""
        <div class="priority-section">
            <div class="card-title">Priority improvement areas</div>
            <div class="card-desc">No repeated complaint pattern was found for this hotel.</div>
        </div>
        """)
        return

    rows_html = ""

    area_url = quote(selected_area, safe="")
    hotel_url = quote(selected_hotel_name, safe="")

    for _, row in management_df.head(8).iterrows():
        issue = str(row["Complaint Area"])
        priority = row["Priority Level"]
        count = int(safe_number(row["Complaint Count"], 0))
        priority_cls = priority_class(priority)
        impact = get_issue_impact(issue)
        issue_url = quote(issue, safe="")
        active_class = "active" if issue == selected_issue else ""

        rows_html += f"""
        <div class="priority-row {active_class}">
            <div>
                <div class="priority-title">{escape(issue)}</div>
                <div class="priority-impact">{escape(impact)}</div>
            </div>

            <div>
                <span class="priority-badge {priority_cls}">{escape(priority)} priority</span>
            </div>

            <a class="signal-link"
               href="?mgmt_access=1&area={area_url}&hotel={hotel_url}&issue={issue_url}#review-evidence"
               target="_self">
               View {escape(count)} signal(s)
            </a>
        </div>
        """

    render_html(f"""
    <div class="priority-section">
        <div class="card-title">Priority improvement areas</div>
        <div class="card-desc">
            Click a complaint signal to view the negative review evidence behind that improvement area.
        </div>
        {rows_html}
    </div>
    """)


def render_review_card(review, index):
    review_text = truncate_text(get_review_text(review))
    sentiment = get_review_sentiment(review)
    source = get_review_source_label(review)

    render_html(f"""
    <div class="evidence-card">
        <div class="evidence-top">
            <div class="evidence-title">Review evidence {escape(index)}</div>
            <span class="sentiment-chip">{escape(sentiment)}</span>
        </div>
        <div class="evidence-text">
            {escape(review_text)}
        </div>
        <div class="metric-sub">{escape(source)}</div>
    </div>
    """)


def render_review_evidence(hotel_name, selected_issue, expected_count):
    if not selected_issue:
        return

    evidence_reviews = get_issue_review_evidence(
        hotel_name,
        selected_issue,
        expected_count
    )

    render_html(f"""
    <div id="review-evidence" class="evidence-section">
        <div class="evidence-header-row">
            <div>
                <div class="card-title">Negative review evidence for {escape(selected_issue)}</div>
                <div class="card-desc">
                    These review snippets help management understand what guests were actually saying about this complaint area.
                </div>
            </div>
            <span class="evidence-pill">
                {escape(len(evidence_reviews))} review evidence shown
            </span>
        </div>
    </div>
    """)

    if not evidence_reviews:
        st.info("No matching negative review evidence was found for this complaint area.")
        return

    preview_limit = min(len(evidence_reviews), 8)

    for index, review in enumerate(evidence_reviews[:preview_limit], start=1):
        render_review_card(review, index)

    remaining_reviews = evidence_reviews[preview_limit:]

    if remaining_reviews:
        with st.expander(f"Show {len(remaining_reviews)} more review evidence"):
            for index, review in enumerate(
                remaining_reviews,
                start=preview_limit + 1
            ):
                render_review_card(review, index)


def render_action_plan(management_df, selected_issue):
    if management_df.empty:
        render_html("""
        <div class="action-section">
            <div class="card-title">Recommended action plan</div>
            <div class="card-desc">No action plan is available because no repeated complaint pattern was found.</div>
        </div>
        """)
        return

    selected_row = None

    for _, row in management_df.iterrows():
        if str(row["Complaint Area"]) == str(selected_issue):
            selected_row = row
            break

    if selected_row is None:
        selected_row = management_df.iloc[0]

    issue = selected_row["Complaint Area"]
    suggested_action = selected_row.get("Suggested Improvement Action", "Not stated")
    steps = get_action_steps(issue, suggested_action)

    action_cards = ""

    for index, step in enumerate(steps[:3], start=1):
        action_cards += f"""
        <div class="action-card">
            <div class="action-number">{escape(index)}</div>
            <div class="action-text">{escape(step)}</div>
        </div>
        """

    render_html(f"""
    <div class="action-section">
        <div class="card-title">Recommended action plan for {escape(issue)}</div>
        <div class="card-desc">
            Suggested operational actions based on the selected complaint evidence.
        </div>
        <div class="action-grid">
            {action_cards}
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
            A structured view of complaint areas, priority levels, and suggested actions.
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

require_management_access()

render_header()
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
selected_issue = get_selected_issue(management_df)

expected_count = 0

if not management_df.empty and selected_issue:
    issue_rows = management_df[
        management_df["Complaint Area"].astype(str) == str(selected_issue)
    ]

    if not issue_rows.empty:
        expected_count = int(safe_number(issue_rows.iloc[0]["Complaint Count"], 0))

render_management_summary(hotel, management_df)
render_metrics(hotel, management_df)

render_priority_areas(
    management_df,
    selected_area,
    selected_hotel_name,
    selected_issue
)

render_review_evidence(
    selected_hotel_name,
    selected_issue,
    expected_count
)

render_action_plan(
    management_df,
    selected_issue
)

render_management_table(
    management_df,
    selected_hotel_name
)

render_footer()