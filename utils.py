import re
from pathlib import Path

import pandas as pd
import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# =========================================================
# Dataset Path
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "Hotel_Review_Summary_Final.csv"


# =========================================================
# Hugging Face DistilBERT Sentiment Model
# =========================================================

HF_MODEL_ID = "qm0720/staywise-kl-distilbert-sentiment"

FALLBACK_LABEL_ID_TO_NAME = {
    0: "Negative",
    1: "Neutral",
    2: "Positive"
}


@st.cache_resource(show_spinner="Loading sentiment model...")
def load_distilbert_sentiment_model():
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL_ID)
    model.eval()
    return tokenizer, model


def normalize_model_label(raw_label, predicted_id):
    if raw_label is None:
        return FALLBACK_LABEL_ID_TO_NAME.get(predicted_id, "Neutral")

    label = str(raw_label).strip().lower()

    label_map = {
        "label_0": "Negative",
        "label_1": "Neutral",
        "label_2": "Positive",
        "negative": "Negative",
        "neutral": "Neutral",
        "positive": "Positive",
        "neg": "Negative",
        "neu": "Neutral",
        "pos": "Positive"
    }

    return label_map.get(label, FALLBACK_LABEL_ID_TO_NAME.get(predicted_id, "Neutral"))


def predict_sentiment_distilbert(review_text):
    tokenizer, model = load_distilbert_sentiment_model()

    text = str(review_text).strip()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities_tensor = torch.softmax(outputs.logits, dim=1).squeeze()
        probabilities = probabilities_tensor.tolist()

    predicted_id = int(torch.argmax(outputs.logits, dim=1).item())

    raw_label = None
    if hasattr(model.config, "id2label"):
        raw_label = model.config.id2label.get(predicted_id)

    predicted_label = normalize_model_label(raw_label, predicted_id)
    confidence = round(float(probabilities[predicted_id]) * 100, 2)

    return {
        "sentiment": predicted_label,
        "confidence": confidence,
        "probabilities": {
            "Negative": round(float(probabilities[0]) * 100, 2),
            "Neutral": round(float(probabilities[1]) * 100, 2),
            "Positive": round(float(probabilities[2]) * 100, 2)
        }
    }


# =========================================================
# Dataset Loading and Cleaning
# =========================================================

def safe_text(value, default=""):
    if pd.isna(value):
        return default

    value = str(value).strip()

    if value.lower() in ["nan", "none", "null"]:
        return default

    return value


def format_area_name(area):
    area = safe_text(area).lower()

    area_map = {
        "klcc": "KLCC",
        "bukit jalil": "Bukit Jalil",
        "petaling jaya": "Petaling Jaya",
        "sunway": "Sunway"
    }

    return area_map.get(area, area.title())


@st.cache_data(show_spinner=False)
def load_hotel_review_summary_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}. "
            "Please place Hotel_Review_Summary_Final.csv inside the data folder."
        )

    df = pd.read_csv(DATASET_PATH)

    required_columns = [
        "ID",
        "Review",
        "Hotel_name",
        "Hotel_Address",
        "sentiment",
        "area",
        "risk_type",
        "Traveller_Suitability",
        "Improvement_Area",
        "Aspect",
        "Source"
    ]

    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns in dataset: {missing_columns}")

    text_columns = [
        "Review",
        "Hotel_name",
        "Hotel_Address",
        "sentiment",
        "area",
        "risk_type",
        "Traveller_Suitability",
        "Improvement_Area",
        "Aspect",
        "Source"
    ]

    for column in text_columns:
        df[column] = df[column].apply(lambda value: safe_text(value))

    df["sentiment"] = df["sentiment"].str.lower().str.strip()
    df["area"] = df["area"].str.lower().str.strip()

    df = df[df["Hotel_name"] != ""].copy()

    return df


# =========================================================
# Hotel Summary Functions for Main System Pages
# =========================================================

