import html
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


def load_review_checker_css():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1180px;
        }

        .review-input-card {
            background: #ffffff;
            border: 1px solid #E5E7EB;
            border-radius: 22px;
            padding: 1.35rem 1.45rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }

        .helper-text {
            color: #64748B;
            font-size: 0.92rem;
            margin-top: -0.35rem;
            margin-bottom: 0.9rem;
        }

        .example-chip {
            display: inline-block;
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.82rem;
            margin-right: 0.4rem;
            margin-bottom: 0.35rem;
        }

        .result-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1rem 0;
        }

        .result-card {
            background: #ffffff;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            min-height: 112px;
        }

        .result-label {
            font-size: 0.82rem;
            color: #64748B;
            font-weight: 600;
            margin-bottom: 0.45rem;
        }

        .result-value {
            font-size: 1.65rem;
            font-weight: 750;
            color: #0F172A;
            line-height: 1.2;
        }

        .result-sub {
            font-size: 0.82rem;
            color: #64748B;
            margin-top: 0.35rem;
        }

        .status-dot {
            display: inline-block;
            width: 0.82rem;
            height: 0.82rem;
            border-radius: 999px;
            margin-right: 0.55rem;
            vertical-align: middle;
        }

        .dot-positive {
            background: #22C55E;
            box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.15);
        }

        .dot-neutral {
            background: #F59E0B;
            box-shadow: 0 0 0 6px rgba(245, 158, 11, 0.16);
        }

        .dot-negative {
            background: #EF4444;
            box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.16);
        }

        .summary-banner {
            border-radius: 22px;
            padding: 1.15rem 1.35rem;
            margin: 0.7rem 0 1rem 0;
            border: 1px solid;
        }

        .summary-positive {
            background: #ECFDF5;
            border-color: #BBF7D0;
            color: #065F46;
        }

        .summary-neutral {
            background: #FFFBEB;
            border-color: #FDE68A;
            color: #92400E;
        }

        .summary-negative {
            background: #FEF2F2;
            border-color: #FECACA;
            color: #991B1B;
        }

        .summary-title {
            font-size: 1.15rem;
            font-weight: 750;
            margin-bottom: 0.35rem;
        }

        .summary-body {
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .mini-section {
            background: #ffffff;
            border: 1px solid #E5E7EB;
            border-radius: 20px;
            padding: 1.05rem 1.15rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.045);
            margin-bottom: 1rem;
        }

        .mini-title {
            font-size: 1rem;
            font-weight: 750;
            color: #0F172A;
            margin-bottom: 0.75rem;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.35rem;
        }

        .aspect-chip {
            display: inline-flex;
            align-items: center;
            background: #EEF2FF;
            color: #3730A3;
            border: 1px solid #C7D2FE;
            border-radius: 999px;
            padding: 0.38rem 0.75rem;
            font-size: 0.84rem;
            font-weight: 650;
        }

        .positive-chip {
            display: inline-flex;
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
            border-radius: 999px;
            padding: 0.38rem 0.75rem;
            font-size: 0.84rem;
            font-weight: 650;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .negative-chip {
            display: inline-flex;
            background: #FEF2F2;
            color: #B91C1C;
            border: 1px solid #FECACA;
            border-radius: 999px;
            padding: 0.38rem 0.75rem;
            font-size: 0.84rem;
            font-weight: 650;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .empty-chip {
            display: inline-flex;
            background: #F1F5F9;
            color: #64748B;
            border: 1px solid #E2E8F0;
            border-radius: 999px;
            padding: 0.38rem 0.75rem;
            font-size: 0.84rem;
            font-weight: 600;
        }

        .signal-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            min-height: 92px;
        }

        .signal-title {
            font-size: 0.82rem;
            color: #64748B;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .signal-value {
            color: #0F172A;
            font-size: 0.95rem;
            font-weight: 650;
        }

        .prob-row {
            margin-bottom: 0.8rem;
        }

        .prob-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.88rem;
            font-weight: 650;
            color: #334155;
            margin-bottom: 0.28rem;
        }

        .bar-track {
            width: 100%;
            height: 10px;
            background: #E2E8F0;
            border-radius: 999px;
            overflow: hidden;
        }

        .bar-positive {
            height: 10px;
            background: #22C55E;
            border-radius: 999px;
        }

        .bar-neutral {
            height: 10px;
            background: #F59E0B;
            border-radius: 999px;
        }

        .bar-negative {
            height: 10px;
            background: #EF4444;
            border-radius: 999px;
        }

        .explanation-box {
            background: #F8FAFC;
            border-left: 5px solid #2563EB;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            color: #1E293B;
            line-height: 1.7;
            font-size: 0.98rem;
        }

        .decision-safe {
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            color: #065F46;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            font-weight: 600;
        }

        .decision-warning {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            color: #92400E;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            font-weight: 600;
        }

        .decision-danger {
            background: #FEF2F2;
            border: 1px solid #FECACA;
            color: #991B1B;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            font-weight: 600;
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 16px;
        }

        div[data-testid="stButton"] button {
            border-radius: 14px;
            height: 3rem;
            font-weight: 750;
            background: linear-gradient(90deg, #2563EB, #4F46E5);
            border: none;
        }

        @media (max-width: 900px) {
            .result-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 600px) {
            .result-grid {
                grid-template-columns: 1fr;
            }

            .result-value {
                font-size: 1.35rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def get_sentiment_class(sentiment):
    sentiment = str(sentiment).lower()

    if sentiment == "positive":
        return "summary-positive", "dot-positive"

    if sentiment == "negative":
        return "summary-negative", "dot-negative"

    return "summary-neutral", "dot-neutral"


def render_result_card(label, value, sub_text=None, dot_class=None):
    dot_html = ""

    if dot_class:
        dot_html = f'<span class="status-dot {dot_class}"></span>'

    sub_html = ""

    if sub_text:
        sub_html = f'<div class="result-sub">{html.escape(str(sub_text))}</div>'

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">{html.escape(str(label))}</div>
            <div class="result-value">{dot_html}{html.escape(str(value))}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_probability_bars(probabilities):
    positive = float(probabilities.get("Positive", 0))
    neutral = float(probabilities.get("Neutral", 0))
    negative = float(probabilities.get("Negative", 0))

    st.markdown(
        f"""
        <div class="mini-section">
            <div class="mini-title">Model Probability Distribution</div>

            <div class="prob-row">
                <div class="prob-label">
                    <span>Positive</span>
                    <span>{positive:.2f}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-positive" style="width: {positive}%;"></div>
                </div>
            </div>

            <div class="prob-row">
                <div class="prob-label">
                    <span>Neutral</span>
                    <span>{neutral:.2f}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-neutral" style="width: {neutral}%;"></div>
                </div>
            </div>

            <div class="prob-row">
                <div class="prob-label">
                    <span>Negative</span>
                    <span>{negative:.2f}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-negative" style="width: {negative}%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chips(items, chip_class, empty_text):
    if items:
        chips = "".join(
            f'<span class="{chip_class}">{html.escape(str(item))}</span>'
            for item in items
        )
    else:
        chips = f'<span class="empty-chip">{html.escape(empty_text)}</span>'

    st.markdown(chips, unsafe_allow_html=True)


def render_aspect_chips(aspects):
    if aspects:
        chips = "".join(
            f'<span class="aspect-chip">{html.escape(str(aspect))}</span>'
            for aspect in aspects
        )
        st.markdown(f'<div class="chip-row">{chips}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="empty-chip">No specific hotel aspect detected</span>',
            unsafe_allow_html=True
        )


def render_signal_card(title, value):
    st.markdown(
        f"""
        <div class="signal-card">
            <div class="signal-title">{html.escape(str(title))}</div>
            <div class="signal-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_traveller_decision(risk):
    if risk == "High":
        css_class = "decision-danger"
        message = "This review contains clear risk signals. Users should compare more reviews before booking."
    elif risk == "Medium":
        css_class = "decision-warning"
        message = "This review is mixed or contains some concerns. Users should check more reviews before deciding."
    else:
        css_class = "decision-safe"
        message = "This review looks generally safe, but users should still compare multiple reviews."

    st.markdown(
        f"""
        <div class="{css_class}">
            {html.escape(message)}
        </div>
        """,
        unsafe_allow_html=True
    )


load_css()
load_review_checker_css()
render_topbar()

render_page_header(
    "Review Checker",
    "Analyze one hotel review using the trained DistilBERT model, with emoji, aspect, risk, pros and cons support."
)

st.markdown(
    """
    <div class="review-input-card">
        <div class="helper-text">
            Paste a hotel review below. The system will classify the overall sentiment and provide supporting analysis.
        </div>
        <span class="example-chip">Example: The room was clean and the staff were friendly.</span>
        <span class="example-chip">Example: The room was noisy but the location was convenient.</span>
        <span class="example-chip">Example: The staff were rude and the toilet was dirty.</span>
    </div>
    """,
    unsafe_allow_html=True
)

review_input = st.text_area(
    "Hotel review input",
    height=120,
    placeholder="Example: The room was clean and comfortable 😊 but the check-in was slow.",
    label_visibility="collapsed"
)

analyze = st.button("Analyze Review", use_container_width=True)

if analyze:
    if review_input.strip() == "":
        st.warning("Please paste a hotel review first.")
    else:
        result = analyze_review_frontend(review_input)

        sentiment = result.get("sentiment", "Neutral")
        confidence = result.get("confidence", 0)
        risk = result.get("risk", "Medium")
        emoji_info = result.get("emoji_info", {})
        aspect_breakdown = result.get("aspect_breakdown", [])
        probabilities = result.get("probabilities", {
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0
        })

        summary_class, dot_class = get_sentiment_class(sentiment)

        st.markdown(
            '<div class="result-grid">',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_result_card(
                "Overall Sentiment",
                sentiment,
                "DistilBERT prediction",
                dot_class
            )

        with col2:
            render_result_card(
                "Confidence",
                f"{confidence}%",
                "Model certainty"
            )

        with col3:
            render_result_card(
                "Risk Level",
                risk,
                "Booking caution level"
            )

        with col4:
            render_result_card(
                "Emoji Signal",
                emoji_info.get("emoji_sentiment", "No emoji signal"),
                "Emoji / emoticon support"
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="summary-banner {summary_class}">
                <div class="summary-title">Overall Result: {html.escape(str(sentiment))}</div>
                <div class="summary-body">{html.escape(str(result.get("suitability", "")))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_overview, tab_aspects, tab_explanation, tab_details = st.tabs([
            "Overview",
            "Aspects & Signals",
            "Explanation",
            "Processing Details"
        ])

        with tab_overview:
            overview_col1, overview_col2 = st.columns([1.05, 1])

            with overview_col1:
                render_probability_bars(probabilities)

            with overview_col2:
                st.markdown(
                    """
                    <div class="mini-section">
                        <div class="mini-title">Traveller Decision Note</div>
                    """,
                    unsafe_allow_html=True
                )

                render_traveller_decision(risk)

                st.markdown("</div>", unsafe_allow_html=True)

            pc_col1, pc_col2 = st.columns(2)

            with pc_col1:
                st.markdown(
                    """
                    <div class="mini-section">
                        <div class="mini-title">Detected Pros</div>
                    """,
                    unsafe_allow_html=True
                )
                render_chips(
                    result.get("pros", []),
                    "positive-chip",
                    "No clear pros detected"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with pc_col2:
                st.markdown(
                    """
                    <div class="mini-section">
                        <div class="mini-title">Detected Cons</div>
                    """,
                    unsafe_allow_html=True
                )
                render_chips(
                    result.get("cons", []),
                    "negative-chip",
                    "No clear cons detected"
                )
                st.markdown("</div>", unsafe_allow_html=True)

        with tab_aspects:
            aspect_col1, aspect_col2 = st.columns([1, 1])

            with aspect_col1:
                st.markdown(
                    """
                    <div class="mini-section">
                        <div class="mini-title">Detected Hotel Aspects</div>
                    """,
                    unsafe_allow_html=True
                )
                render_aspect_chips(result.get("detected_aspects", []))
                st.markdown("</div>", unsafe_allow_html=True)

            with aspect_col2:
                st.markdown(
                    """
                    <div class="mini-section">
                        <div class="mini-title">Emoji / Emoticon Signals</div>
                    """,
                    unsafe_allow_html=True
                )

                sig1, sig2, sig3 = st.columns(3)

                with sig1:
                    positive_signals = emoji_info.get("positive_signals", [])
                    render_signal_card(
                        "Positive",
                        " ".join(positive_signals) if positive_signals else "None"
                    )

                with sig2:
                    negative_signals = emoji_info.get("negative_signals", [])
                    render_signal_card(
                        "Negative",
                        " ".join(negative_signals) if negative_signals else "None"
                    )

                with sig3:
                    neutral_signals = emoji_info.get("neutral_signals", [])
                    render_signal_card(
                        "Neutral",
                        " ".join(neutral_signals) if neutral_signals else "None"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                """
                <div class="mini-section">
                    <div class="mini-title">Aspect Sentiment Breakdown</div>
                """,
                unsafe_allow_html=True
            )

            if aspect_breakdown:
                aspect_df = pd.DataFrame(aspect_breakdown)
                st.dataframe(aspect_df, use_container_width=True, hide_index=True)
            else:
                st.info("No aspect sentiment breakdown available because no hotel aspect was detected.")

            st.markdown("</div>", unsafe_allow_html=True)

        with tab_explanation:
            explanation = result.get("explanation", "")

            st.markdown(
                f"""
                <div class="explanation-box">
                    {html.escape(str(explanation))}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")

            st.markdown(
                """
                <div class="mini-section">
                    <div class="mini-title">How to read this result</div>
                    <div class="summary-body">
                        The overall sentiment is predicted by the DistilBERT transformer model.
                        Keyword signals, emoji signals, hotel aspects, and risk level are used as supporting analysis
                        to make the output easier for travellers to understand.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with tab_details:
            st.markdown(
                """
                <div class="mini-section">
                    <div class="mini-title">Technical Processing Details</div>
                """,
                unsafe_allow_html=True
            )

            processing_df = get_processing_details(review_input)
            st.dataframe(processing_df, use_container_width=True, hide_index=True)

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Paste a hotel review and click Analyze Review to start.")

render_footer()