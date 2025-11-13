# CSE Learning Path Dashboard
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ DARK THEME CSS ------------------
st.markdown("""
    <style>
        body { background-color: #0E1117; color: #FFFFFF; }
        [data-testid="stAppViewContainer"] { background-color: #0E1117; color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #111827; }
        .stButton>button {
            background-color: #1E3A8A; color: white; border-radius: 10px; border: none; transition: 0.3s;
        }
        .stButton>button:hover { background-color: #2563EB; }
        .metric-box {
            background-color: #1E293B; border-radius: 10px; padding: 15px; text-align: center;
            box-shadow: 0px 0px 10px #00BFFF33;
        }
        .chat-user {
            background-color: #2563EB; color: white; padding: 10px; border-radius: 10px;
            text-align: right; margin-bottom: 5px;
        }
        .chat-bot {
            background-color: #1E293B; color: #E2E8F0; padding: 10px; border-radius: 10px;
            text-align: left; margin-bottom: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ STATE ------------------
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "course_data" not in st.session_state:
    st.session_state.course_data = pd.DataFrame({
        "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
        "Completion %": [45, 70, 20, 85, 60, 30, 90]
    })
if "weekly_hours" not in st.session_state:
    st.session_state.weekly_hours = {"Week 1": 0, "Week 2": 0, "Week 3": 0, "Week 4": 0}

# ------------------ SIDEBAR ------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Choose a section:", ["🏠 Home", "📚 Courses", "📆 Weekly Progress", "📈 Insights", "🤖 AI Assistant"])
st.session_state.page = page

theme = st.sidebar.selectbox("Theme", ["🌙 Dark", "☀️ Light"])
if theme == "☀️ Light":
    st.markdown("<style>body{background-color:white;color:black;}</style>", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.title("⚙️ CSE Learning Path Dashboard")
st.markdown("<p style='color:gray;'>Empowering learners to master Computer Science through smart tracking and insights.</p>", unsafe_allow_html=True)

# ------------------ HOME PAGE ------------------
if st.session_state.page == "🏠 Home":
    st.subheader("🎯 Overall Progress")
    overall_progress = st.session_state.course_data["Completion %"].mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_progress,
        title={'text': "Total Completion"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00BFFF"},
            'steps': [
                {'range': [0, 50], 'color': "#222"},
                {'range': [50, 100], 'color': "#1E3A8A"}
            ]
        }
    ))
    fig.update_layout(paper_bgcolor="#0E1117", font={'color': 'white'}, height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🚀 Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><h3>{len(st.session_state.course_data)}</h3><p>Active Courses</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><h3>{int(overall_progress)}%</h3><p>Average Progress</p></div>", unsafe_allow_html=True)
    with col3:
        total_hours = sum(st.session_state.weekly_hours.values())
        st.markdown(f"<div class='metric-box'><h3>{total_hours} hrs</h3><p>Total Study Time</p></div>", unsafe_allow_html=True)

# ------------------ COURSE PAGE ------------------
elif st.session_state.page == "📚 Courses":
    st.subheader("📘 Update Your Progress")
    for i, row in st.session_state.course_data.iterrows():
        new_val = st.slider(f"{row['Course']} Progress", 0, 100, int(row["Completion %"]))
        st.session_state.course_data.at[i, "Completion %"] = new_val
        st.progress(new_val)

    st.download_button("📥 Export Progress (CSV)", st.session_state.course_data.to_csv(index=False).encode("utf-8"), "progress.csv", "text/csv")

# ------------------ WEEKLY PROGRESS PAGE ------------------
elif st.session_state.page == "📆 Weekly Progress":
    st.subheader("📅 Log Weekly Study Time")
    week_input = st.selectbox("Select Week", list(st.session_state.weekly_hours.keys()))
    hours = st.number_input("Hours Studied", min_value=0, max_value=100)
    if st.button("Log Hours"):
        st.session_state.weekly_hours[week_input] = hours
        st.success(f"{hours} hours logged for {week_input}!")

    st.subheader("📊 Weekly Overview")
    fig2 = go.Figure(go.Bar(
        x=list(st.session_state.weekly_hours.keys()),
        y=list(st.session_state.weekly_hours.values()),
        text=list(st.session_state.weekly_hours.values()),
        textposition="auto",
        marker_color="#00BFFF"
    ))
    fig2.update_layout(
        title="Weekly Study Hours",
        xaxis_title="Weeks",
        yaxis_title="Hours",
        height=400,
        paper_bgcolor="#0E1117",
        font={'color': 'white'}
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ INSIGHTS PAGE ------------------
elif st.session_state.page == "📈 Insights":
    st.subheader("📊 Completion Forecast")
    avg_daily_hours = st.slider("Average Daily Study Hours", 1, 10, 2)
    overall_progress = st.session_state.course_data["Completion %"].mean()
    remaining = 100 - overall_progress
    days_left = int(remaining / (avg_daily_hours * 2))
    st.info(f"📅 Estimated {days_left} days to complete your learning path.")

    st.subheader("📈 Performance Insights")
    categories = ["Coding", "Theory", "Projects", "Assignments", "Revisions"]
    scores = np.random.randint(40, 100, size=5)
    fig3 = go.Figure(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        marker_color="#00BFFF"
    ))
    fig3.update_layout(
        polar=dict(
            bgcolor="#0E1117",
            radialaxis=dict(visible=True, range=[0, 100], color="gray")
        ),
        paper_bgcolor="#0E1117",
        font={'color': 'white'},
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    best_area = categories[np.argmax(scores)]
    st.success(f"🏆 Your strongest area is **{best_area}** — keep it up!")

# ------------------ AI CHAT ASSISTANT PAGE ------------------
elif st.session_state.page == "🤖 AI Assistant":
    st.subheader("🤖 Smart Study Assistant")
    st.markdown("<p style='color:gray;'>Ask anything about coding, AI, or motivation.</p>", unsafe_allow_html=True)

    quicks = st.columns(4)
    if quicks[0].button("💪 Motivate Me"):
        st.session_state.chat_history.append(("user", "motivate me"))
    if quicks[1].button("🐍 Python Tip"):
        st.session_state.chat_history.append(("user", "python tip"))
    if quicks[2].button("🧠 AI Info"):
        st.session_state.chat_history.append(("user", "tell me about AI"))
    if quicks[3].button("🌐 Web Help"):
        st.session_state.chat_history.append(("user", "help with web dev"))

    user_input = st.chat_input("💬 Type your message here...")

    def get_bot_response(msg):
        msg = msg.lower()
        if "challenge" in msg:
            return "🧩 Try building a simple calculator in Python using functions and loops!"
        elif "career
