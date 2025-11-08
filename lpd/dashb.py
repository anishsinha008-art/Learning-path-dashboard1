import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
    body {
        background-color: #f7f9fc;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stChat {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.1);
        padding: 10px;
    }
    .chat-bubble-user {
        background-color: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 15px 15px 0px 15px;
        margin: 4px;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .chat-bubble-bot {
        background-color: #e8f5e9;
        color: black;
        padding: 8px 12px;
        border-radius: 15px 15px 15px 0px;
        margin: 4px;
        max-width: 80%;
        float: left;
        clear: both;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "show_more_courses" not in st.session_state:
    st.session_state.show_more_courses = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ SIDEBAR MENU ------------------
with st.sidebar:
    st.title("☰ Dashboard Menu")
    st.markdown("Navigate through your learning journey 🚀")
    if st.button("Toggle Menu"):
        st.session_state.menu_open = not st.session_state.menu_open
    if st.session_state.menu_open:
        st.markdown("### 📂 Sections")
        st.markdown("- 🧠 Overview")
        st.markdown("- 📚 Courses")
        st.markdown("- 📆 Weekly Progress")
        st.markdown("- 💬 Chat Assistant")

# ------------------ HEADER ------------------
st.title("🧠 CSE Learning Path Dashboard")
st.markdown("Track your progress, courses, and overall growth in Computer Science!")

# ------------------ METRICS SECTION ------------------
st.markdown("### 🔍 Quick Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Courses Enrolled", 8, "+2 this month")
with col2:
    st.metric("Average Progress", "68%", "+8% vs last month")
with col3:
    st.metric("Projects Completed", 5, "+1 recent")

# ------------------ OVERALL PROGRESS GAUGE ------------------
st.subheader("🎯 Overall Progress")

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=68,
    delta={'reference': 55, 'increasing': {'color': "#4CAF50"}},
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
fig.update_layout(height=280, margin=dict(t=0, b=0))
st.plotly_chart(fig, use_container_width=True)

# ------------------ COURSE COMPLETION OVERVIEW ------------------
st.subheader("📚 Course Completion Overview")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.button("🐍 Python", key="python_btn")
with col2:
    st.button("💻 C++", key="cpp_btn")
with col3:
    st.button("🌐 Web Dev", key="webdev_btn")
with col4:
    if st.button("More ▼" if not st.session_state.show_more_courses else "Hide ▲"):
        st.session_state.show_more_courses = not st.session_state.show_more_courses

if st.session_state.show_more_courses:
    with st.expander("🎓 Additional Courses", expanded=True):
        cols = st.columns(4)
        courses = [
            "🤖 Artificial Intelligence",
            "📊 Data Science",
            "🧩 Machine Learning",
            "🕹️ Game Development",
            "📱 App Development",
            "⚙️ DSA",
            "☁️ Cloud Computing",
            "🔒 Cybersecurity"
        ]
        for i, course in enumerate(courses):
            with cols[i % 4]:
                st.button(course)

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
    marker=dict(color=progress, colorscale="Greens")
))
fig2.update_layout(
    title="Weekly Growth Trend",
    xaxis_title="Week",
    yaxis_title="Progress (%)",
    height=400,
    template="plotly_white"
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
st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)

# ------------------ INSPIRATION QUOTE ------------------
st.markdown("### 💬 Daily Motivation")
quote = np.random.choice([
    "“Code is like humor. When you have to explain it, it’s bad.” – Cory House",
    "“The only way to learn a new programming language is by writing programs in it.” – Dennis Ritchie",
    "“Great things are done by a series of small things brought together.” – Vincent Van Gogh",
    "“Stay curious, keep learning, and never stop growing.”"
])
st.success(quote)

# ------------------ CHATBOT SECTION ------------------
st.markdown("---")
st.subheader("🤖 AI Chat Assistant")

st.markdown(
    "<p style='color:gray;'>Ask me about programming, motivation, or your course progress!</p>",
    unsafe_allow_html=True,
)

user_input = st.chat_input("Type your message here...")

# Chatbot logic
def get_bot_response(message):
    message = message.lower()
    responses = {
        "python": "Python is a great language to start with! Focus on basics like loops, functions, and lists first.",
        "c++": "C++ helps you build logic and memory management skills — keep practicing coding problems.",
        "ai": "AI is the future! Start with Python, then explore neural networks using libraries like TensorFlow or PyTorch.",
        "motivate": "Remember, consistency beats intensity. Keep coding every day — even for 30 minutes!",
        "web": "Web development opens up creative possibilities — learn HTML, CSS, and JavaScript first.",
    }
    for key in responses:
        if key in message:
            return responses[key]
    # Default generic reply
    return random.choice([
        "That's interesting! Tell me more 🤔",
        "I'm here to help you learn and grow 🚀",
        "Can you elaborate a bit more?",
        "Sounds like you’re making progress! 💪",
        "Hmm… let’s explore that topic together."
    ])

# Handle chat interaction
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Thinking..."):
        time.sleep(0.6)
        bot_reply = get_bot_response(user_input)
        st.session_state.chat_history.append(("bot", bot_reply))

# Display chat history
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='chat-bubble-user'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'>{msg}</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("<p style='text-align:center;'>Developed by <b>Anish</b> | CSE Learning Path Dashboard © 2025 🚀</p>", unsafe_allow_html=True)
