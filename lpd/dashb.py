import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "active_section" not in st.session_state:
    st.session_state.active_section = "Home"

# ------------------ MENU BUTTON ------------------
col1, col2 = st.columns([0.05, 0.95])
with col1:
    if st.button("☰", key="menu_toggle"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* === MENU STYLING === */
.menu-wrapper {
    position: absolute;
    top: 70px;
    left: 15px;
    z-index: 999;
}

.menu-container {
    background-color: #1E1E1E;
    padding: 12px 20px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
    color: white;
    display: flex;
    flex-direction: row;
    gap: 15px;
    overflow: hidden;
    white-space: nowrap;
    transform-origin: left;
    animation: expandRight 0.4s ease-out;
}

.menu-option {
    background: none;
    border: none;
    color: white;
    text-align: center;
    font-size: 16px;
    cursor: pointer;
    transition: color 0.2s, transform 0.2s;
}
.menu-option:hover {
    color: #00BFFF;
    transform: scale(1.05);
}
.active {
    color: #00BFFF;
    font-weight: bold;
}

/* === MENU EXPANSION ANIMATION === */
@keyframes expandRight {
    0% { opacity: 0; transform: scaleX(0); }
    100% { opacity: 1; transform: scaleX(1); }
}

/* === DASHBOARD CONTENT SHIFT === */
.dashboard-content {
    transition: margin-left 0.4s ease;
    margin-left: 0;
}
.dashboard-shifted {
    margin-left: 260px; /* shift when menu is open */
    transition: margin-left 0.4s ease;
}
</style>
""", unsafe_allow_html=True)

# ------------------ MENU SECTION ------------------
if st.session_state.menu_open:
    st.markdown('<div class="menu-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="menu-container">', unsafe_allow_html=True)
    for section in [
        "Home", "Skill Progress", "Course Completion", "Overall Progress",
        "Weekly Trend", "Course Chapters", "Detailed Data"
    ]:
        btn_class = "menu-option active" if st.session_state.active_section == section else "menu-option"
        if st.button(section, key=section, use_container_width=False):
            st.session_state.active_section = section
            st.session_state.menu_open = False  # optional auto-close
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ------------------ DASHBOARD CONTENT ------------------
container_class = "dashboard-shifted" if st.session_state.menu_open else "dashboard-content"
st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)

st.title("🚀 CSE Learning Path Dashboard")

# Example dashboard content
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Courses Enrolled", 8)
with col2:
    st.metric("Courses Completed", 5)
with col3:
    st.metric("Weekly Progress (%)", "74%")

progress = go.Figure(go.Indicator(
    mode="gauge+number",
    value=74,
    title={"text": "Overall Progress"},
    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#00BFFF"}}
))
st.plotly_chart(progress, use_container_width=True)

st.markdown("### 📘 Course Completion Overview")
df = pd.DataFrame({
    "Course": ["Python", "Data Structures", "AI Fundamentals", "Web Dev", "Cybersecurity"],
    "Completion %": [90, 60, 45, 80, 55]
})
st.dataframe(df, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