def get_areas():
    df = load_hotel_review_summary_dataset()

    raw_areas = sorted(df["area"].dropna().unique().tolist())

    preferred_order = ["bukit jalil", "klcc", "petaling jaya", "sunway"]

    ordered_areas = []

    for area in preferred_order:
        if area in raw_areas:
            ordered_areas.append(format_area_name(area))

    for area in raw_areas:
        formatted_area = format_area_name(area)

        if formatted_area not in ordered_areas:
            ordered_areas.append(formatted_area)

    return ordered_areas


def get_top_value(series, default="Not clearly stated", excluded_values=None):
    if excluded_values is None:
        excluded_values = []

    excluded_values = [str(value).lower().strip() for value in excluded_values]

    cleaned_series = series.dropna().astype(str).str.strip()
    cleaned_series = cleaned_series[cleaned_series != ""]
    cleaned_series = cleaned_series[~cleaned_series.str.lower().isin(excluded_values)]

    if cleaned_series.empty:
        return default

    return cleaned_series.value_counts().index[0]


def calculate_hotel_risk_level(negative_pct, risk_counts):
    low_risk_labels = ["low risk", "no risk", "none", "not stated", ""]

    total_risk_count = sum(risk_counts.values())

    if total_risk_count == 0:
        return "Low"

    non_low_risk_count = 0

    for risk_name, count in risk_counts.items():
        risk_text = str(risk_name).lower().strip()

        if risk_text not in low_risk_labels:
            non_low_risk_count += count

    non_low_risk_pct = (non_low_risk_count / total_risk_count) * 100

    if negative_pct >= 25 or non_low_risk_pct >= 55:
        return "High"

    if negative_pct >= 15 or non_low_risk_pct >= 35:
        return "Medium"

    return "Low"


def get_main_strength(hotel_df):
    positive_df = hotel_df[hotel_df["sentiment"] == "positive"]

    if not positive_df.empty:
        return get_top_value(
            positive_df["Aspect"],
            default="Overall stay experience"
        )

    return get_top_value(
        hotel_df["Aspect"],
        default="Overall stay experience"
    )


def get_main_risk(hotel_df):
    negative_df = hotel_df[hotel_df["sentiment"] == "negative"]

    excluded_risks = [
        "low risk",
        "no risk",
        "none",
        "not stated",
        ""
    ]

    excluded_improvements = [
        "no major improvement needed",
        "none",
        "not stated",
        ""
    ]

    if not negative_df.empty:
        risk_value = get_top_value(
            negative_df["risk_type"],
            default="",
            excluded_values=excluded_risks
        )

        if risk_value != "":
            return risk_value

        improvement_value = get_top_value(
            negative_df["Improvement_Area"],
            default="",
            excluded_values=excluded_improvements
        )

        if improvement_value != "":
            return improvement_value

    risk_value = get_top_value(
        hotel_df["risk_type"],
        default="",
        excluded_values=excluded_risks
    )

    if risk_value != "":
        return risk_value

    improvement_value = get_top_value(
        hotel_df["Improvement_Area"],
        default="",
        excluded_values=excluded_improvements
    )

    if improvement_value != "":
        return improvement_value

    return "No major repeated concern"


def get_best_traveller_type(hotel_df):
    return get_top_value(
        hotel_df["Traveller_Suitability"],
        default="General travellers"
    )


def get_hotel_sources(hotel_df):
    sources = sorted(
        source for source in hotel_df["Source"].dropna().astype(str).str.strip().unique()
        if source != ""
    )

    if not sources:
        return "Not stated"

    return ", ".join(sources)


def get_hotel_complaints_dict(hotel_df):
    excluded_improvements = [
        "no major improvement needed",
        "none",
        "not stated",
        ""
    ]

    improvement_series = hotel_df["Improvement_Area"].dropna().astype(str).str.strip()
    improvement_series = improvement_series[improvement_series != ""]
    improvement_series = improvement_series[
        ~improvement_series.str.lower().isin(excluded_improvements)
    ]

    if improvement_series.empty:
        return {}

    return improvement_series.value_counts().to_dict()


