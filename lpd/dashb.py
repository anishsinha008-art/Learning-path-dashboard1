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
        body {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        [data-testid="stSidebar"] {
            background-color: #111827;
        }
        [data-testid="stSidebarNav"] button {
            background: none !important;
            border: none;
        }
        .css-1d391kg, .css-18e3th9 {
            background-color: #0E1117 !important;
            color: #FFFFFF !important;
        }
        .stButton>button {
            background-color: #1E3A8A;
            color: white;
            border-radius: 10px;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #2563EB;
        }
        .metric-box {
            background-color: #1E293B;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0px 0px 10px #00BFFF33;
        }
        .chat-user {
            background-color: #2563EB;
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: right;
            margin-bottom: 5px;
        }
        .chat-bot {
            background-color: #1E293B;
            color: #E2E8F0;
            padding: 10px;
            border-radius: 10px;
            text-align: left;
            margin-bottom: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ STATE ------------------
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Choose a section:",
    ["🏠 Home", "📚 Courses", "📆 Weekly Progress", "📈 Insights", "🤖 AI Assistant"]
)
st.session_state.page = page

# ------------------ HEADER ------------------
st.title("⚙️ CSE Learning Path Dashboard")
st.markdown("<p style='color:gray;'>Empowering learners to master Computer Science through smart tracking and insights.</p>", unsafe_allow_html=True)

# ------------------ RANDOM DATA GENERATOR ------------------
def random_progress_data():
    return np.random.randint(30, 100, size=7).tolist()

# ------------------ HOME PAGE ------------------
if st.session_state.page == "🏠 Home":
    st.subheader("🎯 Overall Progress")
    overall_progress = np.random.randint(40, 100)
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
        st.markdown(f"<div class='metric-box'><h3>{np.random.randint(3, 8)}</h3><p>Active Courses</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box'><h3>{overall_progress}%</h3><p>Average Progress</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><h3>{np.random.randint(20, 120)} hrs</h3><p>Total Study Time</p></div>", unsafe_allow_html=True)

# ------------------ COURSE PAGE ------------------
elif st.session_state.page == "📚 Courses":
    st.subheader("📘 Course Overview")
    courses = ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"]
    completion = random_progress_data()
    statuses = [
        "✅ Completed" if x > 80 else "🟡 In Progress" if x > 40 else "❌ Not Started"
        for x in completion
    ]
    df = pd.DataFrame({"Course": courses, "Completion %": completion, "Status": statuses})

    try:
        st.dataframe(df.style.background_gradient(cmap="Blues"), use_container_width=True)
    except Exception:
        st.dataframe(df, use_container_width=True)

# ------------------ WEEKLY PROGRESS PAGE ------------------
elif st.session_state.page == "📆 Weekly Progress":
    st.subheader("📅 Weekly Growth")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    progress = np.random.randint(50, 100, size=4)
    fig2 = go.Figure(go.Bar(
        x=weeks,
        y=progress,
        text=progress,
        textposition="auto",
        marker_color="#00BFFF"
    ))
    fig2.update_layout(
        title="Weekly Progress Overview",
        xaxis_title="Weeks",
        yaxis_title="Progress (%)",
        height=400,
        paper_bgcolor="#0E1117",
        font={'color': 'white'}
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ INSIGHTS PAGE ------------------
elif st.session_state.page == "📈 Insights":
    st.subheader("📊 Performance Insights")
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
    st.info("💡 Focus on consistency — your strongest area defines your progress speed!")

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
        responses = {
            "python": "🐍 Use list comprehensions and the standard library to speed up your workflow!",
            "ai": "🤖 Start with basics: Python + NumPy + Pandas + scikit-learn!",
            "web": "🌐 Learn HTML → CSS → JavaScript → React for front-end mastery.",
            "motivate": "💪 Every coder starts small — greatness grows with persistence!"
        }
        for key, val in responses.items():
            if key in msg:
                return val
        return np.random.choice([
            "🚀 Keep going, progress compounds over time!",
            "💬 Want a coding challenge suggestion?",
            "✨ You're doing better than you think!"
        ])

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Assistant typing..."):
            time.sleep(1)
            reply = get_bot_response(user_input)
            st.session_state.chat_history.append(("bot", reply))

    for sender, message in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div class='chat-user'><b>You:</b> {message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'><b>Assistant:</b> {message}</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© 2025 CSE Learning Path Dashboard | Developed by <b>Anish</b></p>", unsafe_allow_html=True)
