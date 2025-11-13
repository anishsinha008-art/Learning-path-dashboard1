# learning_assistant_dashboard.py
# ----------------------------------------------------------
# Learning Path Dashboard + AI Learning Assistant (Offline)
# A Streamlit app for personalized learning tracking
# and motivational chat assistance (no API required)
# ----------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import datetime
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Learning Assistant", layout="wide")
st.markdown("""
    <style>
    body {background-color:#0b0f19;color:#e6f1ff;}
    .stApp {background: linear-gradient(180deg,#03050c 0%, #091227 100%);}
    h1,h2,h3 {color:#00bfff !important;}
    div[data-testid="stMetricValue"] {color:#00bfff;}
    .stButton>button {background-color:#0d47a1;color:white;border-radius:10px;}
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIAL STATE ----------------
if "courses" not in st.session_state:
    st.session_state.courses = {
        "Python Fundamentals": 50,
        "Data Analysis": 70,
        "Machine Learning": 35,
        "Web Development": 80,
    }
if "planner" not in st.session_state:
    st.session_state.planner = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- HEADER ----------------
st.title("🤖 AI Learning Assistant Dashboard")
st.caption("Personalized guidance • Smart planning • Progress tracking")

tab1, tab2, tab3 = st.tabs(["📘 Progress Tracker", "🗓️ Learning Planner", "💬 Motivator Chatbot"])

# =======================================================
# 📘 TAB 1 - PROGRESS TRACKER
# =======================================================
with tab1:
    st.subheader("📊 Learning Progress Overview")

    new_course = st.text_input("Add new course")
    progress = st.slider("Progress (%)", 0, 100, 0, key="progress_slider")
    if st.button("➕ Add / Update Course"):
        if new_course.strip():
            st.session_state.courses[new_course.strip()] = progress
            st.success(f"Course '{new_course}' updated!")
        else:
            st.warning("Enter a valid course name.")

    if st.button("🗑️ Reset All Courses"):
        st.session_state.courses = {}
        st.warning("All courses have been reset!")

    if not st.session_state.courses:
        st.info("Add some courses to visualize your learning progress.")
    else:
        df = pd.DataFrame({
            "Course": list(st.session_state.courses.keys()),
            "Progress": list(st.session_state.courses.values())
        })
        cols = st.columns(2)
        for i, (course, val) in enumerate(st.session_state.courses.items()):
            with cols[i % 2]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=val,
                    title={'text': course, 'font': {'size': 18, 'color': '#00bfff'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 0.5},
                        'bar': {'color': '#00bfff'},
                        'bgcolor': "#0a0a0a",
                        'steps': [
                            {'range': [0, 50], 'color': "#222"},
                            {'range': [50, 100], 'color': "#111"},
                        ],
                    }
                ))
                fig.update_layout(height=250, margin=dict(t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

        avg_progress = round(sum(st.session_state.courses.values()) / len(st.session_state.courses), 2)
        st.metric("Average Progress", f"{avg_progress}%")
        if avg_progress < 40:
            st.warning("⚙️ You're getting started — aim for small consistent goals.")
        elif avg_progress < 75:
            st.info("🔥 You're progressing well — keep your momentum going!")
        else:
            st.success("💎 Excellent! You're mastering your skills.")

        st.download_button(
            "📥 Download Progress CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="learning_progress.csv",
            mime="text/csv"
        )

# =======================================================
# 🗓️ TAB 2 - LEARNING PLANNER
# =======================================================
with tab2:
    st.subheader("🗓️ Daily Learning Planner")
    today = datetime.date.today()

    new_task = st.text_input("Add a new learning goal")
    deadline = st.date_input("Deadline", today)
    if st.button("✅ Add Task"):
        if new_task.strip():
            st.session_state.planner.append({
                "task": new_task,
                "deadline": deadline,
                "completed": False
            })
            st.success("Task added successfully!")
        else:
            st.warning("Enter a valid task name.")

    if not st.session_state.planner:
        st.info("Add your daily or weekly goals here.")
    else:
        for i, task in enumerate(st.session_state.planner):
            cols = st.columns([5, 2, 1])
            with cols[0]:
                st.write(f"🎯 **{task['task']}** (Deadline: {task['deadline']})")
            with cols[1]:
                if st.button("Mark Done ✅", key=f"done_{i}"):
                    st.session_state.planner[i]["completed"] = True
                    st.success(f"Marked '{task['task']}' complete!")
            with cols[2]:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.planner.pop(i)
                    st.warning("Task removed!")
                    st.experimental_rerun()

        # Progress Bar for Planner
        completed_tasks = sum(t["completed"] for t in st.session_state.planner)
        total_tasks = len(st.session_state.planner)
        if total_tasks > 0:
            st.progress(completed_tasks / total_tasks)
            st.caption(f"{completed_tasks} of {total_tasks} tasks completed.")

# =======================================================
# 💬 TAB 3 - MOTIVATOR CHATBOT
# =======================================================
with tab3:
    st.subheader("💬 AI Motivator Chatbot (Offline)")
    st.caption("Ask for motivation, study tips, or guidance!")

    user_input = st.text_input("You:", placeholder="Type your question or message...")
    if st.button("Send"):
        if user_input.strip():
            responses = [
                "Keep pushing forward — your consistency will define your success. 🚀",
                "Learning is a journey, not a race. One step at a time. 🌱",
                "You're doing amazing! Remember why you started. 💫",
                "Mistakes mean you're trying. Keep experimenting and learning. 🔥",
                "Believe in progress, not perfection. Each effort counts! 💡"
            ]
            reply = random.choice(responses)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", reply))
        else:
            st.warning("Please type a message first.")

    if st.session_state.chat_history:
        for speaker, msg in st.session_state.chat_history[::-1]:
            if speaker == "You":
                st.markdown(f"🧠 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")
