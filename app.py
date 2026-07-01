import streamlit as st
import pandas as pd
import numpy as np
import joblib
import re
import html

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="Hotel Review Sentiment Analyzer",
    page_icon="🏨",
    layout="wide"
)

# =====================================================
# Load Model
# =====================================================
@st.cache_resource
def load_model():
    return joblib.load("models/hotel_sentiment_model.pkl")

try:
    model = load_model()
except Exception:
    st.error("Model file not found. Please make sure hotel_sentiment_model.pkl is uploaded to GitHub.")
    st.stop()

# =====================================================
# Load Dataset, Report, and Optional Evaluation Files
# =====================================================
@st.cache_data
def load_dataset():
    try:
        return pd.read_csv("cleaned_hotel_reviews_dataset.csv")
    except:
        return None

@st.cache_data
def load_report():
    try:
        with open("classification_report.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Classification report is not uploaded yet."

@st.cache_data
def load_optional_csv(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return None

dataset = load_dataset()
classification_report_text = load_report()

model_eval_df = load_optional_csv("model_evaluation_results.csv")
all_model_reports_df = load_optional_csv("all_model_classification_reports.csv")
confusion_matrix_df = load_optional_csv("model_confusion_matrices.csv")
best_model_summary_df = load_optional_csv("best_model_summary.csv")

# =====================================================
# Text Pre-processing
# =====================================================
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

# =====================================================
# Keywords
# =====================================================
aspect_keywords = {
    "Room": [
        "room", "bed", "bathroom", "toilet", "shower", "pillow",
        "aircond", "air conditioning"
    ],
    "Service": [
        "staff", "service", "reception", "manager", "helpful",
        "friendly", "rude", "employee", "front desk"
    ],
    "Cleanliness": [
        "clean", "cleanliness", "dirty", "smell", "hygiene",
        "dust", "stain", "tidy", "unclean", "smelly"
    ],
    "Location": [
        "location", "near", "distance", "mall", "station",
        "airport", "area", "convenient"
    ],
    "Price": [
        "price", "expensive", "cheap", "value", "worth",
        "cost", "money", "overpriced"
    ],
    "Facilities": [
        "pool", "gym", "wi-fi", "parking", "lift", "elevator",
        "facility", "facilities", "internet"
    ],
    "Food": [
        "breakfast", "food", "restaurant", "meal", "buffet",
        "dinner", "lunch"
    ]
}

hotel_keywords = [
    "hotel", "room", "bed", "bathroom", "toilet", "staff", "service",
    "reception", "clean", "cleanliness", "dirty", "location", "price",
    "expensive", "cheap", "value", "pool", "gym", "wi-fi", "wifi",
    "parking", "lift", "breakfast", "food", "restaurant", "stay",
    "booking", "check in", "check-in", "checkout", "lobby", "guest",
    "resort", "facilities", "facility", "housekeeping", "suite",
    "shower", "pillow", "airport", "mall"
]

positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly",
    "helpful", "nice", "spacious", "convenient", "worth", "amazing",
    "perfect", "pleasant", "beautiful", "fast", "polite", "recommended",
    "satisfied", "enjoyed", "love", "lovely", "best", "quiet", "fresh",
    "smooth", "modern", "affordable"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy",
    "smelly", "broken", "worst", "terrible", "disappointed", "small",
    "uncomfortable", "unclean", "awful", "horrible", "stain", "stained",
    "dusty", "late", "unfriendly", "unhelpful", "problem", "complaint",
    "overpriced", "old", "weak", "poorly", "messy", "leaking", "leak",
    "smell", "noise", "bug", "bugs", "mold", "mould"
]

negative_phrases = [
    "not clean", "not comfortable", "not friendly", "not good",
    "not worth", "not recommended", "not helpful", "not convenient",
    "not satisfied"
]

positive_phrases = [
    "very clean", "very comfortable", "very friendly", "very helpful",
    "highly recommended", "worth the money", "good value"
]

bad_words = ["fuck", "shit", "bitch", "asshole"]
meaningless_words = ["haha", "hahaha", "hehe", "lol", "lmao", "test", "ok", "okay"]

# =====================================================
# Input Validation
# =====================================================
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

# =====================================================
# Helper Functions
# =====================================================
def sentiment_badge(sentiment):
    sentiment = str(sentiment).lower()

    if sentiment == "positive":
        return "🟢 Positive"
    elif sentiment == "neutral":
        return "🟡 Neutral"
    elif sentiment == "negative":
        return "🔴 Negative"
    elif sentiment == "invalid input":
        return "⚠️ Invalid Input"
    return sentiment.capitalize()

def sentiment_css(sentiment):
    sentiment = str(sentiment).lower()

    if sentiment == "positive":
        return "positive"
    elif sentiment == "neutral":
        return "neutral"
    elif sentiment == "negative":
        return "negative"
    return "neutral"

def confidence_level(confidence):
    if confidence is None:
        return "N/A"

    if confidence >= 0.75:
        return "High"
    elif confidence >= 0.55:
        return "Moderate"
    else:
        return "Low"

def get_model_classes():
    if hasattr(model, "classes_"):
        return list(model.classes_)
    return ["negative", "neutral", "positive"]

# =====================================================
# Hybrid Keyword Correction
# =====================================================
def keyword_sentiment_override(text, model_prediction, model_confidence, score_df):
    lowered = normalize_typos(text)
    cleaned = clean_text(text)
    words = cleaned.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    phrase_negative_count = sum(1 for phrase in negative_phrases if phrase in lowered)
    phrase_positive_count = sum(1 for phrase in positive_phrases if phrase in lowered)

    positive_count += phrase_positive_count
    negative_count += phrase_negative_count

    # Strong negative correction
    if negative_count >= 2 and negative_count > positive_count:
        prediction = "negative"
        confidence = max(model_confidence if model_confidence is not None else 0, 0.85)

        score_df = pd.DataFrame({
            "Sentiment": ["negative", "neutral", "positive"],
            "Score": [0.85, 0.10, 0.05]
        })

        note = "Keyword-assisted correction applied because multiple negative words were detected."
        return prediction, confidence, score_df, note

    # Strong positive correction
    if positive_count >= 2 and positive_count > negative_count:
        prediction = "positive"
        confidence = max(model_confidence if model_confidence is not None else 0, 0.85)

        score_df = pd.DataFrame({
            "Sentiment": ["negative", "neutral", "positive"],
            "Score": [0.05, 0.10, 0.85]
        })

        note = "Keyword-assisted correction applied because multiple positive words were detected."
        return prediction, confidence, score_df, note

    # Single strong negative word with low model confidence
    if negative_count >= 1 and positive_count == 0 and (model_confidence is None or model_confidence < 0.60):
        prediction = "negative"
        confidence = 0.70

        score_df = pd.DataFrame({
            "Sentiment": ["negative", "neutral", "positive"],
            "Score": [0.70, 0.20, 0.10]
        })

        note = "Keyword-assisted correction applied because a clear negative word was detected with low model confidence."
        return prediction, confidence, score_df, note

    # Single strong positive word with low model confidence
    if positive_count >= 1 and negative_count == 0 and (model_confidence is None or model_confidence < 0.60):
        prediction = "positive"
        confidence = 0.70

        score_df = pd.DataFrame({
            "Sentiment": ["negative", "neutral", "positive"],
            "Score": [0.10, 0.20, 0.70]
        })

        note = "Keyword-assisted correction applied because a clear positive word was detected with low model confidence."
        return prediction, confidence, score_df, note

    # Mixed review correction
    if positive_count >= 1 and negative_count >= 1:
        prediction = "neutral"
        confidence = max(model_confidence if model_confidence is not None else 0, 0.65)

        score_df = pd.DataFrame({
            "Sentiment": ["negative", "neutral", "positive"],
            "Score": [0.25, 0.60, 0.15]
        })

        note = "Mixed sentiment correction applied because both positive and negative words were detected."
        return prediction, confidence, score_df, note

    note = "Model prediction used."
    return model_prediction, model_confidence, score_df, note

# =====================================================
# Prediction Function
# =====================================================
def predict_with_details(text):
    cleaned = clean_text(text)
    prediction = model.predict([cleaned])[0]

    classes = get_model_classes()
    confidence = None
    score_df = None

    try:
        probabilities = model.predict_proba([cleaned])[0]
        confidence = float(np.max(probabilities))
        score_df = pd.DataFrame({
            "Sentiment": classes,
            "Score": probabilities
        })

    except:
        try:
            scores = model.decision_function([cleaned])
            scores = np.array(scores)

            if scores.ndim == 2:
                scores = scores[0]

            exp_scores = np.exp(scores - np.max(scores))
            probabilities = exp_scores / exp_scores.sum()

            confidence = float(np.max(probabilities))
            score_df = pd.DataFrame({
                "Sentiment": classes,
                "Score": probabilities
            })

        except:
            confidence = None
            score_df = pd.DataFrame({
                "Sentiment": [prediction],
                "Score": [1.0]
            })

    prediction, confidence, score_df, prediction_note = keyword_sentiment_override(
        text,
        prediction,
        confidence,
        score_df
    )

    return prediction, confidence, cleaned, score_df, prediction_note

# =====================================================
# Aspect-Based Sentiment Analysis
# =====================================================
def aspect_sentiment(review):
    review = normalize_typos(review)

    clauses = re.split(
        r"[.!?,;]|\bbut\b|\bhowever\b|\balthough\b|\band\b",
        review
    )

    results = []

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
            prediction, confidence, cleaned, score_df, prediction_note = predict_with_details(aspect_text)

            results.append({
                "Aspect": aspect,
                "Related Text": aspect_text,
                "Sentiment": prediction,
                "Confidence": f"{confidence * 100:.2f}%" if confidence is not None else "N/A",
                "Prediction Note": prediction_note
            })

    return results

# =====================================================
# User-Focused Analysis
# =====================================================
def detect_keywords(review):
    text = clean_text(review)
    words = text.split()

    detected_positive = sorted(list(set([word for word in words if word in positive_words])))
    detected_negative = sorted(list(set([word for word in words if word in negative_words])))

    return detected_positive, detected_negative

def generate_user_summary(overall, aspect_results):
    positive_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "positive"]
    negative_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "negative"]
    neutral_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "neutral"]

    if overall == "positive":
        if positive_aspects:
            return "This review suggests that the guest had a good hotel experience, especially in: " + ", ".join(positive_aspects) + "."
        return "This review suggests that the guest had a generally positive hotel experience."

    elif overall == "neutral":
        if neutral_aspects:
            return "This review shows a mixed or average experience. Users may want to read more reviews before making a booking decision."
        return "This review is moderate and does not strongly show satisfaction or dissatisfaction."

    elif overall == "negative":
        if negative_aspects:
            return "This review highlights possible concerns in: " + ", ".join(negative_aspects) + ". Users should consider these issues before booking."
        return "This review suggests that the guest was not satisfied with the hotel experience."

    return "No user summary available."