def calculate_suitability_score(positive_pct, negative_pct, risk_level):
    score = positive_pct - (negative_pct * 0.7)

    if risk_level == "High":
        score -= 10
    elif risk_level == "Medium":
        score -= 4

    score = max(0, min(100, round(score, 2)))

    return score


def get_hotel_summary_from_group(hotel_name, hotel_df):
    total_reviews = len(hotel_df)

    sentiment_counts = hotel_df["sentiment"].value_counts()

    positive_count = int(sentiment_counts.get("positive", 0))
    neutral_count = int(sentiment_counts.get("neutral", 0))
    negative_count = int(sentiment_counts.get("negative", 0))

    if total_reviews == 0:
        positive_pct = 0
        neutral_pct = 0
        negative_pct = 0
    else:
        positive_pct = round((positive_count / total_reviews) * 100)
        neutral_pct = round((neutral_count / total_reviews) * 100)
        negative_pct = round((negative_count / total_reviews) * 100)

    risk_counts = hotel_df["risk_type"].value_counts().to_dict()
    risk_level = calculate_hotel_risk_level(negative_pct, risk_counts)

    area_value = get_top_value(hotel_df["area"], default="")
    address_value = get_top_value(hotel_df["Hotel_Address"], default="Address not stated")
    source_value = get_hotel_sources(hotel_df)

    main_strength = get_main_strength(hotel_df)
    main_risk = get_main_risk(hotel_df)
    best_traveller_type = get_best_traveller_type(hotel_df)

    complaints = get_hotel_complaints_dict(hotel_df)

    suitability_score = calculate_suitability_score(
        positive_pct=positive_pct,
        negative_pct=negative_pct,
        risk_level=risk_level
    )

    hotel_summary = {
        "hotel": hotel_name,
        "hotel_name": hotel_name,
        "area": format_area_name(area_value),
        "area_raw": area_value,
        "hotel_address": address_value,
        "address": address_value,
        "source": source_value,
        "price_level": f"{total_reviews} reviews",
        "review_count": total_reviews,
        "positive_pct": positive_pct,
        "neutral_pct": neutral_pct,
        "negative_pct": negative_pct,
        "positive_count": positive_count,
        "neutral_count": neutral_count,
        "negative_count": negative_count,
        "main_strength": main_strength,
        "main_risk": main_risk,
        "best_traveller_type": best_traveller_type,
        "risk_level": risk_level,
        "complaints": complaints,
        "suitability_score": suitability_score,
        "description": (
            f"{hotel_name} has {total_reviews} reviews in the dataset. "
            f"The main positive area is {main_strength}, while travellers should check {main_risk} before booking."
        ),
        "hotel_improvement_insight": (
            f"The hotel should maintain its strength in {main_strength} and monitor guest feedback related to {main_risk}."
        )
    }

    return hotel_summary


@st.cache_data(show_spinner=False)
def get_all_hotel_summaries():
    df = load_hotel_review_summary_dataset()

    hotel_summaries = []

    for hotel_name, hotel_df in df.groupby("Hotel_name"):
        hotel_summary = get_hotel_summary_from_group(hotel_name, hotel_df)
        hotel_summaries.append(hotel_summary)

    hotel_summaries = sorted(
        hotel_summaries,
        key=lambda hotel: (
            hotel["area"],
            -hotel["positive_pct"],
            hotel["negative_pct"],
            hotel["hotel"]
        )
    )

    return hotel_summaries


def get_hotels_by_area(area):
    selected_area = format_area_name(area).lower()

    all_hotels = get_all_hotel_summaries()

    return [
        hotel for hotel in all_hotels
        if hotel["area"].lower() == selected_area
    ]


def get_hotel_names(area=None):
    if area:
        return [hotel["hotel"] for hotel in get_hotels_by_area(area)]

    return [hotel["hotel"] for hotel in get_all_hotel_summaries()]


