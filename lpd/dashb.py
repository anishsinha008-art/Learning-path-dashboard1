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
@st.cache_data
def load_data():
    data = {
        "Skill": [
            "Python Programming", "Data Structures & Algorithms", "Operating Systems",
            "Database Management Systems", "Computer Networks", "Artificial Intelligence",
            "Machine Learning", "Deep Learning", "Web Development", "Cloud Computing",
            "Cybersecurity", "Software Engineering", "Internet of Things (IoT)",
            "Blockchain Technology", "DevOps"
        ],
        "Progress": [85, 78, 65, 72, 68, 60, 55, 48, 70, 52, 50, 74, 58, 40, 45],
        "Courses Completed": [5, 4, 3, 4, 3, 2, 2, 1, 3, 2, 2, 4, 2, 1, 1],
        "Total Courses": [6, 5, 4, 5, 4, 4, 3, 3, 4, 3, 3, 5, 3, 3, 3]
    }
    df = pd.DataFrame(data)
    df["Completion %"] = (df["Courses Completed"] / df["Total Courses"] * 100).astype(int)
    return df

df = load_data()

# ------------------ SIDEBAR ------------------
with st.sidebar:
    selected_skill = st.selectbox("Select a CSE Skill:", df["Skill"])
    selected_data = df.loc[df["Skill"] == selected_skill].iloc[0]

    st.markdown("### 🎯 Skill Progress")
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

# ------------------ COURSE COMPLETION ------------------
st.subheader("📘 Course Completion Overview")
for _, row in df.iterrows():
    st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} courses completed ({row['Completion %']}%)")
    st.progress(row["Completion %"] / 100)

# ------------------ OVERALL PROGRESS GAUGE (FIXED & CENTERED) ------------------
st.subheader("🌍 Overall Learning Progress")

overall_progress = round(df["Progress"].mean(), 1)

overall_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=overall_progress,
    number={'suffix': "%", 'font': {'size': 40, 'color': "royalblue"}},
    delta={'reference': 75, 'increasing': {'color': "limegreen"}, 'decreasing': {'color': "crimson"}},
    title={'text': "Average Skill Progress", 'font': {'size': 20}},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
        'bar': {'color': "royalblue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 50], 'color': "#ffcccc"},
            {'range': [50, 80], 'color': "#fff3cd"},
            {'range': [80, 100], 'color': "#d4edda"}
        ],
        'threshold': {
            'line': {'color': "blue", 'width': 4},
            'thickness': 0.75,
            'value': overall_progress
        }
    }
))

overall_gauge.update_layout(
    margin=dict(l=20, r=20, t=40, b=20),
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14)
)

col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
with col2:
    st.plotly_chart(overall_gauge, use_container_width=True)

st.caption("Average progress across all CSE skills.")

# ------------------ WEEKLY TREND ------------------
st.subheader(f"📅 Weekly Progress Trend — {selected_skill}")

np.random.seed(abs(hash(selected_skill)) % 10000)
weeks = [f"Week {i}" for i in range(1, 6)]
base = selected_data["Progress"] - 30
weekly_progress = np.clip(base + np.cumsum(np.random.randint(0, 10, size=len(weeks))), 0, 100)

trend_fig = go.Figure(go.Scatter(
    x=weeks, y=weekly_progress,
    mode='lines+markers',
    line=dict(color='mediumseagreen', width=4, shape='spline'),
    fill='tozeroy', fillcolor='rgba(60,179,113,0.2)',
    marker=dict(size=10, color='lightgreen', line=dict(width=2, color='green'))
))
trend_fig.update_layout(
    title=f"✨ {selected_skill} Weekly Growth Trend",
    xaxis_title="Week", yaxis_title="Progress (%)",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14), height=400
)
st.plotly_chart(trend_fig, use_container_width=True)

# ------------------ COURSE FILE DISPLAY ------------------
st.subheader(f"📂 Chapters for {selected_skill}")

filename = f"courses/{selected_skill.lower().replace(' ', '_').replace('&', 'and')}.txt"

if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        st.text_area("Course Chapters", f.read(), height=200)
else:
    st.info(f"ℹ️ Create `{filename}` to add chapters for **{selected_skill}**.")

# ------------------ DATA TABLE ------------------
st.subheader("📊 Detailed Learning Data")
st.dataframe(df, use_container_width=True)