def generate_travel_advice(overall, aspect_results):
    negative_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "negative"]

    if overall == "positive":
        return "This hotel review looks generally good. It may be suitable for users who value the positive aspects mentioned in the review."

    elif overall == "neutral":
        return "This review is mixed or average. Users are recommended to compare more reviews before deciding whether to book this hotel."

    elif overall == "negative":
        if len(negative_aspects) >= 2:
            return "Users should be careful before booking because several negative hotel aspects were detected."
        elif len(negative_aspects) == 1:
            return "Users should pay attention to the negative aspect detected before booking."
        else:
            return "Users should check more reviews because this review indicates an unsatisfactory hotel experience."

    return "No travel advice available."

def generate_pros_cons(aspect_results, positive_detected_words, negative_detected_words):
    pros = []
    cons = []

    for result in aspect_results:
        if result["Sentiment"] == "positive":
            pros.append(result["Aspect"])
        elif result["Sentiment"] == "negative":
            cons.append(result["Aspect"])

    pros.extend(positive_detected_words)
    cons.extend(negative_detected_words)

    pros = sorted(list(set(pros)))
    cons = sorted(list(set(cons)))

    return pros, cons

def analyze_review(review):
    valid, message = validate_input(review)

    if not valid:
        return {
            "Review": review,
            "Cleaned Review": "",
            "Overall Sentiment": "Invalid Input",
            "Confidence": "",
            "Confidence Level": "",
            "Detected Aspects": "",
            "Pros": "",
            "Cons": "",
            "User Summary": message,
            "Travel Advice": message,
            "Prediction Note": "Input validation applied."
        }

    overall, confidence, cleaned, score_df, prediction_note = predict_with_details(review)
    aspect_results = aspect_sentiment(review)
    positive_detected_words, negative_detected_words = detect_keywords(review)
    pros, cons = generate_pros_cons(
        aspect_results,
        positive_detected_words,
        negative_detected_words
    )

    detected_aspects = []
    for result in aspect_results:
        detected_aspects.append(f"{result['Aspect']}: {result['Sentiment']}")

    return {
        "Review": review,
        "Cleaned Review": cleaned,
        "Overall Sentiment": overall,
        "Confidence": f"{confidence * 100:.2f}%" if confidence is not None else "N/A",
        "Confidence Level": confidence_level(confidence),
        "Detected Aspects": "; ".join(detected_aspects) if detected_aspects else "No aspect detected",
        "Pros": ", ".join(pros) if pros else "None",
        "Cons": ", ".join(cons) if cons else "None",
        "User Summary": generate_user_summary(overall, aspect_results),
        "Travel Advice": generate_travel_advice(overall, aspect_results),
        "Prediction Note": prediction_note
    }

