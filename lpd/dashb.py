import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.title("📘 Navigation")
menu_choice = st.sidebar.radio(
    "Go to:", 
    ["🏠 Home", "📚 Courses", "📆 Weekly Progress", "📈 Detailed Progress", "🤖 AI Chat Assistant"]
)

st.session_state.page = menu_choice

# ------------------ HEADER ------------------
st.title("🧠 CSE Learning Path Dashboard")
st.markdown("Efficiently track your growth and learning journey in Computer Science!")

# ------------------ RANDOM DATA GENERATOR ------------------
def random_progress_data():
    return np.random.randint(30, 100, size=7).tolist()

# ------------------ HOME PAGE ------------------
if st.session_state.page == "🏠 Home":
    st.subheader("🎯 Overall Progress")
    overall_progress = np.random.randint(40, 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_progress,
        title={'text': "Total Completion"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00BFFF"},
            'steps': [
                {'range': [0, 50], 'color': "#f2f2f2"},
                {'range': [50, 100], 'color': "#d9f2e6"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🚀 Quick Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Courses", np.random.randint(3, 8))
    col2.metric("Average Progress", f"{overall_progress}%")
    col3.metric("Total Study Hours", f"{np.random.randint(20, 120)} hrs")

    st.info("💡 Tip: Explore 'Courses' to view progress on specific subjects!")

# ------------------ COURSE PAGE ------------------
elif st.session_state.page == "📚 Courses":
    st.subheader("📘 Course Overview")
    st.write("Below are your enrolled courses and their progress levels:")

    courses = ["Python", "C++", "Web Development", "AI", "Data Science", "Machine Learning", "Cybersecurity"]
    completion = random_progress_data()
    statuses = [
        "Completed" if x > 80 else "In Progress" if x > 40 else "Not Started"
        for x in completion
    ]
    df = pd.DataFrame({"Course": courses, "Completion %": completion, "Status": statuses})

    try:
        st.dataframe(df.style.background_gradient(cmap="Blues"), use_container_width=True)
    except Exception:
        st.dataframe(df, use_container_width=True)

# ------------------ WEEKLY PROGRESS PAGE ------------------
elif st.session_state.page == "📆 Weekly Progress":
    st.subheader("📅 Weekly Growth Tracker")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    progress = np.random.randint(50, 100, size=4)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=weeks,
        y=progress,
        text=progress,
        textposition="auto",
        marker_color="#00BFFF"
    ))
    fig2.update_layout(
        title="Weekly Progress Overview",
        xaxis_title="Weeks",
        yaxis_title="Progress (%)",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.success("📊 Data updates randomly each refresh — keep tracking consistency!")

# ------------------ DETAILED PROGRESS PAGE ------------------
elif st.session_state.page == "📈 Detailed Progress":
    st.subheader("📈 Progress Insights")
    st.write("Visualize your overall learning performance:")

    categories = ["Coding", "Theory", "Projects", "Assignments", "Revisions"]
    scores = np.random.randint(40, 100, size=5)

    fig3 = go.Figure(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        marker_color="#00BFFF"
    ))
    fig3.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400)
    st.plotly_chart(fig3, use_container_width=True)

# ------------------ AI CHAT ASSISTANT PAGE ------------------
elif st.session_state.page == "🤖 AI Chat Assistant":
    st.subheader("🤖 Smart Study Companion")
    st.markdown("<p style='color:gray;'>Ask for coding tips, motivation, or advice!</p>", unsafe_allow_html=True)

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

    def get_bot_response(message):
        message = message.lower()
        responses = {
            "python": "🐍 Try list comprehensions and explore Python's standard library!",
            "ai": "🤖 AI is amazing! Learn with small datasets before deep models.",
            "web": "🌐 Start with HTML, CSS, and JS — then move to React!",
            "motivate": "💪 Every coder was once a beginner — keep pushing!",
        }
        for key in responses:
            if key in message:
                return responses[key]
        return np.random.choice([
            "🚀 Keep learning, consistency beats talent!",
            "✨ Great question — care to elaborate?",
            "💬 I’m always here to help your study journey!"
        ])

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.spinner("Assistant is typing..."):
            time.sleep(0.8)
            bot_reply = get_bot_response(user_input)
            st.session_state.chat_history.append(("bot", bot_reply))

    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div style='background:#DCF8C6; padding:10px; border-radius:10px; margin:5px 0; text-align:right'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#E9E9EB; padding:10px; border-radius:10px; margin:5px 0'><b>Assistant:</b> {msg}</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("**Developed by Anish | CSE Learning Path Dashboard © 2025**")
