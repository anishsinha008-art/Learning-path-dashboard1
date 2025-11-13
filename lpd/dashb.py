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

# ------------------ CHATBOT SECTION ------------------
st.markdown("---")
st.subheader("🤖 AI Chat Assistant")
st.markdown("<p style='color:gray;'>Ask anything — from coding advice to motivation or study tips!</p>", unsafe_allow_html=True)

# Quick reply buttons
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

# --- Chatbot logic ---
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
        "💡 Learn how to use the `zip()` and `enumerate()` functions — they make life easier!",
        "📘 Master Python’s standard library — it saves tons of time!"
    ]

    if "python" in message:
        return np.random.choice(python_tips)
    elif "c++" in message or "cpp" in message:
        return "💻 C++ builds logic — practice memory and pointer problems daily!"
    elif "web" in message:
        return "🌐 Start with HTML & CSS, then learn JavaScript. Build your first portfolio website!"
    elif "ai" in message or "machine learning" in message:
        return "🤖 AI is fascinating! Start with Python, then learn NumPy, Pandas, and scikit-learn."
    elif "motivate" in message or "inspire" in message:
        return np.random.choice(motivational_quotes)
    elif "thanks" in message or "thank you" in message:
        return "😊 You’re very welcome! Keep going, you’re doing amazing!"
    elif "joke" in message:
        return "😂 Why do programmers prefer dark mode? Because light attracts bugs!"
    elif "progress" in message:
        return "📊 You’re progressing well! Remember to revise weekly."
    elif "how are you" in message:
        return "😄 I’m great, just processing data and cheering you on!"
    elif "hello" in message or "hi" in message:
        return "👋 Hey there! Ready to learn something new today?"
    else:
        # Contextual follow-up
        if history and "ai" in history[-1][1].lower():
            return "🧠 Building AI models requires patience — start simple, understand the math first."
        elif history and "python" in history[-1][1].lower():
            return "🐍 Once you’re comfortable with basics, try projects like calculators or quiz apps!"
        else:
            return np.random.choice([
                "🤔 Interesting! Could you explain more?",
                "💬 What topic are you focusing on today?",
                "🚀 I love your curiosity — keep exploring!",
                "✨ Want me to suggest a daily coding challenge?"
            ])

# --- Process input ---
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Assistant is typing..."):
        time.sleep(np.random.uniform(0.6, 1.2))  # Typing delay
        bot_reply = get_bot_response(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append(("bot", bot_reply))

# --- Display chat ---
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div style='background:#DCF8C6; padding:10px; border-radius:10px; margin:5px 0; text-align:right'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background:#E9E9EB; padding:10px; border-radius:10px; margin:5px 0'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")
