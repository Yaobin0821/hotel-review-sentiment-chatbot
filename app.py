import streamlit as st
from styles import load_css, render_topbar, render_page_header, render_footer

st.set_page_config(
    page_title="Hotel Review Decision Support Platform",
    page_icon="🏨",
    layout="wide"
)

load_css()
render_topbar()

render_page_header(
    "Hotel Review Decision Support Platform",
    "A traveller-focused web application for hotel review sentiment, risk, suitability, emoji sentiment, and aspect-based review analysis."
)

st.markdown("""
<div class="hero">
    <div class="hero-badge">Traveller Decision-Support Platform</div>
    <h1>Make Better Hotel Decisions from Reviews</h1>
    <p>Explore hotels by area, compare hotel risks, check review sentiment, and understand common complaint areas before booking.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="card">
        <h3>Find Hotels</h3>
        <p>Browse hotels by area and check sentiment summary, main strength, main risk, and traveller suitability.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Finding Hotels", use_container_width=True):
        st.switch_page("pages/1_find_hotels.py")

with c2:
    st.markdown("""
    <div class="card">
        <h3>Compare Hotels</h3>
        <p>Compare two hotels from the same area using sentiment, risk level, suitability, and review evidence.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Compare Hotels", use_container_width=True):
        st.switch_page("pages/3_compare_hotels.py")

with c3:
    st.markdown("""
    <div class="card">
        <h3>Review Checker</h3>
        <p>Paste one hotel review and analyse sentiment, confidence, risk, emoji signals, and hotel aspects.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Check a Review", use_container_width=True):
        st.switch_page("pages/4_review_checker.py")

render_footer()
