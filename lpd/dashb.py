import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("🚀 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Dashboard", "🤖 Chat Assistant"])

# ------------------ INITIAL STATES ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "topic_memory" not in st.session_state:
    st.session_state.topic_memory = None

# ==========================================================
#  PAGE 1 — DASHBOARD
# ==========================================================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard")
    st.markdown("Track your progress, courses, and overall growth in Computer Science!")

    # Overall Progress Gauge
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

    # Course Completion Overview
    st.subheader("📚 Course Completion Overview")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.8])
    col1.button("🐍 Python")
    col2.button("💻 C++")
    col3.button("🌐 Web Dev")

    # Table of courses
    st.subheader("📈 Detailed Course Progress")
    course_data = {
        "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    }
    df = pd.DataFrame(course_data)
    st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)

# ==========================================================
#  PAGE 2 — CHAT ASSISTANT
# ==========================================================
elif page == "🤖 Chat Assistant":
    # --------- CUSTOM DARK THEME ---------
    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
            color: #39FF14;
        }
        div[data-testid="stChatMessage"] {
            background-color: #0d0d0d !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🤖 AI Chat Assistant")
    st.markdown("<p style='color:#39FF14;'>Your futuristic coding companion with memory & motivation!</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ------------------ BOT LOGIC ------------------
    def get_bot_response(message):
        msg = message.lower()
        topic = st.session_state.topic_memory

        motivational_quotes = [
            "🚀 Greatness comes from consistency, not luck!",
            "🔥 Keep going — every bug you fix is a step toward mastery.",
            "💻 You’re coding your future, one line at a time!",
            "⚡ Stay sharp, coder — even errors teach wisdom."
        ]
        python_tips = [
            "🐍 Python tip: Use list comprehensions — they’re cleaner and faster!",
            "💡 Try `enumerate()` and `zip()` to write elegant loops.",
            "📘 Practice using Python’s built-in modules — they save tons of time!"
        ]
        ai_tips = [
            "🤖 AI is about patterns — start small, understand data deeply.",
            "🧠 Learn NumPy, Pandas, and Scikit-Learn — your AI starter trio!",
            "⚙️ Remember: training data quality > quantity."
        ]
        web_tips = [
            "🌐 Build projects! HTML, CSS, JS — nothing beats practice.",
            "💫 Try adding animations with CSS keyframes for fun UIs.",
            "🧩 Explore frameworks like React or Flask next!"
        ]

        # --- Topic detection & memory ---
        if any(x in msg for x in ["python", "py"]):
            st.session_state.topic_memory = "python"
            return random.choice(python_tips)
        elif any(x in msg for x in ["ai", "machine learning", "ml"]):
            st.session_state.topic_memory = "ai"
            return random.choice(ai_tips)
        elif any(x in msg for x in ["web", "html", "css", "javascript"]):
            st.session_state.topic_memory = "web"
            return random.choice(web_tips)
        elif any(x in msg for x in ["motivate", "inspire", "focus"]):
            return random.choice(motivational_quotes)
        elif "thanks" in msg:
            return "😊 Anytime! Keep building awesome things!"
        elif "hello" in msg or "hi" in msg:
            return "👋 Hello there, future innovator! Ready to create something cool?"

        # Contextual continuation
        if topic == "python":
            return random.choice([
                "🐍 Keep exploring modules — try `itertools` next!",
                "💡 Want a Python mini-project idea?",
                "📈 Practice algorithms — they sharpen your logic."
            ])
        elif topic == "ai":
            return random.choice([
                "🤖 Dive into neural networks next!",
                "🧩 Try visualizing datasets with Matplotlib.",
                "💾 Remember to normalize your data!"
            ])
        elif topic == "web":
            return random.choice([
                "🌐 Build a portfolio website to showcase your work!",
                "💻 Try adding responsive design with media queries.",
                "⚡ Experiment with simple JavaScript animations!"
            ])
        else:
            return random.choice([
                "✨ Interesting thought — tell me more!",
                "🚀 Want a coding challenge idea?",
                "🧠 I love your curiosity — what do you want to explore today?"
            ])

    # ------------------ CHAT INTERFACE ------------------
    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div style='background:#39FF1440;padding:10px;border-radius:10px;margin:5px 0;text-align:right'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#1a1a1a;padding:10px;border-radius:10px;margin:5px 0'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

    # --- Input field (bug-free version) ---
    user_text = st.text_input("Type your message here...", key="user_input_text")
    send_clicked = st.button("Send", key="send_btn")

    if send_clicked and user_text.strip():
        st.session_state.chat_history.append(("user", user_text.strip()))
        with st.spinner("Assistant is typing..."):
            time.sleep(np.random.uniform(0.4, 1.0))
            bot_reply = get_bot_response(user_text.strip())
            st.session_state.chat_history.append(("bot", bot_reply))
        st.experimental_rerun()

    # --- Save Chat History Button ---
    st.markdown("---")
    if st.button("💾 Save Chat History"):
        chat_df = pd.DataFrame(st.session_state.chat_history, columns=["Sender", "Message"])
        chat_df.to_csv("chat_history.csv", index=False)
        st.success("✅ Chat history saved as 'chat_history.csv'!")

    # --- Footer ---
    st.markdown("<p style='text-align:center;color:#39FF14;'>CSE Learning Path Dashboard © 2025 — Designed by Anish</p>", unsafe_allow_html=True)
