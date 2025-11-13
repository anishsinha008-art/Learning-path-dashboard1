import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import json
from io import BytesIO
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path — Optimized", layout="wide")

# ------------------ HELPERS ------------------
def init_session_state():
    """Initialize session state with safe defaults."""
    defaults = {
        "chat_history": [],  # list of dicts: {sender, message, ts}
        "topic_memory": None,
        "download_blob": None,
        "courses": None,
        "theme": "neon",
        "show_more_courses": False,
        "typing": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def now_iso():
    return pd.Timestamp.utcnow().isoformat()


def make_course_df():
    # default course list
    base = [
        {"Course": "Python", "Completion": 85, "Status": "In Progress"},
        {"Course": "C++", "Completion": 60, "Status": "In Progress"},
        {"Course": "Web Development", "Completion": 75, "Status": "In Progress"},
        {"Course": "AI", "Completion": 40, "Status": "Not Started"},
        {"Course": "Data Science", "Completion": 55, "Status": "In Progress"},
        {"Course": "Machine Learning", "Completion": 45, "Status": "In Progress"},
        {"Course": "Cybersecurity", "Completion": 30, "Status": "Not Started"},
    ]
    return pd.DataFrame(base)


def save_state_to_json():
    state = {
        "chat_history": st.session_state.chat_history,
        "topic_memory": st.session_state.topic_memory,
        "courses": st.session_state.courses.to_dict(orient="records") if st.session_state.courses is not None else None,
    }
    return json.dumps(state, indent=2)


# Simple reply generator (deterministic-ish with randomness)
def generate_bot_reply(user_msg: str) -> str:
    msg = user_msg.lower().strip()
    # set typing flag to simulate
    st.session_state.typing = True
    time.sleep(np.random.uniform(0.25, 0.75))
    st.session_state.typing = False

    # pattern matching for quick helpful replies
    if any(k in msg for k in ["python", "py"]):
        st.session_state.topic_memory = "python"
        return random.choice([
            "🐍 Tip: use list comprehensions for concise loops.",
            "💡 Tip: use enumerate() when you need indices.",
            "⚙️ Try virtualenv / venv to isolate project dependencies.",
        ])
    if any(k in msg for k in ["ai", "machine learning", "ml"]):
        st.session_state.topic_memory = "ai"
        return random.choice([
            "🤖 Start with NumPy & Pandas for data wrangling.",
            "🧠 Brush up on linear algebra — it helps model intuition.",
            "📊 Try a small classification project on a public dataset.",
        ])
    if any(k in msg for k in ["web", "html", "css", "javascript", "js"]):
        st.session_state.topic_memory = "web"
        return random.choice([
            "🌐 Learn Flexbox & Grid for responsive layouts.",
            "⚡ Host your portfolio on GitHub Pages to share it.",
            "💫 Practice building a tiny project (todo app) in vanilla JS first.",
        ])
    if any(k in msg for k in ["motivate", "tired", "stuck"]):
        st.session_state.topic_memory = "motivation"
        return random.choice([
            "⚡ Keep going — progress is built out of tiny wins.",
            "🚀 One step every day compounds into something huge.",
            "🔥 Focus on a single micro-goal for 25 minutes (Pomodoro).",
        ])
    if any(k in msg for k in ["bye", "goodbye", "see you"]):
        st.session_state.topic_memory = None
        return "👋 Bye! Topic memory cleared — come back soon!"

    # fallback: respond based on topic memory
    topic = st.session_state.topic_memory
    if topic == "python":
        return "🐍 Want a short Python exercise or a tip?"
    if topic == "ai":
        return "🤖 Want a simple project idea in AI?"
    if topic == "web":
        return "🌐 Would you like a responsive layout example?"
    # default
    return random.choice([
        "✨ Tell me: Python, AI, or Web — what would you like?",
        "🚀 Want a quick coding challenge?",
        "💬 I can give a study plan, tips or a mini-project idea — pick one."
    ])


# ------------------ INITIALIZE ------------------
init_session_state()
if st.session_state.courses is None:
    st.session_state.courses = make_course_df()

# ------------------ THEME STYLES ------------------
NEON_CSS = """
<style>
.stApp { background: #000000; color: #bfffc2; }
.h1, h1, .css-1v3fvcr { color: #bfffc2; }
.card { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.06); }
.chat-area { background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border-radius: 12px; padding: 12px; max-height: 56vh; overflow-y: auto; border: 1px solid rgba(0,255,127,0.04); }
.bubble-user { background: linear-gradient(90deg,#003e13,#1b5e20); color: #eafff0; padding: 10px; border-radius: 14px; margin: 8px 0; text-align: right; display: inline-block; max-width: 85%; }
.bubble-bot { background: linear-gradient(90deg,#134b2b,#2e7d32); color: #eafff0; padding: 10px; border-radius: 14px; margin: 8px 0; text-align: left; display: inline-block; max-width: 85%; }
.memory-badge { background: rgba(0,255,127,0.08); color: #bfffc2; padding: 6px 10px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.06); display:inline-block; margin-bottom:8px; }
.neon-btn { background: linear-gradient(90deg,#00ff7f33,#00ff7f22); color: #000; padding: 8px 14px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.35); }
</style>
"""

DARK_CSS = """
<style>
.stApp { background: #0b0b0b; color: #e6eef1; }
.card { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }
.chat-area { background: rgba(255,255,255,0.01); border-radius: 12px; padding: 12px; max-height: 56vh; overflow-y: auto; }
</style>
"""

if st.session_state.theme == "neon":
    st.markdown(NEON_CSS, unsafe_allow_html=True)
else:
    st.markdown(DARK_CSS, unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.title("☰ Menu")
    page = st.radio("Navigate:", ["🏠 Dashboard", "🤖 Chat Assistant"])
    st.markdown("---")
    st.selectbox("Theme:", ["neon", "dark"], index=0 if st.session_state.theme == "neon" else 1, key="theme_select", on_change=lambda: st.session_state.update({"theme": st.session_state.theme_select}))
    st.markdown("---")
    if st.button("Save App State (.json)"):
        json_blob = save_state_to_json().encode("utf-8")
        st.download_button("⬇️ Download app state", data=json_blob, file_name="cse_dashboard_state.json", mime="application/json")

# =========================
# PAGE: DASHBOARD
# =========================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard")
    st.markdown("<div class='card'>Track progress, plan learning sprints, add courses and export your data.</div>", unsafe_allow_html=True)
    st.markdown(" ")

    # Top metrics
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        # compute overall progress
        overall = int(st.session_state.courses["Completion"].mean())
        gauge_fig = go.Figure(go.Indicator(mode="gauge+number", value=overall, title={'text': "Total Completion"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FF7F"}}))
        gauge_fig.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2')
        st.plotly_chart(gauge_fig, use_container_width=True)
    with col2:
        st.metric(label="Courses", value=len(st.session_state.courses))
        st.metric(label="Active Topic", value=(st.session_state.topic_memory or "—"))
    with col3:
        st.button("➕ Add New Course", on_click=lambda: st.session_state.update({"show_add_course": True}))
        if st.session_state.get("show_add_course"):
            with st.form("add_course_form"):
                name = st.text_input("Course name", value="New Course")
                completion = st.slider("Initial completion %", 0, 100, 0)
                status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"], index=1)
                submitted = st.form_submit_button("Add")
                if submitted:
                    new_row = {"Course": name, "Completion": int(completion), "Status": status}
                    st.session_state.courses = pd.concat([st.session_state.courses, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Added course: {name}")
                    st.session_state.show_add_course = False

    st.markdown("---")

    # Weekly progress editable
    st.subheader("📆 Weekly Progress")
    weeks = [f"Week {i+1}" for i in range(4)]
    cols = st.columns(len(weeks))
    week_vals = []
    for i, c in enumerate(cols):
        val = c.slider(weeks[i], 0, 100, int(np.clip((st.session_state.courses["Completion"].mean() + (i-1)*5), 0, 100)))
        week_vals.append(val)
    bar_fig = go.Figure(go.Bar(x=weeks, y=week_vals, text=week_vals, textposition='auto'))
    bar_fig.update_layout(title="Weekly Growth Chart", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320)
    st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("---")

    # Course cards + controls (interactive)
    st.subheader("📚 Courses")
    search = st.text_input("Search courses (name/status)")
    filtered = st.session_state.courses.copy()
    if search:
        mask = filtered["Course"].str.contains(search, case=False, na=False) | filtered["Status"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    # allow inline editing of completion via sliders
    for idx, row in filtered.reset_index(drop=False).iterrows():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"<div class='card'><b>{row['Course']}</b> — <small>{row['Status']}</small><br></div>", unsafe_allow_html=True)
        with c2:
            new_val = st.slider(f"progress_{row['index']}", 0, 100, int(row['Completion']))
            if new_val != int(row['Completion']):
                # update the main df (match by index)
                st.session_state.courses.at[row['index'], 'Completion'] = int(new_val)
                # auto-update status if needed
                if new_val == 100:
                    st.session_state.courses.at[row['index'], 'Status'] = 'Completed'
                elif new_val == 0:
                    st.session_state.courses.at[row['index'], 'Status'] = 'Not Started'
                else:
                    st.session_state.courses.at[row['index'], 'Status'] = 'In Progress'
                st.experimental_rerun()

    st.markdown("---")

    # Course table with export
    st.subheader("📈 Detailed Course Progress")
    try:
        st.dataframe(st.session_state.courses.style.format({'Completion': '{:.0f}'}), use_container_width=True)
    except Exception:
        st.dataframe(st.session_state.courses, use_container_width=True)

    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        if st.button("Export Courses as CSV"):
            csv_bytes = st.session_state.courses.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="courses.csv", mime="text/csv")
    with col_dl2:
        if st.button("Export Courses as JSON"):
            json_blob = st.session_state.courses.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button("⬇️ Download JSON", data=json_blob, file_name="courses.json", mime="application/json")

    st.markdown("---")
    st.markdown("<div style='color:#bfffc2;'>Developed by Anish | CSE Learning Path Dashboard © 2025</div>", unsafe_allow_html=True)

# =========================
# PAGE: CHAT ASSISTANT
# =========================
elif page == "🤖 Chat Assistant":
    st.markdown("<h2 class='neon-header'>🤖 Neon Chat Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Futuristic black + neon green. Topic memory ON. Type 'bye' to reset topic memory.</div>", unsafe_allow_html=True)

    # Quick starters
    starters = [
        ("💪 Motivate Me", "motivate me"),
        ("🐍 Python Tip", "tell me about python"),
        ("🧠 AI Info", "tell me about ai"),
        ("🌐 Web Help", "help with web dev"),
    ]
    cols = st.columns(len(starters))
    for (label, text), col in zip(starters, cols):
        if col.button(label):
            st.session_state.chat_history.append({"sender": "user", "message": text, "ts": now_iso()})
            reply = generate_bot_reply(text)
            st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})

    st.markdown("")
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.topic_memory = None
        st.success("Chat cleared.")

    # Chat display area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.topic_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Current Topic: {st.session_state.topic_memory.title()}</div>", unsafe_allow_html=True)

    for m in st.session_state.chat_history:
        sender = m.get("sender")
        message = m.get("message")
        ts = m.get("ts")
        time_str = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender == "user":
            st.markdown(f"<div style='text-align:right'><div class='bubble-user'><b>You:</b> {message}</div><div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'><div class='bubble-bot'><b>Assistant:</b> {message}</div><div style='font-size:10px;color:#8fffbf;margin-top:4px'>{time_str}</div></div>", unsafe_allow_html=True)

    # typing indicator
    if st.session_state.typing:
        st.markdown("<div style='font-size:12px;color:#bfffc2'>Assistant is typing...</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area using form to avoid accidental reruns
    with st.form(key="chat_form", clear_on_submit=True):
        user_text = st.text_input("Type your message here...", key="user_input_text")
        submit = st.form_submit_button("Send")
        if submit and user_text and user_text.strip():
            st.session_state.chat_history.append({"sender": "user", "message": user_text.strip(), "ts": now_iso()})
            # simulate typing and reply
            with st.spinner("Assistant is typing..."):
                time.sleep(np.random.uniform(0.3, 0.9))
                reply = generate_bot_reply(user_text.strip())
            st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
            # keep chat state export ready
            st.success("Message sent.")
            st.experimental_rerun()

    st.markdown("---")
    # Save Chat History (manual): prepare CSV blob
    if st.button("💾 Prepare Chat CSV"):
        if st.session_state.chat_history:
            chat_df = pd.DataFrame(st.session_state.chat_history)
            csv_bytes = chat_df.to_csv(index=False).encode("utf-8")
            st.session_state.download_blob = csv_bytes
            st.success("Chat prepared — click the download button below.")
        else:
            st.info("No chat to save yet. Start a conversation first.")

    if st.session_state.download_blob:
        st.download_button(label="⬇️ Download Chat as CSV", data=st.session_state.download_blob, file_name="chat_history.csv", mime="text/csv")

    st.markdown("<div style='color:#bfffc2;text-align:center'>Neon Chat • Developed by Anish © 2025</div>", unsafe_allow_html=True)
