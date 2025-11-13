import streamlit as st
import plotly.graph_objects as go
import json
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path 2.0", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00b7ff, #0077ff);
    }
    .course-card {
        background: #1b1f27;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0, 183, 255, 0.1);
        transition: 0.3s;
    }
    .course-card:hover {
        box-shadow: 0px 4px 20px rgba(0, 183, 255, 0.3);
        transform: scale(1.02);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ DATA SETUP ------------------
courses = [
    "Python Programming", "C Programming", "Data Structures & Algorithms",
    "Database Management Systems", "Operating Systems",
    "Computer Networks", "Artificial Intelligence",
    "Machine Learning", "Web Development"
]

progress_file = "progress.json"

# Load saved progress
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        saved_progress = json.load(f)
else:
    saved_progress = {course: 0 for course in courses}

# ------------------ FUNCTIONS ------------------
def save_progress(data):
    with open(progress_file, "w") as f:
        json.dump(data, f, indent=4)

def create_gauge(value, course):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={'font': {'size': 28, 'color': '#00bfff'}, 'suffix': "%"},
            title={'text': course, 'font': {'size': 16, 'color': '#e0e0e0'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 0},
                'bar': {'color': '#00bfff'},
                'bgcolor': "#1b1f27",
                'borderwidth': 1,
                'bordercolor': "#00bfff",
                'steps': [
                    {'range': [0, 50], 'color': "#112233"},
                    {'range': [50, 100], 'color': "#0f172a"}
                ],
            }
        )
    )
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="#1b1f27",
        font=dict(color="#e0e0e0")
    )
    return fig

# ------------------ MAIN DASHBOARD ------------------
st.title("💎 CSE Learning Path Dashboard — Sleek Pro (Cyber Blue Edition)")
st.markdown("### 🚀 Track, Learn & Elevate Your Skills")

cols = st.columns(3)

for i, course in enumerate(courses):
    col = cols[i % 3]
    with col:
        st.markdown(f"<div class='course-card'>", unsafe_allow_html=True)
        # Gauge chart
        fig = create_gauge(saved_progress.get(course, 0), course)
        st.plotly_chart(fig, use_container_width=True)
        # Slider for dynamic update
        new_val = st.slider(f"Progress for {course}", 0, 100, saved_progress.get(course, 0))
        saved_progress[course] = new_val
        # Save progress after each update
        save_progress(saved_progress)
        # Ask AI button
        if st.button(f"Ask AI about {course}", key=course):
            st.session_state["ai_prompt"] = f"Explain more about {course} in simple terms."
            st.success(f"🤖 AI prompt set for: {course}")
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.markdown("#### 🧠 AI Mentor (DeepSeek / Offline Mode)")
user_query = st.text_input("Ask anything about your courses:")
if st.button("Send to AI"):
    if "ai_prompt" in st.session_state:
        st.info(f"💬 Sending prompt: {st.session_state['ai_prompt']}")
    elif user_query.strip() != "":
        st.info(f"💬 Sending custom query: {user_query}")
    else:
        st.warning("Please enter a question or use the Ask AI button first!")

st.markdown("---")
st.caption("© 2025 Moscifer — Sleek Pro Dashboard (Cyber Blue Edition)")

