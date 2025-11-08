# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from io import BytesIO

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL SESSION STATE ------------------
if "show_more_courses" not in st.session_state:
    st.session_state.show_more_courses = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (sender, message)
if "topic_memory" not in st.session_state:
    st.session_state.topic_memory = None

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("☰ Navigation Menu")
page = st.sidebar.radio("Go to:", ["🏠 Dashboard", "🤖 AI Chat Assistant"])

# ------------------ COMMON STYLES ------------------
st.markdown(
    """
    <style>
    /* General app background (keeps it simple & compatible) */
    .stApp {
        background: #050505;
        color: #e6eef0;
    }
    /* Dashboard card look */
    .dashboard-card {
        background: rgba(255,255,255,0.03);
        padding: 12px;
        border-radius: 10px;
    }
    /* Chat area (scrollable) */
    .chat-area {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        padding: 12px;
        border-radius: 10px;
        max-height: 60vh;
        overflow-y: auto;
    }
    .chat-area::-webkit-scrollbar {
        width: 8px;
    }
    .chat-area::-webkit-scrollbar-thumb {
        background: rgba(0,255,127,0.15);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ FUNCTIONS ------------------
def render_dashboard():
    st.title("🧠 CSE Learning Path Dashboard")
    st.markdown("<div class='dashboard-card'>Track your progress, courses, and overall growth in Computer Science.</div>", unsafe_allow_html=True)
    st.markdown("")

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
                {'range': [0, 50], 'color': "#151515"},
                {'range': [50, 100], 'color': "#1f2f1f"}
            ]
        }
    ))
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Course Completion Overview
    st.subheader("📚 Course Completion Overview")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.8])
    with col1:
        st.button("🐍 Python", key="dash_python")
    with col2:
        st.button("💻 C++", key="dash_cpp")
    with col3:
        st.button("🌐 Web Dev", key="dash_web")
    with col4:
        if st.button("More Courses ▼" if not st.session_state.show_more_courses else "Hide Courses ▲", key="dash_more"):
            st.session_state.show_more_courses = not st.session_state.show_more_courses

    if st.session_state.show_more_courses:
        st.markdown("---")
        extra_courses = [
            "🤖 Artificial Intelligence", "📊 Data Science", "🧩 Machine Learning",
            "🕹️ Game Development", "📱 App Development",
            "⚙️ DSA", "☁️ Cloud Computing", "🔒 Cybersecurity"
        ]
        for i, course in enumerate(extra_courses):
            st.button(course, key=f"extra_course_{i}")
        st.markdown("---")

    # Weekly Progress
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
    fig2.update_layout(title="Weekly Growth Chart", xaxis_title="Week", yaxis_title="Progress (%)", height=400,
                       paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

    # Course Table
    st.subheader("📈 Detailed Course Progress")
    course_data = {
        "Course": ["Python", "C++", "Web Dev", "AI", "Data Science", "ML", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    }
    df = pd.DataFrame(course_data)
    try:
        st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)
    except Exception:
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")

def get_bot_response(message: str):
    """Return a short response based on message and topic memory (updates topic memory when it sees keywords)."""
    msg = message.lower()

    # Response pools
    motivational_quotes = [
        "⚡ Keep coding — greatness compiles over time!",
        "🚀 Every bug you fix powers your journey to mastery!",
        "🔥 Consistency beats talent — one line at a time."
    ]
    python_tips = [
        "🐍 Use list comprehensions for cleaner code.",
        "💡 Use `zip()` and `enumerate()` for tidy loops.",
        "⚙️ Try generators for memory-efficient iteration."
    ]
    web_tips = [
        "🌐 Use Flexbox/Grid for responsive layouts.",
        "⚡ JS + APIs = web interactivity — practice both."
    ]
    ai_tips = [
        "🤖 Start with NumPy & Pandas before models.",
        "📊 Data cleaning is the most time-consuming part of ML."
    ]
    jokes = [
        "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
        "🤣 Debugging is like detective work where you sometimes are the suspect."
    ]

    # Topic detection (update session state)
    if "python" in msg:
        st.session_state.topic_memory = "python"
        return np.random.choice(python_tips)
    if "web" in msg or "html" in msg or "css" in msg or "javascript" in msg:
        st.session_state.topic_memory = "web"
        return np.random.choice(web_tips)
    if "ai" in msg or "machine learning" in msg or "ml" in msg:
        st.session_state.topic_memory = "ai"
        return np.random.choice(ai_tips)
    if "motivate" in msg or "inspire" in msg or "tired" in msg:
        st.session_state.topic_memory = "motivation"
        return np.random.choice(motivational_quotes)
    if "joke" in msg or "funny" in msg:
        st.session_state.topic_memory = "jokes"
        return np.random.choice(jokes)
    if "bye" in msg or "goodnight" in msg or "see you" in msg:
        st.session_state.topic_memory = None
        return "👋 Bye! I've cleared my topic memory."

    # If message didn't set a new topic, continue with existing topic_memory
    topic = st.session_state.topic_memory
    if topic == "python":
        return np.random.choice(python_tips)
    if topic == "web":
        return np.random.choice(web_tips)
    if topic == "ai":
        return np.random.choice(ai_tips)
    if topic == "motivation":
        return np.random.choice(motivational_quotes)
    if topic == "jokes":
        return np.random.choice(jokes)

    # Fallback
    if "hello" in msg or "hi" in msg:
        return "👋 Hello! What would you like help with today — Python, Web, or AI?"
    if "thanks" in msg or "thank you" in msg:
        return "😊 You’re welcome — keep going!"
    return np.random.choice([
        "💬 Tell me which topic: Python, Web, or AI?",
        "🚀 Want a quick coding challenge?",
        "✨ I can give tips, jokes, or study plans — what do you prefer?"
    ])

def render_chat():
    st.title("🤖 Neon Chat Assistant")
    st.markdown("<p style='color:#00FF7F;'>Futuristic black + neon green. Topic memory ON. Type 'bye' to reset topic.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Conversation starters
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💪 Motivate Me", key="starter_motivate"):
        st.session_state.chat_history.append(("user", "motivate me"))
        st.session_state.chat_history.append(("bot", get_bot_response("motivate me")))
    if c2.button("🐍 Python Tip", key="starter_python"):
        st.session_state.chat_history.append(("user", "tell me about python"))
        st.session_state.chat_history.append(("bot", get_bot_response("tell me about python")))
    if c3.button("🧠 AI Info", key="starter_ai"):
        st.session_state.chat_history.append(("user", "tell me about ai"))
        st.session_state.chat_history.append(("bot", get_bot_response("tell me about ai")))
    if c4.button("🌐 Web Help", key="starter_web"):
        st.session_state.chat_history.append(("user", "help with web dev"))
        st.session_state.chat_history.append(("bot", get_bot_response("help with web dev")))

    # Clear chat
    if st.button("🧹 Clear Chat History", key="clear_chat"):
        st.session_state.chat_history = []
        st.session_state.topic_memory = None
        st.success("Chat cleared.")

    # Text input + send button (compatible)
    user_text = st.text_input("Type your message here...", key="user_input_text")
    if st.button("Send", key="send_btn"):
        if user_text and user_text.strip():
            st.session_state.chat_history.append(("user", user_text.strip()))
            with st.spinner("Assistant is typing..."):
                time.sleep(np.random.uniform(0.4, 1.0))
                bot_reply = get_bot_response(user_text.strip())
                st.session_state.chat_history.append(("bot", bot_reply))
            # clear the text input by resetting key (triggers rerun)
            st.session_state.user_input_text = ""

    # Display chat area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.topic_memory:
        st.markdown(f"<div style='color:#aef7c7; margin-bottom:6px'><b>🧠 Current Topic:</b> {st.session_state.topic_memory.title()}</div>", unsafe_allow_html=True)

    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"""
                <div style='
                    background: linear-gradient(90deg,#003e13,#1b5e20);
                    color:#eafaf0;
                    padding:10px;
                    border-radius:10px;
                    margin:8px 0;
                    text-align:right;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.6);
                    font-weight:500;
                '><b>You:</b> {msg}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='
                    background: linear-gradient(90deg,#134b2b,#2e7d32);
                    color:#e9fff0;
                    padding:10px;
                    border-radius:10px;
                    margin:8px 0;
                    text-align:left;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.6);
                '><b>Assistant:</b> {msg}</div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Save / Download chat history (manual)
    if st.session_state.chat_history:
        # Build dataframe
        chat_df = pd.DataFrame(st.session_state.chat_history, columns=["Sender", "Message"])
        csv_bytes = chat_df.to_csv(index=False).encode("utf-8")
        st.download_button(label="💾 Download Chat as CSV", data=csv_bytes, file_name="chat_history.csv", mime="text/csv")
    else:
        st.info("No chat yet — start a conversation or use the Quick Starters above to generate chat.")

# ------------------ ROUTE ------------------
if page == "🏠 Dashboard":
    render_dashboard()
else:
    render_chat()
