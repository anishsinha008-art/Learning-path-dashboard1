# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------
# 🎯 PAGE CONFIGURATION
# ---------------------------------------------
st.set_page_config(
    page_title="Learning Path Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------------------------
# 🧭 SIDEBAR
# ---------------------------------------------
st.sidebar.title("📚 Skill Navigator")
st.sidebar.markdown("Select your skill and view progress.")

skills = {
    "Python": 75,
    "Data Science": 50,
    "Web Development": 40,
    "Machine Learning": 30,
    "Artificial Intelligence": 20
}

selected_skill = st.sidebar.selectbox("Choose a Skill", list(skills.keys()))
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Keep learning every day to boost your completion rate!")

# ---------------------------------------------
# 📊 MAIN DASHBOARD
# ---------------------------------------------
st.title("🚀 Learning Path Dashboard")
st.markdown("Visualize your learning journey and skill progress in one place.")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📈 {selected_skill} Progress")
    progress_value = skills[selected_skill]
    st.progress(progress_value / 100)
    st.metric("Completion", f"{progress_value}%", "Keep it up!" if progress_value < 80 else "Almost there!")

    # -----------------------------------------
    # 🧭 Semi-Circular Gauge Chart
    # -----------------------------------------
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=progress_value,
        title={'text': f"{selected_skill} Mastery Level"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#0078ff", 'thickness': 0.25},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ff4b4b'},
                {'range': [40, 70], 'color': '#ffc300'},
                {'range': [70, 100], 'color': '#00cc96'}
            ],
        }
    ))

    # Make it semi-circular
    gauge_fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=40, b=0),
        template="simple_white",
        # Define semi-circle (half gauge)
        polar=dict(
            radialaxis=dict(visible=False)
        )
    )
    gauge_fig.update_traces(
        gauge_shape="angular",  # semi-circular style
        gauge_axis_range=[None, 100]
    )
    st.plotly_chart(gauge_fig, use_container_width=True)

    st.markdown("---")
    st.write("### 🔍 Recommended Next Topics:")
    if selected_skill == "Python":
        st.markdown("- Object-Oriented Programming (OOP)\n- Modules & Packages\n- APIs & Automation")
    elif selected_skill == "Data Science":
        st.markdown("- Pandas & NumPy\n- Data Visualization (Matplotlib, Seaborn)\n- Exploratory Data Analysis")
    elif selected_skill == "Web Development":
        st.markdown("- HTML/CSS/JS Deep Dive\n- Backend (Flask/Django)\n- Deployment")
    elif selected_skill == "Machine Learning":
        st.markdown("- Regression Models\n- Classification Algorithms\n- Model Evaluation Metrics")
    elif selected_skill == "Artificial Intelligence":
        st.markdown("- Neural Networks\n- Deep Learning Frameworks\n- Generative AI")

with col2:
    st.subheader("📊 Skill Comparison Chart")
    df = pd.DataFrame({
        "Skill": list(skills.keys()),
        "Progress": list(skills.values())
    })
    fig = px.bar(df, x="Skill", y="Progress", text="Progress", color="Skill",
                 title="Overall Skill Progress", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------
# 🕒 LEARNING HISTORY SECTION
# ---------------------------------------------
st.markdown("## 🧠 Learning History")
st.markdown("Track your weekly learning performance below:")

history_data = {
    "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
    "Hours Studied": [5, 8, 6, 10],
    "Skill Growth (%)": [10, 15, 12, 20]
}

history_df = pd.DataFrame(history_data)
line_fig = px.line(history_df, x="Week", y="Skill Growth (%)", markers=True, title="Weekly Skill Growth")
st.plotly_chart(line_fig, use_container_width=True)

# ---------------------------------------------
# 🧩 LEARNING RESOURCES SECTION
# ---------------------------------------------
st.markdown("## 🎓 Recommended Learning Resources")

resources = {
    "Python": ["Python.org Tutorials", "Automate the Boring Stuff", "Real Python"],
    "Data Science": ["Kaggle", "Analytics Vidhya", "DataCamp"],
    "Web Development": ["freeCodeCamp", "MDN Docs", "W3Schools"],
    "Machine Learning": ["Coursera ML", "Scikit-Learn Docs", "Fast.ai"],
    "Artificial Intelligence": ["DeepLearning.ai", "Google AI Blog", "Papers with Code"]
}

res_list = resources[selected_skill]
for item in res_list:
    st.markdown(f"- 🔗 [{item}](https://www.google.com/search?q={item.replace(' ', '+')})")

# ---------------------------------------------
# ✅ FOOTER
# ---------------------------------------------
st.markdown("---")
st.caption("Made with ❤️ using Streamlit | Learning Path Dashboard")
