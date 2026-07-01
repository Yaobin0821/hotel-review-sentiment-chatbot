import streamlit as st
import pandas as pd
import re
import html

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="Hotel Review Decision Support Platform",
    page_icon="🏨",
    layout="wide"
)

# =====================================================
# Demo Data - Replace with Backend Later
# =====================================================
HOTELS = [
    {
        "hotel": "Sunway Luxury Suites",
        "area": "Sunway",
        "total_reviews": 180,
        "positive_pct": 68,
        "neutral_pct": 20,
        "negative_pct": 12,
        "main_strength": "Location",
        "main_risk": "Cleanliness",
        "best_traveller_type": "Family and shopping travellers",
        "risk_level": "Medium",
        "suitability_score": 82,
        "price_level": "Mid-range",
        "description": "A convenient stay near shopping areas, restaurants, and family-friendly attractions.",
        "suitability": ["Family travellers", "Shopping travellers", "Short stay", "First-time visitors"],
        "risk_alerts": [
            "Some guests mentioned cleanliness inconsistency.",
            "A few reviews mentioned slow service during peak hours."
        ],
        "reviews": [
            ("Positive", "The location is very convenient and the room is spacious."),
            ("Positive", "Good stay for family because the mall is nearby."),
            ("Neutral", "The room was acceptable but the service can be improved."),
            ("Negative", "The bathroom was not very clean during my stay.")
        ],
        "complaints": {
            "Cleanliness": 18,
            "Service": 10,
            "Facilities": 7,
            "Price": 5
        }
    },
    {
        "hotel": "Sunway Pyramid Stay",
        "area": "Sunway",
        "total_reviews": 165,
        "positive_pct": 64,
        "neutral_pct": 23,
        "negative_pct": 13,
        "main_strength": "Shopping Access",
        "main_risk": "Waiting Time",
        "best_traveller_type": "Shopping and short-stay travellers",
        "risk_level": "Medium",
        "suitability_score": 79,
        "price_level": "Mid-range",
        "description": "A practical hotel option for users who want to stay near Sunway Pyramid and entertainment areas.",
        "suitability": ["Shopping travellers", "Short stay", "Family travellers"],
        "risk_alerts": [
            "Some reviews mentioned waiting time during check-in.",
            "A few guests mentioned crowded common areas."
        ],
        "reviews": [
            ("Positive", "Very convenient location near the mall."),
            ("Positive", "Good option for shopping and food."),
            ("Neutral", "The room was average but the location was good."),
            ("Negative", "Check-in took too long during peak hours.")
        ],
        "complaints": {
            "Waiting Time": 14,
            "Service": 9,
            "Facilities": 7,
            "Room": 5
        }
    },
    {
        "hotel": "KLCC City Comfort Hotel",
        "area": "KLCC",
        "total_reviews": 160,
        "positive_pct": 60,
        "neutral_pct": 25,
        "negative_pct": 15,
        "main_strength": "Accessibility",
        "main_risk": "Noise",
        "best_traveller_type": "Business and city travellers",
        "risk_level": "Medium",
        "suitability_score": 76,
        "price_level": "Mid-range",
        "description": "A practical option for travellers who need quick access to KLCC, city attractions, and public transport.",
        "suitability": ["Business travellers", "Solo travellers", "City travellers"],
        "risk_alerts": [
            "Some guests mentioned noise from nearby roads.",
            "Room size may feel small for families."
        ],
        "reviews": [
            ("Positive", "The hotel is near public transport and very convenient."),
            ("Neutral", "The room is small but acceptable for a short stay."),
            ("Negative", "The road noise was quite disturbing at night."),
            ("Positive", "Good value for a city hotel.")
        ],
        "complaints": {
            "Noise": 20,
            "Room": 12,
            "Price": 6,
            "Service": 5
        }
    },
    {
        "hotel": "KLCC Luxury Suites",
        "area": "KLCC",
        "total_reviews": 210,
        "positive_pct": 73,
        "neutral_pct": 17,
        "negative_pct": 10,
        "main_strength": "City View",
        "main_risk": "Price",
        "best_traveller_type": "Couples and city travellers",
        "risk_level": "Low",
        "suitability_score": 87,
        "price_level": "Premium",
        "description": "A premium city stay for users who prefer skyline views, comfort, and access to KLCC attractions.",
        "suitability": ["Couples", "City travellers", "Business travellers", "Premium travellers"],
        "risk_alerts": [
            "Some guests felt the room rate was expensive.",
            "A few reviews mentioned extra charges."
        ],
        "reviews": [
            ("Positive", "The city view was beautiful and the room was comfortable."),
            ("Positive", "Excellent location near KLCC and restaurants."),
            ("Neutral", "The stay was good but the price was high."),
            ("Negative", "The room was expensive compared to similar hotels.")
        ],
        "complaints": {
            "Price": 16,
            "Service": 7,
            "Facilities": 5,
            "Room": 4
        }
    },
    {
        "hotel": "PJ Business Hotel",
        "area": "Petaling Jaya",
        "total_reviews": 150,
        "positive_pct": 58,
        "neutral_pct": 27,
        "negative_pct": 15,
        "main_strength": "Business Convenience",
        "main_risk": "Parking",
        "best_traveller_type": "Business travellers",
        "risk_level": "Medium",
        "suitability_score": 74,
        "price_level": "Mid-range",
        "description": "A practical hotel for business travellers who need access to offices and transport routes.",
        "suitability": ["Business travellers", "Solo travellers", "Short stay"],
        "risk_alerts": [
            "Parking availability may be limited.",
            "Some reviews mentioned slow check-in."
        ],
        "reviews": [
            ("Positive", "Good hotel for business travel and short stays."),
            ("Neutral", "Room is acceptable but parking is difficult."),
            ("Negative", "Parking was full and service was slow."),
            ("Positive", "The location is convenient for work.")
        ],
        "complaints": {
            "Parking": 18,
            "Service": 11,
            "Facilities": 8,
            "Room": 5
        }
    },
    {
        "hotel": "PJ City Comfort Hotel",
        "area": "Petaling Jaya",
        "total_reviews": 145,
        "positive_pct": 62,
        "neutral_pct": 24,
        "negative_pct": 14,
        "main_strength": "Value for Money",
        "main_risk": "Room Comfort",
        "best_traveller_type": "Budget and business travellers",
        "risk_level": "Medium",
        "suitability_score": 77,
        "price_level": "Budget",
        "description": "A value-focused hotel option for travellers who want affordable accommodation in Petaling Jaya.",
        "suitability": ["Budget travellers", "Business travellers", "Solo travellers"],
        "risk_alerts": [
            "Some guests mentioned that rooms were small.",
            "A few reviews mentioned older room facilities."
        ],
        "reviews": [
            ("Positive", "Good value for money and convenient location."),
            ("Positive", "The staff were helpful and the price was affordable."),
            ("Neutral", "The room was small but acceptable."),
            ("Negative", "The bed was not very comfortable.")
        ],
        "complaints": {
            "Room Comfort": 15,
            "Facilities": 10,
            "Cleanliness": 7,
            "Service": 6
        }
    },
    {
        "hotel": "Bukit Jalil City Hotel",
        "area": "Bukit Jalil",
        "total_reviews": 155,
        "positive_pct": 65,
        "neutral_pct": 22,
        "negative_pct": 13,
        "main_strength": "Event Access",
        "main_risk": "Traffic",
        "best_traveller_type": "Event and family travellers",
        "risk_level": "Medium",
        "suitability_score": 80,
        "price_level": "Mid-range",
        "description": "A suitable option for users attending events or travelling with family around Bukit Jalil.",
        "suitability": ["Event travellers", "Family travellers", "Short stay", "Sports event visitors"],
        "risk_alerts": [
            "Some guests mentioned traffic during event days.",
            "A few reviews mentioned limited food options nearby."
        ],
        "reviews": [
            ("Positive", "Very convenient for attending events in Bukit Jalil."),
            ("Positive", "The room was clean and suitable for family."),
            ("Neutral", "The hotel was good but traffic was heavy."),
            ("Negative", "It was difficult to get transport after the event.")
        ],
        "complaints": {
            "Traffic": 17,
            "Food": 8,
            "Service": 6,
            "Facilities": 5
        }
    },
    {
        "hotel": "Bukit Jalil Budget Stay",
        "area": "Bukit Jalil",
        "total_reviews": 130,
        "positive_pct": 52,
        "neutral_pct": 28,
        "negative_pct": 20,
        "main_strength": "Price",
        "main_risk": "Room Comfort",
        "best_traveller_type": "Budget travellers",
        "risk_level": "High",
        "suitability_score": 68,
        "price_level": "Budget",
        "description": "A budget-friendly option for travellers who prioritize price and location over room comfort.",
        "suitability": ["Budget travellers", "Solo travellers", "Backpackers"],
        "risk_alerts": [
            "Room comfort risk is higher than other hotels.",
            "Some guests mentioned small rooms and noise."
        ],
        "reviews": [
            ("Positive", "The price is cheap and the location is convenient."),
            ("Neutral", "Good for one night but the room is small."),
            ("Negative", "The bed was uncomfortable and the room was noisy."),
            ("Neutral", "Acceptable for budget travellers.")
        ],
        "complaints": {
            "Room Comfort": 22,
            "Noise": 14,
            "Cleanliness": 10,
            "Service": 6
        }
    }
]

