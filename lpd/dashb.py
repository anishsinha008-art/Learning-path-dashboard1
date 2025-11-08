# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from io import BytesIO
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ SESSION STATE DEFAULTS ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of tuples (sender, message, iso_timestamp)
if "topic_memory" not in st.session_state:
    st.session_state.topic_memory = None
if "download_blob" not in st.session_state:
    st.session_state.download_blob = None

# ------------------ GLOBAL NEON THEME STYLES ------------------
st.markdown(
    """
    <style>
    /* app background */
    .stApp {
        background: #000000;
        color: #bfffc2;
    }

    /* Headings */
    h1, h2, h3 {
        color: #bfffc2;
    }

    /* Neon buttons look */
    .neon-btn {
        background: linear-gradient(90deg,#00ff7f33,#00ff7f22);
        color: #000;
        padding: 8px 14px;
        border-radius: 10px;
        border: 1px solid rgba(0,255,127,0.35);
        box-shadow: 0 0 12px rgba(0,255,127,0.10), inset 0 0 6px rgba(0,255,127,0.03);
        font-weight: 600;
    }

    .neon-btn:hover {
        box-shadow: 0 0 24px rgba(0,255,127,0.18), inset 0 0 8px rgba(0,255,127,0.06);
    }

    /* Dashboard card */
    .card {
        background: rgba(255,255,255,0.02);
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(0,255,127,0.06);
    }

    /* Chat area wrapper */
    .chat-area {
        background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));
        border-radius: 12px;
        padding: 14px;
        max-height: 62vh;
        overflow-y: auto;
        border: 1px solid rgba(0,255,127,0.04);
    }

    /* Chat bubble styles */
    .bubble-user {
        background: linear-gradient(90deg,#003e13,#1b5e20);
        color: #eafff0;
        padding: 12px;
        border-radius: 14px;
        margin: 8px 0;
        text-align: right;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6), 0 0 16px rgba(0,255,127,0.06);
        animation: pulseIn 0.9s ease-out;
    }

    .bubble-bot {
        background: linear-gradient(90deg,#134b2b,#2e7d32);
        color: #eafff0;
        padding: 12px;
        border-radius: 14px;
        margin: 8px 0;
        text-align: left;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6), 0 0 12px rgba(0,255,127,0.06);
        animation: pulseIn 0.9s ease-out;
    }

    /* Neon outline for active chat page header */
    .neon-header {
        color: #bfffc2;
        text-shadow: 0 0 8px rgba(0,255,127,0.18);
    }

    /* Subtle pulsing animation */
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 6px rgba(0,255,127,0.06); }
        50% { box-shadow: 0 0 18px rgba(0,255,127,0.16); }
        100% { box-shadow: 0 0 6px rgba(0,255,127,0.06); }
    }

    @keyframes pulseIn {
        0% { transform: translateY(6px); opacity: 0; box-shadow: 0 0 4px rgba(0,255,127,0.02); }
        60% { transform: translateY(0px); opacity: 1; }
        100% { transform: translateY(0px); opacity: 1; }
    }

    /* small helper for memory badge */
    .memory-badge {
        background: rgba(0,255,127,0.08);
        color: #bfffc2;
        padding: 6px 10px;
        border-radius: 10px;
        border: 1px solid rgba(0,255,127,0.06);
        display:inline-block;
        margin-bottom:8px;
    }

    /* download button container */
    .download-area {
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("☰ Menu")
page = st.sidebar.radio("Navigate:", ["🏠 Dashboard", "🤖 Chat Assistant"])

# =========================
# PAGE: DASHBOARD
# =========================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard", anchor=None)
    st.markdown("<div class='card'>Track your progress, courses, and overall growth in Computer Science.</div>", unsafe_allow_html=True)
    st.markdown("")

    # Overall Progress Gauge (neon colors)
    st.subheader("🎯 Overall Progress")
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=68,
        title={'text': "Total Completion"},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#bfffc2'},
            'bar': {'color': "#00FF7F"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(0,255,127,0.03)"},
                {'range': [50, 100], 'color': "rgba(0,255,127,0.06)"}
            ]
        }
    ))
    gauge_fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2')
    st.plotly_chart(gauge_fig, use_container_width=True)

    # Course Completion Overview
    st.subheader("📚 Course Completion Overview")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.7])
    with col1:
        st.button("🐍 Python", key="dash_py_btn")
    with col2:
        st.button("💻 C++", key="dash_cpp_btn")
    with col3:
        st.button("🌐 Web Dev", key="dash_web_btn")
    with col4:
        if "show_more_courses" not in st.session_state:
            st.session_state.show_more_courses = False
        if st.button("More Courses ▼" if not st.session_state.show_more_courses else "Hide Courses ▲", key="dash_more_btn"):
            st.session_state.show_more_courses = not st.session_state.show_more_courses

    if st.session_state.show_more_courses:
        st.markdown("---")
        extra_courses = [
            "🤖 Artificial Intelligence", "📊 Data Science", "🧩 Machine Learning",
            "🕹️ Game Development", "📱 App Development",
            "⚙️ DSA", "☁️ Cloud Computing", "🔒 Cybersecurity"
        ]
        for i, c in enumerate(extra_courses):
            st.button(c, key=f"extra_course_{i}")
        st.markdown("---")

    # Weekly Progress (neon bar)
    st.subheader("📆 Weekly Progress")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    progress = [70, 82, 90, 100]
    bar_fig = go.Figure(go.Bar(
        x=weeks,
        y=progress,
        text=progress,
        textposition='auto',
        marker_color=['#00FF7F']*len(progress)
    ))
    bar_fig.update_layout(title="Weekly Growth Chart", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2', height=380)
    st.plotly_chart(bar_fig, use_container_width=True)

    # Course table
    st.subheader("📈 Detailed Course Progress")
    course_data = {
        "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    }
    df = pd.DataFrame(course_data)
    try:
        st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)
    except Exception:
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("<div style='color:#bfffc2;'>Developed by Anish | CSE Learning Path Dashboard © 2025</div>", unsafe_allow_html=True)

# =========================
# PAGE: CHAT ASSISTANT
# =========================
elif page == "🤖 Chat Assistant":
    st.markdown("<h2 class='neon-header'>🤖 Neon Chat Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<div style='color:#bfffc2;'>Futuristic black + neon green. Topic memory ON. Type 'bye' to reset topic memory.</div>", unsafe_allow_html=True)
    st.markdown("")

    # Quick starters
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💪 Motivate Me", key="starter_motivate"):
        st.session_state.chat_history.append(("user", "motivate me", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🔥 Keep pushing — small steps every day!", pd.Timestamp.utcnow().isoformat()))
    if c2.button("🐍 Python Tip", key="starter_python"):
        st.session_state.chat_history.append(("user", "tell me about python", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🐍 Use list comprehensions for concise, fast loops.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "python"
    if c3.button("🧠 AI Info", key="starter_ai"):
        st.session_state.chat_history.append(("user", "tell me about ai", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🤖 Start with NumPy & Pandas — clean data first.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "ai"
    if c4.button("🌐 Web Help", key="starter_web"):
        st.session_state.chat_history.append(("user", "help with web dev", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🌐 Learn Flexbox & Grid to build responsive layouts.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "web"

    st.markdown("")  # spacing

    # Clear chat history
    if st.button("🧹 Clear Chat History", key="clear_chat"):
        st.session_state.chat_history = []
        st.session_state.topic_memory = None
        st.success("Chat cleared.")

    # Chat display area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.topic_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Current Topic: {st.session_state.topic_memory.title()}</div>", unsafe_allow_html=True)

    # Render chat messages
    for sender, message, ts in st.session_state.chat_history:
        # Show timestamp on small faint text
        time_str = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender == "user":
            st.markdown(f"""
                <div style='text-align:right'>
                    <div class='bubble-user'><b>You:</b> {message}</div>
                    <div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='text-align:left'>
                    <div class='bubble-bot'><b>Assistant:</b> {message}</div>
                    <div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area (text_input + Send button) — safe pattern
    user_text = st.text_input("Type your message here...", key="user_input_text")
    send_clicked = st.button("Send", key="send_btn")

    def generate_bot_reply(user_msg: str) -> str:
        """Enhanced but lightweight reply generator with topic memory."""
        msg = user_msg.lower().strip()
        # pools
        motivational = [
            "⚡ Keep coding — greatness compiles over time!",
            "🚀 Every bug you fix powers your journey.",
            "🔥 Small steps daily = big wins over time."
        ]
        python_pool = [
            "🐍 Python tip: use list comprehensions for concise loops.",
            "💡 Use `enumerate()` and `zip()` to simplify loops.",
            "⚙️ Try generators for memory efficient sequences."
        ]
        ai_pool = [
            "🤖 Start with NumPy & Pandas to prep your data.",
            "🧠 Learn the math behind models (linear algebra, stats).",
            "📊 Try a small project: classify tweets by sentiment."
        ]
        web_pool = [
            "🌐 Build a small portfolio: HTML, CSS, JS — then host it.",
            "💫 Use CSS Grid / Flexbox for modern layouts.",
            "⚡ Explore a JS library (React) after mastering vanilla JS."
        ]
        jokes = [
            "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
            "🤣 Debugging is like detective work where you might be the suspect."
        ]

        # detect topic keywords
        if any(k in msg for k in ["python", "py"]):
            st.session_state.topic_memory = "python"
            return random.choice(python_pool)
        if any(k in msg for k in ["ai", "machine learning", "ml"]):
            st.session_state.topic_memory = "ai"
            return random.choice(ai_pool)
        if any(k in msg for k in ["web", "html", "css", "javascript", "js"]):
            st.session_state.topic_memory = "web"
            return random.choice(web_pool)
        if any(k in msg for k in ["motivate", "inspire", "tired"]):
            st.session_state.topic_memory = "motivation"
            return random.choice(motivational)
        if any(k in msg for k in ["joke", "funny"]):
            st.session_state.topic_memory = "jokes"
            return random.choice(jokes)
        if any(k in msg for k in ["bye", "goodnight", "see you"]):
            st.session_state.topic_memory = None
            return "👋 Bye! Topic memory cleared — come back soon!"

        # fallback: continue with topic memory if present
        topic = st.session_state.topic_memory
        if topic == "python":
            return random.choice(python_pool)
        if topic == "ai":
            return random.choice(ai_pool)
        if topic == "web":
            return random.choice(web_pool)
        if topic == "motivation":
            return random.choice(motivational)
        if topic == "jokes":
            return random.choice(jokes)

        # general fallback responses
        return random.choice([
            "✨ Tell me what you'd like to learn: Python, AI, or Web?",
            "🚀 Want a quick coding challenge?",
            "💬 I can give tips, a study plan, or a small project idea — what do you prefer?"
        ])

    # When Send is clicked: append and rerun (clears input safely)
    if send_clicked and user_text and user_text.strip():
        # append user's message + timestamp
        st.session_state.chat_history.append(("user", user_text.strip(), pd.Timestamp.utcnow().isoformat()))
        # generate reply
        with st.spinner("Assistant is typing..."):
            time.sleep(np.random.uniform(0.45, 0.95))
            reply = generate_bot_reply(user_text.strip())
            st.session_state.chat_history.append(("bot", reply, pd.Timestamp.utcnow().isoformat()))
        # force rerun so the text_input is cleared visually and UI updates
        st.experimental_rerun()

    # Save Chat History (manual): prepare CSV blob when button clicked
    st.markdown("---")
    if st.button("💾 Save Chat History", key="save_chat_btn"):
        if st.session_state.chat_history:
            chat_df = pd.DataFrame(st.session_state.chat_history, columns=["Sender", "Message", "Timestamp"])
            csv_bytes = chat_df.to_csv(index=False).encode("utf-8")
            st.session_state.download_blob = csv_bytes
            st.success("Chat prepared — click the download button below.")
        else:
            st.info("No chat to save yet. Start a conversation first.")

    # Show download button only when blob ready
    if st.session_state.download_blob:
        st.markdown("<div class='download-area'>", unsafe_allow_html=True)
        st.download_button(label="⬇️ Download Chat as CSV", data=st.session_state.download_blob, file_name="chat_history.csv", mime="text/csv")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("<div style='color:#bfffc2;text-align:center'>Neon Chat • Developed by Anish © 2025</div>", unsafe_allow_html=True)
