import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
.menu-container {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 9999;
}
.sidebar-menu {
    position: fixed;
    top: 60px;
    left: 0;
    width: 280px;
    height: 100%;
    background-color: #1E1E1E;
    color: white;
    padding: 20px;
    box-shadow: 4px 0 15px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
    transform: translateX(-100%);
    border-radius: 0 10px 10px 0;
}
.sidebar-menu.show {
    transform: translateX(0);
}
.sidebar-menu h3 {
    color: #00BFFF;
    border-bottom: 1px solid #333;
    padding-bottom: 10px;
}
.menu-item {
    margin: 15px 0;
    font-size: 16px;
    cursor: pointer;
}
.menu-item:hover {
    color: #00BFFF;
}
</style>
""", unsafe_allow_html=True)

# ------------------ MENU TOGGLE ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# Hamburger menu button
col1, col2 = st.columns([0.05, 0.95])
with col1:
    if st.button("☰"):
        st.session_state.menu_open = not st.session_state.menu_open

# ------------------ MENU BAR CONTENT ------------------
menu_class = "sidebar-menu show" if st.session_state.menu_open else "sidebar-menu"
st.markdown(f"""
<div class="{menu_class}">
    <h3>📚 Menu</h3>
    <div class="menu-item" onclick="window.location.reload()">🏠 Home</div>
    <div class="menu-item">🎯 Skill Progress</div>
    <div class="menu-item">📘 Course Completion</div>
    <div class="menu-item">🌍 Overall Progress</div>
    <div class="menu-item">📅 Weekly Trend</div>
    <div class="menu-item">📂 Course Chapters</div>
    <div class="menu-item">📊 Detailed Data</div>
</div>
""", unsafe_allow_html=True)

# ------------------ DASHBOARD CONTENT ------------------
st.title("💻 CSE Learning Path Dashboard")
st.markdown("Track your Computer Science skills, visualize growth, and open your course chapters interactively.")

skills_data = {
    "Skill": [
        "Python Programming", "Data Structures & Algorithms", "Operating Systems", "Database Management Systems",
        "Computer Networks", "Artificial Intelligence", "Machine Learning", "Deep Learning", "Web Development",
        "Cloud Computing", "Cybersecurity", "Software Engineering", "Internet of Things (IoT)",
        "Blockchain Technology", "DevOps"
    ],
    "Progress": [85, 78, 65, 72, 68, 60, 55, 48, 70, 52, 50, 74, 58, 40, 45],
    "Courses Completed": [5, 4, 3, 4, 3, 2, 2, 1, 3, 2, 2, 4, 2, 1, 1],
    "Total Courses": [6, 5, 4, 5, 4, 4, 3, 3, 4, 3, 3, 5, 3, 3, 3]
}
df = pd.DataFrame(skills_data)

selected_skill = st.selectbox("Select a CSE skill to view details:", df["Skill"])
selected_data = df[df["Skill"] == selected_skill].iloc[0]

# ---- 1. Skill Progress Gauge ----
st.subheader(f"🎯 Skill Progress: {selected_skill}")
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_data["Progress"],
    title={'text': f"{selected_skill} Progress"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "mediumseagreen"},
        'steps': [
            {'range': [0, 50], 'color': "#ffcccc"},
            {'range': [50, 80], 'color': "#fff3cd"},
            {'range': [80, 100], 'color': "#d4edda"}
        ]
    }
))
st.plotly_chart(gauge, use_container_width=True)

# ---- 2. Course Completion ----
st.subheader("📘 Course Completion Overview")
for _, row in df.iterrows():
    percent = int((row["Courses Completed"] / row["Total Courses"]) * 100)
    st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} courses completed ({percent}%)")
    st.progress(percent / 100)

# ---- 3. Overall Gauge ----
st.subheader("🌍 Overall Learning Progress")
overall_progress = df["Progress"].mean()
overall_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_progress,
    title={'text': "Average Skill Progress"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "royalblue"},
        'steps': [
            {'range': [0, 50], 'color': "#ffcccc"},
            {'range': [50, 80], 'color': "#fff3cd"},
            {'range': [80, 100], 'color': "#d4edda"}
        ]
    }
))
st.plotly_chart(overall_gauge, use_container_width=True)

# ---- 4. Weekly Progress ----
st.subheader(f"📅 Weekly Progress Trend — {selected_skill}")
np.random.seed(hash(selected_skill) % 100000)
weeks = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
base = selected_data["Progress"] - 30
weekly_progress = np.clip(base + np.cumsum(np.random.randint(0, 10, size=len(weeks))), 0, 100)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=weeks,
    y=weekly_progress,
    mode='lines+markers',
    line=dict(color='mediumseagreen', width=4, shape='spline'),
    fill='tozeroy',
    fillcolor='rgba(60,179,113,0.2)',
    marker=dict(size=10, color='lightgreen', line=dict(width=2, color='green')),
))
fig.update_layout(
    title=f"✨ {selected_skill} Weekly Growth Trend",
    xaxis_title="Week",
    yaxis_title="Progress (%)",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14),
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# ---- 5. Course Chapters ----
st.subheader(f"📂 Chapters for {selected_skill}")
filename = f"courses/{selected_skill.lower().replace(' ', '_').replace('&', 'and')}.txt"

if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    st.text_area("Course Chapters", content, height=200)
else:
    st.warning(f"No course file found for **{selected_skill}**.\n\nCreate a file named `{filename}` to add chapters.")

# ---- 6. Data Table ----
st.subheader("📊 Detailed Learning Data")
st.dataframe(df, use_container_width=True)