# =====================================================
# Helper Functions
# =====================================================
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

def risk_rank(risk):
    return {"Low": 1, "Medium": 2, "High": 3}.get(risk, 2)

def price_rank(price):
    return {"Budget": 1, "Mid-range": 2, "Premium": 3}.get(price, 2)

def get_sentiment_df(hotel):
    return pd.DataFrame({
        "Sentiment": ["Positive", "Neutral", "Negative"],
        "Percentage": [hotel["positive_pct"], hotel["neutral_pct"], hotel["negative_pct"]]
    })

def risk_explanation(risk_area):
    explanations = {
        "Cleanliness": "Cleanliness risk may affect comfort and hygiene-sensitive travellers.",
        "Waiting Time": "Waiting time risk may affect users arriving during peak check-in hours.",
        "Noise": "Noise risk may affect light sleepers, business travellers, or families.",
        "Price": "Price risk may affect travellers who are sensitive to budget or value for money.",
        "Parking": "Parking risk may affect users travelling by car.",
        "Room Comfort": "Room comfort risk may affect users staying for longer periods.",
        "Traffic": "Traffic risk may affect users attending events or travelling during peak hours.",
        "Food": "Food risk may affect users who rely on hotel breakfast or in-house dining.",
        "Service": "Service risk may affect users who need fast support from hotel staff.",
        "Facilities": "Facilities risk may affect users expecting gym, pool, lift, Wi-Fi, or other amenities."
    }
    return explanations.get(risk_area, "This risk may affect the overall guest experience.")

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
            "Why It Matters": risk_explanation(area),
            "Suggested Improvement Action": action_map.get(
                area,
                "Review related feedback and improve the affected service area."
            )
        })

    return pd.DataFrame(rows).sort_values(by="Complaint Count", ascending=False)

