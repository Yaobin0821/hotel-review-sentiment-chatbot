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
    page_title="Hotel Review Sentiment Analysis System",
    page_icon="🏨",
    layout="wide"
)

# =====================================================
# Load Model
# =====================================================
@st.cache_resource
def load_model():
    return joblib.load("hotel_sentiment_model.pkl")

try:
    model = load_model()
except Exception:
    st.error("Model file not found. Please make sure hotel_sentiment_model.pkl is uploaded.")
    st.stop()

# =====================================================
# Load Optional Dataset and Report
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

dataset = load_dataset()
classification_report_text = load_report()

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
    "Room": ["room", "bed", "bathroom", "toilet", "shower", "pillow", "aircond", "air conditioning"],
    "Service": ["staff", "service", "reception", "manager", "helpful", "friendly", "rude", "employee"],
    "Cleanliness": ["clean", "cleanliness", "dirty", "smell", "hygiene", "dust", "stain", "tidy"],
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
    "lobby", "guest", "resort", "facilities", "facility", "housekeeping", "suite"
]

positive_words = [
    "good", "great", "excellent", "clean", "comfortable", "friendly", "helpful",
    "nice", "spacious", "convenient", "worth", "amazing", "perfect", "pleasant"
]

negative_words = [
    "bad", "dirty", "rude", "slow", "expensive", "poor", "noisy", "smelly",
    "broken", "worst", "terrible", "disappointed", "small", "uncomfortable"
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
# Prediction Functions
# =====================================================
def predict_with_details(text):
    cleaned = clean_text(text)
    prediction = model.predict([cleaned])[0]

    classes = list(model.classes_) if hasattr(model, "classes_") else ["negative", "neutral", "positive"]
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

    return prediction, confidence, cleaned, score_df

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

# =====================================================
# Aspect-Based Sentiment Analysis
# =====================================================
def aspect_sentiment(review):
    review = normalize_typos(review)
    clauses = re.split(r"[.!?,;]|\bbut\b|\bhowever\b|\balthough\b|\band\b", review)
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
            prediction, confidence, cleaned, score_df = predict_with_details(aspect_text)

            if prediction == "negative":
                priority = "High"
            elif prediction == "neutral":
                priority = "Medium"
            else:
                priority = "Low"

            results.append({
                "Aspect": aspect,
                "Related Text": aspect_text,
                "Sentiment": prediction,
                "Confidence": f"{confidence * 100:.2f}%" if confidence is not None else "N/A",
                "Improvement Priority": priority
            })

    return results

# =====================================================
# Extra Analysis
# =====================================================
def detect_keywords(review):
    text = clean_text(review)
    words = text.split()

    detected_positive = sorted(list(set([w for w in words if w in positive_words])))
    detected_negative = sorted(list(set([w for w in words if w in negative_words])))

    return detected_positive, detected_negative

def generate_recommendation(overall, aspect_results):
    negative_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "negative"]
    neutral_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "neutral"]
    positive_aspects = [r["Aspect"] for r in aspect_results if r["Sentiment"] == "positive"]

    if overall == "positive":
        if positive_aspects:
            return "The customer is generally satisfied. The hotel should maintain strong performance in: " + ", ".join(positive_aspects) + "."
        return "The customer is generally satisfied. The hotel should maintain its current service quality."

    elif overall == "neutral":
        if neutral_aspects:
            return "The review contains mixed or moderate opinions. The hotel should monitor these areas: " + ", ".join(neutral_aspects) + "."
        return "The review contains mixed opinions. The hotel should maintain positive areas and improve weaker parts."

    elif overall == "negative":
        if negative_aspects:
            return "The customer is dissatisfied. The hotel should prioritize improvement in: " + ", ".join(negative_aspects) + "."
        return "The customer is dissatisfied. The hotel should review the complaint and improve the related service area."

    return "No recommendation available."

