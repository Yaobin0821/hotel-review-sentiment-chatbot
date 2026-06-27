import streamlit as st
import joblib
import re
import numpy as np

model = joblib.load("hotel_sentiment_model.pkl")

def normalize_typos(text):
    text = str(text).lower()
    text = text.replace("cleaness", "cleanliness")
    text = text.replace("cleanness", "cleanliness")
    text = text.replace("wi fi", "wi-fi")
    text = text.replace("wifi", "wi-fi")
    return text

def clean_text(text):
    text = normalize_typos(text)
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

aspect_keywords = {
    "Room": ["room", "bed", "bathroom", "toilet", "shower", "pillow"],
    "Service": ["staff", "service", "reception", "manager", "helpful", "friendly", "rude"],
    "Cleanliness": ["clean", "cleanliness", "dirty", "smell", "hygiene", "dust", "stain"],
    "Location": ["location", "near", "distance", "mall", "station", "airport", "area", "convenient"],
    "Price": ["price", "expensive", "cheap", "value", "worth", "cost", "money"],
    "Facilities": ["pool", "gym", "wi-fi", "parking", "lift", "elevator", "facility", "facilities"],
    "Food": ["breakfast", "food", "restaurant", "meal", "buffet", "dinner", "lunch"]
}

hotel_keywords = [
    "hotel", "room", "bed", "bathroom", "toilet", "staff", "service", "reception",
    "clean", "cleanliness", "dirty", "location", "price", "expensive", "cheap",
    "value", "pool", "gym", "wi-fi", "wifi", "parking", "lift", "breakfast",
    "food", "restaurant", "stay", "booking", "check in", "check-in", "checkout",
    "lobby", "guest", "resort", "facilities", "facility", "housekeeping"
]

bad_words = ["fuck", "shit", "bitch", "asshole"]
meaningless_words = ["haha", "hahaha", "hehe", "lol", "lmao", "test", "ok", "okay"]

def validate_input(review):
    text = normalize_typos(review).strip()
    words = re.findall(r"[a-zA-Z]+", text)

    if len(words) == 0:
        return False, "Please enter a hotel review before analyzing."

    if len(words) < 3:
        return False, "The input is too short. Please enter a complete hotel review."

    if all(word in meaningless_words for word in words):
        return False, "This input does not look like a hotel review. Please enter a hotel-related review."

    if any(word in bad_words for word in words):
        return False, "This input contains inappropriate or non-review language. Please enter a proper hotel review."

    if not any(keyword in text for keyword in hotel_keywords):
        return False, "This system only analyzes hotel-related reviews. Please enter a review about room, service, cleanliness, location, price, facilities, or food."

    return True, ""

def predict_with_confidence(text):
    cleaned = clean_text(text)
    pred = model.predict([cleaned])[0]
    confidence = None

    try:
        proba = model.predict_proba([cleaned])[0]
        confidence = float(np.max(proba))
    except:
        try:
            scores = model.decision_function([cleaned])
            scores = np.array(scores)

            if scores.ndim == 2:
                scores = scores[0]

            exp_scores = np.exp(scores - np.max(scores))
            proba = exp_scores / exp_scores.sum()
            confidence = float(np.max(proba))
        except:
            confidence = None

    return pred, confidence

def sentiment_badge(sentiment):
    sentiment = str(sentiment).lower()
    if sentiment == "positive":
        return "🟢 Positive"
    elif sentiment == "neutral":
        return "🟡 Neutral"
    elif sentiment == "negative":
        return "🔴 Negative"
    return sentiment.capitalize()

def aspect_sentiment(review):
    review = normalize_typos(review)
    clauses = re.split(r"[.!?,;]|\bbut\b|\bhowever\b|\balthough\b|\band\b", review)
    results = {}

    for aspect, keywords in aspect_keywords.items():
        related = []

        for clause in clauses:
            clause = clause.strip()
            if clause == "":
                continue

            if any(keyword in clause for keyword in keywords):
                related.append(clause)

        if related:
            aspect_text = " ".join(related)
            pred, conf = predict_with_confidence(aspect_text)

            results[aspect] = {
                "sentiment": pred,
                "confidence": conf,
                "text": aspect_text
            }

    return results

def recommendation(overall, aspects):
    negative_aspects = [a for a, r in aspects.items() if r["sentiment"] == "negative"]

    if overall == "positive":
        return "The customer is generally satisfied. The hotel should maintain its current service quality."
    elif overall == "neutral":
        return "The review contains mixed opinions. The hotel should maintain the positive aspects and improve the weaker parts."
    elif overall == "negative":
        if negative_aspects:
            return "The customer is dissatisfied. The hotel should improve: " + ", ".join(negative_aspects) + "."
        return "The customer is dissatisfied. The hotel should review the complaint and improve the related service area."

    return "No recommendation available."

