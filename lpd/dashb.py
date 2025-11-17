# app_superior_custom.py
"""
CSE Learning Path — AI Mentor (Custom Neon UI)
Save as: app_superior_custom.py
Run: streamlit run app_superior_custom.py
"""

import os
import sys
import json
import time
import random
import subprocess
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Learning Path Dashboard", layout="wide", initial_sidebar_state="expanded")

# ------------------ Persistence ------------------
PERSIST_FILE = "cse_dashboard_state.json"

def save_state_local():
    try:
        state = {
            "chat_history": st.session_state.chat_history,
            "topic_memory": st.session_state.topic_memory,
            "chat_summary": st.session_state.chat_summary,
            "courses": st.session_state.courses.to_dict(orient="records") if st.session_state.courses is not None else None,
            "notes": st.session_state.notes,
            "quiz_scores": st.session_state.quiz_scores,
            "spectorial_entries": st.session_state.spectorial_entries,
            "theme": st.session_state.theme,
            "assistant_mode": st.session_state.assistant_mode,
        }
        with open(PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        st.warning(f"Failed to save local state: {e}")
        return False

def load_state_local():
    try:
        with open(PERSIST_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("courses"):
            st.session_state.courses = pd.DataFrame(state.get("courses"))
        st.session_state.chat_history = state.get("chat_history", [])
        st.session_state.topic_memory = state.get("topic_memory")
        st.session_state.chat_summary = state.get("chat_summary")
        st.session_state.notes = state.get("notes", [])
        st.session_state.quiz_scores = state.get("quiz_scores", {})
        st.session_state.spectorial_entries = state.get("spectorial_entries", [])
        st.session_state.theme = state.get("theme", st.session_state.theme)
        st.session_state.assistant_mode = state.get("assistant_mode", st.session_state.assistant_mode)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        st.warning(f"Failed to load local state: {e}")
        return False

# ------------------ Session init ------------------
def init_session_state():
    defaults = {
        "chat_history": [],
        "topic_memory": None,
        "chat_summary": None,
        "download_blob": None,
        "courses": None,
        "theme": "neon",
        "typing": False,
        "assistant_mode": "Tutor",
        "use_memory": True,
        "api_provider": None,
        "api_key": None,
        "deepseek_key": None,
        "use_tts": False,
        "enable_code_exec": False,
        "notes": [],
        "quiz_scores": {},
        "spectorial_entries": [],
        "show_add_course": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def make_course_df():
    base = [
        {"Course": "Python", "Completion": 78, "Status": "In Progress"},
        {"Course": "C++", "Completion": 66, "Status": "In Progress"},
        {"Course": "Web Development", "Completion": 37, "Status": "In Progress"},
        {"Course": "AI", "Completion": 54, "Status": "In Progress"},
        {"Course": "Data Science", "Completion": 45, "Status": "In Progress"},
        {"Course": "Machine Learning", "Completion": 40, "Status": "In Progress"},
        {"Course": "Cybersecurity", "Completion": 30, "Status": "Not Started"},
    ]
    return pd.DataFrame(base)

def now_iso():
    return pd.Timestamp.utcnow().isoformat()

init_session_state()
# default courses if none
if st.session_state.courses is None:
    st.session_state.courses = make_course_df()
# attempt to load persisted state (do not override defaults if missing fields)
load_state_local()

# ------------------ Optional TTS ------------------
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

def tts_speak_bytes(text: str):
    if not TTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text, lang='en')
        bio = BytesIO()
        tts.write_to_fp(bio)
        bio.seek(0)
        return bio.read()
    except Exception as e:
        st.warning(f"TTS failed: {e}")
        return None

# ------------------ LLM simulation / summarizer ------------------
def summarize_memory(max_chars=800):
    msgs = st.session_state.chat_history
    if not msgs:
        return None
    last = msgs[-24:]
    user_texts = [m['message'] for m in last if m['sender']=='user']
    kws = ["python","ai","ml","web","data","project","bug","debug","study","recursion","algorithms","streamlit","openai","deepseek"]
    keywords = set()
    for t in user_texts:
        for k in kws:
            if k in t.lower():
                keywords.add(k)
    summary = "Topics: " + (", ".join(sorted(keywords)) if keywords else "general")
    if user_texts:
        summary += " | Recent: " + " | ".join(user_texts[-3:])
    return summary[:max_chars]

def simulated_llm_reply(user_msg, mode):
    df = st.session_state.courses
    try:
        top = df.loc[df['Completion'].idxmax()]
        top_hint = f"{top['Course']} ({top['Completion']}%)"
    except Exception:
        top_hint = "none"
    msg = user_msg.lower()
    if mode == "Code Helper":
        if any(kw in msg for kw in ["bug","error","traceback","fix"]):
            return "Paste the minimal error or code snippet. I'll propose a fix and runnable example."
        if "streamlit" in msg:
            return "Tip: use st.form to group inputs and st.session_state to persist values. Need snippet?"
        return "Describe the issue and I'll return a short runnable example."
    if mode == "Tutor":
        for c in st.session_state.courses['Course'].tolist():
            if c.lower() in msg:
                comp = int(st.session_state.courses.loc[st.session_state.courses['Course']==c, 'Completion'].values[0])
                if comp < 50:
                    return f"You're {comp}% through {c}. Suggestion: 2 focused Pomodoros (25m) + 3 practice problems."
                else:
                    return f"At {comp}% in {c}, try a mini-project (1–2 hours). Want ideas?"
        if "exercise" in msg or "problem" in msg:
            return "Mini exercise: write a function that reverses the words in a sentence but preserves whitespace. Want the solution in Python?"
        return "Plan: (1) 25m review (2) 45m practice (3) 10m reflect. Want a 7-day plan?"
    if mode == "Motivator":
        choices = [
            "Small wins matter — start with a 25-min pomodoro and log one takeaway.",
            "Consistency > intensity. Pick a micro-goal and do it today.",
            "Stuck? Take a 5-min break, then use rubber-duck debugging."
        ]
        return random.choice(choices)
    return "How can I help — study plan, code snippet, or motivation?"

# ------------------ Safe-ish code runner fix ------------------
def run_code_snippet(code: str, timeout=5):
    """
    Run python code in a subprocess for safety. Returns (stdout, stderr, timed_out_flag).
    WARNING: executing arbitrary code runs on the host machine. Use only in trusted env.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        return "", "Execution timed out.", True
    except Exception as e:
        return "", f"Execution failed: {e}", False

# ------------------ Styling (neon + glass) ------------------
NEON_CSS = """
<style>
/* base */
html, body, .main, .block-container { background: linear-gradient(180deg,#050505 0%, #040406 60%) !important; color: #c8ffdd; }
/* sidebar */
[data-testid="stSidebar"] > div:first-child { background: linear-gradient(180deg,#15161a,#101217); border-right: 1px solid rgba(255,255,255,0.03); padding: 18px 14px; }
/* card */
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius: 12px;
  padding: 14px;
  border: 1px solid rgba(0,255,127,0.04);
  box-shadow: 0 6px 18px rgba(0,0,0,0.6);
}
/* sub-cards inside lists */
.small-card {
  background: rgba(255,255,255,0.01);
  border-radius: 10px;
  padding: 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,0.02);
}
/* chat bubbles */
.bubble-user { background: linear-gradient(90deg,#003e13,#1b5e20); color:#eafff0; padding:10px; border-radius:12px; margin:8px 0; display:inline-block; max-width:86%; }
.bubble-bot  { background: linear-gradient(90deg,#134b2b,#2e7d32); color:#eafff0; padding:10px; border-radius:12px; margin:8px 0; display:inline-block; max-width:86%; }
/* memory badge */
.memory-badge { background: rgba(0,255,127,0.06); color:#bfffc2; padding:7px 10px; border-radius:10px; display:inline-block; margin-bottom:8px; font-weight:600; }
/* small muted */
.small-muted { font-size:12px; color:#7fe9b5; opacity:0.9; }
/* neon header */
.neon-header { color: #bfffc2; font-weight:700; font-size:22px; margin-bottom:6px; }
/* floating manage button */
.manage-floating {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 9999;
  background: linear-gradient(90deg,#8b5cf6,#ec4899);
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(140,52,255,0.16);
  border: none;
}
</style>
"""

# apply NEON_CSS
st.markdown(NEON_CSS, unsafe_allow_html=True)

# ------------------ Sidebar ------------------
with st.sidebar:
    st.markdown("## ☰ Menu", unsafe_allow_html=True)
    page = st.radio("", ["🏠 Dashboard", "🤖 AI Mentor", "📝 Notes", "🧪 Quizzes", "🧪 Code Runner", "🌌 Spectorial"], index=0)
    st.markdown("---")
    st.selectbox("Theme", ["neon"], index=0, help="Theme is currently neon (custom).")
    st.markdown("### Assistant Settings")
    st.session_state.assistant_mode = st.selectbox("Mode", ["Tutor", "Code Helper", "Motivator"], index=["Tutor","Code Helper","Motivator"].index(st.session_state.assistant_mode) if st.session_state.assistant_mode in ["Tutor","Code Helper","Motivator"] else 0)
    st.session_state.use_memory = st.checkbox("Use short-term memory", value=st.session_state.use_memory)
    st.session_state.use_tts = st.checkbox("Enable TTS (gTTS)", value=st.session_state.use_tts)
    st.session_state.enable_code_exec = st.checkbox("Enable Code Execution (unsafe)", value=st.session_state.enable_code_exec)
    st.markdown("---")
    st.markdown("**Provider (optional)**")
    provider = st.selectbox("Provider", ["None", "OpenAI", "DeepSeek"], index=0)
    if provider != "None":
        st.session_state.api_provider = provider
        if provider == "OpenAI":
            st.session_state.api_key = st.text_input("OpenAI API Key (optional)", type="password")
        elif provider == "DeepSeek":
            st.session_state.deepseek_key = st.text_input("DeepSeek API Key (optional)", type="password")
    else:
        st.session_state.api_provider = None
    st.markdown("---")
    if st.button("Save App State (local)"):
        ok = save_state_local()
        if ok:
            st.success("Saved to local JSON.")
    if st.button("Load App State (local)"):
        ok = load_state_local()
        if ok:
            st.success("Loaded local state.")
    st.markdown("Keys: use `.streamlit/secrets.toml` or env vars `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`.")
    st.markdown("---")
    st.caption("Moscifer • CSE Mentor — Built 2025")

# ------------------ Utility: pretty multi-color donut ------------------
def multicolor_donut(value, size=260, title=None, colors=None, show_center=True):
    # colors: list of color hex; if not provided use rainbow
    if colors is None:
        colors = ["#00FFB2","#00A3FF","#A100FF","#FF3FA0","#FFB84D"]
    # create slices: one slice for value and one remainder; then overlay gradient-like ring using multiple thin annular traces
    fig = go.Figure()

    # We'll build a single donut with gradient-ish effect using multiple concentric pie rings (visual trick)
    # Outer ring (decorative)
    fig.add_trace(go.Pie(values=[value, 100-value], hole=0.72,
                         marker=dict(colors=[colors[0], 'rgba(0,0,0,0)']),
                         textinfo='none', sort=False, direction='clockwise', hoverinfo='none', showlegend=False))
    # Middle ring with blended color
    fig.add_trace(go.Pie(values=[value, 100-value], hole=0.58,
                         marker=dict(colors=[colors[1], 'rgba(0,0,0,0)']),
                         textinfo='none', sort=False, hoverinfo='none', showlegend=False))
    # Inner ring (accent)
    fig.add_trace(go.Pie(values=[value, 100-value], hole=0.40,
                         marker=dict(colors=[colors[2], 'rgba(0,0,0,0)']),
                         textinfo='none', sort=False, hoverinfo='none', showlegend=False))

    # layout
    fig.update_layout(
        margin=dict(t=10,b=10,l=10,r=10),
        height=size, width=size,
        paper_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=f"<span style='font-size:30px;font-weight:700;color:#ffffff'>{value}%</span><br><span style='font-size:10px;color:#bfffc2'>{title or ''}</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=14))] if show_center else []
    )
    fig.update_traces(rotation=90)
    return fig

# ------------------ Floating Manage button (UI only) ------------------
manage_button = st.empty()

# ------------------ Dashboard Page ------------------
if page == "🏠 Dashboard":
    # header
    col_title, col_spacer = st.columns([8,2])
    with col_title:
        st.markdown("<div class='neon-header'>🎓 CSE Learning Path Dashboard — AI Mentor (Pro)</div>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>Track progress, use the AI mentor, preserve notes & reflect with Spectorial mode.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # top metrics row
    c1, c2, c3 = st.columns([1.6,1,1])
    overall = int(st.session_state.courses["Completion"].mean())
    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex; align-items:center; gap:14px;'>", unsafe_allow_html=True)
        # big donut
        donut_fig = multicolor_donut(overall, size=260, title="Total Completion", colors=["#00ffb2","#00d1ff","#9a6bff"])
        st.plotly_chart(donut_fig, use_container_width=False, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.metric("Courses", len(st.session_state.courses))
        st.metric("Active Topic", value=(st.session_state.topic_memory or "—"))
    with c3:
        if st.button("➕ Add Course"):
            st.session_state.show_add_course = True
        if st.session_state.get("show_add_course"):
            with st.form("add_course"):
                n = st.text_input("Course name","New Course")
                cperc = st.slider("Initial completion",0,100,0)
                status = st.selectbox("Status",["Not Started","In Progress","Completed"], index=1)
                sub = st.form_submit_button("Add")
                if sub:
                    st.session_state.courses = pd.concat([st.session_state.courses, pd.DataFrame([{"Course":n,"Completion":int(cperc),"Status":status}])], ignore_index=True)
                    st.session_state.show_add_course = False
                    save_state_local()
                    st.success(f"Added {n}")

    st.markdown("---")

    # Weekly progress with four donuts
    st.subheader("📆 Weekly Progress")
    weeks = ["Week 1","Week 2","Week 3","Week 4"]
    # create pseudo-values for weekly donuts (closer to image)
    wvals = [int(np.clip(overall - 5*i + random.randint(-3,6), 6, 96)) for i in range(4)]
    wcols = st.columns(4)
    for i, col in enumerate(wcols):
        with col:
            figw = multicolor_donut(wvals[i], size=180, title=f"{weeks[i]}")
            st.plotly_chart(figw, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # Courses & actions area
    st.subheader("📚 Courses & AI Actions")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    grid_cols = st.columns([3,1,1])
    # left column: course list summary
    left = grid_cols[0]
    mid = grid_cols[1]
    right = grid_cols[2]
    with left:
        # a subtle search bar
        search = st.text_input("Search courses (name/status)")
        df = st.session_state.courses.copy()
        if search:
            mask = df["Course"].str.contains(search, case=False, na=False) | df["Status"].str.contains(search, case=False, na=False)
            df = df[mask]
        # show compact course cards
        for idx, row in df.iterrows():
            st.markdown(f"<div class='small-card'><b style='color:#bfffc2'>{row['Course']}</b> — <small style='color:#8fffbf'>{row['Status']}</small><div style='margin-top:6px;color:#9fffd2'>Completion: {int(row['Completion'])}%</div></div>", unsafe_allow_html=True)

    # middle: showcase three big donuts summarizing top courses (mimicking image)
    with mid:
        # take top three course completions
        top3 = st.session_state.courses.sort_values("Completion", ascending=False).head(3)
        for _, r in top3.iterrows():
            f = multicolor_donut(int(r['Completion']), size=130, title=r['Course'], colors=["#00ffb2","#00d1ff","#ff6bcb"])
            st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False})

    # right column: sliders and actions
    with right:
        st.markdown("<div style='padding:6px 0'>Quick actions</div>", unsafe_allow_html=True)
        # iterate and create sliders for each course (compact)
        for i, row in st.session_state.courses.reset_index().iterrows():
            label = f"{row['Course']} ({int(row['Completion'])}%)"
            new = st.slider(label, 0, 100, int(row['Completion']), key=f"slider_{i}", help="Adjust progress",)
            if new != int(row['Completion']):
                st.session_state.courses.at[row['index'], 'Completion'] = int(new)
                st.session_state.courses.at[row['index'], 'Status'] = 'Completed' if new==100 else ('Not Started' if new==0 else 'In Progress')
                save_state_local()
                st.experimental_rerun()
            # small AI action
            if st.button("Ask AI", key=f"ask_ai_{i}"):
                prompt = f"Give a short study plan for {row['Course']} at {row['Completion']}% completion."
                st.session_state.chat_history.append({"sender":"user","message":prompt,"ts":now_iso()})
                reply = simulated_llm_reply(prompt, mode=st.session_state.assistant_mode)
                st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
                if st.session_state.use_tts and TTS_AVAILABLE:
                    audio = tts_speak_bytes(reply)
                    if audio:
                        st.audio(audio, format='audio/mp3')
                save_state_local()
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Detailed table
    st.subheader("📈 Detailed Course Progress")
    try:
        st.dataframe(st.session_state.courses.style.format({'Completion':'{:.0f}'}), use_container_width=True)
    except Exception:
        st.dataframe(st.session_state.courses, use_container_width=True)

    # export buttons
    dl1, dl2 = st.columns(2)
    with dl1:
        csv = st.session_state.courses.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export CSV", data=csv, file_name="courses.csv", mime="text/csv")
    with dl2:
        j = st.session_state.courses.to_json(orient="records", indent=2).encode("utf-8")
        st.download_button("⬇️ Export JSON", data=j, file_name="courses.json", mime="application/json")

    st.markdown("---")
    st.markdown("<div style='color:#bfffc2'>Developed by Anish • AI Mentor (Ultimate) © 2025</div>", unsafe_allow_html=True)

    # floating manage app button
    st.markdown("<button class='manage-floating'>⚙️ Manage app</button>", unsafe_allow_html=True)


# ------------------ AI Mentor Page ------------------
elif page == "🤖 AI Mentor":
    st.markdown("<div class='neon-header'>🤖 AI Mentor</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Ask the mentor, choose modes, and use quick actions. Offline fallback active if no API is configured.</div>", unsafe_allow_html=True)
    st.markdown("")
    q1,q2,q3,q4 = st.columns(4)
    if q1.button("💪 Motivate Me"):
        st.session_state.chat_history.append({"sender":"user","message":"motivate me","ts":now_iso()})
        r = simulated_llm_reply("motivate me", mode="Motivator")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q2.button("🐍 Python Tip"):
        st.session_state.chat_history.append({"sender":"user","message":"tell me about python","ts":now_iso()})
        r = simulated_llm_reply("tell me about python", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q3.button("🧠 AI Info"):
        st.session_state.chat_history.append({"sender":"user","message":"tell me about ai","ts":now_iso()})
        r = simulated_llm_reply("tell me about ai", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q4.button("🌐 Web Help"):
        st.session_state.chat_history.append({"sender":"user","message":"help with web dev","ts":now_iso()})
        r = simulated_llm_reply("help with web dev", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()

    st.markdown("")
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history=[]; st.session_state.topic_memory=None; st.session_state.chat_summary=None
        save_state_local(); st.success("Cleared chat.")

    # Chat area
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if st.session_state.chat_summary and st.session_state.use_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Memory: {st.session_state.chat_summary}</div>", unsafe_allow_html=True)
    for m in st.session_state.chat_history:
        sender = m.get("sender"); msg = m.get("message"); ts = m.get("ts")
        tstr = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender == "user":
            st.markdown(f"<div style='text-align:right'><div class='bubble-user'><b>You:</b> {msg}</div><div class='small-muted' style='text-align:right'>{tstr}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'><div class='bubble-bot'><b>Assistant:</b> {msg}</div><div class='small-muted'>{tstr}</div></div>", unsafe_allow_html=True)
    if st.session_state.typing:
        st.markdown("<div class='small-muted'>Assistant is typing...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # input
    with st.form("chat_form", clear_on_submit=True):
        user_text = st.text_input("Ask the AI mentor (type 'bye' to clear memory)")
        submitted = st.form_submit_button("Send")
        if submitted and user_text and user_text.strip():
            st.session_state.chat_history.append({"sender":"user","message":user_text.strip(),"ts":now_iso()})
            reply = simulated_llm_reply(user_text.strip(), mode=st.session_state.assistant_mode)
            st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
            if st.session_state.use_tts and TTS_AVAILABLE:
                audio = tts_speak_bytes(reply)
                if audio:
                    st.audio(audio, format='audio/mp3')
            if st.session_state.use_memory:
                st.session_state.chat_summary = summarize_memory()
            save_state_local()
            st.experimental_rerun()

    st.markdown("---")
    if st.button("💾 Save Chat CSV"):
        if st.session_state.chat_history:
            df = pd.DataFrame(st.session_state.chat_history)
            b = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download chat", data=b, file_name="chat_history.csv", mime="text/csv")
        else:
            st.info("No chat yet.")

# ------------------ Notes Page ------------------
elif page == "📝 Notes":
    st.markdown("<div class='neon-header'>📝 Notes</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Quick note-taking. Notes persist to local JSON.</div>", unsafe_allow_html=True)
    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("Title")
        body = st.text_area("Body")
        s = st.form_submit_button("Add Note")
        if s and (title.strip() or body.strip()):
            st.session_state.notes.append({"title":title,"body":body,"ts":now_iso()})
            save_state_local(); st.success("Note saved."); st.experimental_rerun()
    if st.session_state.notes:
        for n in reversed(st.session_state.notes[-30:]):
            st.markdown(f"**{n['title']}** — <span class='small-muted'>{n['ts']}</span>", unsafe_allow_html=True)
            st.write(n['body']); st.markdown("---")
    else:
        st.info("No notes yet.")

# ------------------ Quizzes Page ------------------
elif page == "🧪 Quizzes":
    st.markdown("<div class='neon-header'>🧪 Quizzes</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Short quizzes are generated from your courses. Try one and save your score.</div>", unsafe_allow_html=True)
    top_course = st.session_state.courses.loc[st.session_state.courses['Completion'].idxmax()]['Course']
    st.markdown(f"**Suggested course for quiz:** {top_course}")
    if st.button("Generate 3-question quiz"):
        quiz = [
            {"q":f"What is a common data structure used in {top_course} to implement FIFO?", "a":"queue"},
            {"q":f"In Python, which keyword defines a function?", "a":"def"},
            {"q":f"What complexity (big-O) is average-case for binary search?", "a":"logarithmic"}
        ]
        st.session_state.current_quiz = quiz
        st.experimental_rerun()
    if st.session_state.get("current_quiz"):
        answers = []
        for i, qa in enumerate(st.session_state.current_quiz):
            ans = st.text_input(f"Q{i+1}: {qa['q']}", key=f"quiz_in_{i}")
            answers.append(ans)
        if st.button("Submit Quiz"):
            score = 0
            for i, qa in enumerate(st.session_state.current_quiz):
                if answers[i] and qa['a'] in answers[i].lower():
                    score += 1
            st.session_state.quiz_scores[top_course] = st.session_state.quiz_scores.get(top_course, []) + [{"score": score, "ts": now_iso()}]
            save_state_local()
            st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
            del st.session_state.current_quiz
            st.experimental_rerun()
    if st.session_state.quiz_scores:
        st.markdown("### Past Scores")
        st.write(st.session_state.quiz_scores)

# ------------------ Code Runner Page ------------------
elif page == "🧪 Code Runner":
    st.markdown("<div class='neon-header'>🧪 Code Runner</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Run short Python snippets on this machine. ⚠️ Enable only in trusted environments.</div>", unsafe_allow_html=True)
    st.markdown("**Enable execution toggle** in the sidebar to run code.")
    code = st.text_area("Enter Python code", value='print(\"Hello, world!\")', height=220)
    if st.session_state.enable_code_exec:
        if st.button("Run (5s timeout)"):
            out, err, to = run_code_snippet(code, timeout=5)
            if to:
                st.error("Execution timed out.")
            else:
                if out:
                    st.code(out)
                if err:
                    st.error(err)
    else:
        st.info("Code execution is disabled. Toggle 'Enable Code Execution' in the sidebar to run (unsafe).")

# ------------------ Spectorial Mode ------------------
elif page == "🌌 Spectorial":
    st.markdown("<div class='neon-header'>🌌 Spectorial Mode</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>A reflective journaling and creativity interface inspired by 'Spectorial Consciousness'.</div>", unsafe_allow_html=True)
    prompt = st.selectbox("Prompt", ["Free write","What did I learn today?","Ideas for a creative project","What meaning did I find in my studies?"])
    entry = st.text_area("Write your reflective entry here", height=260)
    if st.button("Save Entry"):
        st.session_state.spectorial_entries.append({"prompt":prompt,"entry":entry,"ts":now_iso()})
        save_state_local(); st.success("Saved.")
    if st.session_state.spectorial_entries:
        st.markdown("### Past Entries")
        for e in reversed(st.session_state.spectorial_entries[-15:]):
            st.markdown(f"**{e['prompt']}** — <span class='small-muted'>{e['ts']}</span>", unsafe_allow_html=True)
            st.write(e['entry']); st.markdown("---")

# ------------------ Footer ------------------
st.markdown("<div style='text-align:center; color:#bfffc2; margin-top:18px'> Learning Path •  Dashboard — Built 2025</div>", unsafe_allow_html=True)