def generate_summary(overall, confidence, aspect_results):
    total_aspects = len(aspect_results)
    negative_count = len([r for r in aspect_results if r["Sentiment"] == "negative"])
    neutral_count = len([r for r in aspect_results if r["Sentiment"] == "neutral"])
    positive_count = len([r for r in aspect_results if r["Sentiment"] == "positive"])

    return {
        "Overall Sentiment": overall,
        "Confidence Level": confidence_level(confidence),
        "Detected Aspects": total_aspects,
        "Positive Aspects": positive_count,
        "Neutral Aspects": neutral_count,
        "Negative Aspects": negative_count
    }

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
            "Positive Keywords": "",
            "Negative Keywords": "",
            "Recommendation": message
        }

    overall, confidence, cleaned, score_df = predict_with_details(review)
    aspect_results = aspect_sentiment(review)
    pos_words, neg_words = detect_keywords(review)
    recommendation = generate_recommendation(overall, aspect_results)

    detected_aspects = []
    for r in aspect_results:
        detected_aspects.append(f"{r['Aspect']}: {r['Sentiment']}")

    return {
        "Review": review,
        "Cleaned Review": cleaned,
        "Overall Sentiment": overall,
        "Confidence": f"{confidence * 100:.2f}%" if confidence is not None else "N/A",
        "Confidence Level": confidence_level(confidence),
        "Detected Aspects": "; ".join(detected_aspects) if detected_aspects else "No aspect detected",
        "Positive Keywords": ", ".join(pos_words) if pos_words else "None",
        "Negative Keywords": ", ".join(neg_words) if neg_words else "None",
        "Recommendation": recommendation
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
    background: linear-gradient(135deg, #111827, #1e3a8a);
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
    st.title("📌 System Menu")
    st.write("**Project:** Hotel Review Sentiment Analysis")
    st.write("**Domain:** Malaysia Tourism / Hotel Reviews")
    st.write("**Model:** TF-IDF + Machine Learning Classifier")

    st.divider()

    st.write("**Result Outputs:**")
    st.write("✅ Overall sentiment")
    st.write("✅ Confidence score")
    st.write("✅ Sentiment score chart")
    st.write("✅ Aspect table")
    st.write("✅ Key sentiment words")
    st.write("✅ Recommendation")
    st.write("✅ Downloadable result")
    st.write("✅ Analysis history")

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="hero">
    <h1>🏨 Hotel Review Sentiment Analysis System</h1>
    <p>An NLP-based system for analyzing hotel reviews, detecting sentiment, identifying hotel aspects, and supporting hotel management decision-making.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Tabs
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Single Review Analysis",
    "📋 Batch Analysis",
    "📊 Model & Dataset",
    "🕘 Analysis History",
    "📘 User Guide"
])

