import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="CSE Learning Path Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "A dashboard to track CSE skill progress."}
)

# ------------------ CONSTANTS & HELPERS ------------------
COURSE_DIR = "courses"

# Define gauge steps once (DRY principle)
GAUGE_STEPS = [
    {'range': [0, 50], 'color': "#ffcccc"},
    {'range': [50, 80], 'color': "#fff3cd"},
    {'range': [80, 100], 'color': "#d4edda"}
]

def setup_course_files():
    """Creates 'courses' directory and sample files if missing."""
    os.makedirs(COURSE_DIR, exist_ok=True)

    sample_chapters = {
        "python_programming.txt": """--- Chapter 1: Basics ---
- Variables and Data Types
- Operators
- Input/Output

--- Chapter 2: Control Flow ---
- Conditional Statements (if/else)
- Loops (for/while)

--- Chapter 3: Functions ---
- Defining Functions
- Arguments and Return Values
- Lambda Functions
""",
        "data_structures_and_algorithms.txt": """--- Unit 1: Basic Data Structures ---
- Arrays and Lists
- Stacks and Queues
- Linked Lists
- Hash Tables

--- Unit 2: Trees ---
- Binary Trees
- Binary Search Trees (BST)
- AVL Trees

--- Unit 3: Sorting Algorithms ---
- Bubble Sort
- Merge Sort
- Quick Sort
""",
        "machine_learning.txt": """--- Module 1: Introduction ---
- What is Machine Learning?
- Supervised vs. Unsupervised Learning

--- Module 2: Supervised Learning ---
- Linear Regression
- Logistic Regression
- Support Vector Machines (SVM)

--- Module 3: Unsupervised Learning ---
- K-Means Clustering
- Principal Component Analysis (PCA)
"""
    }

    for filename, content in sample_chapters.items():
        filepath = os.path.join(COURSE_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

setup_course_files()

# ------------------ DATA ------------------
@st.cache_data
def load_data():
    data = {
        "Skill": [
            "Python Programming", "Data Structures & Algorithms", "Operating Systems",
            "Database Management Systems", "Computer Networks", "Artificial Intelligence",
            "Machine Learning", "Deep Learning", "Web Development", "Cloud Computing",
            "Cybersecurity", "Software Engineering", "Internet of Things (IoT)",
            "Blockchain Technology", "DevOps"
        ],
        "Progress": [85, 78, 65, 72, 68, 60, 55, 48, 70, 52, 50, 74, 58, 40, 45],
        "Courses Completed": [5, 4, 3, 4, 3, 2, 2, 1, 3, 2, 2, 4, 2, 1, 1],
        "Total Courses": [6, 5, 4, 5, 4, 4, 3, 3, 4, 3, 3, 5, 3, 3, 3]
    }
    df = pd.DataFrame(data)
    df["Completion %"] = (df["Courses Completed"] / df["Total Courses"]) * 100
    return df

df = load_data()

# ------------------ HEADER ------------------
st.title("💻 CSE Learning Path Dashboard")
st.markdown("Track your Computer Science skills, visualize growth, and manage your learning journey.")

# ------------------ SIDEBAR ------------------
st.sidebar.title("🛠️ Controls")

selected_skill = st.sidebar.selectbox(
    "Select a CSE skill to view details:",
    df["Skill"],
    index=0
)
selected_data = df[df["Skill"] == selected_skill].iloc[0]

# --- INDIVIDUAL GAUGE ---
st.sidebar.markdown(f"### 🎯 {selected_skill} Progress")
gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=selected_data["Progress"],
    title={'text': "Skill Progress (%)"},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "mediumseagreen"},
        'steps': GAUGE_STEPS
    }
))
gauge.update_layout(
    height=250,
    margin=dict(l=10, r=10, t=60, b=10),
)
st.sidebar.plotly_chart(gauge, use_container_width=True)

# --- COURSE COMPLETION STATUS ---
st.sidebar.info(
    f"**Course Status:** {selected_data['Courses Completed']} / {selected_data['Total Courses']} courses completed."
)

# ------------------ MAIN PAGE (Tabs) ------------------
tab1, tab2 = st.tabs(["📊 Overall Dashboard", "🚀 Skill Deep Dive"])

# =============================================================
# TAB 1 — OVERALL DASHBOARD
# =============================================================
with tab1:
    st.header("📈 Your Learning At-a-Glance")

    # --- KPI METRICS ---
    col1, col2, col3 = st.columns(3)
    avg_progress = df["Progress"].mean()
    top_skill = df.loc[df['Progress'].idxmax(), 'Skill']
    focus_skill = df.loc[df['Progress'].idxmin(), 'Skill']

    col1.metric("Average Skill Progress", f"{avg_progress:.1f}%")
    col2.metric("🥇 Top Skill", top_skill, f"{df['Progress'].max()}%")
    col3.metric("🌱 Skill to Focus On", focus_skill, f"{df['Progress'].min()}%")

    st.markdown("---")

    # --- OVERALL GAUGE ---
    st.subheader("🌍 Overall Learning Progress")
    overall_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_progress,
        delta={'reference': 75, 'increasing': {'color': "limegreen"}, 'decreasing': {'color': "crimson"}},
        title={'text': "Average Skill Progress"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "royalblue"},
            'steps': GAUGE_STEPS,
        }
    ))
    overall_gauge.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=10))
    st.plotly_chart(overall_gauge, use_container_width=True)

    st.markdown("---")

    # --- DATA TABLE ---
    st.subheader("📊 Detailed Learning Data")
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Skill": st.column_config.TextColumn("Skill", max_width=250),
            "Progress": st.column_config.ProgressColumn("Progress", format="%d%%", min_value=0, max_value=100),
            "Completion %": st.column_config.ProgressColumn("Course Completion", format="%.0f%%", min_value=0, max_value=100),
        },
        hide_index=True
    )

# =============================================================
# TAB 2 — DEEP DIVE
# =============================================================
with tab2:
    st.header(f"🚀 Deep Dive: {selected_skill}")

    # --- WEEKLY TREND ---
    st.subheader("📅 Weekly Progress Trend")

    np.random.seed(abs(hash(selected_skill)) % 10000)
    weeks = [f"Week {i}" for i in range(1, 6)]
    base = selected_data["Progress"] - np.random.randint(20, 40)
    weekly_progress = np.clip(base + np.cumsum(np.random.randint(2, 8, len(weeks))), 0, 100)
    weekly_progress[-1] = selected_data["Progress"]

    trend_fig = go.Figure(go.Scatter(
        x=weeks, y=weekly_progress,
        mode='lines+markers',
        line=dict(color='mediumseagreen', width=4, shape='spline'),
        fill='tozeroy', fillcolor='rgba(60,179,113,0.2)',
        marker=dict(size=10, color='lightgreen', line=dict(width=2, color='green'))
    ))
    trend_fig.update_layout(
        title=f"✨ {selected_skill} Weekly Growth Trend",
        xaxis_title="Week", yaxis_title="Progress (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        height=400,
        yaxis_range=[0, 100]
    )
    st.plotly_chart(trend_fig, use_container_width=True)

    st.markdown("---")

    # --- COURSE FILE DISPLAY ---
    st.subheader(f"📂 Chapters for {selected_skill}")

    filename_base = selected_skill.lower().replace(" ", "_").replace("&", "and")
    filename = os.path.join(COURSE_DIR, f"{filename_base}.txt")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        st.text_area(f"Course Chapters for {selected_skill}", content, height=300)
    else:
        st.warning(f"No course file found for **{selected_skill}**.\n\nCreate `{filename}` to add chapters.")
