import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ------------------ INITIAL STATES ------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False
if "active_section" not in st.session_state:
    st.session_state.active_section = "Home"

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* ---- Light Slide Menu ---- */
.menu-panel {
    position: fixed;
    top: 0;
    left: 0;
    width: 260px;
    height: 100%;
    background-color: #fdfdfd;
    box-shadow: 4px 0 15px rgba(0,0,0,0.2);
    padding: 20px;
    transform: translateX(-270px);
    transition: transform 0.4s ease-in-out, opacity 0.4s ease-in-out;
    opacity: 0;
    z-index: 10;
}
.menu-panel.open {
    transform: translateX(0);
    opacity: 1;
}
.menu-header {
    font-weight: bold;
    color: #0078D7;
    font-size: 20px;
    margin-bottom: 10px;
    text-align: center;
}
.menu-button {
    display: block;
    width: 100%;
    border: none;
    background: none;
    text-align: left;
    font-size: 16px;
    padding: 8px 0;
    color: #333;
    cursor: pointer;
}
.menu-button:hover {
    color: #0078D7;
    font-weight: 600;
}
.menu-active {
    color: #0078D7;
    font-weight: 700;
}

/* ---- Fade + Slide transition for main content ---- */
.section-container {
    animation: fadeSlide 0.4s ease-in-out;
}
@keyframes fadeSlide {
    0% {opacity: 0; transform: translateX(30px);}
    100% {opacity: 1; transform: translateX(0);}
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
col1, col2 = st.columns([0.06, 0.94])
with col1:
    if st.button("☰", help="Open/Close Menu"):
        st.session_state.menu_open = not st.session_state.menu_open
with col2:
    st.title("💻 CSE Learning Path Dashboard")

st.markdown("Track your Computer Science skills, visualize growth, and access your course chapters interactively.")

# ------------------ MENU PANEL ------------------
menu_html = f"""
<div class="menu-panel {'open' if st.session_state.menu_open else ''}">
  <div class="menu-header">📚 Dashboard Menu</div>
"""
sections = [
    "Home", "Skill Progress", "Course Completion", "Overall Progress",
    "Weekly Trend", "Course Chapters", "Detailed Data"
]

# Create clickable buttons (using JS-based onclick triggers)
for section in sections:
    active_class = "menu-active" if st.session_state.active_section == section else "menu-button"
    menu_html += f"""
    <form action="" method="post">
        <input type="hidden" name="section" value="{section}">
        <button class="{active_class}" type="submit">{section}</button>
    </form>
    """

menu_html += "</div>"
st.markdown(menu_html, unsafe_allow_html=True)

# ------------------ SECTION CHANGE HANDLER ------------------
# This allows Streamlit to switch sections when you click buttons
section = st.experimental_get_query_params().get("section", [st.session_state.active_section])[0]
st.session_state.active_section = section

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
        st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} courses completed ({percent}%)")
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
        st.warning(f"No course file found for **{selected_skill}**.\n\nCreate a file named `{filename}` to add chapters.")

elif st.session_state.active_section == "Detailed Data":
    st.subheader("📊 Detailed Learning Data")
    st.dataframe(df, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.active_section = "Home"

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* --- Sidebar menu --- */
.dashboard-menu {
    background-color: #1E1E1E;
    padding: 15px 20px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
    color: white;
    width: 260px;
}
.dashboard-menu h3 {
    color: #00BFFF;
    text-align: center;
    border-bottom: 1px solid #333;
    padding-bottom: 8px;
    margin-bottom: 15px;
}
.menu-option {
    background: none;
    border: none;
    color: white;
    text-align: left;
    font-size: 16px;
    padding: 8px 0;
    cursor: pointer;
    width: 100%;
}
.menu-option:hover {
    color: #00BFFF;
}
.active {
    color: #00BFFF;
    font-weight: bold;
}

/* --- Fade + slide animation --- */
.section-container {
    animation: fadeSlide 0.4s ease-in-out;
}
@keyframes fadeSlide {
    0% {opacity: 0; transform: translateX(30px);}
    100% {opacity: 1; transform: translateX(0);}
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

# ------------------ LAYOUT: MENU + CONTENT ------------------
menu_col, main_col = st.columns([0.25, 0.75])

# ---- MENU SECTION ----
with menu_col:
    if st.session_state.menu_open:
        st.markdown('<div class="dashboard-menu">', unsafe_allow_html=True)
        st.markdown("<h3>📚 Dashboard Menu</h3>", unsafe_allow_html=True)
        for section in [
            "Home", "Skill Progress", "Course Completion", "Overall Progress",
            "Weekly Trend", "Course Chapters", "Detailed Data"
        ]:
            btn_class = "menu-option active" if st.session_state.active_section == section else "menu-option"
            if st.button(section, key=section, use_container_width=True):
                st.session_state.active_section = section
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---- MAIN CONTENT ----
with main_col:
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
            st.markdown(f"**{row['Skill']}** — {row['Courses Completed']} / {row['Total Courses']} courses completed ({percent}%)")
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
            st.warning(f"No course file found for **{selected_skill}**.\n\nCreate a file named `{filename}` to add chapters.")

    elif st.session_state.active_section == "Detailed Data":
        st.subheader("📊 Detailed Learning Data")
        st.dataframe(df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
