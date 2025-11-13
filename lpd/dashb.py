import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ CUSTOM STYLE ------------------
st.markdown("""
<style>
body {background-color:#060b17;color:#e3f2fd;}
.stApp {background: radial-gradient(circle at top left,#08142a,#03050c);}
h1,h2,h3,h4,h5 {color:#00bfff !important;}
.sidebar .sidebar-content {background:linear-gradient(180deg,#001f3f,#000814);}
.stButton>button {background-color:#0d47a1;color:white;border:none;border-radius:10px;transition:0.3s;}
.stButton>button:hover {background-color:#1976d2;transform:scale(1.03);}
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
    st.markdown("Navigate your learning journey 🚀")
    if st.button("🔁 Toggle Menu"):
        st.session_state.menu_open = not st.session_state.menu_open
    st.markdown("---")
    st.write("**Quick Actions:**")
    if st.button("🧠 Refresh Data"):
        st.experimental_rerun()
    st.write("Version: `2.5.0`")

# ------------------ HEADER ------------------
st.title("🧠 CSE Learning Path Dashboard")
st.markdown("Effortlessly visualize your progress and enhance your Computer Science learning path!")

# ------------------ OVERALL PROGRESS GAUGE ------------------
st.subheader("🎯 Overall Progress")
random_progress = random.randint(45, 100)

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=random_progress,
    title={'text': "Total Completion"},
    number={'suffix': "%", 'font': {'size': 36, 'color': "#00bfff"}},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#00bfff"},
        'bgcolor': "#0a0a0a",
        'steps': [
            {'range': [0, 50], 'color': "#111"},
            {'range': [50, 100], 'color': "#1c1f26"}
        ],
    }
))
fig.update_layout(height=300, margin=dict(t=30, b=0))
st.plotly_chart(fig, use_container_width=True)

st.caption(f"⚡ Auto-updated metric: {random_progress}% this session")

# ------------------ COURSE COMPLETION OVERVIEW ------------------
st.subheader("📚 Course Completion Overview")
col1, col2, col3, col4 = st.columns([1, 1, 1, 0.8])

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
    st.markdown("---")
    extra_courses = [
        "🤖 AI", "📊 Data Science", "🧩 ML", "🕹️ Game Dev", "📱 App Dev",
        "⚙️ DSA", "☁️ Cloud", "🔒 Cybersecurity"
    ]
    for course in extra_courses:
        st.button(course)
    st.markdown("---")

# ------------------ WEEKLY PROGRESS ------------------
st.subheader("📆 Weekly Progress")
weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
progress = [random.randint(40, 100) for _ in range(4)]

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=weeks,
    y=progress,
    text=progress,
    textposition="auto",
    marker_color="#00bfff"
))
fig2.update_layout(
    title="Weekly Growth Chart",
    xaxis_title="Week",
    yaxis_title="Progress (%)",
    height=400,
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e3f2fd")
)
st.plotly_chart(fig2, use_container_width=True)

# ------------------ COURSE COMPLETION TABLE ------------------
st.subheader("📈 Detailed Course Progress")
course_data = {
    "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
    "Completion %": [random.randint(30, 100) for _ in range(7)],
    "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
}
df = pd.DataFrame(course_data)
st.dataframe(df.style.background_gradient(cmap="Blues"), use_container_width=True)

# ------------------ CHATBOT SECTION ------------------
st.markdown("---")
st.subheader("🤖 AI Chat Assistant")
st.caption("Ask anything — from coding help to motivation or AI insights!")

cols = st.columns(4)
if cols[0].button("💪 Motivate Me"):
    st.session_state.chat_history.append(("user", "motivate me"))
if cols[1].button("🐍 Python Tip"):
    st.session_state.chat_history.append(("user", "python tip"))
if cols[2].button("🧠 AI Info"):
    st.session_state.chat_history.append(("user", "tell me about AI"))
if cols[3].button("🌐 Web Help"):
    st.session_state.chat_history.append(("user", "help with web dev"))

user_input = st.chat_input("Type your message here...")

# --- Chatbot Logic ---
def get_bot_response(message, history):
    message = message.lower()
    motivational_quotes = [
        "🚀 Greatness is built on consistency — keep going!",
        "🌟 Every bug fixed is a victory for your logic!",
        "🔥 The code may fail, but you never do when you try again.",
        "💻 The best way to learn is to build — start something today!"
    ]
    python_tips = [
        "🐍 Use f-strings for cleaner output formatting!",
        "💡 `enumerate()` and `zip()` are Python power tools — learn them!",
        "📘 The `collections` module is full of useful data structures!"
    ]

    if "python" in message:
        return np.random.choice(python_tips)
    elif "motivate" in message or "inspire" in message:
        return np.random.choice(motivational_quotes)
    elif "web" in message:
        return "🌐 Learn HTML/CSS, then move to JS frameworks like React."
    elif "ai" in message or "ml" in message:
        return "🤖 AI starts with math + Python. Explore TensorFlow and scikit-learn!"
    elif "data" in message:
        return "📊 Data Science thrives on Pandas and visualization — practice with Kaggle!"
    elif "hello" in message:
        return "👋 Hello, future innovator! What are we learning today?"
    else:
        if history and "ai" in history[-1][1].lower():
            return "🧠 The secret to mastering AI is understanding data first."
        else:
            return np.random.choice([
                "💬 That's interesting! Want me to suggest a project?",
                "🤔 Tell me more about what you’re working on.",
                "⚙️ Every concept connects — shall I explain one?",
            ])

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Assistant is thinking..."):
        time.sleep(np.random.uniform(0.6, 1.2))
        bot_reply = get_bot_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append(("bot", bot_reply))

# --- Display Chat ---
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div style='background:#1a2a3a; color:#fff; padding:10px; border-radius:10px; margin:5px 0; text-align:right'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#101820; color:#00bfff; padding:10px; border-radius:10px; margin:5px 0'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("<center>Developed by <b>Anish</b> | © 2025 CSE Learning Path Dashboard v2.5</center>", unsafe_allow_html=True)