# =====================================================
# Session State
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.hero {
    padding: 35px;
    border-radius: 24px;
    background: linear-gradient(135deg, #0f172a, #2563eb);
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 44px;
    margin-bottom: 10px;
}
.hero p {
    color: #dbeafe;
    font-size: 18px;
}
.card {
    padding: 20px;
    border-radius: 18px;
    background-color: white;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}
.positive {
    background-color: #dcfce7;
    border-left: 8px solid #16a34a;
}
.neutral {
    background-color: #fef9c3;
    border-left: 8px solid #ca8a04;
}
.negative {
    background-color: #fee2e2;
    border-left: 8px solid #dc2626;
}
.info-box {
    background-color: #eff6ff;
    border-left: 8px solid #2563eb;
}
.small {
    color: #475569;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Sidebar
# =====================================================
with st.sidebar:
    st.title("📌 User Menu")
    st.write("**System:** Hotel Review Sentiment Analyzer")
    st.write("**Target Users:** Travellers and hotel customers")
    st.write("**Purpose:** Help users understand hotel reviews before booking")

    st.divider()

    st.write("**Main Functions:**")
    st.write("✅ Analyze hotel review sentiment")
    st.write("✅ Detect hotel aspects")
    st.write("✅ Show pros and cons")
    st.write("✅ Provide travel decision advice")
    st.write("✅ Compare multiple reviews")
    st.write("✅ Download analysis result")
    st.write("✅ Hybrid keyword correction")
    st.write("✅ Model evaluation dashboard")

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="hero">
    <h1>🏨 Hotel Review Sentiment Analyzer</h1>
    <p>A user-friendly NLP system that helps travellers understand hotel reviews before making booking decisions.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Main Tabs
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Analyze Review",
    "📋 Compare Reviews",
    "📊 Model & Dataset",
    "🕘 My Analysis History",
    "📘 Help"
])

