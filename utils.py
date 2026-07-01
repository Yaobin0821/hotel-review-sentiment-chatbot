import pandas as pd
import re
from data import HOTELS

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

def analyze_review_frontend(review):
    text = str(review).lower()
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = cleaned_text.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    emoji_info = detect_emoji_sentiment(review)

    if negative_count > positive_count:
        sentiment = "Negative"
        confidence = min(90, 60 + negative_count * 10)
        risk = "High" if negative_count >= 2 else "Medium"
        explanation = "The review contains more negative expressions than positive expressions."
    elif positive_count > negative_count:
        sentiment = "Positive"
        confidence = min(90, 60 + positive_count * 10)
        risk = "Low"
        explanation = "The review contains more positive expressions than negative expressions."
    else:
        if emoji_info["emoji_sentiment"] == "Positive":
            sentiment = "Positive"
            confidence = 68
            risk = "Low"
            explanation = "The text is not strongly positive or negative, but positive emoji or emoticon signals were detected."
        elif emoji_info["emoji_sentiment"] == "Negative":
            sentiment = "Negative"
            confidence = 68
            risk = "Medium"
            explanation = "The text is not strongly positive or negative, but negative emoji or emoticon signals were detected."
        elif emoji_info["emoji_sentiment"] == "Neutral":
            sentiment = "Neutral"
            confidence = 62
            risk = "Medium"
            explanation = "The review contains neutral emoji or emoticon signals and does not strongly lean positive or negative."
        else:
            sentiment = "Neutral"
            confidence = 60
            risk = "Medium"
            explanation = "The review does not strongly lean toward positive or negative sentiment."

    if emoji_info["emoji_sentiment"] == "Mixed":
        confidence = max(55, confidence - 8)
        risk = "Medium"
        explanation += " However, the emoji or emoticon signals are mixed, so the result should be interpreted carefully."

    detected_aspects = []

    for aspect, keywords in aspect_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_aspects.append(aspect)

    pros = [word for word in sorted(set(words)) if word in positive_words]
    cons = [word for word in sorted(set(words)) if word in negative_words]

    if sentiment == "Positive":
        suitability = "This review suggests the hotel may be suitable for users who value comfort, service, or convenience."
    elif sentiment == "Negative":
        suitability = "Users should be careful before booking because this review contains possible risk indicators."
    else:
        suitability = "This review is mixed or average. Users may need to compare more reviews before booking."

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
        "aspect_breakdown": get_aspect_sentiment_breakdown(review)
    }

def get_processing_details(review):
    text = str(review)
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    words = cleaned_text.split()
    emoji_info = detect_emoji_sentiment(review)
    aspect_breakdown = get_aspect_sentiment_breakdown(review)

    return pd.DataFrame([
        {
            "Processing Step": "Lowercasing",
            "Result": "Applied"
        },
        {
            "Processing Step": "Punctuation Removal",
            "Result": "Applied for keyword-based text analysis"
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