st.set_page_config(
    page_title="Hotel Review Sentiment Analysis Chatbot",
    page_icon="🏨",
    layout="wide"
)

st.markdown("""
<style>
.title-box {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #1f2937, #334155);
    color: white;
    margin-bottom: 25px;
}
.title-box h1 {
    color: white;
    font-size: 42px;
}
.card {
    padding: 18px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}
.positive {
    background-color: #dcfce7;
    border-left: 7px solid #16a34a;
}
.neutral {
    background-color: #fef9c3;
    border-left: 7px solid #ca8a04;
}
.negative {
    background-color: #fee2e2;
    border-left: 7px solid #dc2626;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("📌 Project Info")
    st.write("**Dataset:** 360 hotel review sentences")
    st.write("**Classes:** Positive, Neutral, Negative")
    st.write("**Model:** TF-IDF + Machine Learning Classifier")
    st.write("**Advanced Features:**")
    st.write("- Input validation")
    st.write("- Aspect-based sentiment analysis")
    st.write("- Confidence display")
    st.write("- Management recommendation")

st.markdown("""
<div class="title-box">
    <h1>🏨 Hotel Review Sentiment Analysis Chatbot</h1>
    <p>This NLP system analyzes hotel reviews, predicts sentiment, detects hotel aspects, and provides simple improvement recommendations.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("💬 Enter Hotel Review")
    review = st.text_area(
        "Type or paste a hotel review here:",
        height=180,
        placeholder="Example: The room was clean and the staff were friendly, but the price was expensive."
    )

    analyze = st.button("🔍 Analyze Review", use_container_width=True)

with col2:
    st.subheader("📊 System Overview")
    st.markdown("""
    <div class="card">
        <h3>360 Reviews</h3>
        <p>Balanced dataset with 120 positive, 120 neutral, and 120 negative reviews.</p>
    </div>
    <div class="card">
        <h3>7 Hotel Aspects</h3>
        <p>Room, Service, Cleanliness, Location, Price, Facilities, and Food.</p>
    </div>
    <div class="card">
        <h3>Input Validation</h3>
        <p>Rejects irrelevant, meaningless, or inappropriate non-review inputs.</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("📌 Sample Reviews")

samples = {
    "Positive Sample": "The room was clean and spacious. The staff were friendly and helpful.",
    "Neutral Sample": "The location was good but the room was average and the price was quite expensive.",
    "Negative Sample": "The room was dirty, the wi-fi was slow, and the staff were rude.",
    "Invalid Sample": "hahaha"
}

for label, sample in samples.items():
    with st.expander(label):
        st.write(sample)

if analyze:
    valid, message = validate_input(review)

    st.divider()
    st.subheader("🤖 Chatbot Response")

    if not valid:
        st.warning(message)
    else:
        overall, conf = predict_with_confidence(review)
        aspects = aspect_sentiment(review)

        css_class = str(overall).lower()

        conf_text = ""
        if conf is not None:
            conf_text = f"Estimated Confidence: {conf * 100:.2f}%"

        st.markdown(f"""
        <div class="card {css_class}">
            <h2>Overall Sentiment: {sentiment_badge(overall)}</h2>
            <p>{conf_text}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧩 Aspect-Based Sentiment Analysis")

        if aspects:
            for aspect, result in aspects.items():
                aspect_class = str(result["sentiment"]).lower()

                aspect_conf = ""
                if result["confidence"] is not None:
                    aspect_conf = f"Estimated Confidence: {result['confidence'] * 100:.2f}%"

                st.markdown(f"""
                <div class="card {aspect_class}">
                    <h4>{aspect}: {sentiment_badge(result["sentiment"])}</h4>
                    <p><b>Related text:</b> {result["text"]}</p>
                    <p>{aspect_conf}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific hotel aspect was detected from this review.")

        st.markdown("### 💡 Management Recommendation")
        rec = recommendation(overall, aspects)

        if overall == "positive":
            st.success(rec)
        elif overall == "neutral":
            st.warning(rec)
        elif overall == "negative":
            st.error(rec)

        st.markdown("### 📝 Explanation")
        if overall == "positive":
            st.write("The review mainly contains positive opinions about the hotel experience.")
        elif overall == "neutral":
            st.write("The review contains mixed or moderate opinions, so the system classified it as neutral.")
        elif overall == "negative":
            st.write("The review mainly contains negative opinions or complaints about the hotel experience.")
