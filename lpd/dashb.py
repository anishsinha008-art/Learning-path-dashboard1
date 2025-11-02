import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ HEADER ------------------
st.title("💻 CSE Learning Path Dashboard")
st.markdown("Track your Computer Science skills, visualize growth, and open your course chapters interactively.")

# ------------------ DATA ------------------
skills_data = {
    "Skill": [
        "Python Programming",
        "Data Structures & Algorithms",
        "Operating Systems",
        "Database Management Systems",
        "Computer Networks",
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Web Development",
        "Cloud Computing",
        "Cybersecurity",
        "Software Engineering",
        "Internet of Things (IoT)",
        "Blockchain Technology",
        "DevOps"
    ],
    "Progress": [85, 78, 65, 72, 68, 60, 55, 48, 70, 52, 50, 74, 58, 40, 45],
    "Courses Completed": [5, 4, 3, 4, 3, 2, 2, 1, 3, 2, 2, 4, 2, 1, 1],
    "Total Courses": [6, 5, 4, 5, 4, 4, 3, 3, 4, 3, 3, 5, 3, 3, 3]
}
df = pd.DataFrame(skills_data)

# ------------------ SIDEBAR FILTER ------------------
selected_skill = st.sidebar.selectbox("Select a CSE skill to view details:", df["Skill"])
selected_data = df[df["Skill"] == selected_skill].iloc[0]

# ------------------ 1. INDIVIDUAL GAUGE ------------------
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

# ------------------ 2. COURSE COMPLETION ------------------
st.subheader("📘 Course Completion Overview")

for _, row in df.iterrows():
    percent = int((row["Courses Completed"] / row["Total Courses"]) * 100)
    st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} courses completed ({percent}%)")
    st.progress(percent / 100)

# ------------------ 3. OVERALL GAUGE ------------------
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

# ------------------ 4. WEEKLY TREND ------------------
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

# ------------------ 5. COURSE FILE DISPLAY ------------------
st.subheader(f"📂 Chapters for {selected_skill}")

# Convert skill name to lowercase filename
filename = f"courses/{selected_skill.lower()}.txt"
filename = filename.replace(" ", "_").replace("&", "and")

if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    st.text_area("Course Chapters", content, height=200)
else:
    st.warning(f"No course file found for **{selected_skill}**.\n\nCreate a file named `{filename}` to add chapters.")

# ------------------ 6. DATA TABLE ------------------
st.subheader("📊 Detailed Learning Data")
st.dataframe(df, use_container_width=True)
