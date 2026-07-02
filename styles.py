import streamlit as st
from textwrap import dedent


def load_css():
    st.markdown(
        dedent("""
        <style>
            :root {
                --bg-main: #F7F3EC;
                --bg-card: #FFFFFF;
                --text-main: #172033;
                --text-muted: #6B7280;
                --brand: #C7653A;
                --brand-dark: #9B4325;
                --sage: #52796F;
                --sage-light: #EAF3EF;
                --sand: #F2E3D0;
                --cream: #FFFDF8;
                --border: #E7DDD0;
                --green: #2F855A;
                --green-bg: #EAF7F0;
                --amber: #B7791F;
                --amber-bg: #FFF4D6;
                --red: #C24136;
                --red-bg: #FFF0EE;
                --shadow-soft: 0 18px 45px rgba(74, 55, 40, 0.08);
                --shadow-card: 0 10px 28px rgba(74, 55, 40, 0.07);
                --radius-xl: 28px;
                --radius-lg: 22px;
                --radius-md: 16px;
            }

            html, body, [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at top left, rgba(199, 101, 58, 0.10), transparent 28%),
                    radial-gradient(circle at top right, rgba(82, 121, 111, 0.10), transparent 26%),
                    var(--bg-main);
                color: var(--text-main);
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            /* Hide Streamlit default menu / toolbar / setting area */
            [data-testid="stToolbar"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }

            [data-testid="stDecoration"] {
                display: none !important;
                visibility: hidden !important;
            }

            [data-testid="stStatusWidget"] {
                display: none !important;
                visibility: hidden !important;
            }

            #MainMenu {
                visibility: hidden !important;
                display: none !important;
            }

            footer {
                visibility: hidden !important;
                display: none !important;
            }

            header {
                visibility: hidden !important;
                height: 0 !important;
            }

            /* Hide Streamlit default sidebar navigation */
            section[data-testid="stSidebar"] {
                display: none !important;
                visibility: hidden !important;
            }

            div[data-testid="collapsedControl"] {
                display: none !important;
                visibility: hidden !important;
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.3rem;
                padding-bottom: 2.2rem;
            }

            h1, h2, h3, h4 {
                color: var(--text-main);
                letter-spacing: -0.03em;
            }

            p {
                color: #334155;
                line-height: 1.65;
            }

            a {
                text-decoration: none;
            }

            .app-shell {
                max-width: 1180px;
                margin: 0 auto 1rem auto;
            }

            .brand-card {
                background: rgba(255, 255, 255, 0.86);
                backdrop-filter: blur(14px);
                border: 1px solid var(--border);
                border-radius: 28px;
                padding: 1.15rem 1.35rem;
                box-shadow: var(--shadow-soft);
                margin-bottom: 0.85rem;
            }

            .brand-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                flex-wrap: wrap;
            }

            .brand-left {
                display: flex;
                align-items: center;
                gap: 0.85rem;
            }

            .brand-logo {
                width: 46px;
                height: 46px;
                border-radius: 16px;
                background: linear-gradient(135deg, #C7653A, #E6A15F);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.45rem;
                box-shadow: 0 12px 26px rgba(199, 101, 58, 0.25);
            }

            .brand-title {
                font-size: 1.35rem;
                font-weight: 850;
                color: var(--text-main);
                line-height: 1.15;
            }

            .brand-subtitle {
                color: var(--text-muted);
                font-size: 0.92rem;
                margin-top: 0.25rem;
            }

            .brand-pill {
                background: var(--sage-light);
                color: var(--sage);
                border: 1px solid #CFE2DA;
                border-radius: 999px;
                padding: 0.5rem 0.8rem;
                font-size: 0.83rem;
                font-weight: 750;
            }

            .nav-card {
                background: rgba(255, 255, 255, 0.76);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.48rem;
                box-shadow: 0 8px 24px rgba(74, 55, 40, 0.055);
                margin-bottom: 1.1rem;
                overflow-x: auto;
                white-space: nowrap;
            }

            .nav-row {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.35rem;
            }

            .nav-link {
                display: inline-flex;
                align-items: center;
                gap: 0.42rem;
                color: #5F6B7A;
                padding: 0.62rem 1rem;
                border-radius: 999px;
                font-weight: 720;
                font-size: 0.92rem;
                transition: all 0.16s ease;
            }

            .nav-link:hover {
                background: #FFF7EF;
                color: var(--brand-dark);
            }

            .page-hero {
                background: rgba(255, 255, 255, 0.86);
                border: 1px solid var(--border);
                border-radius: 30px;
                padding: 1.65rem 1.75rem;
                box-shadow: var(--shadow-soft);
                margin-bottom: 1.15rem;
            }

            .page-kicker {
                display: inline-flex;
                align-items: center;
                gap: 0.42rem;
                background: #FFF4E8;
                color: var(--brand-dark);
                border: 1px solid #F2CBAE;
                border-radius: 999px;
                padding: 0.38rem 0.72rem;
                font-size: 0.8rem;
                font-weight: 800;
                margin-bottom: 0.85rem;
            }

            .page-title {
                font-size: clamp(2rem, 4vw, 3rem);
                font-weight: 900;
                letter-spacing: -0.06em;
                color: var(--text-main);
                line-height: 1.05;
                margin-bottom: 0.6rem;
            }

            .page-desc {
                max-width: 760px;
                font-size: 1.02rem;
                color: #475569;
                line-height: 1.65;
            }

            .soft-card {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid var(--border);
                border-radius: var(--radius-lg);
                padding: 1.2rem;
                box-shadow: var(--shadow-card);
            }

            .section-title {
                font-size: 1.18rem;
                font-weight: 850;
                color: var(--text-main);
                margin-bottom: 0.45rem;
            }

            .section-muted {
                color: var(--text-muted);
                font-size: 0.93rem;
                line-height: 1.55;
            }

            .footer-card {
                color: #7C6F64;
                font-size: 0.85rem;
                text-align: center;
                padding: 1.2rem 0 0.4rem 0;
                margin-top: 1.2rem;
                border-top: 1px solid rgba(120, 105, 90, 0.18);
            }

            div[data-testid="stTextArea"] label {
                color: var(--text-main);
                font-weight: 750;
            }

            div[data-testid="stTextArea"] textarea {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid #D8CDBE;
                border-radius: 20px;
                color: var(--text-main);
                font-size: 1rem;
                line-height: 1.55;
                box-shadow: inset 0 2px 8px rgba(74, 55, 40, 0.03);
            }

            div[data-testid="stTextArea"] textarea:focus {
                border-color: var(--brand);
                box-shadow: 0 0 0 3px rgba(199, 101, 58, 0.12);
            }

            div[data-testid="stButton"] button {
                border-radius: 18px;
                height: 3.1rem;
                font-weight: 850;
                font-size: 1rem;
                color: #FFFFFF !important;
                background: linear-gradient(135deg, var(--brand), var(--brand-dark)) !important;
                border: none !important;
                box-shadow: 0 12px 24px rgba(155, 67, 37, 0.22);
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }

            div[data-testid="stButton"] button:hover {
                transform: translateY(-1px);
                box-shadow: 0 16px 30px rgba(155, 67, 37, 0.28);
            }

            div[data-testid="stButton"] button p {
                color: #FFFFFF !important;
                font-weight: 850;
            }

            .stDataFrame {
                border-radius: 18px;
                overflow: hidden;
            }

            div[data-testid="stExpander"] {
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid var(--border);
                border-radius: 18px;
                box-shadow: 0 8px 24px rgba(74, 55, 40, 0.04);
            }

            div[data-testid="stExpander"] details summary {
                font-weight: 780;
                color: var(--text-main);
            }

            @media (max-width: 720px) {
                .brand-row {
                    align-items: flex-start;
                }

                .brand-pill {
                    display: none;
                }

                .nav-row {
                    justify-content: flex-start;
                }

                .page-hero {
                    padding: 1.3rem;
                }
            }
        </style>
        """),
        unsafe_allow_html=True
    )