def get_hotel_by_name(name):
    selected_name = safe_text(name)

    for hotel in get_all_hotel_summaries():
        if hotel["hotel"] == selected_name:
            return hotel

    return None


def get_all_hotels():
    return get_all_hotel_summaries()


def get_sentiment_df(hotel):
    return pd.DataFrame({
        "Sentiment": ["Positive", "Neutral", "Negative"],
        "Percentage": [
            hotel["positive_pct"],
            hotel["neutral_pct"],
            hotel["negative_pct"]
        ]
    })


def get_complaint_df(hotel):
    df = load_hotel_review_summary_dataset()

    hotel_name = hotel.get("hotel", hotel.get("hotel_name", ""))

    hotel_df = df[df["Hotel_name"] == hotel_name]

    if hotel_df.empty:
        return pd.DataFrame(columns=[
            "Complaint Area",
            "Complaint Count",
            "Priority Level",
            "Suggested Improvement Action"
        ])

    excluded_improvements = [
        "no major improvement needed",
        "none",
        "not stated",
        ""
    ]

    complaint_source = hotel_df.copy()
    complaint_source = complaint_source[
        ~complaint_source["Improvement_Area"].str.lower().isin(excluded_improvements)
    ]

    if complaint_source.empty:
        return pd.DataFrame([{
            "Complaint Area": "No major repeated complaint",
            "Complaint Count": 0,
            "Priority Level": "Low",
            "Suggested Improvement Action": "Maintain current service quality and continue monitoring guest feedback."
        }])

    complaint_df = (
        complaint_source
        .groupby("Improvement_Area")
        .size()
        .reset_index(name="Complaint Count")
        .rename(columns={"Improvement_Area": "Complaint Area"})
    )

    def get_priority(count):
        if count >= 25:
            return "High"
        if count >= 10:
            return "Medium"
        return "Low"

    def get_action(area):
        action_map = {
            "Cleanliness": "Improve housekeeping checks and room inspection frequency.",
            "Overall Experience": "Review common guest feedback and improve the overall stay experience.",
            "Check-in, Booking & Payment Process": "Improve check-in, booking and payment process clarity.",
            "Room Comfort": "Improve room maintenance, bedding, ventilation and comfort facilities.",
            "Room & Comfort": "Improve room maintenance, bedding, ventilation and comfort facilities.",
            "Staff & Service": "Provide additional staff training and improve service response time.",
            "Location & Accessibility": "Provide clearer transport and accessibility information.",
            "Facilities": "Inspect and maintain hotel facilities more regularly.",
            "Food & Breakfast": "Improve breakfast variety and food quality control.",
            "Noise": "Improve soundproofing and provide quieter room options where possible."
        }

        return action_map.get(
            area,
            "Review this repeated complaint area and improve the affected service process."
        )

    complaint_df["Priority Level"] = complaint_df["Complaint Count"].apply(get_priority)
    complaint_df["Suggested Improvement Action"] = complaint_df["Complaint Area"].apply(get_action)

    complaint_df = complaint_df.sort_values(
        by="Complaint Count",
        ascending=False
    )

    return complaint_df


def get_hotel_reviews(hotel_name, limit=10):
    df = load_hotel_review_summary_dataset()

    hotel_df = df[df["Hotel_name"] == hotel_name].copy()

    if hotel_df.empty:
        return pd.DataFrame(columns=[
            "Review",
            "sentiment",
            "risk_type",
            "Traveller_Suitability",
            "Improvement_Area",
            "Aspect",
            "Source"
        ])

    return hotel_df.head(limit)


def recommend_better_hotel(hotel_a, hotel_b):
    score_a = (
        hotel_a["positive_pct"] * 0.50
        - hotel_a["negative_pct"] * 0.35
        + hotel_a["suitability_score"] * 0.15
    )

    score_b = (
        hotel_b["positive_pct"] * 0.50
        - hotel_b["negative_pct"] * 0.35
        + hotel_b["suitability_score"] * 0.15
    )

    if score_a > score_b:
        winner = hotel_a
        loser = hotel_b
    elif score_b > score_a:
        winner = hotel_b
        loser = hotel_a
    else:
        return (
            "Both hotels are quite similar. Users should choose based on location, repeated concerns, "
            "and personal travel needs."
        )

    return (
        f"Recommended Hotel: **{winner['hotel']}**. "
        f"It looks more suitable because it has a stronger review profile, "
        f"better traveller suitability, and lower negative review impact compared with {loser['hotel']}."
    )


