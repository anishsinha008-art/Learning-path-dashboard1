# app_cyber_blue.py
"""
CSE Learning Path — Cyber Blue (Dynamic)
- Dynamic course progress (sliders + gauges with centered percent)
- Expanded course list
- Local persistence to progress.json
- Simple AI Mentor scaffold (offline fallback); clicking Ask AI sends contextual prompt to chat
"""

import os
import json
import time
import random
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests

# ------------------ CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path — Cyber Blue", layout="wide")
PERSIST_FILE = "progress.json"

# ------------------ STYLES (CYBER BLUE) ------------------
CYBER_CSS = """
<style>
:root {
  --bg: #0b0d10;
  --card: #0f1417;
  --muted: #9fb7c9;
  --accent: #00d1ff;
  --glass: rgba(255,255,255,0.02);
}
.stApp {
  background: linear-gradient(180deg,var(--bg) 0%, #060708 100%);
  color: #e6f7fb;
  font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}
.header-row { display:flex; align-items:center; gap:12px; }
.app-title { font-size:20px; font-weight:700; color:#e7fbff; }
.app-sub { color:var(--muted); font-size:13px; }
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.015), rgba(255,255,255,0.01));
  border-radius:12px; padding:14px; border:1px solid rgba(0,209,255,0.06);
  box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}
.course-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:14px; }
.course-card { padding:10px; border-radius:10px; }
.slider-compact .stSlider > div { padding: 4px 0; }
.small-muted { color:var(--muted); font-size:13px; }
.kpi { color:var(--accent); font-weight:700; font-size:22px; }
.center-note { text-align:center; color:var(--muted); font-size:13px; margin-top:8px; }
.chat-area { max-height:42vh; overflow-y:auto; padding-right:6px; }
.bubble-user { margin:8px; padding:10px 12px; background: linear-gradient(180deg,#022b35,#013b47); border-radius:12px; color:#eaffff; align-self:flex-end; max-width:84%; }
.bubble-bot { margin:8px; padding:10px 12px; background: linear-gradient(180deg,#082026,#05292f); border-radius:12px; color:#dff9ff; align-self:flex-start; max-width:84%; }
</style>
"""
st.markdown(CYBER_CSS, unsafe_allow_html=True)

# ------------------ UTILITIES ------------------
def now_iso():
    return pd.Timestamp.utcnow().isoformat()

