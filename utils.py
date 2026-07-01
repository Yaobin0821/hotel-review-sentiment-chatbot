import pandas as pd
import re
import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from data import HOTELS


# =========================================================
# Hugging Face DistilBERT Sentiment Model
# =========================================================

HF_MODEL_ID = "qm0720/staywise-kl-distilbert-sentiment"

# Your training label order:
# 0 = negative, 1 = neutral, 2 = positive
FALLBACK_LABEL_ID_TO_NAME = {
    0: "Negative",
    1: "Neutral",
    2: "Positive"
}


@st.cache_resource(show_spinner="Loading DistilBERT sentiment model...")
def load_distilbert_sentiment_model():
    """
    Load trained DistilBERT sentiment model from Hugging Face Hub.
    Cached by Streamlit so the model is not reloaded every time.
    """
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(HF_MODEL_ID)
    model.eval()
    return tokenizer, model


def normalize_model_label(raw_label, predicted_id):
    """
    Convert model label into display label: Positive / Neutral / Negative.
    This handles both custom labels and default Transformer labels such as LABEL_0.
    """
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
    """
    Predict overall sentiment using the uploaded DistilBERT model from Hugging Face.
    Returns sentiment, confidence, and probability breakdown.
    """
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
# Hotel Data Helper Functions
# =========================================================

def get_areas():
    return ["Bukit Jalil", "KLCC", "Petaling Jaya", "Sunway"]


def get_hotels_by_area(area):
    return [hotel for hotel in HOTELS if hotel["area"] == area]


def get_hotel_names(area=None):
    if area:
        return [hotel["hotel"] for hotel in HOTELS if hotel["area"] == area]
    return [hotel["hotel"] for hotel in HOTELS]


def get_hotel_by_name(name):
    for hotel in HOTELS:
        if hotel["hotel"] == name:
            return hotel
    return None


def sentiment_label_style(label):
    label = str(label).lower()
    if label == "positive":
        return "🟢 Positive"
    if label == "neutral":
        return "🟡 Neutral"
    if label == "negative":
        return "🔴 Negative"
    return label


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
    rows = []

    for area, count in hotel["complaints"].items():
        if count >= 15:
            priority = "High"
        elif count >= 8:
            priority = "Medium"
        else:
            priority = "Low"

        action_map = {
            "Cleanliness": "Improve housekeeping checks and room inspection frequency.",
            "Service": "Provide additional staff training and improve front desk response time.",
            "Facilities": "Inspect and maintain hotel facilities more regularly.",
            "Price": "Review pricing fairness and highlight value-added services.",
            "Food": "Improve breakfast variety and food quality control.",
            "Noise": "Improve soundproofing and inform guests about quieter room options.",
            "Room": "Improve room maintenance and provide clearer room size information.",
            "Room Comfort": "Improve bedding quality, room ventilation and comfort facilities.",
            "Waiting Time": "Improve check-in workflow and add queue management during peak hours.",
            "Parking": "Provide clearer parking information and alternative parking suggestions.",
            "Traffic": "Provide clearer transport guidance and event-day travel advice."
        }

        rows.append({
            "Complaint Area": area,
            "Complaint Count": count,
            "Priority Level": priority,
            "Suggested Improvement Action": action_map.get(
                area,
                "Review related feedback and improve the affected service area."
            )
        })

    return pd.DataFrame(rows).sort_values(by="Complaint Count", ascending=False)


def recommend_better_hotel(hotel_a, hotel_b):
    score_a = (
        hotel_a["positive_pct"] * 0.45
        - hotel_a["negative_pct"] * 0.35
        + hotel_a["suitability_score"] * 0.20
    )

    score_b = (
        hotel_b["positive_pct"] * 0.45
        - hotel_b["negative_pct"] * 0.35
        + hotel_b["suitability_score"] * 0.20
    )

    if score_a > score_b:
        winner = hotel_a
        loser = hotel_b
    elif score_b > score_a:
        winner = hotel_b
        loser = hotel_a
    else:
        return "Both hotels are quite similar. Users should choose based on location, price, and personal travel needs."

    return (
        f"Recommended Hotel: **{winner['hotel']}**. "
        f"It is more suitable because it has stronger overall sentiment, "
        f"a lower negative review impact, and better traveller suitability compared with {loser['hotel']}."
    )


# =========================================================
# Keyword, Emoji, Emoticon and Aspect Rules
# =========================================================

positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly",
    "helpful", "nice", "spacious", "convenient", "worth", "amazing",
    "perfect", "pleasant", "beautiful", "recommended", "polite", "fast"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy",
    "smelly", "broken", "worst", "terrible", "disappointed",
    "uncomfortable", "unclean", "overpriced", "delay", "small"
]

positive_emojis = ["😊", "😍", "👍", "😁", "😄", "❤️", "✨", "🥰", "👏", "✅"]
negative_emojis = ["😡", "😠", "👎", "😞", "😢", "🤮", "😤", "❌", "💔", "😭"]
neutral_emojis = ["😐", "🤔", "🙂", "😶"]

positive_emoticons = [":)", ":-)", ":D", ":-D", ";)", ";-)"]
negative_emoticons = [":(", ":-(", ":'(", ">:(", ":-/"]
neutral_emoticons = [":|", ":-|", ":/"]

aspect_keywords = {
    "Room": ["room", "bed", "bathroom", "toilet", "shower", "pillow"],
    "Service": ["staff", "service", "reception", "manager", "friendly", "rude", "helpful"],
    "Cleanliness": ["clean", "dirty", "cleanliness", "smell", "dust", "stain", "hygiene"],
    "Location": ["location", "near", "mall", "station", "airport", "convenient", "area"],
    "Price": ["price", "expensive", "cheap", "value", "worth", "money", "overpriced"],
    "Facilities": ["pool", "gym", "wifi", "wi-fi", "parking", "lift", "elevator"],
    "Food": ["breakfast", "food", "restaurant", "meal", "buffet"]
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


def detect_review_aspects(review):
    text = str(review).lower()
    detected_aspects = []

    for aspect, keywords in aspect_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_aspects.append(aspect)

    return detected_aspects


def get_keyword_signals(review):
    text = str(review).lower()
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = cleaned_text.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    pros = [word for word in sorted(set(words)) if word in positive_words]
    cons = [word for word in sorted(set(words)) if word in negative_words]

    return words, positive_count, negative_count, pros, cons


def calculate_risk_level(sentiment, confidence, negative_count, emoji_info, aspect_breakdown):
    """
    Risk is not only based on model sentiment.
    It also considers negative keywords, negative emoji signals and negative aspect sentiment.
    """
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
        return "Although the overall sentiment is positive, users should still check the highlighted concerns before booking."

    if sentiment == "Negative":
        return "Users should be careful before booking because this review contains possible risk indicators."

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
        f"The overall sentiment was predicted as {sentiment} by the DistilBERT transformer model "
        f"with {confidence}% confidence. "
        f"The model probability distribution is: "
        f"Positive {probabilities['Positive']}%, "
        f"Neutral {probabilities['Neutral']}%, "
        f"Negative {probabilities['Negative']}%. "
    )

    if positive_count > 0 or negative_count > 0:
        explanation += (
            f"Keyword analysis detected {positive_count} positive keyword signal(s) "
            f"and {negative_count} negative keyword signal(s). "
        )
    else:
        explanation += "No strong positive or negative keyword signal was detected. "

    if emoji_info["emoji_sentiment"] != "No emoji signal":
        explanation += (
            f"Emoji or emoticon analysis detected a {emoji_info['emoji_sentiment']} signal. "
        )

    if positive_aspect_count > 0 or negative_aspect_count > 0:
        explanation += (
            f"Aspect-based analysis found {positive_aspect_count} positive aspect(s) "
            f"and {negative_aspect_count} negative aspect(s). "
        )

    if emoji_info["emoji_sentiment"] == "Mixed":
        explanation += (
            "However, the emoji or emoticon signals are mixed, so the result should be interpreted carefully."
        )

    return explanation


# =========================================================
# Main Review Checker Function
# =========================================================

def analyze_review_frontend(review):
    """
    Main function used by Review Checker page.
    Overall sentiment is predicted by Hugging Face DistilBERT.
    Emoji, aspect, risk, pros and cons are still handled by rule-based analysis.
    """
    # 1. DistilBERT sentiment prediction
    sentiment_result = predict_sentiment_distilbert(review)

    sentiment = sentiment_result["sentiment"]
    confidence = sentiment_result["confidence"]
    probabilities = sentiment_result["probabilities"]

    # 2. Rule-based supporting analysis
    words, positive_count, negative_count, pros, cons = get_keyword_signals(review)
    emoji_info = detect_emoji_sentiment(review)
    detected_aspects = detect_review_aspects(review)
    aspect_breakdown = get_aspect_sentiment_breakdown(review)

    # 3. Risk and explanation
    risk = calculate_risk_level(
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