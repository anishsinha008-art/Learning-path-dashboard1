import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "show_more_courses" not in st.session_state:
    st.session_state.show_more_courses = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

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

if st.session_state.show_more_courses:
    st.markdown("---")
    extra_courses = [
        "🤖 Artificial Intelligence", "📊 Data Science", "🧩 Machine Learning",
        "🕹️ Game Development", "📱 App Development",
        "⚙️ Data Structures & Algorithms", "☁️ Cloud Computing", "🔒 Cybersecurity"
    ]
    for course in extra_courses:
        st.button(course)
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

try:
    st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)
except ImportError:
    st.warning("Matplotlib not found — showing plain table instead.")
    st.dataframe(df, use_container_width=True)

# ------------------ FLOATING CHATBOT SECTION ------------------
chat_toggle = st.button("💬 Open AI Assistant")

if chat_toggle:
    st.session_state.show_chat = not st.session_state.show_chat

if st.session_state.show_chat:
    # --- Chat Styles ---
    st.markdown("""
    <style>
    .chat-float {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 360px;
        background: rgba(250,250,250,0.98);
        border-radius: 16px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
        z-index: 9999;
        padding: 0;
        overflow: hidden;
    }
    .chat-header {
        font-weight: 600;
        font-size: 18px;
        color: white;
        background: linear-gradient(135deg, #4A00E0, #8E2DE2);
        padding: 10px;
        text-align: center;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 10px;
        background: #F7F9FB;
        max-height: 300px;
        overflow-y: auto;
    }
    .chat-bubble-user {
        background: linear-gradient(135deg, #4CAF50, #81C784);
        color: white;
        padding: 10px 14px;
        border-radius: 18px;
        margin: 6px 0;
        max-width: 75%;
        text-align: right;
        align-self: flex-end;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
    }
    .chat-bubble-bot {
        background: linear-gradient(135deg, #2C3E50, #4CA1AF);
        color: white;
        padding: 10px 14px;
        border-radius: 18px;
        margin: 6px 0;
        max-width: 75%;
        text-align: left;
        align-self: flex-start;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Chat Box Structure ---
    st.markdown("<div class='chat-float'><div class='chat-header'>🤖 AI Learning Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {msg}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Chat Input ---
    user_input = st.text_input("Type your message here...", key="chat_input")

    # --- Chatbot Logic ---
    def get_bot_response(message, history):
        message = message.lower()
        motivational_quotes = [
            "🌟 Keep pushing forward — every line of code takes you closer to mastery!",
            "🔥 You’re improving every day — trust the process!",
            "💻 Code. Debug. Learn. Repeat. That’s how legends are made!",
            "🚀 Success is just consistent effort over time."
        ]
        python_tips = [
            "🐍 Use list comprehensions instead of loops — it's cleaner and faster!",
            "💡 Learn to use `zip()` and `enumerate()` — they simplify your logic!",
            "📘 Explore Python’s standard library — it saves tons of time!"
        ]
        if "python" in message:
            return np.random.choice(python_tips)
        elif "c++" in message or "cpp" in message:
            return "💻 Practice logic-building problems with pointers and memory handling!"
        elif "web" in message:
            return "🌐 Start with HTML & CSS, then JavaScript. Create a simple website first!"
        elif "ai" in message or "machine" in message:
            return "🤖 Start with Python, then learn libraries like NumPy, Pandas, and scikit-learn."
        elif "motivate" in message:
            return np.random.choice(motivational_quotes)
        elif "hello" in message or "hi" in message:
            return "👋 Hey there! Ready to learn something exciting today?"
        elif "progress" in message:
            return "📊 You’re improving fast! Keep learning one topic at a time!"
        elif "thanks" in message:
            return "😊 You're welcome! Stay consistent and keep growing!"
        else:
            return np.random.choice([
                "🤔 Interesting thought! Tell me more.",
                "💬 Which course are you focusing on today?",
                "🚀 I love your curiosity — want a coding challenge?",
                "✨ You’re doing great — what topic should we explore next?"
            ])

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("AI is typing..."):
            time.sleep(np.random.uniform(0.6, 1.2))
            bot_reply = get_bot_response(user_input, st.session_state.chat_history)
            st.session_state.chat_history.append(("bot", bot_reply))
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")