def save_progress(df, chat_history):
    try:
        payload = {
            "courses": df.to_dict(orient="records"),
            "chat_history": chat_history,
            "saved_at": now_iso()
        }
        with open(PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return True
    except Exception as e:
        st.warning(f"Could not save progress: {e}")
        return False

def load_progress():
    if not os.path.exists(PERSIST_FILE):
        return None, []
    try:
        with open(PERSIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        courses = data.get("courses")
        chat_history = data.get("chat_history", [])
        if courses:
            return pd.DataFrame(courses), chat_history
        return None, chat_history
    except Exception as e:
        st.warning(f"Could not load progress: {e}")
        return None, []

# ------------------ DEFAULT COURSES ------------------
DEFAULT_COURSES = [
    {"Course": "Python Programming", "Completion": 72, "Status": "In Progress"},
    {"Course": "C Programming", "Completion": 40, "Status": "In Progress"},
    {"Course": "Data Structures & Algorithms", "Completion": 35, "Status": "In Progress"},
    {"Course": "Database Management Systems (DBMS)", "Completion": 28, "Status": "In Progress"},
    {"Course": "Operating Systems", "Completion": 20, "Status": "Not Started"},
    {"Course": "Computer Networks", "Completion": 18, "Status": "Not Started"},
    {"Course": "Artificial Intelligence", "Completion": 15, "Status": "Not Started"},
    {"Course": "Machine Learning", "Completion": 12, "Status": "Not Started"},
    {"Course": "Web Development (HTML/CSS/JS)", "Completion": 50, "Status": "In Progress"},
]

# ------------------ SESSION STATE ------------------
if "courses" not in st.session_state:
    df_loaded, chat_loaded = load_progress()
    if df_loaded is None:
        st.session_state.courses = pd.DataFrame(DEFAULT_COURSES)
    else:
        st.session_state.courses = df_loaded
    st.session_state.chat_history = chat_loaded or []
    st.session_state.topic_memory = None

# ------------------ SIMULATED AI (fallback) ------------------
def simulated_reply(prompt: str):
    p = prompt.lower()
    if "python" in p:
        return "Python tip: practice list comprehensions and use virtual environments for projects."
    if "data structure" in p or "algorithm" in p:
        return "Start with arrays, linked lists, stacks and queues. Then try sorting and binary search."
    if "os" in p or "operating system" in p:
        return "Understand processes, threads, scheduling, and memory management basics."
    if "network" in p or "computer networks" in p:
        return "Learn the OSI model and basic TCP/IP concepts; try packet tracing tools later."
    if "ai" in p or "machine learning" in p:
        return "Begin with linear algebra and probability; try a small classification project with scikit-learn."
    if "web" in p:
        return "Practice building a simple responsive site using HTML, CSS, and vanilla JS before frameworks."
    if "exercise" in p or "problem" in p:
        return "Exercise: implement binary search on a sorted array and return index or -1."
    return random.choice([
        "Tell me which course you'd like a study plan for.",
        "Would you like a mini exercise, project idea, or debugging help?",
        "I can generate a 7-day plan for practice — want that?"
    ])

# ------------------ LAYOUT: HEADER ------------------
st.markdown("<div class='header-row'><img src='https://cdn-icons-png.flaticon.com/512/1055/1055687.png' width=36>"
            f"<div><div class='app-title'>CSE Learning Path — Cyber Blue</div><div class='app-sub'>Dynamic progress, AI mentor, local save</div></div></div>",
            unsafe_allow_html=True)
st.markdown("---")

# ------------------ MAIN LAYOUT ------------------
left, right = st.columns([2.4, 1])

# LEFT: Course grid and charts
with left:
    # Top KPIs
    overall = int(np.clip(st.session_state.courses["Completion"].mean(), 0, 100))
    top_course = st.session_state.courses.loc[st.session_state.courses['Completion'].idxmax()]['Course']
    k1, k2 = st.columns([1, 1])
    with k1:
        st.markdown(f"<div class='card'><div class='small-muted'>Overall Progress</div><div class='kpi'>{overall}%</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='card'><div class='small-muted'>Top Course</div><div class='kpi'>{top_course}</div></div>", unsafe_allow_html=True)

    st.markdown("")

    # Courses grid (dynamic gauges + sliders)
    st.subheader("Courses")
    st.markdown("<div class='card'><div class='course-grid'>", unsafe_allow_html=True)

    courses_df = st.session_state.courses.reset_index(drop=True)

    # create 3-column responsive layout using streamlit columns
    num_cols = 3
    cols = st.columns(num_cols)
    for i, row in courses_df.iterrows():
        column = cols[i % num_cols]
        with column:
            course_name = row["Course"]
            completion = int(row["Completion"])
            status = row.get("Status", "In Progress")
            # Card wrapper
            st.markdown(f"<div class='card course-card'>", unsafe_allow_html=True)

            # Gauge: centered percentage using plotly indicator
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=completion,
                number={"suffix": "%", "font": {"size": 36, "color": "#00d1ff", "family": "Inter, sans-serif"}},
                gauge={
                    "axis": {"range": [0, 100], "visible": False},
                    "bar": {"color": "#00d1ff"},
                    "bgcolor": "rgba(255,255,255,0.02)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 50], "color": "rgba(0,209,255,0.06)"},
                        {"range": [50, 100], "color": "rgba(0,209,255,0.10)"}
                    ],
                    "threshold": {
                        "line": {"color": "#00d1ff", "width": 2},
                        "thickness": 0.75,
                        "value": completion
                    }
                }
            ))
            gauge.update_layout(height=200, margin={"t": 10, "b": 0, "l":0, "r":0}, paper_bgcolor="rgba(0,0,0,0)", font_color="#e6f7fb")
            st.plotly_chart(gauge, use_container_width=True)

            st.markdown(f"<div style='font-weight:700'>{course_name}</div><div class='small-muted'>Status: {status}</div>", unsafe_allow_html=True)

            # slider to update progress (compact)
            new_val = st.slider(f"slider_{i}", 0, 100, completion, key=f"slider_{i}")
            if new_val != completion:
                # update main df and persist
                st.session_state.courses.at[i, "Completion"] = int(new_val)
                if new_val == 100:
                    st.session_state.courses.at[i, "Status"] = "Completed"
                elif new_val == 0:
                    st.session_state.courses.at[i, "Status"] = "Not Started"
                else:
                    st.session_state.courses.at[i, "Status"] = "In Progress"
                # save immediately
                save_progress(st.session_state.courses, st.session_state.chat_history)
                # visually update (no full rerun required, but safe to rerun to refresh gauges)
                st.experimental_rerun()

            # Quick AI action button
            if st.button(f"Ask AI about {course_name}", key=f"ask_{i}"):
                prompt = f"Give a short study plan for {course_name} at {st.session_state.courses.at[i,'Completion']}% completion."
                st.session_state.chat_history.append({"sender":"user","message":prompt,"ts":now_iso()})
                # try to call external provider? fallback to simulated
                reply = simulated_reply(prompt)
                st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
                save_progress(st.session_state.courses, st.session_state.chat_history)
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Weekly progress bar (derived)
    st.subheader("Weekly Growth (derived)")
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    base = int(st.session_state.courses["Completion"].mean())
    weekly = [int(np.clip(base + (i-1) * 4, 0, 100)) for i in range(4)]
    bar = go.Figure(go.Bar(x=weeks, y=weekly, text=weekly, textposition='auto', marker={"color":"#00d1ff"}))
    bar.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin={"t":10,"b":10})
    st.plotly_chart(bar, use_container_width=True)

