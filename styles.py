import streamlit as st

def load_css():
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

    section[data-testid="stSidebar"] {
        display: none !important;
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
        margin-bottom: 16px;
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

    .nav-box {
        background: white;
        border: 1px solid #dbeafe;
        padding: 12px;
        border-radius: 22px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        margin-bottom: 22px;
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

    .card {
        padding: 24px;
        border-radius: 24px;
        background: rgba(255,255,255,0.95);
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        border: 1px solid #e5e7eb;
        margin-bottom: 18px;
        min-height: 190px;
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
    </style>
    """, unsafe_allow_html=True)

def render_topbar():
    st.markdown("""
    <div class="topbar">
        <div class="brand-title">🏨 Hotel Review Decision Support Platform</div>
        <div class="brand-subtitle">A traveller-focused web application for hotel review sentiment, risk, and suitability analysis.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-box">', unsafe_allow_html=True)

    nav_cols = st.columns(5)

    with nav_cols[0]:
        st.page_link("pages/1_find_hotels.py", label="Find Hotels", icon="🏠")

    with nav_cols[1]:
        st.page_link("pages/2_hotel_detail.py", label="Hotel Detail", icon="🏨")

    with nav_cols[2]:
        st.page_link("pages/3_compare_hotels.py", label="Compare", icon="⚖️")

    with nav_cols[3]:
        st.page_link("pages/4_review_checker.py", label="Review Checker", icon="🔍")

    with nav_cols[4]:
        st.page_link("pages/5_improvement_insights.py", label="Insights", icon="📊")

    st.markdown('</div>', unsafe_allow_html=True)

def render_page_header(title, description):
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.divider()
    st.markdown(
        '<p class="footer-note">Hotel Review Decision Support Platform for traveller-focused hotel review analysis.</p>',
        unsafe_allow_html=True
    )
