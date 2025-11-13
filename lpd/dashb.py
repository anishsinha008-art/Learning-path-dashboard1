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
    .stApp {
        background: #000000;
        color: #bfffc2;
    }
    h1, h2, h3 {
        color: #bfffc2;
    }
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
    .card {
        background: rgba(255,255,255,0.02);
        padding: 14px;
        border-radius: 12px;
        border: 1px solid rgba(0,255,127,0.06);
    }
    .chat-area {
        background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005));
        border-radius: 12px;
        padding: 14px;
        max-height: 62vh;
        overflow-y: auto;
        border: 1px solid rgba(0,255,127,0.04);
    }
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
    .neon-header {
        color: #bfffc2;
        text-shadow: 0 0 8px rgba(0,255,127,0.18);
    }
    @keyframes pulseIn {
        0% { transform: translateY(6px); opacity: 0; }
        60% { transform: translateY(0px); opacity: 1; }
        100% { transform: translateY(0px); opacity: 1; }
    }
    .memory-badge {
        background: rgba(0,255,127,0.08);
        color: #bfffc2;
        padding: 6px 10px;
        border-radius: 10px;
        border: 1px solid rgba(0,255,127,0.06);
        display:inline-block;
        margin-bottom:8px;
    }
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

    # Overall Progress Gauge
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

    # Weekly Progress
    st.subheader("📆 Weekly Progress")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    progress = [70, 82, 90, 100]
    bar_fig = go.Figure(go.Bar(
        x=weeks, y=progress, text=progress, textposition='auto',
        marker_color=['#00FF7F']*len(progress)
    ))
    bar_fig.update_layout(title="Weekly Growth Chart", paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2', height=380)
    st.plotly_chart(bar_fig, use_container_width=True)

    # Course table
    st.subheader("📈 Detailed Course Progress")
    df = pd.DataFrame({
        "Course": ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    })
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

    # Quick starter buttons
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💪 Motivate Me"):
        st.session_state.chat_history.append(("user", "motivate me", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🔥 Keep pushing — small steps every day!", pd.Timestamp.utcnow().isoformat()))
    if c2.button("🐍 Python Tip"):
        st.session_state.chat_history.append(("user", "tell me about python", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🐍 Use list comprehensions for concise, fast loops.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "python"
    if c3.button("🧠 AI Info"):
        st.session_state.chat_history.append(("user", "tell me about ai", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🤖 Start with NumPy & Pandas — clean data first.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "ai"
    if c4.button("🌐 Web Help"):
        st.session_state.chat_history.append(("user", "help with web dev", pd.Timestamp.utcnow().isoformat()))
        st.session_state.chat_history.append(("bot", "🌐 Learn Flexbox & Grid to build responsive layouts.", pd.Timestamp.utcnow().isoformat()))
        st.session_state.topic_memory = "web"

    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.topic_memory = None
        st.success("Chat cleared.")

    # Chat display area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.topic_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Current Topic: {st.session_state.topic_memory.title()}</div>", unsafe_allow_html=True)

    for sender, message, ts in st.session_state.chat_history:
        time_str = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender == "user":
            st.markdown(f"<div style='text-align:right'><div class='bubble-user'><b>You:</b> {message}</div><div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'><div class='bubble-bot'><b>Assistant:</b> {message}</div><div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    user_text = st.text_input("Type your message here...", key="user_input_text")
    send_clicked = st.button("Send", key="send_btn")

    # -------- Enhanced Reply Generator --------
    def generate_bot_reply(user_msg: str) -> str:
        msg = user_msg.lower().strip()

        motivational = [
            "⚡ Keep coding — greatness compiles over time!",
            "🚀 Every bug you fix powers your journey.",
            "🔥 Small steps daily = big wins over time.",
            "🌟 Even a single line of code can change the world.",
            "💪 Remember: progress, not perfection.",
            "✨ Don’t stop when you’re tired; stop when you’re proud!"
        ]
        python_pool = [
            "🐍 Python tip: use list comprehensions for concise loops.",
            "💡 Use `enumerate()` and `zip()` to simplify loops elegantly.",
            "⚙️ Try generators for memory-efficient sequences.",
            "📘 Learn how `*args` and `**kwargs` make functions flexible!",
            "🧩 Did you know? `f-strings` are faster than `format()`!",
            "🐢 Start small — build a to-do app or a calculator project!"
        ]
        ai_pool = [
            "🤖 Start with NumPy & Pandas to prep your data.",
            "🧠 Learn the math behind ML — linear algebra & stats are key.",
            "📊 Try a fun project: classify movie reviews by sentiment!",
            "🦾 Train your first model with Scikit-learn — easy and powerful.",
            "💭 Ever explored how neural networks mimic human learning?",
            "🧬 AI isn’t magic — it’s just math, data, and persistence!"
        ]
        web_pool = [
            "🌐 Build a personal portfolio — HTML + CSS + JS to start.",
            "💫 Learn CSS Grid / Flexbox for responsive layouts.",
            "⚡ Try JavaScript DOM events — make your site interactive!",
            "🧩 Ever heard of REST APIs? They’re the bridge between web apps.",
            "🪄 Use animations and transitions to bring life to your UI.",
            "🌈 Start small — a landing page is a perfect first project!"
        ]
        jokes = [
            "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
            "🤣 Debugging: where you are both the detective and the culprit.",
            "😆 A SQL query walks into a bar, asks two tables: 'Can I join you?'",
            "🧠 Programmer’s diet: coffee, pizza, and more coffee!",
            "💻 I would tell you a UDP joke… but you might not get it."
        ]
        greetings = [
            "👋 Hey there! How’s your learning journey going?",
            "✨ Hi! Ready to dive into something new today?",
            "🌟 Hello! What are we working on today?",
            "👽 Welcome back, code explorer!",
            "😄 Hey! Let’s make something awesome today."
        ]
        random_comments = [
            "💬 That’s interesting! Tell me more.",
            "🤔 Hmm, sounds like you’re thinking deeply — I like that.",
            "😄 Cool! You’ve got a curious mind.",
            "🧠 I love that question — reminds me of creative thinkers!",
            "💡 Every chat adds a spark of knowledge!"
        ]

        if any(k in msg for k in ["hello", "hi", "hey", "hola", "yo"]):
            st.session_state.topic_memory = "greetings"
            return random.choice(greetings)
        if any(k in msg for k in ["python", "py"]):
            st.session_state.topic_memory = "python"
            return random.choice(python_pool)
        if any(k in msg for k in ["ai", "machine learning", "ml"]):
            st.session_state.topic_memory = "ai"
            return random.choice(ai_pool)
        if any(k in msg for k in ["web", "html", "css", "javascript", "js"]):
            st.session_state.topic_memory = "web"
            return random.choice(web_pool)
        if any(k in msg for k in ["motivate", "inspire", "tired", "sad"]):
            st.session_state.topic_memory = "motivation"
            return random.choice(motivational)
        if any(k in msg for k in ["joke", "funny", "laugh"]):
            st.session_state.topic_memory = "jokes"
            return random.choice(jokes)
        if any(k in msg for k in ["bye", "goodnight", "see you", "exit"]):
            st.session_state.topic_memory = None
            return "👋 Bye! Topic memory cleared — take care and keep learning!"

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
        if topic == "greetings":
            return random.choice(random_comments)

        general_fallbacks = [
            "✨ Tell me what you’d like to learn: Python, AI, or Web?",
            "🚀 Want a quick coding challenge or a new project idea?",
            "💬 I can share tips, study plans, or tech facts — what do you want?",
            "🔮 Curious question! Can you tell me more?",
            "🌱 Learning never stops — what’s your focus this week?"
        ]
        return random.choice(general_fallbacks)

    # Handle chat send
    if send_clicked and user_text and user_text.strip():
        st.session_state.chat_history.append(("user", user_text.strip(), pd.Timestamp.utcnow().isoformat()))
        with st.spinner("Assistant is typing..."):
            time.sleep(np.random.uniform(0.45, 0.95))
            reply = generate_bot_reply(user_text.strip())
            st.session_state.chat_history.append(("bot", reply, pd.Timestamp.utcnow().isoformat()))
        st.experimental_rerun()

    st.markdown("---")
    if st.button("💾 Save Chat History"):
        if st.session_state.chat_history:
            chat_df = pd.DataFrame(st.session_state.chat_history, columns=["Sender", "Message", "Timestamp"])
            st.session_state.download_blob = chat_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", st.session_state.download_blob, file_name="chat_history.csv", mime="text/csv", use_container_width=True)
        else:
            st.warning("No chat history to download.")
