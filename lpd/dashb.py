# app.py — Enhanced Neon Edition (Debugged + Improved)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
import time
from io import BytesIO

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ SESSION STATE DEFAULTS ------------------
for key, default in {
    "chat_history": [],
    "topic_memory": None,
    "download_blob": None,
    "show_more_courses": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------ GLOBAL NEON THEME STYLES ------------------
st.markdown(
    """
    <style>
    .stApp { background: #000; color: #bfffc2; font-family: 'Trebuchet MS', sans-serif; }
    h1, h2, h3 { color: #bfffc2; text-shadow: 0 0 8px rgba(0,255,127,0.25); }
    .neon-btn {
        background: linear-gradient(90deg,#00ff7f33,#00ff7f22);
        color: #bfffc2; font-weight: 600;
        padding: 8px 14px; border-radius: 10px;
        border: 1px solid rgba(0,255,127,0.35);
        box-shadow: 0 0 8px rgba(0,255,127,0.2);
        transition: 0.3s;
    }
    .neon-btn:hover { box-shadow: 0 0 16px rgba(0,255,127,0.4); }
    .card {
        background: rgba(255,255,255,0.03);
        padding: 14px; border-radius: 12px;
        border: 1px solid rgba(0,255,127,0.06);
    }
    .chat-area {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px; padding: 14px;
        max-height: 62vh; overflow-y: auto;
        border: 1px solid rgba(0,255,127,0.06);
    }
    .bubble-user, .bubble-bot {
        padding: 10px 14px; border-radius: 14px; margin: 6px 0;
        display: inline-block; max-width: 85%;
        animation: fadeIn 0.8s ease-out;
        box-shadow: 0 0 12px rgba(0,255,127,0.08);
    }
    .bubble-user {
        background: linear-gradient(90deg,#003e13,#1b5e20);
        text-align: right; color: #eafff0; float: right;
    }
    .bubble-bot {
        background: linear-gradient(90deg,#134b2b,#2e7d32);
        text-align: left; color: #eafff0; float: left;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(6px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .neon-header { text-align:center; color:#bfffc2; margin-bottom:10px; }
    .memory-badge {
        background: rgba(0,255,127,0.08);
        color: #bfffc2; padding: 5px 10px; border-radius: 8px;
        display: inline-block; margin-bottom: 10px;
    }
    .glow-line {
        width: 100%; height: 1px; margin: 10px 0;
        background: linear-gradient(90deg, transparent, #00ff7f55, transparent);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ SIDEBAR ------------------
st.sidebar.title("☰ Menu")
page = st.sidebar.radio("Navigate:", ["🏠 Dashboard", "🤖 Chat Assistant"])

# =====================================================
# PAGE 1: DASHBOARD
# =====================================================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard")
    st.markdown("<div class='card'>Track your progress, courses, and growth in Computer Science.</div>", unsafe_allow_html=True)

    # Gauge with centered value
    st.subheader("🎯 Overall Progress")
    overall_progress = random.randint(60, 95)
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_progress,
        number={'font': {'size': 44, 'color': '#00FF7F'}},
        title={'text': "Total Completion", 'font': {'color': '#bfffc2'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#bfffc2'},
            'bar': {'color': "#00FF7F"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(0,255,127,0.05)"},
                {'range': [50, 100], 'color': "rgba(0,255,127,0.10)"}
            ],
        }
    ))
    gauge_fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2')
    st.plotly_chart(gauge_fig, use_container_width=True)

    # Courses
    st.subheader("📚 Course Completion Overview")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.7])
    for name, key in zip(["🐍 Python", "💻 C++", "🌐 Web Dev"], ["py", "cpp", "web"]):
        c1.button(name, key=f"btn_{key}")
    if c4.button("More ▼" if not st.session_state.show_more_courses else "Hide ▲"):
        st.session_state.show_more_courses = not st.session_state.show_more_courses

    if st.session_state.show_more_courses:
        st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)
        for c in ["🤖 AI", "📊 Data Science", "🧩 ML", "🕹️ Game Dev", "📱 App Dev", "⚙️ DSA", "☁️ Cloud", "🔒 Cybersecurity"]:
            st.button(c)
        st.markdown("<div class='glow-line'></div>", unsafe_allow_html=True)

    # Weekly progress chart
    st.subheader("📆 Weekly Progress")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    progress = [random.randint(60, 100) for _ in weeks]
    bar_fig = go.Figure(go.Bar(
        x=weeks, y=progress, text=progress, textposition='auto', marker_color=['#00FF7F']*len(progress)
    ))
    bar_fig.update_layout(title="Weekly Growth Chart", paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2', height=350)
    st.plotly_chart(bar_fig, use_container_width=True)

    # Data table
    st.subheader("📈 Detailed Course Progress")
    df = pd.DataFrame({
        "Course": ["Python", "C++", "Web Dev", "AI", "DS", "ML", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    })
    st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#bfffc2;'>Developed by Anish | Neon Dashboard © 2025</div>", unsafe_allow_html=True)

# =====================================================
# PAGE 2: CHAT ASSISTANT
# =====================================================
elif page == "🤖 Chat Assistant":
    st.markdown("<h2 class='neon-header'>🤖 Neon Chat Assistant</h2>", unsafe_allow_html=True)
    st.caption("Type 'bye' to clear memory • Futuristic Black + Neon Green Mode")

    # Quick Starters
    cols = st.columns(4)
    starters = {
        "💪 Motivate": "motivate me",
        "🐍 Python Tip": "python tips",
        "🧠 AI Info": "tell me about ai",
        "🌐 Web Help": "help with web dev",
    }
    for (label, msg), col in zip(starters.items(), cols):
        if col.button(label):
            st.session_state.chat_history.append(("user", msg, pd.Timestamp.utcnow().isoformat()))
            st.session_state.chat_history.append(("bot", "✅ Got it! Let's dive in.", pd.Timestamp.utcnow().isoformat()))

    # Clear chat
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history.clear()
        st.session_state.topic_memory = None
        st.session_state.download_blob = None
        st.toast("Chat cleared!", icon="🧽")

    # Chat display
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.topic_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Topic: {st.session_state.topic_memory.title()}</div>", unsafe_allow_html=True)

    for sender, msg, ts in st.session_state.chat_history:
        timestamp = pd.Timestamp(ts).strftime("%H:%M:%S")
        bubble_class = "bubble-user" if sender == "user" else "bubble-bot"
        align = "right" if sender == "user" else "left"
        st.markdown(
            f"<div style='text-align:{align}'><div class='{bubble_class}'><b>{sender.title()}:</b> {msg}</div><br><small style='color:#8fffbf'>{timestamp}</small></div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Input and send
    user_text = st.text_input("Type your message:", key="chat_input")
    if st.button("Send"):
        if user_text.strip():
            st.session_state.chat_history.append(("user", user_text.strip(), pd.Timestamp.utcnow().isoformat()))

            # Typing effect
            with st.spinner("Assistant is typing..."):
                time.sleep(random.uniform(0.5, 1.2))

            # Simplified smart reply
            def quick_reply(msg):
                low = msg.lower()
                if "python" in low: return "🐍 Use list comprehensions—they’re elegant and fast!"
                if "ai" in low: return "🤖 AI is about learning patterns—start with Scikit-learn!"
                if "web" in low: return "🌐 HTML + CSS + JS form the holy trinity of web dev."
                if "motivate" in low: return random.choice(["💪 Keep going!", "🚀 You’re leveling up!", "🔥 Progress > Perfection!"])
                if "bye" in low: 
                    st.session_state.topic_memory = None
                    return "👋 Goodbye! Memory cleared."
                return random.choice(["✨ Keep exploring!", "💡 Ask me a coding fact!", "🧩 Want a small challenge?"])
            
            reply = quick_reply(user_text)
            st.session_state.chat_history.append(("bot", reply, pd.Timestamp.utcnow().isoformat()))
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#bfffc2;'>Neon Chat • Developed by Anish © 2025</div>", unsafe_allow_html=True)