def render_topbar():
    import streamlit as st

    st.markdown(
        """
        <style>
            /* Remove the extra Streamlit gap around the topbar */
            div[data-testid="stHorizontalBlock"]:has(.topbar-brand-display) {
                background: rgba(255, 252, 247, 0.96);
                backdrop-filter: blur(14px);
                border: 1px solid var(--border, #E7DDD0);
                border-radius: 26px;
                box-shadow: var(--shadow-card, 0 10px 28px rgba(74, 55, 40, 0.07));
                padding: 0.75rem 1rem;
                margin: 0 auto 1rem auto;
                align-items: center;
            }

            .topbar-brand-display {
                display: flex;
                align-items: center;
                gap: 0.55rem;
                color: var(--text-main, #172033);
                font-weight: 950;
                font-size: 1.05rem;
                letter-spacing: -0.04em;
                white-space: nowrap;
                min-height: 38px;
            }

            .topbar-logo-display {
                width: 38px;
                height: 38px;
                border-radius: 14px;
                background: linear-gradient(135deg, var(--brand, #C7653A), var(--brand-dark, #9B4325));
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.05rem;
                box-shadow: 0 8px 18px rgba(155, 67, 37, 0.18);
            }

            div[data-testid="stPageLink"] {
                width: fit-content !important;
            }

            div[data-testid="stPageLink"] a {
                text-decoration: none !important;
                color: #5F5148 !important;
                font-size: 0.82rem !important;
                font-weight: 850 !important;
                padding: 0.5rem 0.7rem !important;
                border-radius: 999px !important;
                transition: all 0.16s ease !important;
                white-space: nowrap !important;
                min-height: 38px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                background: transparent !important;
            }

            div[data-testid="stPageLink"] a:hover {
                background: #FFF4E8 !important;
                color: var(--brand-dark, #9B4325) !important;
            }

            div[data-testid="stPageLink"] p {
                font-size: 0.82rem !important;
                font-weight: 850 !important;
                margin: 0 !important;
                color: inherit !important;
                white-space: nowrap !important;
            }

            div[data-testid="stPageLink"] svg {
                display: none !important;
            }

            .staff-link-wrap {
                background: #EAF7F0;
                border: 1px solid #BFE3CF;
                border-radius: 999px;
                min-height: 38px;
                padding: 0 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
                width: fit-content;
            }

            .staff-link-wrap div[data-testid="stPageLink"] a {
                color: #216E46 !important;
                background: transparent !important;
                padding: 0 !important;
                min-height: auto !important;
                font-weight: 900 !important;
            }

            .staff-link-wrap div[data-testid="stPageLink"] a:hover {
                background: transparent !important;
                color: #1D5F3E !important;
            }

            @media (max-width: 900px) {
                div[data-testid="stHorizontalBlock"]:has(.topbar-brand-display) {
                    border-radius: 22px;
                    padding: 0.75rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    (
        brand_col,
        home_col,
        find_col,
        detail_col,
        compare_col,
        review_col,
        insights_col,
        staff_col
    ) = st.columns(
        [1.75, 0.65, 0.95, 1.05, 0.75, 1.25, 1.05, 1.25],
        gap="small"
    )

    with brand_col:
        st.markdown(
            """
            <div class="topbar-brand-display">
                <div class="topbar-logo-display">🏨</div>
                <span>StayWise KL</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with home_col:
        st.page_link("app.py", label="Home")

    with find_col:
        st.page_link("pages/1_find_hotels.py", label="Find Hotels")

    with detail_col:
        st.page_link("pages/2_hotel_detail.py", label="Hotel Detail")

    with compare_col:
        st.page_link("pages/3_compare_hotels.py", label="Compare")

    with review_col:
        st.page_link("pages/4_review_checker.py", label="Review Checker")

    with insights_col:
        st.page_link("pages/5_improvement_insights.py", label="Area Insights")

    with staff_col:
        st.markdown('<div class="staff-link-wrap">', unsafe_allow_html=True)
        st.page_link("pages/6_management_insights.py", label="Staff Portal 🔒")
        st.markdown('</div>', unsafe_allow_html=True)


def render_page_header(title, subtitle):
    st.markdown(
        dedent(f"""
        <div class="page-hero">
            <div class="page-kicker">Travel decision support</div>
            <div class="page-title">{title}</div>
            <div class="page-desc">{subtitle}</div>
        </div>
        """),
        unsafe_allow_html=True
    )


def render_footer():
    st.markdown(
        dedent("""
        <div class="footer-card">
            StayWise KL helps travellers understand hotel review signals before making a booking decision.
        </div>
        """),
        unsafe_allow_html=True
    )