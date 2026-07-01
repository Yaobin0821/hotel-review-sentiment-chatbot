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
# Area dropdown only: Bukit Jalil, KLCC, Petaling Jaya, Sunway
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
        "description": "Suitable for travellers who want easy access to shopping malls, restaurants, and family-friendly facilities.",
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
        "description": "A convenient hotel option for users who want to stay near Sunway Pyramid, restaurants, and entertainment areas.",
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
        "description": "A premium city stay suitable for users who prefer skyline views, comfort, and easy access to KLCC attractions.",
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
        "description": "Suitable for business travellers who need a practical hotel near offices and transport routes.",
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
        "description": "Suitable for users attending events or travelling with family around Bukit Jalil.",
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

# =====================================================
# Demo Review Checker Logic
# Frontend-only until backend is ready
# =====================================================
positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly",
    "helpful", "nice", "spacious", "convenient", "worth", "amazing",
    "perfect", "pleasant", "beautiful", "recommended"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy",
    "smelly", "broken", "worst", "terrible", "disappointed",
    "uncomfortable", "unclean", "overpriced"
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
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none;
}

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

.nav-hint {
    padding: 18px 20px;
    border-radius: 20px;
    background: #ffffff;
    border: 1px solid #dbeafe;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    margin-bottom: 22px;
}

.nav-hint b {
    color: #1d4ed8;
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
    min-height: 370px;
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
    <h2>{page}</h2>
    <p>{PAGE_INFO[page]["desc"]}</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Page 1: Home / Find Hotels
# =====================================================
if page == "🏠 Home / Find Hotels":
    st.markdown("""
    <div class="nav-hint">
        <b>How to use:</b> Select an area → Review hotel cards → Open hotel detail before booking.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Find Hotels by Area")
    st.write("Select an area to discover hotels with sentiment summary, main strength, main risk, and best traveller type.")

    selected_area = st.selectbox("Select Area", get_areas())

    hotels = get_hotels_by_area(selected_area)

    st.markdown("### Recommended Hotels in This Area")

    cols = st.columns(2)

    for index, hotel in enumerate(hotels):
        with cols[index % 2]:
            risk_class = risk_css_class(hotel["risk_level"])

            st.markdown(f"""
            <div class="hotel-card">
                <h3>{hotel["hotel"]}</h3>
                <p class="small-text">{hotel["area"]} • {hotel["price_level"]}</p>
                <p><b>Sentiment Summary</b></p>
                <p>🟢 Positive: {hotel["positive_pct"]}%<br>
                🟡 Neutral: {hotel["neutral_pct"]}%<br>
                🔴 Negative: {hotel["negative_pct"]}%</p>
                <p><b>Main Strength:</b> {hotel["main_strength"]}</p>
                <p><b>Main Risk:</b> {hotel["main_risk"]}</p>
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
    st.markdown("""
    <div class="nav-hint">
        <b>Use this page to:</b> check full hotel sentiment, risk alerts, suitability, and review examples.
    </div>
    """, unsafe_allow_html=True)

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

        for sentiment, review in hotel["reviews"]:
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
    st.markdown("""
    <div class="nav-hint">
        <b>Use this page to:</b> compare two hotels from the same area and get a booking recommendation.
    </div>
    """, unsafe_allow_html=True)

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

            st.markdown("### Recommendation")
            recommendation = recommend_better_hotel(hotel_a, hotel_b)
            st.success(recommendation)

# =====================================================
# Page 4: Review Checker
# =====================================================
elif page == "🔍 Review Checker":
    st.markdown("""
    <div class="nav-hint">
        <b>Use this page to:</b> paste one hotel review and understand its sentiment, risks, pros, cons, and explanation.
    </div>
    """, unsafe_allow_html=True)

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

# =====================================================
# Page 5: Improvement Insights
# =====================================================
elif page == "📊 Improvement Insights":
    st.markdown("""
    <div class="nav-hint">
        <b>Use this page to:</b> identify common complaint areas and priority improvement actions for a selected hotel.
    </div>
    """, unsafe_allow_html=True)

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
    '<p class="footer-note">Frontend prototype for traveller decision-support platform. Backend sentiment model and final dataset can be integrated later.</p>',
    unsafe_allow_html=True
)