# =====================================================
# Tab 1: Analyze Review
# =====================================================
with tab1:
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("💬 Paste a Hotel Review")

        review = st.text_area(
            "Enter one hotel review:",
            height=180,
            placeholder="Example: The room was clean and spacious. The staff were friendly, but the price was expensive."
        )

        analyze_button = st.button("🔍 Analyze This Review", use_container_width=True)

        st.subheader("📌 Try Sample Reviews")

        samples = {
            "Good Review": "The room was clean and spacious. The staff were friendly and helpful.",
            "Mixed Review": "The location was good but the room was average and the price was quite expensive.",
            "Bad Review": "The room was dirty, the wi-fi was slow, and the staff were rude.",
            "Invalid Input": "hahaha"
        }

        for label, sample in samples.items():
            with st.expander(label):
                st.write(sample)

    with right:
        st.subheader("✨ What This System Helps You Know")

        st.markdown("""
        <div class="card info-box">
            <h3>Before Booking</h3>
            <p>You can paste a hotel review to understand whether it is positive, neutral, or negative.</p>
        </div>
        <div class="card info-box">
            <h3>Aspect Understanding</h3>
            <p>The system checks hotel aspects such as room, service, cleanliness, location, price, facilities, and food.</p>
        </div>
        <div class="card info-box">
            <h3>Decision Support</h3>
            <p>The system gives simple travel advice based on detected sentiment and hotel aspects.</p>
        </div>
        """, unsafe_allow_html=True)

    if analyze_button:
        st.divider()
        st.subheader("🤖 Review Analysis Result")

        valid, message = validate_input(review)

        if not valid:
            st.warning(message)

        else:
            overall, confidence, cleaned, score_df, prediction_note = predict_with_details(review)
            aspect_results = aspect_sentiment(review)
            positive_detected_words, negative_detected_words = detect_keywords(review)
            pros, cons = generate_pros_cons(
                aspect_results,
                positive_detected_words,
                negative_detected_words
            )

            user_summary = generate_user_summary(overall, aspect_results)
            travel_advice = generate_travel_advice(overall, aspect_results)

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric("Overall Sentiment", sentiment_badge(overall))

            with m2:
                st.metric(
                    "Confidence",
                    f"{confidence * 100:.2f}%" if confidence is not None else "N/A"
                )

            with m3:
                st.metric("Confidence Level", confidence_level(confidence))

            with m4:
                st.metric("Detected Aspects", len(aspect_results))

            css_class = sentiment_css(overall)

            st.markdown(f"""
            <div class="card {css_class}">
                <h2>Overall Sentiment: {sentiment_badge(overall)}</h2>
                <p>This review is predicted as <b>{overall}</b>.</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View Prediction Note"):
                st.write(prediction_note)

            st.markdown("### 🧾 What This Review Means")
            st.info(user_summary)

            st.markdown("### 🧭 Travel Decision Advice")

            if overall == "positive":
                st.success(travel_advice)
            elif overall == "neutral":
                st.warning(travel_advice)
            else:
                st.error(travel_advice)

            st.markdown("### ✅ Pros and ⚠️ Cons Detected")

            pros_col, cons_col = st.columns(2)

            with pros_col:
                if pros:
                    st.success(", ".join(pros))
                else:
                    st.info("No clear pros detected.")

            with cons_col:
                if cons:
                    st.error(", ".join(cons))
                else:
                    st.info("No clear cons detected.")

            st.markdown("### 📈 Sentiment Score Distribution")

            if score_df is not None:
                score_df_display = score_df.copy()
                score_df_display["Score"] = score_df_display["Score"].astype(float)
                st.bar_chart(score_df_display.set_index("Sentiment"))

                with st.expander("View Score Details"):
                    score_table = score_df_display.copy()
                    score_table["Score (%)"] = score_table["Score"] * 100
                    st.dataframe(score_table, use_container_width=True)

            st.markdown("### 🧩 Hotel Aspect Analysis")

            if aspect_results:
                aspect_df = pd.DataFrame(aspect_results)
                st.dataframe(aspect_df, use_container_width=True)

                for result in aspect_results:
                    aspect_class = sentiment_css(result["Sentiment"])
                    safe_text = html.escape(result["Related Text"])

                    st.markdown(f"""
                    <div class="card {aspect_class}">
                        <h4>{result["Aspect"]}: {sentiment_badge(result["Sentiment"])}</h4>
                        <p><b>Related text:</b> {safe_text}</p>
                        <p><b>Confidence:</b> {result["Confidence"]}</p>
                        <p><b>Prediction Note:</b> {result["Prediction Note"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific hotel aspect was detected from this review.")

            with st.expander("View Pre-processed Text"):
                st.code(cleaned)

            result_row = analyze_review(review)
            st.session_state.history.append(result_row)

            result_df = pd.DataFrame([result_row])
            csv = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download This Analysis Result",
                data=csv,
                file_name="hotel_review_analysis_result.csv",
                mime="text/csv"
            )

# =====================================================
# Tab 2: Compare Reviews
# =====================================================
with tab2:
    st.subheader("📋 Compare Multiple Hotel Reviews")
    st.write("Paste several hotel reviews. Each line will be analyzed as one review.")

    batch_text = st.text_area(
        "Paste multiple reviews here, one review per line:",
        height=250,
        placeholder="The room was clean and comfortable.\nThe staff were rude and the bathroom was dirty.\nThe location was convenient but the room was average."
    )

    batch_button = st.button("📊 Compare Reviews", use_container_width=True)

    if batch_button:
        reviews = [line.strip() for line in batch_text.split("\n") if line.strip() != ""]

        if len(reviews) == 0:
            st.warning("Please enter at least one review.")
        else:
            batch_results = [analyze_review(review) for review in reviews]
            batch_df = pd.DataFrame(batch_results)

            st.success(f"Analysis completed for {len(batch_results)} reviews.")
            st.dataframe(batch_df, use_container_width=True)

            st.markdown("### 📊 Overall Sentiment Summary")
            sentiment_counts = batch_df["Overall Sentiment"].value_counts()
            st.bar_chart(sentiment_counts)

            st.session_state.history.extend(batch_results)

            csv = batch_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Comparison Result",
                data=csv,
                file_name="hotel_review_comparison_result.csv",
                mime="text/csv"
            )

# =====================================================
# Tab 3: Model & Dataset
# =====================================================
with tab3:
    st.subheader("📊 Model and Dataset Information")

    dataset_tab, preprocessing_tab, comparison_tab, individual_tab, best_tab = st.tabs([
        "📁 Dataset Overview",
        "🧹 Pre-processing",
        "📈 Model Comparison",
        "📋 Individual Model Results",
        "🏆 Best Model"
    ])

    # ==============================
    # Dataset Overview
    # ==============================
    with dataset_tab:
        st.markdown("### 📁 Dataset Overview")

        if dataset is not None:
            total_reviews = len(dataset)
            sentiment_counts = dataset["Sentiment"].value_counts() if "Sentiment" in dataset.columns else None

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric("Total Reviews", total_reviews)

            if sentiment_counts is not None:
                with c2:
                    st.metric("Positive Reviews", int(sentiment_counts.get("positive", 0)))
                with c3:
                    st.metric("Neutral Reviews", int(sentiment_counts.get("neutral", 0)))
                with c4:
                    st.metric("Negative Reviews", int(sentiment_counts.get("negative", 0)))

                st.markdown("### Sentiment Distribution Graph")
                st.bar_chart(sentiment_counts)

                sentiment_distribution_df = sentiment_counts.reset_index()
                sentiment_distribution_df.columns = ["Sentiment", "Count"]
                st.markdown("### Sentiment Distribution Table")
                st.dataframe(sentiment_distribution_df, use_container_width=True)

            if "Source" in dataset.columns:
                st.markdown("### Review Source Distribution")
                source_counts = dataset["Source"].value_counts()
                st.bar_chart(source_counts)

                source_df = source_counts.reset_index()
                source_df.columns = ["Source", "Count"]
                st.dataframe(source_df, use_container_width=True)

            if "Location" in dataset.columns:
                st.markdown("### Review Location Distribution")
                location_counts = dataset["Location"].value_counts()
                st.bar_chart(location_counts)

                location_df = location_counts.reset_index()
                location_df.columns = ["Location", "Count"]
                st.dataframe(location_df, use_container_width=True)

            st.markdown("### Dataset Preview")
            st.dataframe(dataset.head(10), use_container_width=True)

        else:
            st.warning("Dataset file is not uploaded. Please upload cleaned_hotel_reviews_dataset.csv to GitHub.")

    # ==============================
    # Pre-processing
    # ==============================
    with preprocessing_tab:
        st.markdown("### 🧹 Text Pre-processing Pipeline")

        preprocessing_steps = pd.DataFrame({
            "Step": [
                "Lowercasing",
                "Typo Normalization",
                "URL Removal",
                "Special Character Removal",
                "Whitespace Normalization",
                "TF-IDF Vectorization"
            ],
            "Purpose": [
                "Convert all text into lowercase for consistency.",
                "Normalize common spelling variations such as cleaness to cleanliness.",
                "Remove links that do not contribute to sentiment classification.",
                "Remove punctuation, numbers, and symbols.",
                "Remove extra spaces after text cleaning.",
                "Represent cleaned reviews as numerical features for model training."
            ]
        })

        st.dataframe(preprocessing_steps, use_container_width=True)

        st.markdown("### Knowledge Representation")

        knowledge_df = pd.DataFrame({
            "Component": [
                "Cleaned Dataset",
                "Sentiment Labels",
                "TF-IDF Features",
                "Aspect Keyword Dictionary",
                "Saved Model File",
                "Hybrid Keyword Correction",
                "Evaluation Files"
            ],
            "Representation": [
                "CSV format",
                "Positive, Neutral, Negative",
                "Numerical vector representation",
                "Dictionary-based aspect mapping",
                "hotel_sentiment_model.pkl",
                "Rule-based sentiment correction",
                "CSV and TXT evaluation reports"
            ],
            "Purpose": [
                "Store collected and cleaned hotel reviews.",
                "Represent target sentiment categories.",
                "Convert text into machine-readable format.",
                "Support aspect-based sentiment analysis.",
                "Deploy the trained model in Streamlit.",
                "Improve obvious sentiment predictions for user input.",
                "Display model performance in the system."
            ]
        })

        st.dataframe(knowledge_df, use_container_width=True)

    # ==============================
    # Model Comparison
    # ==============================
    with comparison_tab:
        st.markdown("### 📈 Overall Model Comparison")

        if model_eval_df is not None:
            st.markdown("#### Model Performance Table")
            st.dataframe(model_eval_df, use_container_width=True)

            st.markdown("#### Accuracy Comparison Graph")
            accuracy_chart = model_eval_df.set_index("Model")[["Accuracy"]]
            st.bar_chart(accuracy_chart)

            st.markdown("#### Macro F1-score Comparison Graph")
            f1_chart = model_eval_df.set_index("Model")[["Macro F1-score"]]
            st.bar_chart(f1_chart)

            required_cols = ["Macro Precision", "Macro Recall", "Macro F1-score"]

            if all(col in model_eval_df.columns for col in required_cols):
                st.markdown("#### Precision, Recall and F1-score Comparison")
                metric_chart = model_eval_df.set_index("Model")[required_cols]
                st.bar_chart(metric_chart)

            st.info(
                "The best model is selected based on Macro F1-score because the dataset contains three sentiment classes and the system should perform well across positive, neutral, and negative reviews."
            )

        else:
            st.warning("Model evaluation file is missing. Please upload model_evaluation_results.csv to GitHub.")

    # ==============================
    # Individual Model Results
    # ==============================
    with individual_tab:
        st.markdown("### 📋 Individual Model Results")

        if all_model_reports_df is not None:
            model_names = all_model_reports_df["Model"].unique().tolist()

            selected_model = st.selectbox(
                "Select a model to view detailed result:",
                model_names
            )

            selected_report = all_model_reports_df[
                all_model_reports_df["Model"] == selected_model
            ]

            st.markdown(f"#### Classification Report: {selected_model}")
            st.dataframe(selected_report, use_container_width=True)

            class_report_for_chart = selected_report[
                selected_report["Class"].isin(["positive", "neutral", "negative"])
            ]

            if not class_report_for_chart.empty:
                st.markdown(f"#### F1-score by Class: {selected_model}")
                f1_by_class = class_report_for_chart.set_index("Class")[["F1-score"]]
                st.bar_chart(f1_by_class)

                st.markdown(f"#### Precision, Recall and F1-score by Class: {selected_model}")

                metric_by_class = class_report_for_chart.set_index("Class")[
                    ["Precision", "Recall", "F1-score"]
                ]

                st.bar_chart(metric_by_class)

            if confusion_matrix_df is not None:
                st.markdown(f"#### Confusion Matrix: {selected_model}")

                selected_cm = confusion_matrix_df[
                    confusion_matrix_df["Model"] == selected_model
                ]

                cm_pivot = selected_cm.pivot(
                    index="Actual",
                    columns="Predicted",
                    values="Count"
                ).fillna(0).astype(int)

                st.dataframe(cm_pivot, use_container_width=True)

                st.markdown("The confusion matrix shows how many reviews were correctly or incorrectly classified for each sentiment class.")

        else:
            st.warning("Individual model report file is missing. Please upload all_model_classification_reports.csv to GitHub.")

    # ==============================
    # Best Model
    # ==============================
    with best_tab:
        st.markdown("### 🏆 Best Model Final Summary")

        if best_model_summary_df is not None:
            st.markdown("#### Best Model Summary Table")
            st.dataframe(best_model_summary_df, use_container_width=True)

            best_model_name = best_model_summary_df.iloc[0]["Model"]
            best_accuracy = best_model_summary_df.iloc[0]["Accuracy"]
            best_macro_f1 = best_model_summary_df.iloc[0]["Macro F1-score"]

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Best Model", best_model_name)

            with c2:
                st.metric("Accuracy", f"{best_accuracy * 100:.2f}%")

            with c3:
                st.metric("Macro F1-score", f"{best_macro_f1 * 100:.2f}%")

            st.markdown("#### Best Model Classification Report")
            st.code(classification_report_text)

            st.success(
                "This model is selected as the final deployed model because it achieved the highest Macro F1-score among the tested models."
            )

            if confusion_matrix_df is not None:
                st.markdown("#### Best Model Confusion Matrix")

                best_cm = confusion_matrix_df[
                    confusion_matrix_df["Model"] == best_model_name
                ]

                best_cm_pivot = best_cm.pivot(
                    index="Actual",
                    columns="Predicted",
                    values="Count"
                ).fillna(0).astype(int)

                st.dataframe(best_cm_pivot, use_container_width=True)

        else:
            st.warning("Best model summary file is missing. Please upload best_model_summary.csv to GitHub.")

# =====================================================
# Tab 4: History
# =====================================================
with tab4:
    st.subheader("🕘 My Analysis History")

    if len(st.session_state.history) == 0:
        st.info("No analysis history yet. Analyze a review first.")
    else:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)

        csv = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download My Analysis History",
            data=csv,
            file_name="my_hotel_review_analysis_history.csv",
            mime="text/csv"
        )

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

