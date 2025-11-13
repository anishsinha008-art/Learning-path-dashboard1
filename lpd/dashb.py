import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Learning Path Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Mockups ---
# Mock data for skill progress
skills_progress = {
    "Python": 85,
    "Data Analysis": 60,
    "Machine Learning": 45,
    "Streamlit": 70,
    "SQL": 30,
    "Statistics": 50
}

# [cite_start]Mock data for Trend Analysis [cite: 42]
# Simulating weekly progress
trend_data = pd.DataFrame({
    'Week': pd.to_datetime(['2025-10-06', '2025-10-13', '2025-10-20', '2025-10-27', '2025-11-03', '2025-11-10']),
    'Modules Completed': [1, 2, 2, 3, 1, 4]
})
trend_data['Cumulative Modules'] = trend_data['Modules Completed'].cumsum()
trend_data = trend_data.set_index('Week')

# [cite_start]Mock data for Course Completion [cite: 44]
courses = {
    "Python for Data Science": [
        ("Module 1: Python Basics", True),
        ("Module 2: NumPy", True),
        ("Module 3: Pandas", True),
        ("Module 4: Matplotlib", False),
    ],
    "Streamlit Fundamentals": [
        ("Chapter 1: Getting Started", True),
        ("Chapter 2: Displaying Data", True),
        ("Chapter 3: Interactive Widgets", True),
        ("Chapter 4: State Management", True),
        ("Chapter 5: Deployment", False),
    ]
}

# --- Sidebar ---
[cite_start]# [cite: 38] Sidebar for skill selection
[cite_start]# [cite: 54] Skill gauge (progress bar) moved to sidebar
st.sidebar.title("My Skillset")
st.sidebar.markdown("Select skills to view your progress.")

selected_skills = st.sidebar.multiselect(
    "Select skills:",
    options=list(skills_progress.keys()),
    default=list(skills_progress.keys())[0:3]
)

st.sidebar.markdown("---")
[cite_start]st.sidebar.subheader("Skill Progress") # [cite: 40]
if not selected_skills:
    st.sidebar.info("Select one or more skills to see progress.")
else:
    for skill in selected_skills:
        progress = skills_progress[skill]
        st.sidebar.write(f"{skill}")
        st.sidebar.progress(progress / 100)


# --- Main Dashboard ---
st.title("🎓 My Learning Path Dashboard")
st.markdown("Welcome back! Here is a summary of your learning journey.")

st.markdown("---")

# --- Overall Progress (Prominent) ---
[cite_start]# [cite: 55] Overall progress prominence
[cite_start]# [cite: 49] "Visual gauges loved"
st.subheader("Overall Progress")

# Calculate overall progress
overall_progress = int(np.mean([skills_progress[s] for s in selected_skills] if selected_skills else [0]))

col1, col2 = st.columns([2, 1])

with col1:
    # Using a Plotly Gauge for a better visual
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = overall_progress,
        title = {'text': "Average Progress (Selected Skills)"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#ff8c00"}, # Color inspired by presentation palette
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    [cite_start]# [cite: 40] Individual & overall metrics
    st.metric(label="Total Skills Selected", value=len(selected_skills))
    st.metric(label="Highest Skill", value=f"{max(skills_progress, key=skills_progress.get)} ({skills_progress[max(skills_progress, key=skills_progress.get)]}%)" if selected_skills else "N/A")
    st.metric(label="Lowest Skill", value=f"{min(skills_progress, key=skills_progress.get)} ({skills_progress[min(skills_progress, key=skills_progress.get)]}%)" if selected_skills else "N/A")


st.markdown("---")

# --- Trend Analysis & Course Completion ---
col3, col4 = st.columns(2)

with col3:
    [cite_start]# [cite: 42] Trend Analysis: Weekly progress visualization
    [cite_start]# [cite: 50] "Trend charts effective"
    st.subheader("Progress Trend Analysis")
    st.line_chart(trend_data['Cumulative Modules'], height=300)
    st.caption("Cumulative modules completed per week.")

with col4:
    [cite_start]# [cite: 44] Course Completion
    [cite_start]# [cite: 45] Chapter tracking & viewer
    st.subheader("Course Completion Status")
    
    selected_course = st.selectbox(
        "Select a course to view chapter status:",
        options=list(courses.keys())
    )
    
    if selected_course:
        for chapter, completed in courses[selected_course]:
            # Using disabled checkbox as a "viewer"
            st.checkbox(chapter, value=completed, disabled=True)
