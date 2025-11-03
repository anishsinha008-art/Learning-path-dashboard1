import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "show_more_courses" not in st.session_state:
    st.session_state.show_more_courses = False

# ------------------ SIDEBAR MENU ------------------
with st.sidebar:
    st.title("☰ Dashboard Menu")
    st.markdown("Navigate through your learning journey 🚀")
    if st.button("Toggle Menu"):
        st.session_state.menu_open = not st.session_state.menu_open

# ------------------ HEADER ------------------
st.title("🧠 CSE Learning Path Dashboard")
st.markdown("Track your progress, courses, and overall growth in Computer Science!")

# ------------------ OVERALL PROGRESS GAUGE ------------------
st.subheader("🎯 Overall Progress")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=68,
    title={'text': "Total Completion"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#4CAF50"},
        'steps': [
            {'range': [0, 50], 'color': "#f2f2f2"},
            {'range': [50, 100], 'color': "#d9f2e6"}
        ]
    }
))
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# ------------------ COURSE COMPLETION OVERVIEW ------------------
st.subheader("📚 Course Completion Overview")

# --- Top Menu Bar with 3 Main Courses ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 0.8])

with col1:
    st.button("🐍 Python", key="python_btn")
with col2:
    st.button("💻 C++", key="cpp_btn")
with col3:
    st.button("🌐 Web Dev", key="webdev_btn")
with col4:
    if st.button("More Courses ▼" if not st.session_state.show_more_courses else "Hide Courses ▲"):
        st.session_state.show_more_courses = not st.session_state.show_more_courses

# --- Expand Vertically When "More Courses" Clicked ---
if st.session_state.show_more_courses:
    st.markdown("---")
    st.button("🤖 Artificial Intelligence", key="ai_btn")
    st.button("📊 Data Science", key="ds_btn")
    st.button("🧩 Machine Learning", key="ml_btn")
    st.button("🕹️ Game Development", key="gamedev_btn")
    st.button("📱 App Development", key="appdev_btn")
    st.button("⚙️ Data Structures & Algorithms", key="dsa_btn")
    st.button("☁️ Cloud Computing", key="cloud_btn")
    st.button("🔒 Cybersecurity", key="cyber_btn")
    st.markdown("---")

# ------------------ WEEKLY PROGRESS ------------------
st.subheader("📆 Weekly Progress")

weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
progress = [70, 82, 90, 100]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=weeks,
    y=progress,
    text=progress,
    textposition="auto",
    marker_color="#4CAF50"
))
fig2.update_layout(
    title="Weekly Growth Chart",
    xaxis_title="Week",
    yaxis_title="Progress (%)",
    height=400
)
st.plotly_chart(fig2, use_container_width=True)

# ------------------ COURSE COMPLETION TABLE ------------------
st.subheader("📈 Detailed Course Progress")

course_data = {
    "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
    "Completion %": [85, 60, 75, 40, 55, 45, 30],
    "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
}

df = pd.DataFrame(course_data)
st.dataframe(df, use_container_width=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")