# =====================================================
# Tab 1: Single Review Analysis
# =====================================================
with tab1:
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("💬 Enter Hotel Review")

        review = st.text_area(
            "Type or paste one hotel review:",
            height=180,
            placeholder="Example: The room was clean and spacious. The staff were friendly, but the price was expensive."
        )

        analyze_button = st.button("🔍 Analyze Review", use_container_width=True)

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

    with right:
        st.subheader("📊 System Overview")

        st.markdown("""
        <div class="card">
            <h3>Result Output</h3>
            <p>The system shows overall sentiment, confidence score, aspect sentiment, keywords, and recommendation.</p>
        </div>
        <div class="card">
            <h3>Aspect Detection</h3>
            <p>Room, Service, Cleanliness, Location, Price, Facilities, and Food.</p>
        </div>
        <div class="card">
            <h3>Hotel Manager Support</h3>
            <p>The system highlights improvement priority for negative aspects.</p>
        </div>
        """, unsafe_allow_html=True)

    if analyze_button:
        st.divider()
        st.subheader("🤖 Detailed Analysis Result")

        valid, message = validate_input(review)

        if not valid:
            st.warning(message)

        else:
            overall, confidence, cleaned, score_df = predict_with_details(review)
            aspect_results = aspect_sentiment(review)
            pos_words, neg_words = detect_keywords(review)
            recommendation = generate_recommendation(overall, aspect_results)
            summary = generate_summary(overall, confidence, aspect_results)

            # Summary metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Overall Sentiment", sentiment_badge(overall))
            m2.metric("Confidence", f"{confidence * 100:.2f}%" if confidence is not None else "N/A")
            m3.metric("Confidence Level", confidence_level(confidence))
            m4.metric("Detected Aspects", len(aspect_results))

            # Overall result card
            css_class = sentiment_css(overall)
            st.markdown(f"""
            <div class="card {css_class}">
                <h2>Overall Sentiment: {sentiment_badge(overall)}</h2>
                <p>The model predicts that this review is mainly <b>{overall}</b>.</p>
            </div>
            """, unsafe_allow_html=True)

            # Sentiment score distribution
            st.markdown("### 📈 Sentiment Score Distribution")
            if score_df is not None:
                score_df_display = score_df.copy()
                score_df_display["Score"] = score_df_display["Score"].astype(float)
                st.bar_chart(score_df_display.set_index("Sentiment"))

                with st.expander("View Sentiment Score Table"):
                    score_df_display["Score (%)"] = score_df_display["Score"] * 100
                    st.dataframe(score_df_display, use_container_width=True)

            # Preprocessed text
            st.markdown("### 🧹 Pre-processed Text")
            st.code(cleaned)

            # Aspect table
            st.markdown("### 🧩 Aspect-Based Sentiment Analysis")

            if aspect_results:
                aspect_df = pd.DataFrame(aspect_results)
                st.dataframe(aspect_df, use_container_width=True)

                for r in aspect_results:
                    aspect_class = sentiment_css(r["Sentiment"])
                    safe_text = html.escape(r["Related Text"])

                    st.markdown(f"""
                    <div class="card {aspect_class}">
                        <h4>{r["Aspect"]}: {sentiment_badge(r["Sentiment"])}</h4>
                        <p><b>Related text:</b> {safe_text}</p>
                        <p><b>Confidence:</b> {r["Confidence"]}</p>
                        <p><b>Improvement Priority:</b> {r["Improvement Priority"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific hotel aspect was detected from this review.")

            # Keyword detection
            st.markdown("### 🔑 Key Sentiment Words Detected")

            k1, k2 = st.columns(2)

            with k1:
                if pos_words:
                    st.success("Positive words: " + ", ".join(pos_words))
                else:
                    st.info("Positive words: None detected")

            with k2:
                if neg_words:
                    st.error("Negative words: " + ", ".join(neg_words))
                else:
                    st.info("Negative words: None detected")

            # Summary table
            st.markdown("### 📌 Analysis Summary")
            summary_df = pd.DataFrame([summary])
            st.dataframe(summary_df, use_container_width=True)

            # Recommendation
            st.markdown("### 💡 Management Recommendation")

            if overall == "positive":
                st.success(recommendation)
            elif overall == "neutral":
                st.warning(recommendation)
            else:
                st.error(recommendation)

            # Save result to history
            result_row = analyze_review(review)
            st.session_state.history.append(result_row)

            result_df = pd.DataFrame([result_row])
            csv = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download This Result as CSV",
                data=csv,
                file_name="single_review_analysis_result.csv",
                mime="text/csv"
            )

# =====================================================
# Tab 2: Batch Analysis
# =====================================================
with tab2:
    st.subheader("📋 Batch Review Analysis")
    st.write("Enter multiple hotel reviews. Each line will be analyzed as one review.")

    batch_text = st.text_area(
        "Paste multiple reviews here, one review per line:",
        height=250,
        placeholder="The room was clean and comfortable.\nThe staff were rude and the bathroom was dirty.\nThe location was convenient but the room was average."
    )

    batch_button = st.button("📊 Analyze Batch Reviews", use_container_width=True)

    if batch_button:
        reviews = [line.strip() for line in batch_text.split("\n") if line.strip() != ""]

        if len(reviews) == 0:
            st.warning("Please enter at least one review.")
        else:
            batch_results = [analyze_review(review) for review in reviews]
            batch_df = pd.DataFrame(batch_results)

            st.success(f"Batch analysis completed for {len(batch_results)} reviews.")
            st.dataframe(batch_df, use_container_width=True)

            # Batch summary
            st.markdown("### 📊 Batch Sentiment Summary")
            batch_counts = batch_df["Overall Sentiment"].value_counts()
            st.bar_chart(batch_counts)

            st.session_state.history.extend(batch_results)

            csv = batch_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Batch Results as CSV",
                data=csv,
                file_name="batch_review_analysis_results.csv",
                mime="text/csv"
            )

# =====================================================
# Tab 3: Model & Dataset
# =====================================================
with tab3:
    st.subheader("📊 Model and Dataset Information")

    if dataset is not None:
        total_reviews = len(dataset)
        sentiment_counts = dataset["Sentiment"].value_counts() if "Sentiment" in dataset.columns else None

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Total Reviews", total_reviews)

        if sentiment_counts is not None:
            with c2:
                st.metric("Positive", int(sentiment_counts.get("positive", 0)))
            with c3:
                st.metric("Neutral", int(sentiment_counts.get("neutral", 0)))
            with c4:
                st.metric("Negative", int(sentiment_counts.get("negative", 0)))

            st.markdown("### Sentiment Distribution")
            st.bar_chart(sentiment_counts)

        st.markdown("### Dataset Preview")
        st.dataframe(dataset.head(10), use_container_width=True)

    else:
        st.info("Upload cleaned_hotel_reviews_dataset.csv to GitHub to display dataset information here.")

    st.markdown("### Text Pre-processing Pipeline")
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
            "Remove links that do not contribute to sentiment.",
            "Remove punctuation, numbers, and symbols.",
            "Remove extra spaces after cleaning.",
            "Represent cleaned reviews as numerical features for model training."
        ]
    })
    st.dataframe(preprocessing_steps, use_container_width=True)

    st.markdown("### Knowledge Representation")
    st.write("The system represents knowledge using:")
    st.write("- Cleaned CSV dataset")
    st.write("- TF-IDF numerical feature representation")
    st.write("- Sentiment labels: positive, neutral, negative")
    st.write("- Aspect keyword dictionary")
    st.write("- Saved model file: hotel_sentiment_model.pkl")

    st.markdown("### Model Performance")
    st.code(classification_report_text)

# =====================================================
# Tab 4: Analysis History
# =====================================================
with tab4:
    st.subheader("🕘 Analysis History")

    if len(st.session_state.history) == 0:
        st.info("No analysis history yet. Analyze a review first.")
    else:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)

        csv = history_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Full Analysis History",
            data=csv,
            file_name="analysis_history.csv",
            mime="text/csv"
        )

        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

# =====================================================
# Tab 5: User Guide
# =====================================================
with tab5:
    st.subheader("📘 User Guide")

    st.markdown("""
    ### How to Use the System

    1. Go to **Single Review Analysis**.
    2. Enter one hotel-related review.
    3. Click **Analyze Review**.
    4. The system will display:
       - Overall sentiment
       - Confidence score
       - Sentiment score distribution
       - Pre-processed text
       - Aspect-based sentiment
       - Key sentiment words
       - Management recommendation
    5. Use **Batch Analysis** to analyze multiple reviews.
    6. Download results as CSV.

    ### System Limitation

    This system is trained on hotel review data only. It may not perform well on:
    - Non-hotel-related input
    - Very short input
    - Sarcasm
    - Slang
    - Reviews with unclear meaning

    Therefore, input validation is included to reject irrelevant or inappropriate text before prediction.
    """)
