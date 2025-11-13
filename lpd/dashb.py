# learning_dashboard.py
# 🚀 Enhanced Learning Path Dashboard — Cyber Blue Theme (with File Uploads per Course)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path

# ------------------ CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")
DATA_FILE = "learning_data.json"
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# ------------------ HELPERS: load/save ------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # default structure includes uploads mapping course -> list
    return {"courses": [], "planner": [], "chat_history": [], "uploads": {}}

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=4, ensure_ascii=False)

def safe_course_folder(course_name: str) -> Path:
    safe_name = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in course_name).strip().replace(" ", "_")
    folder = UPLOADS_DIR / safe_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_uploaded_file(course_name: str, uploaded_file) -> dict:
    """Save uploaded file to disk and return metadata dict."""
    folder = safe_course_folder(course_name)
    filename = uploaded_file.name
    # avoid accidental overwrite: append timestamp if file exists
    target = folder / filename
    if target.exists():
        stem = target.stem
        suffix = target.suffix
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target = folder / f"{stem}_{timestamp}{suffix}"
    # write bytes
    with open(target, "wb") as f:
        f.write(uploaded_file.getbuffer())
    meta = {
        "filename": target.name,
        "path": str(target.as_posix()),
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "size_bytes": target.stat().st_size
    }
    return meta

# ------------------ INITIALIZE ------------------
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None

data = st.session_state.data

