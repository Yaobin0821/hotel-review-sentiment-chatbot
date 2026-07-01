import html
import streamlit as st
import pandas as pd
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import (
    analyze_review_frontend,
    get_processing_details
)


st.set_page_config(
    page_title="Review Checker",
    page_icon="🔍",
    layout="wide"
)


def load_tourist_review_css():
    st.markdown("""
    <style>
        .block-container {
            max-width: 1120px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .tourist-hero {
            background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 60%, #ECFDF5 100%);
            border: 1px solid #DBEAFE;
            border-radius: 26px;
            padding: 1.5rem 1.6rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        }

        .hero-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.35rem;
        }

        .hero-subtitle {
            color: #475569;
            font-size: 0.98rem;
            line-height: 1.55;
            margin-bottom: 0.9rem;
        }

        .tourist-chip {
            display: inline-block;
            background: #FFFFFF;
            color: #2563EB;
            border: 1px solid #BFDBFE;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.82rem;
            font-weight: 650;
            margin-right: 0.4rem;
            margin-bottom: 0.35rem;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 18px;
            border: 1px solid #CBD5E1;
            font-size: 1rem;
        }

        div[data-testid="stButton"] button {
            border-radius: 16px;
            height: 3.1rem;
            font-size: 1rem;
            font-weight: 800;
            background: linear-gradient(90deg, #2563EB, #16A34A);
            border: none;
            color: white;
        }

        .main-advice-card {
            border-radius: 28px;
            padding: 1.45rem 1.55rem;
            margin: 1.1rem 0;
            border: 1px solid;
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
        }

        .advice-positive {
            background: linear-gradient(135deg, #ECFDF5, #F0FDF4);
            border-color: #BBF7D0;
        }

        .advice-neutral {
            background: linear-gradient(135deg, #FFFBEB, #FEFCE8);
            border-color: #FDE68A;
        }

        .advice-negative {
            background: linear-gradient(135deg, #FEF2F2, #FFF1F2);
            border-color: #FECACA;
        }

        .advice-small {
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
            color: #64748B;
        }

        .advice-title {
            font-size: 2rem;
            font-weight: 850;
            color: #0F172A;
            margin-bottom: 0.45rem;
            line-height: 1.18;
        }

        .advice-body {
            color: #334155;
            font-size: 1.02rem;
            line-height: 1.65;
            max-width: 880px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.2rem 0;
        }

        .summary-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 22px;
            padding: 1rem 1.05rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
            min-height: 112px;
        }

        .summary-label {
            color: #64748B;
            font-size: 0.84rem;
            font-weight: 750;
            margin-bottom: 0.4rem;
        }

        .summary-value {
            color: #0F172A;
            font-size: 1.35rem;
            font-weight: 850;
            line-height: 1.2;
        }

        .summary-note {
            color: #64748B;
            font-size: 0.84rem;
            margin-top: 0.42rem;
            line-height: 1.4;
        }

        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-top: 0.8rem;
        }

        .info-box {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 24px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
            min-height: 150px;
        }

        .box-title {
            color: #0F172A;
            font-size: 1.08rem;
            font-weight: 850;
            margin-bottom: 0.75rem;
        }

        .box-subtitle {
            color: #64748B;
            font-size: 0.9rem;
            margin-bottom: 0.7rem;
            line-height: 1.45;
        }

        .good-item {
            display: inline-block;
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            font-weight: 700;
            font-size: 0.88rem;
            margin-right: 0.38rem;
            margin-bottom: 0.38rem;
        }

        .bad-item {
            display: inline-block;
            background: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            font-weight: 700;
            font-size: 0.88rem;
            margin-right: 0.38rem;
            margin-bottom: 0.38rem;
        }

        .topic-item {
            display: inline-block;
            background: #EEF2FF;
            color: #3730A3;
            border: 1px solid #C7D2FE;
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            font-weight: 700;
            font-size: 0.88rem;
            margin-right: 0.38rem;
            margin-bottom: 0.38rem;
        }

        .empty-text {
            background: #F8FAFC;
            color: #64748B;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.8rem 0.9rem;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .plain-note {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            color: #334155;
            border-radius: 20px;
            padding: 1rem 1.05rem;
            line-height: 1.65;
            font-size: 0.96rem;
            margin-top: 1rem;
        }

        .aspect-table-card {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 24px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
            margin-top: 1rem;
        }

        .friendly-divider {
            height: 1px;
            background: #E2E8F0;
            margin: 1rem 0;
        }

        @media (max-width: 900px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }

            .content-grid {
                grid-template-columns: 1fr;
            }

            .advice-title {
                font-size: 1.55rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def get_advice_info(sentiment, risk):
    sentiment_lower = str(sentiment).lower()
    risk_lower = str(risk).lower()

    if sentiment_lower == "positive" and risk_lower == "low":
        return {
            "css": "advice-positive",
            "title": "Looks good to consider",
            "short": "This review sounds mostly positive.",
            "body": "This review gives a good impression of the hotel. It mentions positive experiences and does not show strong warning signs. You can consider this hotel, but it is still better to compare a few more reviews before booking."
        }

    if sentiment_lower == "negative" or risk_lower == "high":
        return {
            "css": "advice-negative",
            "title": "Be careful before booking",
            "short": "This review shows possible problems.",
            "body": "This review contains negative signals or possible risk areas. Before booking, you should read more reviews and check whether other guests mention the same problems."
        }

    return {
        "css": "advice-neutral",
        "title": "Compare more reviews first",
        "short": "This review is mixed or not strong enough.",
        "body": "This review does not give a very clear positive or negative answer. It may contain mixed feedback, so you should compare more reviews before making a decision."
    }


def render_main_advice(sentiment, risk):
    advice = get_advice_info(sentiment, risk)

    st.markdown(
        f"""
        <div class="main-advice-card {advice["css"]}">
            <div class="advice-small">Booking Advice</div>
            <div class="advice-title">{html.escape(advice["title"])}</div>
            <div class="advice-body">{html.escape(advice["body"])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_cards(sentiment, confidence, risk):
    sentiment_text = {
        "Positive": "Mostly Positive",
        "Neutral": "Mixed / Neutral",
        "Negative": "Mostly Negative"
    }.get(str(sentiment), str(sentiment))

    risk_text = {
        "Low": "Low Concern",
        "Medium": "Some Concern",
        "High": "High Concern"
    }.get(str(risk), str(risk))

    st.markdown('<div class="summary-grid">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Review Feeling</div>
                <div class="summary-value">{html.escape(sentiment_text)}</div>
                <div class="summary-note">Overall feeling detected from this review.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Confidence</div>
                <div class="summary-value">{html.escape(str(confidence))}%</div>
                <div class="summary-note">How confident the AI is about this result.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Booking Concern</div>
                <div class="summary-value">{html.escape(risk_text)}</div>
                <div class="summary-note">How much caution this review suggests.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


def render_chip_list(items, css_class, empty_message):
    if items:
        chips = "".join(
            f'<span class="{css_class}">{html.escape(str(item).title())}</span>'
            for item in items
        )
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="empty-text">{html.escape(empty_message)}</div>',
            unsafe_allow_html=True
        )


def get_simple_reason(result):
    sentiment = result.get("sentiment", "Neutral")
    confidence = result.get("confidence", 0)
    pros = result.get("pros", [])
    cons = result.get("cons", [])
    aspects = result.get("detected_aspects", [])

    if sentiment == "Positive":
        opening = f"The review sounds positive with {confidence}% confidence."
    elif sentiment == "Negative":
        opening = f"The review sounds negative with {confidence}% confidence."
    else:
        opening = f"The review sounds mixed or neutral with {confidence}% confidence."

    reason_parts = [opening]

    if pros:
        reason_parts.append(
            "Positive words detected include " + ", ".join([str(x).title() for x in pros[:4]]) + "."
        )

    if cons:
        reason_parts.append(
            "Concern words detected include " + ", ".join([str(x).title() for x in cons[:4]]) + "."
        )

    if aspects:
        reason_parts.append(
            "The review mainly talks about " + ", ".join(aspects[:4]) + "."
        )

    return " ".join(reason_parts)


def render_tourist_details(result):
    aspects = result.get("detected_aspects", [])
    aspect_breakdown = result.get("aspect_breakdown", [])
    emoji_info = result.get("emoji_info", {})

    with st.expander("Show more details"):
        st.markdown("#### Hotel topics mentioned")
        render_chip_list(
            aspects,
            "topic-item",
            "No specific hotel topic was clearly mentioned."
        )

        st.markdown('<div class="friendly-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### Emoji or emoticon signal")
        emoji_signal = emoji_info.get("emoji_sentiment", "No emoji signal")
        st.write(f"Emoji signal: **{emoji_signal}**")

        if aspect_breakdown:
            st.markdown("#### Topic breakdown")
            aspect_df = pd.DataFrame(aspect_breakdown)

            display_columns = [
                "Aspect",
                "Aspect Sentiment",
                "Matched Keywords"
            ]

            available_columns = [
                col for col in display_columns
                if col in aspect_df.columns
            ]

            st.dataframe(
                aspect_df[available_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No detailed topic breakdown available.")


def render_project_details(review_input):
    with st.expander("Project technical details"):
        st.caption("This section is mainly for project demonstration, not for normal hotel users.")
        processing_df = get_processing_details(review_input)
        st.dataframe(processing_df, use_container_width=True, hide_index=True)


load_css()
load_tourist_review_css()
render_topbar()

render_page_header(
    "Review Checker",
    "Paste a hotel review and get a simple booking-friendly summary."
)

st.markdown(
    """
    <div class="tourist-hero">
        <div class="hero-title">Should I trust this review?</div>
        <div class="hero-subtitle">
            Paste one hotel review below. The system will summarize whether the review sounds positive,
            mixed, or risky, and highlight what travellers may like or need to watch out for.
        </div>
        <span class="tourist-chip">Fast review summary</span>
        <span class="tourist-chip">Booking concern check</span>
        <span class="tourist-chip">Pros and cons</span>
    </div>
    """,
    unsafe_allow_html=True
)

review_input = st.text_area(
    "Paste a hotel review",
    height=115,
    placeholder="Example: The room was clean and comfortable, but the check-in was slow."
)

analyze = st.button("Check This Review", use_container_width=True)

if analyze:
    if review_input.strip() == "":
        st.warning("Please paste a hotel review first.")
    else:
        result = analyze_review_frontend(review_input)

        sentiment = result.get("sentiment", "Neutral")
        confidence = result.get("confidence", 0)
        risk = result.get("risk", "Medium")

        render_main_advice(sentiment, risk)
        render_summary_cards(sentiment, confidence, risk)

        content_col1, content_col2 = st.columns(2)

        with content_col1:
            st.markdown(
                """
                <div class="info-box">
                    <div class="box-title">What travellers may like</div>
                    <div class="box-subtitle">Positive points found in this review.</div>
                """,
                unsafe_allow_html=True
            )

            render_chip_list(
                result.get("pros", []),
                "good-item",
                "No clear positive point was detected in this review."
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with content_col2:
            st.markdown(
                """
                <div class="info-box">
                    <div class="box-title">What to watch out for</div>
                    <div class="box-subtitle">Possible concerns found in this review.</div>
                """,
                unsafe_allow_html=True
            )

            render_chip_list(
                result.get("cons", []),
                "bad-item",
                "No clear concern was detected in this review."
            )

            st.markdown("</div>", unsafe_allow_html=True)

        simple_reason = get_simple_reason(result)

        st.markdown(
            f"""
            <div class="plain-note">
                <b>Why this result?</b><br>
                {html.escape(simple_reason)}
            </div>
            """,
            unsafe_allow_html=True
        )

        render_tourist_details(result)

        render_project_details(review_input)

else:
    st.info("Paste a review and click Check This Review to start.")

render_footer()