# =====================================================
# Tab 5: Help
# =====================================================
with tab5:
    st.subheader("📘 Help")

    st.markdown("""
    ### How to Use This System

    1. Go to **Analyze Review**.
    2. Paste one hotel-related review.
    3. Click **Analyze This Review**.
    4. The system will show:
       - Overall sentiment
       - Confidence score
       - What the review means
       - Travel decision advice
       - Pros and cons
       - Hotel aspect analysis
    5. Go to **Compare Reviews** if you want to analyze several reviews at once.
    6. Download the result as CSV if needed.

    ### Who Can Use This System?

    This system is designed for:
    - Travellers
    - Hotel customers
    - Users comparing hotel reviews before booking
    - Tourism review analysis users

    ### Model and Dataset Section

    The **Model & Dataset** section shows:
    - Dataset overview
    - Sentiment distribution
    - Text pre-processing pipeline
    - Knowledge representation
    - Model comparison results
    - Individual model performance
    - Confusion matrix
    - Best model summary

    ### Advanced Feature

    This system combines machine learning prediction with keyword-assisted correction.
    The machine learning model provides the main sentiment prediction, while keyword correction helps improve obvious cases such as reviews containing multiple strong negative or positive words.

    ### System Limitation

    This system is trained on hotel review data only. It may not perform well on:
    - Non-hotel-related input
    - Very short input
    - Sarcasm
    - Slang
    - Unclear reviews

    Therefore, input validation is included to reject irrelevant or inappropriate text before prediction.
    """)