def risk_badge(risk):
    risk = str(risk).lower()

    if risk == "low":
        return "🟢 Low Risk"

    if risk == "medium":
        return "🟡 Medium Risk"

    if risk == "high":
        return "🔴 High Risk"

    return risk


def risk_css_class(risk):
    risk = str(risk).lower()

    if risk == "low":
        return "risk-low"

    if risk == "medium":
        return "risk-medium"

    if risk == "high":
        return "risk-high"

    return "risk-medium"


def sentiment_label_style(label):
    label = str(label).lower()

    if label == "positive":
        return "🟢 Positive"

    if label == "neutral":
        return "🟡 Neutral"

    if label == "negative":
        return "🔴 Negative"

    return label


# =========================================================
# Review Checker Rule-Based Supporting Analysis
# =========================================================

positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly",
    "helpful", "nice", "spacious", "convenient", "worth", "amazing",
    "perfect", "pleasant", "beautiful", "recommended", "polite", "fast",
    "strategic", "delicious", "wonderful", "large", "modern", "safe"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy",
    "smelly", "broken", "worst", "terrible", "disappointed",
    "uncomfortable", "unclean", "overpriced", "delay", "small",
    "old", "stained", "dusty", "leaking", "crowded", "problem",
    "issue", "faulty", "not working"
]

positive_emojis = ["😊", "😍", "👍", "😁", "😄", "❤️", "✨", "🥰", "👏", "✅"]
negative_emojis = ["😡", "😠", "👎", "😞", "😢", "🤮", "😤", "❌", "💔", "😭"]
neutral_emojis = ["😐", "🤔", "🙂", "😶"]

positive_emoticons = [":)", ":-)", ":D", ":-D", ";)", ";-)"]
negative_emoticons = [":(", ":-(", ":'(", ">:(", ":-/"]
neutral_emoticons = [":|", ":-|", ":/"]

aspect_keywords = {
    "Room": [
        "room", "bed", "bathroom", "toilet", "shower", "pillow", "suite",
        "apartment", "window", "space", "spacious"
    ],
    "Service": [
        "staff", "service", "reception", "manager", "friendly", "rude",
        "helpful", "polite", "responded", "check-in", "checkin"
    ],
    "Cleanliness": [
        "clean", "dirty", "cleanliness", "smell", "dust", "stain",
        "hygiene", "stained", "unclean", "dusty"
    ],
    "Location": [
        "location", "near", "mall", "station", "airport", "convenient",
        "area", "city", "centre", "center", "access", "accessible"
    ],
    "Price": [
        "price", "expensive", "cheap", "value", "worth", "money", "overpriced",
        "budget"
    ],
    "Facilities": [
        "pool", "gym", "wifi", "wi-fi", "parking", "lift", "elevator",
        "facility", "facilities", "amenities", "restaurant"
    ],
    "Food": [
        "breakfast", "food", "restaurant", "meal", "buffet", "delicious"
    ],
    "Noise": [
        "noise", "noisy", "sound", "soundproof", "loud"
    ]
}