def traveller_match_score(hotel, traveller_type, risk_tolerance, budget_level):
    score = 50

    text = (
        hotel["best_traveller_type"] + " " +
        " ".join(hotel["suitability"]) + " " +
        hotel["description"]
    ).lower()

    traveller_keywords = {
        "Any": [],
        "Family": ["family"],
        "Business": ["business"],
        "Budget": ["budget", "value", "affordable"],
        "Shopping": ["shopping", "mall"],
        "Event": ["event", "sports"],
        "Couple": ["couple", "couples", "premium"]
    }

    for keyword in traveller_keywords.get(traveller_type, []):
        if keyword in text:
            score += 15

    if budget_level != "Any":
        if hotel["price_level"] == budget_level:
            score += 18
        else:
            score -= 6

    tolerance_rank = {"Low": 1, "Medium": 2, "High": 3}.get(risk_tolerance, 2)

    if risk_rank(hotel["risk_level"]) <= tolerance_rank:
        score += 14
    else:
        score -= 15

    score += int(hotel["positive_pct"] * 0.12)
    score -= int(hotel["negative_pct"] * 0.10)

    return max(0, min(100, score))

def sort_hotels(hotels, sort_by):
    if sort_by == "Best match score":
        return hotels
    if sort_by == "Highest positive reviews":
        return sorted(hotels, key=lambda h: h["positive_pct"], reverse=True)
    if sort_by == "Lowest risk":
        return sorted(hotels, key=lambda h: risk_rank(h["risk_level"]))
    if sort_by == "Highest suitability score":
        return sorted(hotels, key=lambda h: h["suitability_score"], reverse=True)
    if sort_by == "Most reviews":
        return sorted(hotels, key=lambda h: h["total_reviews"], reverse=True)
    return hotels

