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
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# ------------------ SIDEBAR MENU ------------------
def sidebar_menu():
    st.markdown(
        """
        <style>
        .menu-button {
            position: fixed;
            top: 20px;
            left: 25px;
            font-size: 30px;
            cursor: pointer;
            z-index: 999;
        }
        .menu {
            position: fixed;
            top: 0;
            left: 0;
            width: 270px;
            height: 100%;
            background-color: #0e1117;
            padding-top: 60px;
            transform: translateX(-100%);
            transition: all 0.4s ease;
            z-index: 998;
            box-shadow: 4px 0 10px rgba(0, 0, 0, 0.4);
        }
        .menu.open {
            transform: translateX(0);
        }
        .menu a {
            display: block;
            padding: 15px 30px;
            color: white;
            text-decoration: none;
            font-size: 18px;
        }
        .menu a:hover {
            background-color: #262730;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("☰", key="menu_button", help="Open Menu"):
        st.session_state.menu_open = not st.session_state.menu_open

    menu_class = "menu open" if st.session_state.menu_open else "menu"

    st.markdown(
        f"""
        <div class="{menu_class}">
            <a href="#" onclick="window.parent.postMessage('Home', '*')">🏠 Home</a>
            <a href="#" onclick="window.parent.postMessage('Progress', '*')">📈 Progress</a>
            <a href="#" onclick="window.parent.postMessage('Courses', '*')">📚 Courses</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------ OVERALL PROGRESS GAUGE ------------------
def overall_progress_gauge(value):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": "Overall Progress", "font": {"size": 22}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#00cc96"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 50], "color": "#ff4b4b"},
                    {"range": [50, 80], "color": "#ffa600"},
                    {"range": [80, 100], "color": "#00cc96"},
                ],
            },
            number={"suffix": "%"},
        )
    )
    fig.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)


# ------------------ DASHBOARD CONTENT ------------------
def main_dashboard():
    st.markdown("<h1 style='text-align:center;'>💻 CSE Learning Path Dashboard</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        overall_progress_gauge(72)

    with col2:
        st.subheader("Weekly Progress")
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
        progress = [45, 60, 75, 85]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=progress,
                mode="lines+markers",
                line=dict(width=4),
                marker=dict(size=10),
            )
        )
        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            height=350,
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Course Completion Overview")

    df = pd.DataFrame({
        "Skill": ["Python", "Data Science", "Machine Learning", "Cyber Security", "Web Development"],
        "Progress": [90, 70, 65, 40, 85],
        "Completion %": [0.9, 0.7, 0.65, 0.4, 0.85],
        "Courses Completed": [9, 7, 6, 4, 8],
        "Total Courses": [10, 10, 10, 10, 10],
    })

    # Fixed section: Removed st.column_config.TextColumn for compatibility
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Progress": st.column_config.ProgressColumn("Progress", format="%d%%", min_val=0, max_val=100),
            "Completion %": st.column_config.ProgressColumn("Course Completion", format="%.0f%%", min_val=0, max_val=1),
            "Courses Completed": "Completed",
            "Total Courses": "Total",
        },
        hide_index=True,
    )

# ------------------ MAIN LAYOUT ------------------
sidebar_menu()
main_dashboard()