# ------------------ THEME CSS ------------------
st.markdown(
    """
    <style>
    body { background-color: #0b0f1a; color: #cfe3ff; font-family: 'Poppins', sans-serif; }
    .stButton > button { background: linear-gradient(90deg, #00bfff, #0066ff); color: white; border-radius: 12px; border: none; font-weight: bold; transition: 0.15s; }
    .stButton > button:hover { transform: scale(1.03); }
    .metric-box { background: rgba(0, 102, 255, 0.08); padding: 12px; border-radius: 10px; text-align: center; }
    .card { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(0,102,255,0.06); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ HEADER ------------------
st.title("💻 CSE Learning Path Dashboard")
st.subheader("🚀 Empower your learning journey — now with per-course file uploads")

# ------------------ SIDEBAR: Add Course ------------------
st.sidebar.header("📘 Add New Course")
course_name = st.sidebar.text_input("Course Name")
total_topics = st.sidebar.number_input("Total Topics", min_value=1, max_value=500, value=10)
if st.sidebar.button("Add Course"):
    if not course_name.strip():
        st.sidebar.error("Please provide a course name.")
    else:
        new_course = {"name": course_name.strip(), "progress": 0, "topics": int(total_topics)}
        data["courses"].append(new_course)
        # ensure uploads mapping exists for the course
        if course_name.strip() not in data.get("uploads", {}):
            data.setdefault("uploads", {})[course_name.strip()] = []
        save_data(data)
        st.sidebar.success(f"Course '{course_name.strip()}' added!")
        st.experimental_rerun()

# ------------------ COURSE SELECTION ------------------
course_names = [c["name"] for c in data["courses"]]
if not course_names:
    st.warning("No courses added yet. Add a course in the sidebar to start.")
    st.stop()

selected = st.selectbox("Select a Course", course_names)
course = next((c for c in data["courses"] if c["name"] == selected), None)
st.markdown(f"### 📚 Course: **{course['name']}**")

# ------------------ UPLOADS: File Upload Per Course ------------------
st.subheader("📎 Course Materials — Upload & Manage Files")

# file uploader (allow multiple)
uploaded_files = st.file_uploader("Upload files for this course (PDF, PNG, PPTX, ZIP, etc.)", type=None, accept_multiple_files=True)

if uploaded_files:
    saved_meta = []
    for f in uploaded_files:
        try:
            meta = save_uploaded_file(course['name'], f)
            # record in JSON structure under course
            data.setdefault("uploads", {})
            data["uploads"].setdefault(course['name'], [])
            data["uploads"][course['name']].append(meta)
            saved_meta.append(meta)
        except Exception as e:
            st.error(f"Failed to save {f.name}: {e}")
    if saved_meta:
        save_data(data)
        st.success(f"Saved {len(saved_meta)} file(s) to uploads for course '{course['name']}'")
        st.experimental_rerun()

# show existing uploads for this course
course_uploads = data.get("uploads", {}).get(course['name'], [])
if course_uploads:
    st.markdown("**Uploaded files:**")
    for i, meta in enumerate(course_uploads):
        fn = meta.get("filename", "unknown")
        uploaded_at = meta.get("uploaded_at", "")
        size_kb = int(meta.get("size_bytes", 0) // 1024)
        cols = st.columns([3, 1, 1])
        cols[0].markdown(f"📄 **{fn}**  \n<small>Uploaded: {uploaded_at}</small>", unsafe_allow_html=True)
        # Download button: read bytes and present as download
        file_path = meta.get("path", "")
        try:
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as fh:
                    file_bytes = fh.read()
                cols[1].download_button(label=f"⬇️ {size_kb} KB", data=file_bytes, file_name=fn, mime="application/octet-stream")
            else:
                cols[1].write("⚠️ Missing")
        except Exception as e:
            cols[1].write("Err")
        # delete
        if cols[2].button("🗑️ Delete", key=f"del_upload_{course['name']}_{i}"):
            # remove file from disk if exists
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            # remove metadata entry
            data["uploads"][course['name']].pop(i)
            save_data(data)
            st.success(f"Deleted {fn}")
            st.experimental_rerun()
else:
    st.info("No files uploaded for this course yet. Use the uploader above to add materials.")

st.markdown("---")

# ------------------ PROGRESS TRACKER ------------------
st.subheader(f"📊 Progress — {course['name']}")
progress = st.slider("Update your progress (%)", 0, 100, course.get("progress", 0), key=f"progress_{course['name']}")
if progress != course.get("progress", 0):
    course['progress'] = int(progress)
    save_data(data)

# Gauge chart (progress)
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=course["progress"],
        title={"text": "Progress", "font": {"size": 18}},
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
        number={"font": {"color": "#00bfff", "size": 36}},
    )
)
fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig, use_container_width=True)

# ------------------ METRICS ------------------
cols = st.columns(3)
with cols[0]:
    st.markdown(f"<div class='metric-box'><h4>Total Topics</h4><h2>{course.get('topics', 0)}</h2></div>", unsafe_allow_html=True)
with cols[1]:
    completed = int(course.get('topics', 0) * course.get('progress', 0) / 100)
    st.markdown(f"<div class='metric-box'><h4>Completed</h4><h2>{completed}</h2></div>", unsafe_allow_html=True)
with cols[2]:
    remaining = course.get('topics', 0) - completed
    st.markdown(f"<div class='metric-box'><h4>Remaining</h4><h2>{remaining}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ------------------ PLANNER (compact) ------------------
st.subheader("🗓️ Study Planner")
task = st.text_input("Add a new task")
if st.button("Add Task"):
    if task.strip():
        data.setdefault("planner", []).append({"task": task.strip(), "done": False, "created": str(datetime.now())})
        save_data(data)
        st.success("Task added!")
        st.experimental_rerun()

if data.get("planner"):
    for i, t in enumerate(data["planner"]):
        cols = st.columns([0.05, 0.75, 0.2])
        done = cols[0].checkbox("", t["done"], key=f"task_{i}")
        cols[1].write(f"{'✅ ' if done else '🕒 '}{t['task']}")
        if cols[2].button("❌ Remove", key=f"remove_{i}"):
            data["planner"].pop(i)
            save_data(data)
            st.experimental_rerun()
        if done != t["done"]:
            t["done"] = done
            save_data(data)

st.markdown("---")

# ------------------ CHATBOT SIM ------------------
st.subheader("💬 Motivator Bot")
prompt = st.text_input("Say something to your motivator bot", key="bot_prompt")
if st.button("Send", key="send_bot"):
    if prompt.strip():
        responses = [
            "Keep going! You’re doing amazing! 🚀",
            "Every step counts — progress is power. 💪",
            "Don’t give up now; success is closer than you think! 🌟",
            "Your effort defines your excellence. 🔥",
        ]
        reply = np.random.choice(responses)
        data.setdefault("chat_history", []).append({"user": prompt.strip(), "bot": reply, "time": datetime.utcnow().isoformat()})
        save_data(data)
        st.success("Bot replied!")
        st.experimental_rerun()

if data.get("chat_history"):
    for chat in reversed(data["chat_history"][-6:]):
        st.markdown(f"**You:** {chat.get('user','')}  \n**Bot:** {chat.get('bot','')}  \n<small>{chat.get('time','')}</small>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.markdown(
    """
    <hr>
    <center>
    <p style='color:#4fc3f7;'>Made with 💙 by your AI Learning Assistant — Files saved locally in /uploads</p>
    </center>
    """,
    unsafe_allow_html=True,
)