def compare_breakdown(hotel_a, hotel_b):
    rows = []

    rows.append({
        "Decision Factor": "Higher Positive Sentiment",
        "Winner": hotel_a["hotel"] if hotel_a["positive_pct"] > hotel_b["positive_pct"] else hotel_b["hotel"],
        "Reason": f"{hotel_a['hotel']}: {hotel_a['positive_pct']}%, {hotel_b['hotel']}: {hotel_b['positive_pct']}%"
    })

    rows.append({
        "Decision Factor": "Lower Negative Risk",
        "Winner": hotel_a["hotel"] if hotel_a["negative_pct"] < hotel_b["negative_pct"] else hotel_b["hotel"],
        "Reason": f"{hotel_a['hotel']}: {hotel_a['negative_pct']}%, {hotel_b['hotel']}: {hotel_b['negative_pct']}%"
    })

    rows.append({
        "Decision Factor": "Better Traveller Suitability",
        "Winner": hotel_a["hotel"] if hotel_a["suitability_score"] > hotel_b["suitability_score"] else hotel_b["hotel"],
        "Reason": f"{hotel_a['hotel']}: {hotel_a['suitability_score']}/100, {hotel_b['hotel']}: {hotel_b['suitability_score']}/100"
    })

    rows.append({
        "Decision Factor": "Lower Risk Level",
        "Winner": hotel_a["hotel"] if risk_rank(hotel_a["risk_level"]) < risk_rank(hotel_b["risk_level"]) else hotel_b["hotel"],
        "Reason": f"{hotel_a['hotel']}: {hotel_a['risk_level']}, {hotel_b['hotel']}: {hotel_b['risk_level']}"
    })

    rows.append({
        "Decision Factor": "More Review Evidence",
        "Winner": hotel_a["hotel"] if hotel_a["total_reviews"] > hotel_b["total_reviews"] else hotel_b["hotel"],
        "Reason": f"{hotel_a['hotel']}: {hotel_a['total_reviews']} reviews, {hotel_b['hotel']}: {hotel_b['total_reviews']} reviews"
    })

    return pd.DataFrame(rows)

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
        f"It is more suitable because it has stronger overall sentiment, lower negative review impact, "
        f"and better traveller suitability compared with {loser['hotel']}."
    )

# =====================================================
# Review Checker Logic
# =====================================================
positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly",
    "helpful", "nice", "spacious", "convenient", "worth", "amazing",
    "perfect", "pleasant", "beautiful", "recommended", "polite", "fast"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy",
    "smelly", "broken", "worst", "terrible", "disappointed",
    "uncomfortable", "unclean", "overpriced", "small", "delay"
]

hotel_related_words = [
    "hotel", "room", "bed", "bathroom", "staff", "service", "clean",
    "dirty", "location", "price", "breakfast", "parking", "wifi",
    "wi-fi", "lift", "pool", "gym", "restaurant", "check", "lobby"
]

aspect_keywords = {
    "Room": ["room", "bed", "bathroom", "toilet", "shower", "pillow"],
    "Service": ["staff", "service", "reception", "manager", "friendly", "rude", "helpful"],
    "Cleanliness": ["clean", "dirty", "cleanliness", "smell", "dust", "stain", "hygiene"],
    "Location": ["location", "near", "mall", "station", "airport", "convenient", "area"],
    "Price": ["price", "expensive", "cheap", "value", "worth", "money", "overpriced"],
    "Facilities": ["pool", "gym", "wifi", "wi-fi", "parking", "lift", "elevator"],
    "Food": ["breakfast", "food", "restaurant", "meal", "buffet"]
}

def input_quality_check(review):
    text = str(review).lower()
    words = re.findall(r"[a-zA-Z]+", text)

    detected_hotel_words = [word for word in words if word in hotel_related_words]
    detected_aspects = []

    for aspect, keywords in aspect_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_aspects.append(aspect)

    if len(words) < 5:
        quality = "Low"
        note = "The review is very short, so the result may be less reliable."
    elif len(detected_hotel_words) == 0:
        quality = "Low"
        note = "No strong hotel-related keywords were detected."
    elif len(detected_aspects) >= 2:
        quality = "High"
        note = "The review contains clear hotel-related aspects."
    else:
        quality = "Medium"
        note = "The review is hotel-related but contains limited aspect detail."

    return {
        "Review Length": len(words),
        "Hotel Keywords Detected": ", ".join(sorted(set(detected_hotel_words))) if detected_hotel_words else "None",
        "Detected Aspects": ", ".join(detected_aspects) if detected_aspects else "None",
        "Input Quality": quality,
        "Note": note
    }

def analyze_review_frontend(review):
    text = str(review).lower()
    cleaned_text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = cleaned_text.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    if negative_count > positive_count:
        sentiment = "Negative"
        confidence = min(90, 60 + negative_count * 10)
        risk = "High" if negative_count >= 2 else "Medium"
    elif positive_count > negative_count:
        sentiment = "Positive"
        confidence = min(90, 60 + positive_count * 10)
        risk = "Low"
    else:
        sentiment = "Neutral"
        confidence = 60
        risk = "Medium"

    detected_aspects = []

    for aspect, keywords in aspect_keywords.items():
        if any(keyword in text for keyword in keywords):
            detected_aspects.append(aspect)

    pros = [word for word in sorted(set(words)) if word in positive_words]
    cons = [word for word in sorted(set(words)) if word in negative_words]

    if sentiment == "Positive":
        suitability = "This review suggests the hotel may be suitable for users who value comfort, service, or convenience."
        explanation = "The review contains more positive expressions than negative expressions."
    elif sentiment == "Negative":
        suitability = "Users should be careful before booking because this review contains possible risk indicators."
        explanation = "The review contains more negative expressions than positive expressions."
    else:
        suitability = "This review is mixed or average. Users may need to compare more reviews before booking."
        explanation = "The review does not strongly lean toward positive or negative sentiment."

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "risk": risk,
        "suitability": suitability,
        "pros": pros,
        "cons": cons,
        "detected_aspects": detected_aspects,
        "explanation": explanation
    }

