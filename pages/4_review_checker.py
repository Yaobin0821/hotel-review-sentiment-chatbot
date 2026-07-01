import streamlit as st
import pandas as pd
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import (
    analyze_review_frontend,
    sentiment_label_style,
    get_processing_details
)

st.set_page_config(
    page_title="Review Checker",
    page_icon="🔍",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Review Checker",
    "Paste one review and check its sentiment, emoji signals, hotel aspects, risks, pros, cons, and explanation."
)

st.caption("User input is not saved in this page.")

review_input = st.text_area(
    "Paste one hotel review",
    height=170,
    placeholder="Example: The room was clean and comfortable 😊 but the check-in was slow."
)

analyze = st.button("Analyze Review", use_container_width=True)

if analyze:
    if review_input.strip() == "":
        st.warning("Please paste a hotel review first.")
    else:
        result = analyze_review_frontend(review_input)
        emoji_info = result["emoji_info"]
        aspect_breakdown = result["aspect_breakdown"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sentiment", sentiment_label_style(result["sentiment"]))
        c2.metric("Confidence", f"{result['confidence']}%")
        c3.metric("Risk", result["risk"])
        c4.metric("Emoji Signal", emoji_info["emoji_sentiment"])

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

        st.markdown("### Emoji / Emoticon Sentiment Integration")

        emoji_col1, emoji_col2, emoji_col3 = st.columns(3)

        with emoji_col1:
            if emoji_info["positive_signals"]:
                st.success("Positive signals: " + " ".join(emoji_info["positive_signals"]))
            else:
                st.info("No positive emoji signals")

        with emoji_col2:
            if emoji_info["negative_signals"]:
                st.error("Negative signals: " + " ".join(emoji_info["negative_signals"]))
            else:
                st.info("No negative emoji signals")

        with emoji_col3:
            if emoji_info["neutral_signals"]:
                st.warning("Neutral signals: " + " ".join(emoji_info["neutral_signals"]))
            else:
                st.info("No neutral emoji signals")

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

        st.markdown("### Aspect Sentiment Breakdown")

        if aspect_breakdown:
            aspect_df = pd.DataFrame(aspect_breakdown)
            st.dataframe(aspect_df, use_container_width=True)
        else:
            st.info("No aspect sentiment breakdown available because no hotel aspect was detected.")

        st.markdown("### Explanation")
        st.write(result["explanation"])

        st.markdown("### Traveller Decision Note")

        if result["risk"] == "High":
            st.error("This review contains clear risk signals. Users should compare more reviews before booking.")
        elif result["risk"] == "Medium":
            st.warning("This review is mixed or has some concerns. Users should check more reviews before deciding.")
        else:
            st.success("This review looks generally safe, but users should still compare multiple reviews.")

        with st.expander("View Processing Details"):
            processing_df = get_processing_details(review_input)
            st.dataframe(processing_df, use_container_width=True)

render_footer()
