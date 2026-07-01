import streamlit as st
from styles import load_css, render_topbar, render_footer


st.set_page_config(
    page_title="StayWise KL",
    page_icon="🏨",
    layout="wide"
)


def load_home_css():
    st.markdown("""
    <style>
        .home-hero {
            background:
                linear-gradient(135deg, rgba(255, 253, 248, 0.95), rgba(234, 243, 239, 0.92)),
                radial-gradient(circle at top right, rgba(199, 101, 58, 0.12), transparent 35%);
            border: 1px solid var(--border);
            border-radius: 34px;
            padding: 2.2rem 2.3rem;
            box-shadow: var(--shadow-soft);
            margin-bottom: 1.25rem;
        }

        .home-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: #FFF4E8;
            color: var(--brand-dark);
            border: 1px solid #F2CBAE;
            border-radius: 999px;
            padding: 0.42rem 0.78rem;
            font-size: 0.82rem;
            font-weight: 850;
            margin-bottom: 1rem;
        }

        .home-title {
            font-size: clamp(2.3rem, 5vw, 4.1rem);
            font-weight: 950;
            letter-spacing: -0.075em;
            line-height: 1.02;
            color: var(--text-main);
            max-width: 850px;
            margin-bottom: 0.85rem;
        }

        .home-subtitle {
            color: #475569;
            font-size: 1.08rem;
            line-height: 1.7;
            max-width: 760px;
            margin-bottom: 1.25rem;
        }

        .home-highlight-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }

        .home-highlight {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid #EAD7C6;
            color: #6D4B30;
            border-radius: 999px;
            padding: 0.45rem 0.8rem;
            font-size: 0.86rem;
            font-weight: 750;
        }

        .home-section-title {
            font-size: 1.45rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            color: var(--text-main);
            margin: 1.5rem 0 0.35rem 0;
        }

        .home-section-desc {
            color: #64748B;
            font-size: 0.98rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .home-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 1.35rem;
            box-shadow: var(--shadow-card);
            min-height: 275px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.16s ease, box-shadow 0.16s ease;
        }

        .home-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 18px 38px rgba(74, 55, 40, 0.12);
        }

        .home-card-icon {
            width: 48px;
            height: 48px;
            border-radius: 18px;
            background: #FFF4E8;
            border: 1px solid #F2CBAE;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.45rem;
            margin-bottom: 1rem;
        }

        .home-card-title {
            color: var(--text-main);
            font-size: 1.3rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            margin-bottom: 0.5rem;
        }

        .home-card-text {
            color: #475569;
            font-size: 0.96rem;
            line-height: 1.65;
            margin-bottom: 1.15rem;
        }

        .home-card-link {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, var(--brand), var(--brand-dark));
            color: white !important;
            border-radius: 16px;
            padding: 0.78rem 1rem;
            font-size: 0.95rem;
            font-weight: 850;
            text-decoration: none !important;
            box-shadow: 0 10px 22px rgba(155, 67, 37, 0.20);
        }

        .home-card-link:hover {
            color: white !important;
            filter: brightness(1.03);
        }

        .home-note {
            background: rgba(255, 255, 255, 0.72);
            border: 1px dashed #D8CDBE;
            border-radius: 22px;
            padding: 1rem 1.15rem;
            color: #7C6F64;
            font-size: 0.92rem;
            line-height: 1.6;
            margin-top: 1.2rem;
        }

        @media (max-width: 900px) {
            .home-hero {
                padding: 1.65rem;
            }

            .home-card {
                min-height: auto;
                margin-bottom: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def render_home_card(icon, title, text, button_text, href):
    card_html = (
        '<div class="home-card">'
        '<div>'
        f'<div class="home-card-icon">{icon}</div>'
        f'<div class="home-card-title">{title}</div>'
        f'<div class="home-card-text">{text}</div>'
        '</div>'
        f'<a class="home-card-link" href="{href}" target="_self">{button_text}</a>'
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


load_css()
load_home_css()
render_topbar()

st.markdown("""
<div class="home-hero">
    <div class="home-badge">🏨 Traveller decision support</div>
    <div class="home-title">Make smarter hotel choices from real review signals.</div>
    <div class="home-subtitle">
        StayWise KL helps travellers understand hotel reviews before booking.
        Check hotel strengths, compare risks, and turn long guest comments into simple booking guidance.
    </div>
    <div class="home-highlight-row">
        <span class="home-highlight">Find hotels by area</span>
        <span class="home-highlight">Compare hotel concerns</span>
        <span class="home-highlight">Check one review quickly</span>
        <span class="home-highlight">Understand common complaints</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="home-section-title">What would you like to do?</div>
<div class="home-section-desc">
    Choose one of the tools below based on your booking situation.
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    render_home_card(
        icon="🔎",
        title="Find Hotels",
        text=(
            "Browse hotels by area and see a simple summary of guest sentiment, "
            "main strengths, main concerns, and traveller suitability."
        ),
        button_text="Start Finding Hotels",
        href="/find_hotels"
    )

with c2:
    render_home_card(
        icon="⚖️",
        title="Compare Hotels",
        text=(
            "Compare two hotels side by side so you can quickly understand which one "
            "looks safer, more suitable, or more worth considering."
        ),
        button_text="Compare Hotels",
        href="/compare_hotels"
    )

with c3:
    render_home_card(
        icon="💬",
        title="Review Checker",
        text=(
            "Paste one hotel review and get a booking-friendly summary of what sounds good, "
            "what to watch out for, and whether to compare more reviews."
        ),
        button_text="Check a Review",
        href="/review_checker"
    )

st.markdown("""
<div class="home-note">
    Tip: Hotel reviews are useful, but one review should not decide everything.
    For a better booking decision, compare several reviews and check whether the same concern appears repeatedly.
</div>
""", unsafe_allow_html=True)

render_footer()