# =====================================================
# CSS Styling
# =====================================================
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

.topbar {
    padding: 20px 24px;
    border-radius: 24px;
    background: rgba(255,255,255,0.88);
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
    margin-bottom: 20px;
}

.brand-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 3px;
}

.brand-subtitle {
    font-size: 14px;
    color: #64748b;
}

.hero {
    padding: 42px;
    border-radius: 30px;
    background:
        radial-gradient(circle at top right, rgba(96,165,250,0.35), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, #eff6ff 48%, #dbeafe 100%);
    color: #0f172a;
    margin-bottom: 24px;
    box-shadow: 0 18px 40px rgba(30, 64, 175, 0.12);
    border: 1px solid #dbeafe;
}

.hero h1 {
    color: #0f172a;
    font-size: 46px;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}

.hero p {
    color: #334155;
    font-size: 18px;
    max-width: 900px;
}

.hero-badge {
    display: inline-block;
    background: #dbeafe;
    border: 1px solid #bfdbfe;
    padding: 8px 14px;
    border-radius: 999px;
    color: #1d4ed8;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 15px;
}

.page-header {
    padding: 22px 24px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
    margin-bottom: 22px;
}

.page-header h2 {
    margin: 0 0 8px 0;
    color: #0f172a;
}

.page-header p {
    margin: 0;
    color: #475569;
    font-size: 16px;
}

.card {
    padding: 24px;
    border-radius: 24px;
    background: rgba(255,255,255,0.95);
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
    border: 1px solid #e5e7eb;
    margin-bottom: 18px;
}

.hotel-card {
    padding: 24px;
    border-radius: 26px;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
    border: 1px solid #e2e8f0;
    min-height: 405px;
    margin-bottom: 22px;
    transition: all 0.2s ease-in-out;
}

.hotel-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 38px rgba(15, 23, 42, 0.12);
}

.hotel-card h3 {
    margin-bottom: 8px;
    color: #0f172a;
    font-size: 22px;
}

.hotel-card p {
    color: #334155;
}

.tag {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: #eff6ff;
    color: #1d4ed8;
    font-size: 13px;
    margin: 4px 5px 4px 0;
    font-weight: 600;
}

.risk-low {
    background: #dcfce7;
    color: #166534;
    padding: 8px 13px;
    border-radius: 999px;
    display: inline-block;
    font-weight: 700;
}

.risk-medium {
    background: #fef9c3;
    color: #854d0e;
    padding: 8px 13px;
    border-radius: 999px;
    display: inline-block;
    font-weight: 700;
}

.risk-high {
    background: #fee2e2;
    color: #991b1b;
    padding: 8px 13px;
    border-radius: 999px;
    display: inline-block;
    font-weight: 700;
}

.info-box {
    padding: 20px;
    border-radius: 20px;
    background: #eff6ff;
    border-left: 8px solid #2563eb;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.08);
}

.warning-box {
    padding: 20px;
    border-radius: 20px;
    background: #fff7ed;
    border-left: 8px solid #ea580c;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(234, 88, 12, 0.08);
}

.good-box {
    padding: 20px;
    border-radius: 20px;
    background: #ecfdf5;
    border-left: 8px solid #16a34a;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(22, 163, 74, 0.08);
}

.bad-box {
    padding: 20px;
    border-radius: 20px;
    background: #fef2f2;
    border-left: 8px solid #dc2626;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(220, 38, 38, 0.08);
}

.small-text {
    color: #64748b;
    font-size: 14px;
}

.footer-note {
    color: #64748b;
    font-size: 13px;
}

.stButton > button {
    border-radius: 14px;
    padding: 0.65rem 1rem;
    font-weight: 700;
    border: 1px solid #2563eb;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
}

.stButton > button:hover {
    border: 1px solid #1e40af;
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    color: white;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.92);
    padding: 16px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}

div[role="radiogroup"] {
    background: white;
    border: 1px solid #dbeafe;
    padding: 10px;
    border-radius: 22px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    margin-bottom: 22px;
}

div[role="radiogroup"] label {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 12px 16px;
    border-radius: 16px;
    margin-right: 8px;
    font-weight: 700;
    color: #0f172a;
    transition: all 0.2s ease-in-out;
}