def detect_emoji_sentiment(review):
    text = str(review)

    detected_positive = []
    detected_negative = []
    detected_neutral = []

    for signal in positive_emojis + positive_emoticons:
        if signal in text:
            detected_positive.append(signal)

    for signal in negative_emojis + negative_emoticons:
        if signal in text:
            detected_negative.append(signal)

    for signal in neutral_emojis + neutral_emoticons:
        if signal in text:
            detected_neutral.append(signal)

    positive_count = len(detected_positive)
    negative_count = len(detected_negative)
    neutral_count = len(detected_neutral)

    if positive_count == 0 and negative_count == 0 and neutral_count == 0:
        emoji_sentiment = "No emoji signal"
    elif positive_count > negative_count and positive_count >= neutral_count:
        emoji_sentiment = "Positive"
    elif negative_count > positive_count and negative_count >= neutral_count:
        emoji_sentiment = "Negative"
    elif neutral_count > positive_count and neutral_count > negative_count:
        emoji_sentiment = "Neutral"
    else:
        emoji_sentiment = "Mixed"

    return {
        "emoji_sentiment": emoji_sentiment,
        "positive_signals": detected_positive,
        "negative_signals": detected_negative,
        "neutral_signals": detected_neutral,
        "total_signals": positive_count + negative_count + neutral_count
    }


def get_keyword_signals(review):
    text = str(review).lower()
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = cleaned_text.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    pros = [word for word in sorted(set(words)) if word in positive_words]
    cons = [word for word in sorted(set(words)) if word in negative_words]

    return words, positive_count, negative_count, pros, cons


def detect_review_aspects(review):
    text = str(review).lower()
    detected_aspects = []

    for aspect, keywords in aspect_keywords.items():
        if any(keyword.lower() in text for keyword in keywords):
            detected_aspects.append(aspect)

    return detected_aspects


def get_aspect_sentiment_breakdown(review):
    text = str(review).lower()
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = cleaned_text.split()

    rows = []

    for aspect, keywords in aspect_keywords.items():
        matched_keywords = []
        aspect_positions = []

        for index, word in enumerate(words):
            for keyword in keywords:
                clean_keyword = keyword.replace("-", "").lower()
                clean_word = word.replace("-", "").lower()

                if clean_word == clean_keyword or clean_keyword in clean_word:
                    matched_keywords.append(keyword)
                    aspect_positions.append(index)

        if not matched_keywords:
            continue

        local_positive = 0
        local_negative = 0

        for position in aspect_positions:
            start = max(0, position - 5)
            end = min(len(words), position + 6)
            context_words = words[start:end]

            local_positive += sum(1 for word in context_words if word in positive_words)
            local_negative += sum(1 for word in context_words if word in negative_words)

        if local_positive > local_negative:
            aspect_sentiment = "Positive"
        elif local_negative > local_positive:
            aspect_sentiment = "Negative"
        else:
            aspect_sentiment = "Neutral"

        rows.append({
            "Aspect": aspect,
            "Aspect Sentiment": aspect_sentiment,
            "Matched Keywords": ", ".join(sorted(set(matched_keywords))),
            "Positive Signals": local_positive,
            "Negative Signals": local_negative
        })

    return rows


def calculate_review_risk_level(sentiment, confidence, negative_count, emoji_info, aspect_breakdown):
    negative_aspect_count = sum(
        1 for row in aspect_breakdown
        if row["Aspect Sentiment"] == "Negative"
    )

    emoji_sentiment = emoji_info["emoji_sentiment"]

    if sentiment == "Negative":
        if confidence >= 75 or negative_count >= 2 or negative_aspect_count >= 2:
            return "High"

        return "Medium"

    if sentiment == "Neutral":
        if negative_count >= 2 or negative_aspect_count >= 2 or emoji_sentiment == "Negative":
            return "Medium"

        return "Medium"

    if sentiment == "Positive":
        if negative_count >= 2 or negative_aspect_count >= 2 or emoji_sentiment == "Mixed":
            return "Medium"

        return "Low"

    return "Medium"


def generate_suitability_note(sentiment, risk):
    if sentiment == "Positive":
        if risk == "Low":
            return "This review suggests the hotel may be suitable for users who value comfort, service, or convenience."

        return "Although the overall feeling is positive, users should still check the highlighted concerns before booking."

    if sentiment == "Negative":
        return "Users should be careful before booking because this review contains possible concern indicators."

    return "This review is mixed or average. Users may need to compare more reviews before booking."


