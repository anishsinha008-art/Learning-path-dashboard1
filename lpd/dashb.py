# futuristic_dashboard.py
# Run with: streamlit run futuristic_dashboard.py

import streamlit as st
import time
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Cyber Learning Dashboard", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
        body {
            background-color: #020617;
            color: #00e5ff;
        }
        .title {
            text-align: center;
            font-size: 40px;
            font-weight: 700;
            color: #00e5ff;
            text-shadow: 0 0 15px #00e5ff;
            margin-bottom: 20px;
        }
        .course-card {
            background: rgba(0, 229, 255, 0.05);
            border: 1px solid #00e5ff33;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 0 15px #00e5ff22;
            transition: 0.3s ease;
        }
        .course-card:hover {
            transform: scale(1.02);
            box-shadow: 0 0 25px #00e5ff44;
        }
        .course-title {
            color: #00e5ff;
            font-size: 22px;
            font-weight: 600;
            text-align: center;
        }
        .progress-container {
            text-align: center;
            color: white;
        }
        .stProgress > div > div > div > div {
            background-color: #00e5ff !important;
        }
        .add-button {
            background-color: #00e5ff;
            color: #000;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
            border: none;
        }
        .add-button:hover {
            background-color: #00ffff;
            color: #000;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("<div class='title'>⚡ Cyber Learning Dashboard ⚡</div>", unsafe_allow_html=True)

# ------------------ INITIALIZE COURSES ------------------
if "courses" not in st.session_state:
    st.session_state.courses = [
        {"name": "Python Basics", "progress": 60},
        {"name": "Web Development", "progress": 40},
        {"name": "AI & ML", "progress": 20},
        {"name": "Cyber Security", "progress": 35}
    ]

# ------------------ COURSE DISPLAY ------------------
cols = st.columns(2)
for i, course in enumerate(st.session_state.courses):
    with cols[i % 2]:
        st.markdown(f"<div class='course-card'><div class='course-title'>{course['name']}</div></div>", unsafe_allow_html=True)
        st.progress(course["progress"] / 100)
        st.write(f"Progress: **{course['progress']}%**")
        new_value = st.slider(f"Update {course['name']} progress", 0, 100, course["progress"], key=f"slider_{i}")
        st.session_state.courses[i]["progress"] = new_value
        st.write("---")

# ------------------ ADD COURSE ------------------
st.subheader("➕ Add a New Course")
new_course = st.text_input("Enter course name:")
if st.button("Add Course", key="add_course", help="Click to add new course"):
    if new_course.strip() != "":
        st.session_state.courses.append({"name": new_course.strip(), "progress": 0})
        st.success(f"✅ Added new course: {new_course}")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("⚠️ Please enter a valid course name.")

# ------------------ DYNAMIC MESSAGE ------------------
motivations = [
    "Keep going — your future self will thank you!",
    "Every bit of progress counts ⚡",
    "Stay focused and keep pushing!",
    "You're mastering your path — one course at a time!"
]
st.markdown(f"<p style='text-align:center;color:#00e5ff;margin-top:30px;font-size:18px;'>{random.choice(motivations)}</p>", unsafe_allow_html=True)
