import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ PAGE SELECTION ------------------
st.sidebar.title("☰ Navigation Menu")
page = st.sidebar.radio("Go to:", ["🏠 Dashboard", "🤖 AI Chat Assistant"])

# ============================================================
# 🏠 PAGE 1 — DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard")
    st.markdown("Track your progress, courses, and overall growth in Computer Science! 🚀")

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

    # ------------------ COURSE COMPLETION ------------------
    st.subheader("📚 Course Completion Overview")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 0.8])

    if "show_more_courses" not in st.session_state:
        st.session_state.show_more_courses = False

    with col1:
        st.button("🐍 Python")
    with col2:
        st.button("💻 C++")
    with col3:
        st.button("🌐 Web Dev")
    with col4:
        if st.button("More Courses ▼" if not st.session_state.show_more_courses else "Hide Courses ▲"):
            st.session_state.show_more_courses = not st.session_state.show_more_courses

    if st.session_state.show_more_courses:
        st.markdown("---")
        extra_courses = [
            "🤖 Artificial Intelligence", "📊 Data Science", "🧩 Machine Learning",
            "🕹️ Game Development", "📱 App Development",
            "⚙️ DSA", "☁️ Cloud Computing", "🔒 Cybersecurity"
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
    fig2.update_layout(title="Weekly Growth Chart", xaxis_title="Week", yaxis_title="Progress (%)", height=400)
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------ COURSE TABLE ------------------
    st.subheader("📈 Detailed Course Progress")
    course_data = {
        "Course": ["Python", "C++", "Web Dev", "AI", "Data Science", "ML", "Cybersecurity"],
        "Completion %": [85, 60, 75, 40, 55, 45, 30],
        "Status": ["Completed", "In Progress", "In Progress", "Not Started", "In Progress", "In Progress", "Not Started"]
    }
    df = pd.DataFrame(course_data)
    st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)

    # ------------------ FOOTER ------------------
    st.markdown("---")
    st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")

# ============================================================
# 🤖 PAGE 2 — AI CHAT ASSISTANT
# ============================================================
elif page == "🤖 AI Chat Assistant":
    # ------------------ INITIAL STATES ------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "topic_memory" not in st.session_state:
        st.session_state.topic_memory = None

    # ------------------ STYLE ------------------
    st.markdown("""
        <style>
            .main {
                background-color: #000;
                color: #00FF7F;
            }
            div[data-testid="stMarkdownContainer"] p {
                color: #00FF7F !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🤖 Neon Chat Assistant")
    st.markdown("<p style='color:#00FF7F;'>Your futuristic AI companion for coding, motivation, and creativity ⚡</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ------------------ CHAT RESPONSE FUNCTION ------------------
    def get_bot_response(message, history, topic_memory):
        msg = message.lower()

        motivational_quotes = [
            "⚡ Keep coding — greatness compiles over time!",
            "🚀 Every bug you fix powers your journey to mastery!",
            "🔥 Consistency beats talent — one line at a time.",
            "💡 Every error hides a new lesson — embrace it."
        ]
        python_tips = [
            "🐍 Use comprehensions — they make your code elegant.",
            "⚙️ Learn the `itertools` module — it’s a power boost for iteration.",
            "📘 Use `enumerate()` and `zip()` — clean and efficient loops!",
            "🧠 Write readable code, not just working code."
        ]
        ai_tips = [
            "🤖 Start with data — good AI begins with clean datasets.",
            "🧩 Learn how models think: it’s all math and logic at the core.",
            "💥 Try hands-on: train a small neural network in TensorFlow or PyTorch!",
        ]
        web_tips = [
            "🌐 Learn Flexbox & Grid — they’ll make you a CSS wizard.",
            "⚡ JavaScript + APIs = Web magic!",
            "🧱 Build small web projects; every one adds a new skill layer."
        ]

        # --- Detect or maintain topic memory ---
        if "python" in msg:
            st.session_state.topic_memory = "python"
            return np.random.choice(python_tips)
        elif "ai" in msg or "machine learning" in msg:
            st.session_state.topic_memory = "ai"
            return np.random.choice(ai_tips)
        elif "web" in msg or "frontend" in msg:
            st.session_state.topic_memory = "web"
            return np.random.choice(web_tips)
        elif "motivate" in msg:
            st.session_state.topic_memory = "motivation"
            return np.random.choice(motivational_quotes)
        elif "thanks" in msg:
            return "😊 Always here to help — keep the neon energy alive!"

        # Contextual follow-up
        elif topic_memory == "python":
            return np.random.choice(python_tips)
        elif topic_memory == "ai":
            return np.random.choice(ai_tips)
        elif topic_memory == "web":
            return np.random.choice(web_tips)
        elif topic_memory == "motivation":
            return np.random.choice(motivational_quotes)
        else:
            return np.random.choice([
                "💬 Tell me what you're working on today.",
                "🚀 I sense great creativity in your flow.",
                "⚡ Want me to give you a random coding challenge?",
                "🧠 Let's explore a new tech topic — name one!"
            ])

    # ------------------ USER INPUT ------------------
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Assistant is typing..."):
            time.sleep(np.random.uniform(0.5, 1.1))
            bot_reply = get_bot_response(user_input, st.session_state.chat_history, st.session_state.topic_memory)
            st.session_state.chat_history.append(("bot", bot_reply))

    # ------------------ DISPLAY CHAT ------------------
    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"""
                <div style='
                    background-color:#00FF7F;
                    color:black;
                    padding:10px;
                    border-radius:10px;
                    margin:6px 0;
                    text-align:right;
                    box-shadow:0 0 15px #00FF7F;
                '><b>You:</b> {msg}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='
                    background-color:#111;
                    color:#00FF7F;
                    padding:10px;
                    border-radius:10px;
                    margin:6px 0;
                    box-shadow:0 0 10px #00FF7F;
                '><b>Assistant:</b> {msg}</div>
            """, unsafe_allow_html=True)

    # ------------------ SAVE CHAT HISTORY ------------------
    if st.button("💾 Save Chat History"):
        chat_df = pd.DataFrame(st.session_state.chat_history, columns=["Sender", "Message"])
        csv = chat_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="⬇️ Download Chat as CSV", data=csv, file_name="chat_history.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("<center>💚 Futuristic Neon Chat | Developed by Anish © 2025</center>", unsafe_allow_html=True)
