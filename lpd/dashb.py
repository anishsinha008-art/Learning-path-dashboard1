# learning_dashboard.py
# 🚀 Enhanced Learning Path Dashboard — Cyber Blue Theme (Debugged & Optimized)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
from datetime import datetime

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ FILE PATHS ------------------
DATA_FILE = "learning_data.json"

# ------------------ LOAD / SAVE FUNCTIONS ------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"courses": [], "planner": [], "chat_history": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ INITIALIZE SESSION STATE ------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

data = st.session_state.data

# ------------------ CYBER BLUE THEME CSS ------------------
st.markdown(
    """
    <style>
    body {
        background-color: #0b0f1a;
        color: #cfe3ff;
        font-family: 'Poppins', sans-serif;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00bfff, #0066ff);
        color: white;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0066ff, #00bfff);
        transform: scale(1.05);
    }
    .stTextInput > div > div > input {
        background-color: #10172a;
        color: white;
        border-radius: 8px;
    }
    .metric-box {
        background: rgba(0, 102, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ HEADER ------------------
st.title("💻 CSE Learning Path Dashboard")
st.subheader("🚀 Empower your learning journey with interactive progress tracking")

# ------------------ ADD NEW COURSE ------------------
st.sidebar.header("📘 Add New Course")
course_name = st.sidebar.text_input("Course Name")
total_topics = st.sidebar.number_input("Total Topics", min_value=1, max_value=100, value=10)
if st.sidebar.button("Add Course"):
    new_course = {"name": course_name, "progress": 0, "topics": total_topics}
    data["courses"].append(new_course)
    save_data(data)
    st.sidebar.success(f"Course '{course_name}' added!")

# ------------------ COURSE SELECTION ------------------
course_names = [c["name"] for c in data["courses"]]
if course_names:
    selected_course = st.selectbox("Select a Course", course_names)
    course = next((c for c in data["courses"] if c["name"] == selected_course), None)
else:
    st.warning("No courses added yet. Please add a course in the sidebar.")
    st.stop()

# ------------------ PROGRESS TRACKER ------------------
st.subheader(f"📊 Progress — {course['name']}")

progress = st.slider("Update your progress (%)", 0, 100, course["progress"])
if progress != course["progress"]:
    course["progress"] = progress
    save_data(data)

# Gauge chart (progress in center)
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=course["progress"],
        title={"text": "Progress", "font": {"size": 20}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00bfff"},
            "bgcolor": "#0b0f1a",
            "borderwidth": 2,
            "bordercolor": "#0066ff",
            "steps": [
                {"range": [0, 50], "color": "#102030"},
                {"range": [50, 100], "color": "#0b1f3a"},
            ],
        },
        number={"font": {"color": "#00bfff", "size": 40}},
    )
)
fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig, use_container_width=True)

# ------------------ COURSE METRICS ------------------
cols = st.columns(3)
with cols[0]:
    st.markdown(
        f"<div class='metric-box'><h4>Total Topics</h4><h2>{course['topics']}</h2></div>",
        unsafe_allow_html=True,
    )
with cols[1]:
    completed = int(course['topics'] * course['progress'] / 100)
    st.markdown(
        f"<div class='metric-box'><h4>Completed</h4><h2>{completed}</h2></div>",
        unsafe_allow_html=True,
    )
with cols[2]:
    remaining = course['topics'] - completed
    st.markdown(
        f"<div class='metric-box'><h4>Remaining</h4><h2>{remaining}</h2></div>",
        unsafe_allow_html=True,
    )

# ------------------ PLANNER ------------------
st.subheader("🗓️ Study Planner")
task = st.text_input("Add a new task")
if st.button("Add Task"):
    if task:
        data["planner"].append({"task": task, "done": False, "created": str(datetime.now())})
        save_data(data)
        st.success("Task added!")

if data["planner"]:
    for i, t in enumerate(data["planner"]):
        cols = st.columns([0.05, 0.7, 0.25])
        done = cols[0].checkbox("", t["done"], key=f"task_{i}")
        cols[1].write(f"{'✅ ' if done else '🕒 '}{t['task']}")
        if cols[2].button("❌ Remove", key=f"remove_{i}"):
            data["planner"].pop(i)
            save_data(data)
            st.experimental_rerun()
        if done != t["done"]:
            t["done"] = done
            save_data(data)

# ------------------ CHATBOT SIMULATION ------------------
st.subheader("💬 Motivator Bot")
prompt = st.text_input("Say something to your motivator bot")
if st.button("Send"):
    responses = [
        "Keep going! You’re doing amazing! 🚀",
        "Every step counts — progress is power. 💪",
        "Don’t give up now; success is closer than you think! 🌟",
        "Your effort defines your excellence. 🔥",
    ]
    reply = np.random.choice(responses)
    st.session_state.data["chat_history"].append({"user": prompt, "bot": reply})
    save_data(st.session_state.data)

if data["chat_history"]:
    for chat in reversed(data["chat_history"][-5:]):
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")

# ------------------ FOOTER ------------------
st.markdown(
    """
    <hr>
    <center>
    <p style='color:#4fc3f7;'>Made with 💙 by your AI Learning Assistant</p>
    </center>
    """,
    unsafe_allow_html=True,
)
