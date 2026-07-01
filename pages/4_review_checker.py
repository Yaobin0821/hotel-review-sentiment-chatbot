import html
import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer
from utils import analyze_review_frontend


st.set_page_config(
    page_title="Review Checker",
    page_icon="🔍",
    layout="wide"
)


def load_review_checker_css():
    st.markdown("""
    <style>
        .booking-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
        }

        .booking-card.sticky {
            position: sticky;
            top: 1rem;
        }

        .card-kicker {
            color: var(--brand-dark);
            background: #FFF4E8;
            border: 1px solid #F2CBAE;
            display: inline-flex;
            border-radius: 999px;
            padding: 0.35rem 0.68rem;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.85rem;
        }

        .input-title {
            font-size: 1.45rem;
            font-weight: 900;
            color: var(--text-main);
            letter-spacing: -0.04em;
            line-height: 1.12;
            margin-bottom: 0.45rem;
        }

        .input-desc {
            color: #64748B;
            line-height: 1.6;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }

        .sample-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.95rem 0 1rem 0;
        }

        .sample-chip {
            background: #FFFDF8;
            color: #7A4D33;
            border: 1px solid #EAD7C6;
            border-radius: 999px;
            padding: 0.38rem 0.72rem;
            font-size: 0.82rem;
            font-weight: 720;
        }

        .privacy-note {
            margin-top: 0.85rem;
            background: #F8F4EE;
            color: #7C6F64;
            border: 1px dashed #D8CDBE;
            border-radius: 16px;
            padding: 0.75rem 0.85rem;
            font-size: 0.86rem;
            line-height: 1.45;
        }

        .empty-result {
            min-height: 410px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            background:
                linear-gradient(135deg, rgba(255, 244, 232, 0.95), rgba(234, 243, 239, 0.95));
            border: 1px solid #E7DDD0;
            border-radius: 30px;
            padding: 2rem;
            box-shadow: var(--shadow-card);
        }

        .empty-icon {
            width: 58px;
            height: 58px;
            border-radius: 20px;
            background: white;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.7rem;
            box-shadow: 0 10px 24px rgba(74, 55, 40, 0.08);
            margin-bottom: 1rem;
        }

        .empty-title {
            font-size: 1.55rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            margin-bottom: 0.55rem;
            color: var(--text-main);
        }

        .empty-desc {
            color: #64748B;
            line-height: 1.65;
            max-width: 520px;
        }

        .advice-card {
            border-radius: 30px;
            padding: 1.55rem;
            border: 1px solid;
            box-shadow: var(--shadow-card);
            margin-bottom: 1rem;
        }

        .advice-good {
            background: linear-gradient(135deg, #F0FFF7, #FFFFFF);
            border-color: #BCE8CF;
        }

        .advice-mid {
            background: linear-gradient(135deg, #FFF9E8, #FFFFFF);
            border-color: #F0DDA0;
        }

        .advice-risk {
            background: linear-gradient(135deg, #FFF1EE, #FFFFFF);
            border-color: #F4C7BF;
        }

        .advice-label {
            color: #7C6F64;
            font-size: 0.8rem;
            font-weight: 900;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .advice-title {
            color: var(--text-main);
            font-size: 2rem;
            font-weight: 950;
            letter-spacing: -0.06em;
            line-height: 1.08;
            margin-bottom: 0.65rem;
        }

        .advice-text {
            color: #334155;
            font-size: 1rem;
            line-height: 1.7;
            max-width: 720px;
        }

        .strip-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 1rem;
        }

        .strip-label {
            color: #7C6F64;
            font-size: 0.78rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .strip-value {
            color: var(--text-main);
            font-size: 1.25rem;
            font-weight: 900;
            letter-spacing: -0.03em;
        }

        .strip-help {
            color: #64748B;
            font-size: 0.82rem;
            margin-top: 0.3rem;
            line-height: 1.35;
        }

        .traveller-box {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.15rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            min-height: 145px;
            margin-bottom: 0.9rem;
        }

        .box-title {
            color: var(--text-main);
            font-size: 1.08rem;
            font-weight: 900;
            letter-spacing: -0.03em;
            margin-bottom: 0.35rem;
        }

        .box-desc {
            color: #64748B;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 0.75rem;
        }

        .chip-area {
            margin-top: 0.75rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        .chip-good, .chip-bad, .chip-topic {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.72rem;
            font-size: 0.85rem;
            font-weight: 760;
            margin: 0;
        }

        .chip-good {
            color: #216E46;
            background: #EAF7F0;
            border: 1px solid #BFE3CF;
        }

        .chip-bad {
            color: #A33A2F;
            background: #FFF0EE;
            border: 1px solid #F4C7BF;
        }

        .chip-topic {
            color: #6D4B30;
            background: #FFF4E8;
            border: 1px solid #EAD7C6;
        }

        .empty-line {
            color: #7C6F64;
            background: #F8F4EE;
            border: 1px solid #E5D8CA;
            border-radius: 16px;
            padding: 0.75rem 0.85rem;
            font-size: 0.9rem;
            line-height: 1.45;
            width: 100%;
        }

        .reason-box {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.15rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 0.9rem;
        }

        .reason-title {
            font-weight: 900;
            color: var(--text-main);
            font-size: 1.05rem;
            margin-bottom: 0.45rem;
        }

        .reason-text {
            color: #334155;
            line-height: 1.65;
            font-size: 0.95rem;
        }

        .friendly-detail-box {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.15rem;
            box-shadow: 0 8px 20px rgba(74, 55, 40, 0.045);
            margin-bottom: 0.9rem;
        }

        .friendly-detail-title {
            font-size: 1.08rem;
            font-weight: 900;
            color: var(--text-main);
            margin-bottom: 0.35rem;
        }

        .friendly-detail-desc {
            color: #64748B;
            font-size: 0.92rem;
            line-height: 1.5;
            margin-bottom: 0.9rem;
        }

        .detail-row {
            margin-bottom: 0.95rem;
        }

        .detail-label {
            color: #7C6F64;
            font-size: 0.82rem;
            font-weight: 850;
            margin-bottom: 0.4rem;
        }

        .simple-explanation {
            background: #FFFDF8;
            border: 1px solid #EAD7C6;
            color: #334155;
            border-radius: 18px;
            padding: 0.9rem 1rem;
            line-height: 1.6;
            font-size: 0.92rem;
        }

        @media (max-width: 950px) {
            .booking-card.sticky {
                position: static;
            }

            .advice-title {
                font-size: 1.55rem;
            }

            .empty-result {
                min-height: 280px;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def escape(value):
    return html.escape(str(value))


def get_advice(sentiment, risk):
    sentiment = str(sentiment).lower()
    risk = str(risk).lower()

    if sentiment == "negative" or risk == "high":
        return {
            "class": "advice-risk",
            "title": "Check carefully before booking",
            "text": "This review shows possible guest concerns. Read more reviews and see whether other travellers mention the same issue before you decide.",
        }

    if sentiment == "neutral" or risk == "medium":
        return {
            "class": "advice-mid",
            "title": "Worth comparing with more reviews",
            "text": "This review is not strongly positive or negative. It is better to compare a few more reviews before making your booking decision.",
        }

    return {
        "class": "advice-good",
        "title": "Looks safe to consider",
        "text": "This review gives a positive impression and does not show strong warning signs. You can consider this hotel, but checking more reviews is still recommended.",
    }


def get_review_feeling(sentiment):
    sentiment = str(sentiment).lower()

    if sentiment == "positive":
        return "Positive"

    if sentiment == "negative":
        return "Negative"

    return "Mixed"


def get_concern_text(risk):
    risk = str(risk).lower()

    if risk == "high":
        return "High"

    if risk == "medium":
        return "Some"

    return "Low"


def build_chip_html(items, chip_class, empty_message):
    if not items:
        return (
            f'<div class="empty-line">'
            f'{escape(empty_message)}'
            f'</div>'
        )

    chips = []

    for item in items:
        chips.append(
            f'<span class="{chip_class}">'
            f'{escape(str(item).title())}'
            f'</span>'
        )

    return "".join(chips)


def render_traveller_box(title, desc, items, chip_class, empty_message):
    chips_html = build_chip_html(items, chip_class, empty_message)

    st.markdown(
        f"""
        <div class="traveller-box">
            <div class="box-title">{escape(title)}</div>
            <div class="box-desc">{escape(desc)}</div>
            <div class="chip-area">
                {chips_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def build_simple_reason(result):
    sentiment = result.get("sentiment", "Neutral")
    confidence = result.get("confidence", 0)
    pros = result.get("pros", [])
    cons = result.get("cons", [])
    aspects = result.get("detected_aspects", [])

    if sentiment == "Positive":
        sentence = "This review sounds positive and the result is quite clear."
    elif sentiment == "Negative":
        sentence = "This review sounds negative and may contain booking concerns."
    else:
        sentence = "This review sounds mixed, so it is better to compare more guest feedback."

    parts = [sentence]

    if pros:
        parts.append(
            "Good signs mentioned: "
            + ", ".join(str(item).title() for item in pros[:4])
            + "."
        )

    if cons:
        parts.append(
            "Possible concerns mentioned: "
            + ", ".join(str(item).title() for item in cons[:4])
            + "."
        )

    if aspects:
        parts.append(
            "Main hotel topics: "
            + ", ".join(str(item) for item in aspects[:4])
            + "."
        )

    parts.append(f"Clarity score: {confidence}%.")

    return " ".join(parts)


def build_friendly_detail_sentence(result):
    sentiment = result.get("sentiment", "Neutral")
    pros = result.get("pros", [])
    cons = result.get("cons", [])
    aspects = result.get("detected_aspects", [])

    parts = []

    if sentiment == "Positive":
        parts.append("This review gives a generally good impression.")
    elif sentiment == "Negative":
        parts.append("This review gives a generally negative impression.")
    else:
        parts.append("This review feels mixed, so it is better to compare more guest feedback.")

    if pros:
        parts.append(
            "It mentions positive points such as "
            + ", ".join(str(item).title() for item in pros[:3])
            + "."
        )

    if cons:
        parts.append(
            "It also mentions possible concerns such as "
            + ", ".join(str(item).title() for item in cons[:3])
            + "."
        )

    if aspects:
        parts.append(
            "The main hotel areas mentioned are "
            + ", ".join(str(item) for item in aspects[:4])
            + "."
        )

    return " ".join(parts)


def render_friendly_review_details(result):
    pros = result.get("pros", [])
    cons = result.get("cons", [])
    aspects = result.get("detected_aspects", [])
    emoji_info = result.get("emoji_info", {})
    emoji_signal = emoji_info.get("emoji_sentiment", "No emoji signal")

    positive_html = build_chip_html(
        pros,
        "chip-good",
        "No clear positive point was found."
    )

    concern_html = build_chip_html(
        cons,
        "chip-bad",
        "No clear concern was found."
    )

    topic_html = build_chip_html(
        aspects,
        "chip-topic",
        "No specific hotel area was clearly mentioned."
    )

    emoji_html = ""

    if emoji_signal != "No emoji signal":
        emoji_html = (
            '<div class="detail-row">'
            '<div class="detail-label">Emoji clue</div>'
            '<div class="chip-area">'
            f'<span class="chip-topic">{escape(emoji_signal)}</span>'
            '</div>'
            '</div>'
        )

    detail_html = (
        '<div class="friendly-detail-box">'
        '<div class="friendly-detail-title">What this review talks about</div>'
        '<div class="friendly-detail-desc">'
        'A simple breakdown of useful booking signals found in this review.'
        '</div>'

        '<div class="detail-row">'
        '<div class="detail-label">Good signs</div>'
        '<div class="chip-area">'
        f'{positive_html}'
        '</div>'
        '</div>'

        '<div class="detail-row">'
        '<div class="detail-label">Possible concerns</div>'
        '<div class="chip-area">'
        f'{concern_html}'
        '</div>'
        '</div>'

        '<div class="detail-row">'
        '<div class="detail-label">Hotel areas mentioned</div>'
        '<div class="chip-area">'
        f'{topic_html}'
        '</div>'
        '</div>'

        f'{emoji_html}'

        '<div class="simple-explanation">'
        '<b>Simple explanation:</b><br>'
        f'{escape(build_friendly_detail_sentence(result))}'
        '</div>'

        '</div>'
    )

    st.markdown(detail_html, unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
    <div class="empty-result">
        <div class="empty-icon">🧳</div>
        <div class="empty-title">Paste a review to get booking guidance</div>
        <div class="empty-desc">
            The result will focus on what travellers need most: whether the review sounds positive,
            what is good, what to watch out for, and which hotel topics are mentioned.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_result_summary_card(label, value, help_text):
    st.markdown(
        f"""
        <div class="strip-card">
            <div class="strip-label">{escape(label)}</div>
            <div class="strip-value">{escape(value)}</div>
            <div class="strip-help">{escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_result(result):
    sentiment = result.get("sentiment", "Neutral")
    confidence = result.get("confidence", 0)
    risk = result.get("risk", "Medium")
    advice = get_advice(sentiment, risk)

    st.markdown(
        f"""
        <div class="advice-card {advice["class"]}">
            <div class="advice-label">Booking guidance</div>
            <div class="advice-title">{escape(advice["title"])}</div>
            <div class="advice-text">{escape(advice["text"])}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        render_result_summary_card(
            "Review feeling",
            get_review_feeling(sentiment),
            "Overall tone of this review."
        )

    with summary_col2:
        render_result_summary_card(
            "Result clarity",
            f"{confidence}%",
            "How clear the review signal is."
        )

    with summary_col3:
        render_result_summary_card(
            "Booking concern",
            get_concern_text(risk),
            "How much caution is suggested."
        )

    good_col, concern_col = st.columns(2)

    with good_col:
        render_traveller_box(
            title="What looks good",
            desc="Positive points found in the review.",
            items=result.get("pros", []),
            chip_class="chip-good",
            empty_message="No clear positive point was found."
        )

    with concern_col:
        render_traveller_box(
            title="What to watch out for",
            desc="Possible concerns found in the review.",
            items=result.get("cons", []),
            chip_class="chip-bad",
            empty_message="No clear concern was found."
        )

    st.markdown(
        f"""
        <div class="reason-box">
            <div class="reason-title">Why this result?</div>
            <div class="reason-text">{escape(build_simple_reason(result))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_friendly_review_details(result)


load_css()
load_review_checker_css()
render_topbar()

render_page_header(
    "Review Checker",
    "Paste one hotel review and receive simple booking guidance."
)

left_col, right_col = st.columns([0.95, 1.05], gap="large")

with left_col:
    st.markdown("""
    <div class="booking-card sticky">
        <div class="card-kicker">For travellers</div>
        <div class="input-title">Is this review helpful for booking?</div>
        <div class="input-desc">
            Paste a hotel review. StayWise will turn it into a simple booking note:
            what looks good, what to watch out for, and whether you should compare more reviews.
        </div>
        <div class="sample-row">
            <span class="sample-chip">Clean room</span>
            <span class="sample-chip">Slow check-in</span>
            <span class="sample-chip">Good location</span>
            <span class="sample-chip">Noisy at night</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    review_input = st.text_area(
        "Paste a hotel review",
        height=155,
        placeholder="Example: The room was clean and comfortable, but the check-in was slow."
    )

    analyze = st.button("Get Booking Guidance", use_container_width=True)

    st.markdown("""
    <div class="privacy-note">
        Your text is only used to generate this result. For a better decision, compare several reviews before booking.
    </div>
    """, unsafe_allow_html=True)

with right_col:
    if analyze:
        if review_input.strip() == "":
            st.warning("Please paste a hotel review first.")
            render_empty_state()
        else:
            result = analyze_review_frontend(review_input)
            render_result(result)
    else:
        render_empty_state()

render_footer()