# RIGHT: Chat, Save/Load, Quick actions
with right:
    st.markdown("<div class='card'><div style='font-weight:700'>AI Mentor</div><div class='small-muted'>Ask course-specific questions or general study advice.</div></div>", unsafe_allow_html=True)
    st.markdown("")

    # show chat history
    st.markdown("<div class='card chat-area'>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        for m in st.session_state.chat_history[-60:]:
            if m.get("sender") == "user":
                st.markdown(f"<div class='bubble-user'><b>You:</b> {m.get('message')}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bubble-bot'><b>Mentor:</b> {m.get('message')}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-muted'>No conversation yet. Use 'Ask AI' buttons or type a message below.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # chat input
    with st.form("chat_form", clear_on_submit=True):
        user_text = st.text_input("Send message to Mentor (type 'bye' to clear memory)")
        submit = st.form_submit_button("Send")
        if submit and user_text and user_text.strip():
            st.session_state.chat_history.append({"sender":"user","message":user_text.strip(),"ts":now_iso()})
            if user_text.strip().lower() in ("bye","goodbye","reset memory"):
                reply = "👋 Memory cleared."
                st.session_state.topic_memory = None
                st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
            else:
                # try external provider (not implemented here) -> fallback simulated
                reply = simulated_reply(user_text.strip())
                st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
            save_progress(st.session_state.courses, st.session_state.chat_history)
            st.experimental_rerun()

    st.markdown("---")

    # Save / Load
    if st.button("Save Progress Now"):
        ok = save_progress(st.session_state.courses, st.session_state.chat_history)
        if ok:
            st.success("Progress saved to progress.json")
    if st.button("Load Progress"):
        loaded_df, loaded_chat = load_progress()
        if loaded_df is not None:
            st.session_state.courses = loaded_df
            st.session_state.chat_history = loaded_chat
            st.success("Loaded progress from progress.json")
            st.experimental_rerun()
        else:
            st.info("No saved progress file found.")

    st.markdown("---")
    st.markdown("<div class='card'><div style='font-weight:700'>Quick Actions</div><div class='small-muted'>Shortcuts</div></div>", unsafe_allow_html=True)
    if st.button("Add Demo Progress +10% to all"):
        st.session_state.courses["Completion"] = (st.session_state.courses["Completion"] + 10).clip(0, 100)
        # adjust statuses
        st.session_state.courses["Status"] = st.session_state.courses["Completion"].apply(lambda v: "Completed" if v==100 else ("Not Started" if v==0 else "In Progress"))
        save_progress(st.session_state.courses, st.session_state.chat_history)
        st.experimental_rerun()
    if st.button("Reset All Progress to 0"):
        st.session_state.courses["Completion"] = 0
        st.session_state.courses["Status"] = "Not Started"
        save_progress(st.session_state.courses, st.session_state.chat_history)
        st.experimental_rerun()

# Footer
st.markdown("<div style='text-align:center; margin-top:14px; color:#9fb7c9'>Cyber Blue • CSE Learning Path — saved locally in progress.json</div>", unsafe_allow_html=True)