def generate_explanation(sentiment, confidence, probabilities, emoji_info, positive_count, negative_count, aspect_breakdown):
    negative_aspect_count = sum(
        1 for row in aspect_breakdown
        if row["Aspect Sentiment"] == "Negative"
    )

    positive_aspect_count = sum(
        1 for row in aspect_breakdown
        if row["Aspect Sentiment"] == "Positive"
    )

    explanation = (
        f"The overall sentiment was predicted as {sentiment} with {confidence}% confidence. "
        f"The review shows Positive {probabilities['Positive']}%, "
        f"Neutral {probabilities['Neutral']}%, "
        f"Negative {probabilities['Negative']}%. "
    )

    if positive_count > 0 or negative_count > 0:
        explanation += (
            f"Supporting keyword analysis detected {positive_count} positive signal(s) "
            f"and {negative_count} negative signal(s). "
        )
    else:
        explanation += "No strong positive or negative keyword signal was detected. "

    if emoji_info["emoji_sentiment"] != "No emoji signal":
        explanation += (
            f"Emoji or emoticon analysis detected a {emoji_info['emoji_sentiment']} signal. "
        )

    if positive_aspect_count > 0 or negative_aspect_count > 0:
        explanation += (
            f"Aspect analysis found {positive_aspect_count} positive aspect(s) "
            f"and {negative_aspect_count} negative aspect(s). "
        )

    return explanation


def analyze_review_frontend(review):
    sentiment_result = predict_sentiment_distilbert(review)

    sentiment = sentiment_result["sentiment"]
    confidence = sentiment_result["confidence"]
    probabilities = sentiment_result["probabilities"]

    words, positive_count, negative_count, pros, cons = get_keyword_signals(review)
    emoji_info = detect_emoji_sentiment(review)
    detected_aspects = detect_review_aspects(review)
    aspect_breakdown = get_aspect_sentiment_breakdown(review)

    risk = calculate_review_risk_level(
        sentiment=sentiment,
        confidence=confidence,
        negative_count=negative_count,
        emoji_info=emoji_info,
        aspect_breakdown=aspect_breakdown
    )

    suitability = generate_suitability_note(sentiment, risk)

    explanation = generate_explanation(
        sentiment=sentiment,
        confidence=confidence,
        probabilities=probabilities,
        emoji_info=emoji_info,
        positive_count=positive_count,
        negative_count=negative_count,
        aspect_breakdown=aspect_breakdown
    )

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "risk": risk,
        "suitability": suitability,
        "pros": pros,
        "cons": cons,
        "detected_aspects": detected_aspects,
        "explanation": explanation,
        "emoji_info": emoji_info,
        "aspect_breakdown": aspect_breakdown,
        "probabilities": probabilities
    }


def get_processing_details(review):
    text = str(review)
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    words = cleaned_text.split()
    emoji_info = detect_emoji_sentiment(review)
    aspect_breakdown = get_aspect_sentiment_breakdown(review)

    return pd.DataFrame([
        {
            "Processing Step": "Input Text",
            "Result": text
        },
        {
            "Processing Step": "Overall Sentiment Model",
            "Result": f"DistilBERT transformer model loaded from Hugging Face Hub: {HF_MODEL_ID}"
        },
        {
            "Processing Step": "Lowercasing",
            "Result": "Applied for keyword-based supporting analysis"
        },
        {
            "Processing Step": "Punctuation Removal",
            "Result": "Applied for keyword-based supporting analysis"
        },
        {
            "Processing Step": "Token Count",
            "Result": len(words)
        },
        {
            "Processing Step": "Emoji / Emoticon Sentiment Integration",
            "Result": emoji_info["emoji_sentiment"]
        },
        {
            "Processing Step": "Detected Emoji / Emoticon Signals",
            "Result": emoji_info["total_signals"]
        },
        {
            "Processing Step": "Aspect-based Analysis",
            "Result": f"{len(aspect_breakdown)} hotel aspect(s) detected"
        }
    ])