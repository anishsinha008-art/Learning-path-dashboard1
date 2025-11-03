import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = True
if "active_section" not in st.session_state:
    st.session_state.active_section = "Home"

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* --- Top-left attached expanding menu --- */
.menu-wrapper {
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 1000;
}

.menu-container {
    background-color: #1E1E1E;
    padding: 10px 18px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
    color: white;
    display: flex;
    flex-direction: row;
    gap: 15px;
    overflow: hidden;
    white-space: nowrap;
    transform-origin: left;
    animation: expandRight 0.4s ease-out;
}

.menu-option {
    background: none;
    border: none;
    color: white;
    text-align: center;
    font-size: 15px;
    cursor: pointer;
    transition: color 0.2s, transform 0.2s;
}
.menu-option:hover {
    color: #00BFFF;
    transform: scale(1.05);
}
.active {
    color: #00BFFF;
    font-weight: bold;
}

/* --- Animation for smooth horizontal expand --- */
@keyframes expandRight {
    0% {
        opacity: 0;
        transform: scaleX(0);
    }
    100% {
        opacity: 1;
        transform: scaleX(1);
    }
}

/* --- Fade + slide animation for section content --- */
.section-container {
    animation: fadeSlide 0.4s ease-in-out;
}
@keyframes fadeSlide {
    0% {opacity: 0; transform: translateY(15px);}
    100% {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
col1, col2 = st.columns([0.06, 0.94])
with col1:
    if st.button("☰"):
        st.session_state.menu_open = not st.session_state.menu_open
with col2:
    st.title("💻 CSE Learning Path Dashboard")

st.markdown("Track your Computer Science skills, visualize growth, and access your course chapters interactively.")

# ------------------ DATA ------------------
skills_data = {
    "Skill": [
        "Python Programming", "Data Structures & Algorithms", "Operating Systems", "Database Management Systems",
        "Computer Networks", "Artificial Intelligence", "Machine Learning", "Deep Learning", "Web Development",
        "Cloud Computing", "Cybersecurity", "Software Engineering", "Internet of Things (IoT)",
        "Blockchain Technology", "DevOps"
    ],
    "Progress": [85, 78, 65, 72, 68, 60, 55, 48, 70, 52, 50, 74, 58, 40, 45],
    "Courses Completed": [5, 4, 3, 4, 3, 2, 2, 1, 3, 2, 2, 4, 2, 1, 1],
    "Total Courses": [6, 5, 4, 5, 4, 4, 3, 3, 4, 3, 3, 5, 3, 3, 3]
}
df = pd.DataFrame(skills_data)
selected_skill = st.selectbox("Select a CSE skill to view details:", df["Skill"])
selected_data = df[df["Skill"] == selected_skill].iloc[0]

# ------------------ MENU SECTION ------------------
if st.session_state.menu_open:
    st.markdown('<div class="menu-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="menu-container">', unsafe_allow_html=True)
    for section in [
        "Home", "Skill Progress", "Course Completion", "Overall Progress",
        "Weekly Trend", "Course Chapters", "Detailed Data"
    ]:
        btn_class = "menu-option active" if st.session_state.active_section == section else "menu-option"
        if st.button(section, key=section, use_container_width=False):
            st.session_state.active_section = section
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ------------------ MAIN CONTENT ------------------
st.markdown('<div class="section-container">', unsafe_allow_html=True)

if st.session_state.active_section == "Home":
    st.subheader("🏠 Welcome to the Dashboard")
    st.markdown("""
    This dashboard helps you:
    - Visualize your progress in each CSE domain  
    - Track weekly learning growth  
    - Access course chapters  
    - View total completion data  
    Use the ☰ icon to toggle the Dashboard Menu.
    """)

elif st.session_state.active_section == "Skill Progress":
    st.subheader(f"🎯 Skill Progress: {selected_skill}")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=selected_data["Progress"],
        title={'text': f"{selected_skill} Progress"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "mediumseagreen"},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccc"},
                {'range': [50, 80], 'color': "#fff3cd"},
                {'range': [80, 100], 'color': "#d4edda"}
            ]
        }
    ))
    st.plotly_chart(gauge, use_container_width=True)

elif st.session_state.active_section == "Course Completion":
    st.subheader("📘 Course Completion Overview")
    for _, row in df.iterrows():
        percent = int((row["Courses Completed"] / row["Total Courses"]) * 100)
        st.markdown(f"**{row['Skill']} — {row['Courses Completed']} / {row['Total Courses']} courses completed ({percent}%)**")
        st.progress(percent / 100)

elif st.session_state.active_section == "Overall Progress":
    st.subheader("🌍 Overall Learning Progress")
    overall_progress = df["Progress"].mean()
    overall_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_progress,
        title={'text': "Average Skill Progress"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "royalblue"},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccc"},
                {'range': [50, 80], 'color': "#fff3cd"},
                {'range': [80, 100], 'color': "#d4edda"}
            ]
        }
    ))
    st.plotly_chart(overall_gauge, use_container_width=True)

elif st.session_state.active_section == "Weekly Trend":
    st.subheader(f"📅 Weekly Progress Trend — {selected_skill}")
    np.random.seed(hash(selected_skill) % 100000)
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
    base = selected_data["Progress"] - 30
    weekly_progress = np.clip(base + np.cumsum(np.random.randint(0, 10, size=len(weeks))), 0, 100)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks,
        y=weekly_progress,
        mode='lines+markers',
        line=dict(color='mediumseagreen', width=4, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(60,179,113,0.2)',
        marker=dict(size=10, color='lightgreen', line=dict(width=2, color='green')),
    ))
    fig.update_layout(
        title=f"✨ {selected_skill} Weekly Growth Trend",
        xaxis_title="Week",
        yaxis_title="Progress (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.active_section == "Course Chapters":
    st.subheader(f"📂 Chapters for {selected_skill}")
    filename = f"courses/{selected_skill.lower().replace(' ', '_').replace('&', 'and')}.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        st.text_area("Course Chapters", content, height=200)
    else:
        st.warning(f"No course file found for *{selected_skill}*.\n\nCreate a file named {filename} to add chapters.")

elif st.session_state.active_section == "Detailed Data":
    st.subheader("📊 Detailed Learning Data")
    st.dataframe(df, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
