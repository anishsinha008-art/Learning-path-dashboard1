import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ SIDEBAR MENU ------------------
with st.sidebar:
    st.markdown("## ☰ Dashboard Menu")
    if st.button("Toggle Menu"):
        st.session_state.menu_open = not st.session_state.menu_open
        st.rerun()

    st.markdown("---")
    if st.button("💬 Open AI Assistant"):
        st.session_state.show_chat = not st.session_state.show_chat
        st.rerun()

# ------------------ HEADER ------------------
st.markdown(
    "<h1 style='text-align:center; color:#2e8b57;'>🌱 CSE Learning Path Dashboard</h1>",
    unsafe_allow_html=True
)

# ------------------ COURSE DATA ------------------
courses = {
    "Python Programming": 85,
    "Data Science": 72,
    "Web Development": 90,
    "Machine Learning": 67,
    "Artificial Intelligence": 60,
    "Cybersecurity": 78,
    "Cloud Computing": 55,
    "C++ Programming": 82,
    "Database Systems": 70
}

df = pd.DataFrame(list(courses.items()), columns=["Course", "Completion %"])

# ------------------ SAFE DATAFRAME DISPLAY ------------------
try:
    st.dataframe(df.style.background_gradient(cmap="Greens"), use_container_width=True)
except ImportError:
    st.warning("Matplotlib not found — showing plain table.")
    st.dataframe(df, use_container_width=True)

# ------------------ PROGRESS GAUGE ------------------
st.markdown("### 📈 Overall Progress")

overall_progress = np.mean(list(courses.values()))
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=overall_progress,
    title={'text': "Overall Completion %"},
    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}}
))
st.plotly_chart(fig, use_container_width=True)

# ------------------ CHATBOT SECTION ------------------
if st.session_state.show_chat:
    st.markdown(
        """
        <div style="
            background-color:#111111;
            padding:20px;
            border-radius:15px;
            color:white;
            max-height:500px;
            overflow-y:auto;
            border: 2px solid #2e8b57;
        ">
        <h3>🤖 AI Learning Assistant</h3>
        """,
        unsafe_allow_html=True
    )

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div style='text-align:right; color:#00ffb3;'>🧑‍💻 You: {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; color:#00bfff;'>🤖 AI: {message['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area
    user_input = st.text_input("Type your message here:", key="chat_input", placeholder="Ask about your learning path...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # --- Simulated AI Response ---
        with st.spinner("Thinking..."):
            time.sleep(1)
        response = "That's a great question! Keep focusing on your active courses, and aim to improve one skill every week."
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ------------------ FOOTER ------------------
st.markdown(
    "<hr><p style='text-align:center; color:gray;'>© 2025 CSE Learning Path | Interactive Dashboard with AI Assistant</p>",
    unsafe_allow_html=True
)
