import streamlit as st
import plotly.graph_objects as go
import json
import os
import streamlit_ace as ace

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path 2.0", layout="wide")

# ------------------ STYLE ------------------
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00b7ff, #0077ff);
    }
    .course-card {
        background: #1b1f27;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0, 183, 255, 0.15);
        transition: 0.3s;
    }
    .course-card:hover {
        box-shadow: 0px 4px 25px rgba(0, 183, 255, 0.4);
        transform: scale(1.03);
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        color: #00b7ff;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ DATA ------------------
courses = [
    "Python Programming", "C Programming", "Data Structures & Algorithms",
    "Database Management Systems", "Operating Systems",
    "Computer Networks", "Artificial Intelligence",
    "Machine Learning", "Web Development"
]

progress_file = "progress.json"
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        saved_progress = json.load(f)
else:
    saved_progress = {course: 0 for course in courses}

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

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("<div class='sidebar-title'>⚡ Control Hub</div>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🤖 AI Mentor", "💻 Code Runner", "🧘 Spectorial Mode", "🗒 Goals & Notes"],
    label_visibility="collapsed"
)

# ------------------ MAIN PAGES ------------------
if page == "🏠 Dashboard":
    st.title("💎 CSE Learning Path — Sleek Pro+ (Cyber Blue Edition)")
    st.markdown("### 🚀 Track, Learn & Elevate Your Skills")

    cols = st.columns(3)
    for i, course in enumerate(courses):
        col = cols[i % 3]
        with col:
            st.markdown(f"<div class='course-card'>", unsafe_allow_html=True)
            fig = create_gauge(saved_progress.get(course, 0), course)
            st.plotly_chart(fig, use_container_width=True)
            new_val = st.slider(f"Progress for {course}", 0, 100, saved_progress.get(course, 0))
            saved_progress[course] = new_val
            save_progress(saved_progress)
            if st.button(f"Ask AI about {course}", key=course):
                st.session_state["ai_prompt"] = f"Explain more about {course} in simple terms."
                st.success(f"🤖 AI prompt set for: {course}")
            st.markdown("</div>", unsafe_allow_html=True)

elif page == "🤖 AI Mentor":
    st.title("🤖 AI Mentor")
    st.markdown("### Ask questions, clarify concepts, or seek course guidance.")
    user_query = st.text_input("Ask your AI Mentor:")
    if st.button("Send"):
        if user_query.strip():
            st.info(f"💬 Query sent: {user_query}")
        elif "ai_prompt" in st.session_state:
            st.info(f"💬 Sending last course prompt: {st.session_state['ai_prompt']}")
        else:
            st.warning("Please enter a question or use the Dashboard Ask AI buttons.")

elif page == "💻 Code Runner":
    st.title("💻 Code Runner")
    st.markdown("### Test Python code safely within your dashboard.")
    code = ace.st_ace(
        value="print('Hello, Moscifer!')",
        language="python",
        theme="monokai",
        key="ace_editor",
        height=300
    )
    if st.button("Run Code"):
        try:
            exec_output = {}
            exec(code, {}, exec_output)
            st.success(f"✅ Output:\n{exec_output}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

elif page == "🧘 Spectorial Mode":
    st.title("🧘 Spectorial Mode")
    st.markdown("Enter your reflective state — observe and write your realizations.")
    reflection = st.text_area("Your reflections:", placeholder="Write your thoughts in Spectorial Consciousness mode...")
    if st.button("Save Reflection"):
        st.success("🪶 Reflection saved. You’re ascending through awareness, Moscifer.")

elif page == "🗒 Goals & Notes":
    st.title("🗒 Goals & Notes")
    daily_goal = st.text_input("🎯 Today's Goal:")
    note = st.text_area("📓 Notes:")
    if st.button("Save"):
        st.success("✅ Goal & Notes saved for today!")

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 Moscifer — Sleek Pro+ Dashboard (Cyber Blue Edition)")
