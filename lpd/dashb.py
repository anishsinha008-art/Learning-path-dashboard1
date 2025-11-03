import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ FIXED MENU BAR (CSS) ------------------
st.markdown("""
    <style>
        /* Fixed top menu bar */
        .menu-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #262730;
            padding: 12px 25px;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #40414F;
        }
        .menu-title {
            color: white;
            font-size: 22px;
            font-weight: 700;
        }
        .menu-expander {
            background-color: #40414F;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }
        .menu-expander:hover {
            background-color: #5E5F73;
        }
        .main-content {
            margin-top: 90px; /* Push content below fixed bar */
        }
    </style>

    <div class="menu-bar">
        <div class="menu-title">💻 CSE Learning Path Dashboard</div>
        <details>
            <summary class="menu-expander">☰ Menu</summary>
            <div style='background-color:#2B2B39;padding:10px;border-radius:8px;margin-top:10px;'>
                <p style='color:white;font-size:16px;'>Use the options below to customize your view 👇</p>
            </div>
        </details>
    </div>
""", unsafe_allow_html=True)

# ------------------ MENU OPTIONS (placed below menu in Streamlit UI) ------------------
with st.expander("⚙️ Menu Options (Click to Open)", expanded=True):
    theme = st.radio("🎨 Choose Theme", ["Dark", "Light"])

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

    selected_skill = st.selectbox("📚 Select a Skill", df["Skill"])
    st.session_state["selected_skill"] = selected_skill
    st.session_state["theme"] = theme

# Retrieve values
selected_skill = st.session_state.get("selected_skill", "Python Programming")
theme = st.session_state.get("theme", "Dark")

# ------------------ THEME COLORS ------------------
if theme == "Light":
    bg_color = "white"
    text_color = "black"
    template = "plotly_white"
else:
    bg_color = "rgba(0,0,0,0)"
    text_color = "white"
    template = "plotly_dark"

# ------------------ DATAFRAME ------------------
df = pd.DataFrame(skills_data)
selected_data = df[df["Skill"] == selected_skill].iloc[0]

# ------------------ MAIN CONTENT ------------------
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# 1️⃣ Skill Gauge
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

# 2️⃣ Course Completion
st.subheader("📘 Course Completion Overview")
for _, row in df.iterrows():
    percent = int((row["Courses Completed"] / row["Total Courses"]) * 100)
    st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} ({percent}%)")
    st.progress(percent / 100)

# 3️⃣ Overall Gauge
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

# 4️⃣ Weekly Trend
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
    template=template,
    paper_bgcolor=bg_color,
    plot_bgcolor=bg_color,
    font=dict(size=14, color=text_color),
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# 5️⃣ Course File Display & Upload
st.subheader(f"📂 Chapters for {selected_skill}")
filename = f"courses/{selected_skill.lower()}.txt".replace(" ", "_").replace("&", "and")

uploaded_file = st.file_uploader(f"Upload or update chapters for {selected_skill}", type="txt")
if uploaded_file:
    os.makedirs("courses", exist_ok=True)
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded successfully for {selected_skill}!")

if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    st.text_area("Course Chapters", content, height=200)
else:
    st.warning(f"No course file found for **{selected_skill}**.\nUpload `{filename}` to add chapters.")

# 6️⃣ Top Skills
st.subheader("🏆 Top 3 Performing Skills")
st.table(df.nlargest(3, "Progress")[["Skill", "Progress"]])

# 7️⃣ Data Table
st.subheader("📊 Detailed Learning Data")
st.dataframe(df, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