div[role="radiogroup"] label:hover {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Top Navigation
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home / Find Hotels"

PAGE_INFO = {
    "🏠 Home / Find Hotels": {
        "title": "Home / Find Hotels",
        "desc": "Browse hotels by area and quickly understand each hotel's review-based strengths and risks."
    },
    "🏨 Hotel Detail": {
        "title": "Hotel Detail",
        "desc": "View full sentiment summary, risk alerts, traveller suitability, and review examples."
    },
    "⚖️ Compare Hotels": {
        "title": "Compare Hotels",
        "desc": "Compare two hotels from the same area before making a booking decision."
    },
    "🔍 Review Checker": {
        "title": "Review Checker",
        "desc": "Paste one review and check its sentiment, risks, pros, cons, and explanation."
    },
    "📊 Improvement Insights": {
        "title": "Improvement Insights",
        "desc": "View common complaint areas and suggested improvement actions for a selected hotel."
    }
}

st.markdown("""
<div class="topbar">
    <div class="brand-title">🏨 Hotel Review Decision Support Platform</div>
    <div class="brand-subtitle">A traveller-focused web application for hotel review sentiment, risk, and suitability analysis.</div>
</div>
""", unsafe_allow_html=True)

page_options = list(PAGE_INFO.keys())
current_page = st.session_state.get("page", page_options[0])

if current_page not in page_options:
    current_page = page_options[0]

page = st.radio(
    "Navigation",
    page_options,
    index=page_options.index(current_page),
    horizontal=True,
    label_visibility="collapsed"
)

st.session_state.page = page

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="hero">
    <div class="hero-badge">Traveller Decision-Support Platform</div>
    <h1>Make Better Hotel Decisions from Reviews</h1>
    <p>Explore hotels by area, understand review sentiment, compare booking risks, and identify whether a hotel matches your traveller profile.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="page-header">
    <h2>{PAGE_INFO[page]["title"]}</h2>
    <p>{PAGE_INFO[page]["desc"]}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Page 1: Home / Find Hotels
# =====================================================
if page == "🏠 Home / Find Hotels":
    st.subheader("Find Hotels by Area")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        selected_area = st.selectbox("Area", get_areas())

    with filter_col2:
        traveller_type = st.selectbox(
            "Traveller Type",
            ["Any", "Family", "Business", "Budget", "Shopping", "Event", "Couple"]
        )

    with filter_col3:
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Low", "Medium", "High"],
            index=1
        )

    with filter_col4:
        budget_level = st.selectbox(
            "Budget Level",
            ["Any", "Budget", "Mid-range", "Premium"]
        )

    sort_by = st.selectbox(
        "Sort Hotels By",
        [
            "Best match score",
            "Highest positive reviews",
            "Lowest risk",
            "Highest suitability score",
            "Most reviews"
        ]
    )

    hotels = get_hotels_by_area(selected_area)

    for hotel in hotels:
        hotel["match_score"] = traveller_match_score(
            hotel,
            traveller_type,
            risk_tolerance,
            budget_level
        )

    if sort_by == "Best match score":
        hotels = sorted(hotels, key=lambda h: h["match_score"], reverse=True)
    else:
        hotels = sort_hotels(hotels, sort_by)

    st.markdown("### Recommended Hotels")

    cols = st.columns(2)

    for index, hotel in enumerate(hotels):
        with cols[index % 2]:
            risk_class = risk_css_class(hotel["risk_level"])

            st.markdown(f"""
            <div class="hotel-card">
                <h3>{hotel["hotel"]}</h3>
                <p class="small-text">{hotel["area"]} • {hotel["price_level"]}</p>
                <p><b>Match Score:</b> {hotel["match_score"]}/100</p>
                <p><b>Sentiment Summary</b></p>
                <p>🟢 Positive: {hotel["positive_pct"]}%<br>
                🟡 Neutral: {hotel["neutral_pct"]}%<br>
                🔴 Negative: {hotel["negative_pct"]}%</p>
                <p><b>Main Strength:</b> {hotel["main_strength"]}</p>
                <p><b>Main Risk:</b> {hotel["main_risk"]}</p>
                <p class="small-text">{risk_explanation(hotel["main_risk"])}</p>
                <p><b>Best Traveller Type:</b><br>{hotel["best_traveller_type"]}</p>
                <p><span class="{risk_class}">{risk_badge(hotel["risk_level"])}</span></p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Details", key=f"view_{hotel['hotel']}"):
                st.session_state.selected_hotel = hotel["hotel"]
                st.session_state.page = "🏨 Hotel Detail"
                st.rerun()

# =====================================================
# Page 2: Hotel Detail
# =====================================================
elif page == "🏨 Hotel Detail":
    default_hotel = st.session_state.get("selected_hotel", get_hotel_names()[0])

    hotel_name = st.selectbox(
        "Select Hotel",
        get_hotel_names(),
        index=get_hotel_names().index(default_hotel) if default_hotel in get_hotel_names() else 0
    )

    hotel = get_hotel_by_name(hotel_name)

    if hotel:
        st.markdown(f"## {hotel['hotel']}")
        st.write(hotel["description"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Reviews", hotel["total_reviews"])
        c2.metric("Positive", f"{hotel['positive_pct']}%")
        c3.metric("Neutral", f"{hotel['neutral_pct']}%")
        c4.metric("Negative", f"{hotel['negative_pct']}%")

        st.markdown("### Sentiment Distribution")
        sentiment_df = get_sentiment_df(hotel)
        st.bar_chart(sentiment_df.set_index("Sentiment"))

        left, right = st.columns([1, 1])

        with left:
            st.markdown("### Risk Alerts")
            for alert in hotel["risk_alerts"]:
                st.markdown(f"""
                <div class="warning-box">
                    ⚠️ {alert}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### Main Risk Explanation")
            st.info(risk_explanation(hotel["main_risk"]))

        with right:
            st.markdown("### Traveller Suitability")

            st.markdown(f"""
            <div class="good-box">
                <b>Best for:</b> {hotel["best_traveller_type"]}<br>
                <b>Suitability Score:</b> {hotel["suitability_score"]}/100<br>
                <b>Risk Level:</b> {risk_badge(hotel["risk_level"])}
            </div>
            """, unsafe_allow_html=True)

            for item in hotel["suitability"]:
                st.markdown(f'<span class="tag">{item}</span>', unsafe_allow_html=True)

        st.markdown("### Review List")

        review_filter = st.selectbox(
            "Filter Reviews",
            ["All", "Positive", "Neutral", "Negative"]
        )

        for sentiment, review in hotel["reviews"]:
            if review_filter != "All" and sentiment != review_filter:
                continue

            if sentiment == "Positive":
                box_class = "good-box"
            elif sentiment == "Negative":
                box_class = "bad-box"
            else:
                box_class = "warning-box"

            st.markdown(f"""
            <div class="{box_class}">
                <b>{sentiment_label_style(sentiment)}</b><br>
                {html.escape(review)}
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# Page 3: Compare Hotels
# =====================================================
elif page == "⚖️ Compare Hotels":
    selected_area = st.selectbox("Select Area", get_areas(), key="compare_area")
    hotel_options = get_hotel_names(selected_area)

    if len(hotel_options) < 2:
        st.warning("This area does not have enough hotels for comparison.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            hotel_a_name = st.selectbox("Select Hotel A", hotel_options, key="hotel_a")

        with col2:
            hotel_b_name = st.selectbox("Select Hotel B", hotel_options, key="hotel_b")

        hotel_a = get_hotel_by_name(hotel_a_name)
        hotel_b = get_hotel_by_name(hotel_b_name)

        if hotel_a_name == hotel_b_name:
            st.warning("Please select two different hotels.")
        else:
            comparison_df = pd.DataFrame({
                "Criteria": [
                    "Area",
                    "Total Reviews",
                    "Positive %",
                    "Neutral %",
                    "Negative %",
                    "Main Strength",
                    "Main Risk",
                    "Risk Level",
                    "Best Traveller Type",
                    "Suitability Score",
                    "Price Level"
                ],
                hotel_a["hotel"]: [
                    hotel_a["area"],
                    hotel_a["total_reviews"],
                    f"{hotel_a['positive_pct']}%",
                    f"{hotel_a['neutral_pct']}%",
                    f"{hotel_a['negative_pct']}%",
                    hotel_a["main_strength"],
                    hotel_a["main_risk"],
                    hotel_a["risk_level"],
                    hotel_a["best_traveller_type"],
                    hotel_a["suitability_score"],
                    hotel_a["price_level"]
                ],
                hotel_b["hotel"]: [
                    hotel_b["area"],
                    hotel_b["total_reviews"],
                    f"{hotel_b['positive_pct']}%",
                    f"{hotel_b['neutral_pct']}%",
                    f"{hotel_b['negative_pct']}%",
                    hotel_b["main_strength"],
                    hotel_b["main_risk"],
                    hotel_b["risk_level"],
                    hotel_b["best_traveller_type"],
                    hotel_b["suitability_score"],
                    hotel_b["price_level"]
                ]
            })

            st.markdown("### Comparison Table")
            st.dataframe(comparison_df, use_container_width=True)

            st.markdown("### Sentiment Comparison")
            chart_df = pd.DataFrame({
                "Hotel": [hotel_a["hotel"], hotel_b["hotel"]],
                "Positive": [hotel_a["positive_pct"], hotel_b["positive_pct"]],
                "Neutral": [hotel_a["neutral_pct"], hotel_b["neutral_pct"]],
                "Negative": [hotel_a["negative_pct"], hotel_b["negative_pct"]]
            })
            st.bar_chart(chart_df.set_index("Hotel"))

            st.markdown("### Decision Breakdown")
            breakdown_df = compare_breakdown(hotel_a, hotel_b)
            st.dataframe(breakdown_df, use_container_width=True)

            st.markdown("### Recommendation")
            recommendation = recommend_better_hotel(hotel_a, hotel_b)
            st.success(recommendation)

# =====================================================
# Page 4: Review Checker
# =====================================================
elif page == "🔍 Review Checker":
    st.caption("User input is not saved in this page.")

    review_input = st.text_area(
        "Paste one hotel review",
        height=170,
        placeholder="Example: The room was dirty, the wi-fi was slow, and the staff were rude."
    )

    analyze = st.button("Analyze Review", use_container_width=True)

    if analyze:
        if review_input.strip() == "":
            st.warning("Please paste a hotel review first.")
        else:
            quality = input_quality_check(review_input)
            result = analyze_review_frontend(review_input)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sentiment", sentiment_label_style(result["sentiment"]))
            c2.metric("Confidence", f"{result['confidence']}%")
            c3.metric("Risk", result["risk"])
            c4.metric("Detected Aspects", len(result["detected_aspects"]))

            if result["sentiment"] == "Positive":
                st.markdown(f"""
                <div class="good-box">
                    <h3>Overall Result: Positive</h3>
                    <p>{result["suitability"]}</p>
                </div>
                """, unsafe_allow_html=True)
            elif result["sentiment"] == "Negative":
                st.markdown(f"""
                <div class="bad-box">
                    <h3>Overall Result: Negative</h3>
                    <p>{result["suitability"]}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    <h3>Overall Result: Neutral</h3>
                    <p>{result["suitability"]}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### Pros and Cons")

            p_col, c_col = st.columns(2)

            with p_col:
                if result["pros"]:
                    st.success(", ".join(result["pros"]))
                else:
                    st.info("No clear pros detected.")

            with c_col:
                if result["cons"]:
                    st.error(", ".join(result["cons"]))
                else:
                    st.info("No clear cons detected.")

            st.markdown("### Detected Hotel Aspects")
            if result["detected_aspects"]:
                for aspect in result["detected_aspects"]:
                    st.markdown(f'<span class="tag">{aspect}</span>', unsafe_allow_html=True)
            else:
                st.info("No specific hotel aspect detected.")

            st.markdown("### Explanation")
            st.write(result["explanation"])

            st.markdown("### Traveller Decision Note")
            if result["risk"] == "High":
                st.error("This review contains clear risk signals. Users should compare more reviews before booking.")
            elif result["risk"] == "Medium":
                st.warning("This review is mixed or has some concerns. Users should check more reviews before deciding.")
            else:
                st.success("This review looks generally safe, but users should still compare multiple reviews.")

            with st.expander("View Input Quality Check"):
                quality_df = pd.DataFrame([quality])
                st.dataframe(quality_df, use_container_width=True)

# =====================================================
# Page 5: Improvement Insights
# =====================================================
elif page == "📊 Improvement Insights":
    hotel_name = st.selectbox("Select Hotel", get_hotel_names(), key="insight_hotel")
    hotel = get_hotel_by_name(hotel_name)

    if hotel:
        st.markdown(f"## {hotel['hotel']}")

        complaint_df = get_complaint_df(hotel)

        c1, c2, c3 = st.columns(3)
        c1.metric("Main Risk", hotel["main_risk"])
        c2.metric("Risk Level", hotel["risk_level"])
        c3.metric("Negative Reviews", f"{hotel['negative_pct']}%")

        st.markdown("### Most Common Complaint Areas")
        st.bar_chart(complaint_df.set_index("Complaint Area")[["Complaint Count"]])

        st.markdown("### Priority Table")
        st.dataframe(complaint_df, use_container_width=True)

        st.markdown("### Suggested Improvement Focus")
        top_issue = complaint_df.iloc[0]

        if top_issue["Priority Level"] == "High":
            st.error(
                f"Highest priority area: {top_issue['Complaint Area']}. "
                f"Suggested action: {top_issue['Suggested Improvement Action']}"
            )
        elif top_issue["Priority Level"] == "Medium":
            st.warning(
                f"Medium priority area: {top_issue['Complaint Area']}. "
                f"Suggested action: {top_issue['Suggested Improvement Action']}"
            )
        else:
            st.success(
                f"Current complaint level is low. Continue monitoring {top_issue['Complaint Area']}."
            )

# =====================================================
# Footer
# =====================================================
st.divider()
st.markdown(
    '<p class="footer-note">Hotel Review Decision Support Platform for traveller-focused hotel review analysis.</p>',
    unsafe_allow_html=True
)
