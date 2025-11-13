# app_sleek_pro.py
"""
Sleek Pro — CSE Learning Path (Streamlit)
Dark, professional UI with AI Mentor, courses, notes, quizzes and a code runner.

Keys:
- Put DEEPSEEK_API_KEY or OPENAI_API_KEY in .streamlit/secrets.toml or as environment variables.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import json
import requests
import subprocess
import shlex
from io import BytesIO
import random

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Sleek Pro — AI Mentor", layout="wide", initial_sidebar_state="expanded")
PERSIST_FILE = "sleek_pro_state.json"

# ------------------ SESSION DEFAULTS ------------------
def init_state():
    defaults = {
        "courses": None,
        "chat_history": [],
        "topic_memory": None,
        "chat_summary": None,
        "notes": [],
        "tasks": [],
        "quiz_scores": {},
        "theme": "dark",
        "typing": False,
        "provider": None,
        "openai_key": None,
        "deepseek_key": None,
        "enable_code": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def make_default_courses():
    rows = [
        {"Course":"Python", "Completion":85, "Status":"In Progress"},
        {"Course":"C++", "Completion":60, "Status":"In Progress"},
        {"Course":"Web Dev", "Completion":75, "Status":"In Progress"},
        {"Course":"AI", "Completion":40, "Status":"Not Started"},
        {"Course":"Data Science", "Completion":55, "Status":"In Progress"}
    ]
    return pd.DataFrame(rows)

init_state()
if st.session_state.courses is None:
    st.session_state.courses = make_default_courses()

# ------------------ PERSISTENCE ------------------
def save_state():
    try:
        state = {
            "courses": st.session_state.courses.to_dict(orient="records"),
            "chat_history": st.session_state.chat_history,
            "topic_memory": st.session_state.topic_memory,
            "notes": st.session_state.notes,
            "tasks": st.session_state.tasks,
            "quiz_scores": st.session_state.quiz_scores,
        }
        with open(PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        st.warning(f"Save failed: {e}")
        return False

def load_state():
    try:
        with open(PERSIST_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("courses"):
            st.session_state.courses = pd.DataFrame(state["courses"])
        st.session_state.chat_history = state.get("chat_history", [])
        st.session_state.topic_memory = state.get("topic_memory")
        st.session_state.notes = state.get("notes", [])
        st.session_state.tasks = state.get("tasks", [])
        st.session_state.quiz_scores = state.get("quiz_scores", {})
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        st.warning(f"Load failed: {e}")
        return False

load_state()

# ------------------ STYLES (SLEEK PRO) ------------------
SLEEK_CSS = """
<style>
:root {
  --bg: #0f1113;
  --card: #141619;
  --muted: #9aa6b2;
  --accent: #1ec2ff;
  --glass: rgba(255,255,255,0.03);
}
.stApp {
  background: linear-gradient(90deg, var(--bg) 0%, #0b0b0b 100%);
  color: #e6eef1;
  font-family: Inter, sans-serif;
}
.header {
  display:flex;
  align-items:center;
  gap:12px;
}
.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.03);
}
.small { color: var(--muted); font-size:13px; }
.title { font-weight:700; font-size:20px; color:#ffffff; }
.kpi { font-size:22px; font-weight:700; color:var(--accent); }
.course-badge { background: var(--glass); padding:6px 10px; border-radius:8px; border:1px solid rgba(255,255,255,0.02); display:inline-block; }
.chat-area { background: transparent; max-height:56vh; overflow-y:auto; padding-right:8px; }
.bubble-user { background: linear-gradient(180deg,#132027,#0b3948); color:#e8fbff; padding:10px 12px; border-radius:12px; margin:8px 0; align-self:flex-end; max-width:78%; }
.bubble-bot { background: linear-gradient(180deg,#1b1f22,#122028); color:#e6fff9; padding:10px 12px; border-radius:12px; margin:8px 0; align-self:flex-start; max-width:78%; }
.neutral { color: var(--muted); }
.small-muted { font-size:12px; color:var(--muted); }
</style>
"""
st.markdown(SLEEK_CSS, unsafe_allow_html=True)

# ------------------ UTILITIES ------------------
def now_iso():
    return pd.Timestamp.utcnow().isoformat()

# Safe-ish code runner (host machine) — enable only when you trust environment
def run_code(code: str, timeout=4):
    try:
        proc = subprocess.run(["python", "-c", code], capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return "", "Execution timed out."
    except Exception as e:
        return "", f"Execution error: {e}"

# ------------------ AI: Summarizer + Simulated assistant ------------------
def summarize_chat(max_chars=600):
    msgs = st.session_state.chat_history[-30:]
    if not msgs:
        return None
    user_lines = [m["message"] for m in msgs if m["sender"]=="user"]
    kws = ["python","ai","data","web","bug","exercise","project","pomodoro","streamlit","deepseek","openai"]
    found = sorted({k for t in user_lines for k in kws if k in t.lower()})
    summary = "Topics: " + (", ".join(found) if found else "general") + ". "
    summary += "Recent: " + " | ".join(user_lines[-3:]) if user_lines else ""
    return summary[:max_chars]

def simulated_assistant(msg: str, mode="Tutor"):
    msg_l = msg.lower()
    if mode=="Code Helper":
        if any(x in msg_l for x in ["error","traceback","bug","fix"]):
            return "Paste the error or a minimal code snippet and I'll suggest fixes plus a corrected example."
        if "streamlit" in msg_l:
            return "Tip: use `st.form` to group inputs and `st.session_state` for persistent values. Want a snippet?"
        return "Describe the issue and I'll return a short runnable sample."
    if mode=="Motivator":
        return random.choice([
            "Start with a 25-min focus session. Small steps compound.",
            "Celebrate one small win today — even a single solved problem counts.",
            "If stuck, break the task into 5-minute chunks and try again."
        ])
    # Tutor
    # Inspect courses for contextual reply
    for c in st.session_state.courses["Course"].tolist():
        if c.lower() in msg_l:
            comp = int(st.session_state.courses.loc[st.session_state.courses['Course']==c,'Completion'].values[0])
            if comp < 50:
                return f"You're {comp}% through {c}. Suggestion: revisit fundamentals for two 25-min sessions, then solve 3 basic problems. Want problems now?"
            else:
                return f"At {comp}% in {c}, try a 1-2 hour mini-project or 5 medium problems. Want a project idea?"
    if "exercise" in msg_l or "problem" in msg_l:
        return "Mini exercise: write a function to reverse words while preserving whitespace. Want the solution in Python?"
    return "I can help with study plans, exercises, debugging, or motivation — which would you like?"

# ------------------ External LLM scaffolds ------------------
def call_openai(api_key, system_prompt, user_prompt):
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if False else "gpt-4o-mini",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            max_tokens=400, temperature=0.6
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.warning(f"OpenAI call failed: {e}")
        return None

def call_deepseek(api_key, user_prompt):
    # prefer explicit, then secrets, then env
    key = api_key or st.secrets.get("DEEPSEEK_API_KEY") if "DEEPSEEK_API_KEY" in st.secrets else os.getenv("DEEPSEEK_API_KEY")
    if not key:
        st.warning("DeepSeek key missing. Add to .streamlit/secrets.toml or env var DEEPSEEK_API_KEY.")
        return None
    try:
        endpoint = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model":"deepseek-reasoner", "messages":[{"role":"system","content":"You are a helpful CS tutor."},{"role":"user","content":user_prompt}], "temperature":0.7, "max_tokens":400}
        r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        # handle common shapes
        if isinstance(data, dict):
            choices = data.get("choices")
            if choices and isinstance(choices, list) and len(choices)>0:
                first = choices[0]
                if isinstance(first.get("message"), dict):
                    return first["message"].get("content")
                if first.get("text"):
                    return first.get("text")
            if data.get("text"): return data.get("text")
            if data.get("output"): return data.get("output")
        return None
    except Exception as e:
        st.warning(f"DeepSeek call failed: {e}")
        return None

def generate_reply(user_msg, mode="Tutor"):
    st.session_state.typing = True
    time.sleep(np.random.uniform(0.2,0.8))
    st.session_state.typing = False
    # update summary
    st.session_state.chat_summary = summarize_chat()
    provider = st.session_state.provider
    if provider == "OpenAI":
        key = st.session_state.openai_key or (st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY"))
        if key:
            sys = build_system_prompt(mode)
            text = call_openai(key, sys, user_msg)
            if text: return text
    if provider == "DeepSeek":
        key = st.session_state.deepseek_key or None
        text = call_deepseek(key, user_msg)
        if text: return text
    # fallback
    return simulated_assistant(user_msg, mode)

def build_system_prompt(mode):
    base = {
        "Tutor":"You are a helpful computer science tutor. Keep answers concise and actionable.",
        "Code Helper":"You are a pragmatic code assistant. Provide runnable examples and debugging tips.",
        "Motivator":"You give short motivational prompts and micro-goals."
    }.get(mode, "You are a helpful assistant.")
    ctx = (" Memory: " + (st.session_state.chat_summary or "")) if st.session_state.chat_summary else ""
    return base + ctx

# ------------------ LAYOUT ------------------
# Sidebar
with st.sidebar:
    st.markdown("<div class='card'><div class='title'>Sleek Pro • Settings</div><div class='small'>Configure assistant & persistence</div></div>", unsafe_allow_html=True)
    # Provider
    st.markdown("### AI Provider")
    prov = st.selectbox("Provider", ["None","DeepSeek","OpenAI"], index=0)
    st.session_state.provider = prov if prov!="None" else None
    if st.session_state.provider == "OpenAI":
        st.session_state.openai_key = st.text_input("OpenAI Key (paste)", type="password", value=st.session_state.openai_key or "")
    if st.session_state.provider == "DeepSeek":
        st.session_state.deepseek_key = st.text_input("DeepSeek Key (paste)", type="password", value=st.session_state.deepseek_key or "")
    st.markdown("---")
    st.session_state.theme = st.selectbox("Theme", ["dark","light"], index=0 if st.session_state.theme=="dark" else 1)
    st.session_state.enable_code = st.checkbox("Enable code execution (unsafe)", value=st.session_state.enable_code)
    if st.button("Save app state"):
        ok = save_state()
        if ok: st.success("Saved locally.")
    if st.button("Load app state"):
        ok = load_state()
        if ok: st.success("Loaded.")

# Top bar
st.markdown("<div class='header'><img src='https://cdn-icons-png.flaticon.com/512/1055/1055687.png' width=36><div><div class='title'>Sleek Pro — AI Mentor</div><div class='small'>Professional dark UI for learning & coding</div></div></div>", unsafe_allow_html=True)
st.markdown("---")

# Main columns
left, right = st.columns([2.2, 1])

# LEFT: Dashboard & Chat
with left:
    # Cards row
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("<div class='card'><div class='small'>Overall Progress</div><div class='kpi'>%d%%</div></div>" % int(st.session_state.courses["Completion"].mean()), unsafe_allow_html=True)
        # progress donut
        fig = go.Figure(go.Pie(values=[st.session_state.courses["Completion"].mean(), 100-st.session_state.courses["Completion"].mean()], hole=0.7,
                               marker=dict(colors=["#1ec2ff","#111214"])))
        fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)", height=160)
        st.plotly_chart(fig, use_container_width=True)
    with r2:
        st.markdown("<div class='card'><div class='small'>Top Course</div><div class='kpi'>%s</div></div>" % st.session_state.courses.loc[st.session_state.courses['Completion'].idxmax(),"Course"], unsafe_allow_html=True)

    st.markdown("---")
    # Courses table + sliders
    st.subheader("Courses")
    for idx, row in st.session_state.courses.reset_index().iterrows():
        c1, c2 = st.columns([3,1])
        with c1:
            st.markdown(f"<div class='card'><b>{row['Course']}</b> — <span class='small-muted'>{row['Status']}</span><br><span class='small'>Completion: {int(row['Completion'])}%</span></div>", unsafe_allow_html=True)
        with c2:
            new = st.slider(f"prog_{row['index']}", 0, 100, int(row['Completion']), key=f"prog_{row['index']}")
            if new != int(row['Completion']):
                st.session_state.courses.at[row['index'],'Completion'] = int(new)
                st.session_state.courses.at[row['index'],'Status'] = 'Completed' if new==100 else ('Not Started' if new==0 else 'In Progress')
                save_state()
                st.experimental_rerun()

    st.markdown("---")
    # Interactive weekly growth
    st.subheader("Weekly Growth")
    weeks = ["Wk1","Wk2","Wk3","Wk4"]
    vals = [int(np.clip(st.session_state.courses["Completion"].mean() + i*3 - 4, 0, 100)) for i in range(4)]
    bar = go.Figure(go.Bar(x=weeks, y=vals, text=vals, textposition="auto"))
    bar.update_layout(margin=dict(t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", height=260)
    st.plotly_chart(bar, use_container_width=True)

    st.markdown("---")
    # Chat panel
    st.subheader("AI Mentor Chat")
    st.markdown("<div class='card chat-area' id='chat-area'>", unsafe_allow_html=True)
    if st.session_state.chat_summary:
        st.markdown(f"<div class='small-muted'>Memory: {st.session_state.chat_summary}</div>", unsafe_allow_html=True)
    # show messages
    for m in st.session_state.chat_history[-60:]:
        if m["sender"] == "user":
            st.markdown(f"<div style='display:flex; justify-content:flex-end'><div class='bubble-user'><b>You:</b> {m['message']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='display:flex; justify-content:flex-start'><div class='bubble-bot'><b>Mentor:</b> {m['message']}</div></div>", unsafe_allow_html=True)
    if st.session_state.typing:
        st.markdown("<div class='small-muted'>Mentor is typing...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # chat input
    with st.form("chat", clear_on_submit=True):
        user_text = st.text_input("Ask the AI Mentor (type 'bye' to clear memory)")
        mode = st.selectbox("Mode", ["Tutor","Code Helper","Motivator"], index=0)
        submit = st.form_submit_button("Send")
        if submit and user_text.strip():
            st.session_state.chat_history.append({"sender":"user","message":user_text.strip(),"ts":now_iso()})
            # clear memory if bye
            if user_text.strip().lower() in ("bye","goodbye","reset memory"):
                st.session_state.topic_memory = None
                st.session_state.chat_summary = None
                reply = "👋 Memory cleared. See you soon."
            else:
                reply = generate_reply(user_text.strip(), mode=mode)
            st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
            # update memory
            st.session_state.chat_summary = summarize_chat()
            save_state()
            st.experimental_rerun()

# RIGHT: Notes, Tasks, Code Runner, Quizzes quick view
with right:
    st.markdown("<div class='card'><div class='small'>Notes</div></div>", unsafe_allow_html=True)
    with st.form("note_form", clear_on_submit=True):
        t = st.text_input("Title")
        b = st.text_area("Note")
        add = st.form_submit_button("Add Note")
        if add and (t.strip() or b.strip()):
            st.session_state.notes.append({"title":t,"body":b,"ts":now_iso()})
            save_state()
            st.success("Note added.")
            st.experimental_rerun()
    if st.session_state.notes:
        for n in reversed(st.session_state.notes[-6:]):
            st.markdown(f"**{n['title']}** — <span class='small-muted'>{n['ts']}</span>", unsafe_allow_html=True)
            st.write(n['body'])
            st.markdown("---")
    else:
        st.info("No notes yet.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><div class='small'>Tasks</div></div>", unsafe_allow_html=True)
    with st.form("task_form", clear_on_submit=True):
        task = st.text_input("New task")
        due = st.text_input("Optional due date")
        addt = st.form_submit_button("Add Task")
        if addt and task.strip():
            st.session_state.tasks.append({"task":task,"due":due,"done":False,"ts":now_iso()})
            save_state()
            st.success("Task added.")
            st.experimental_rerun()
    if st.session_state.tasks:
        for i,tk in enumerate(st.session_state.tasks):
            cols = st.columns([0.1,4,1])
            ok = cols[0].checkbox("", value=tk.get("done",False), key=f"task_{i}")
            if ok != tk.get("done",False):
                st.session_state.tasks[i]["done"] = ok
                save_state()
                st.experimental_rerun()
            cols[1].markdown(f"{tk['task']} <div class='small-muted'>{tk.get('due','')}</div>", unsafe_allow_html=True)
            if cols[2].button("✖", key=f"del_{i}"):
                st.session_state.tasks.pop(i)
                save_state()
                st.experimental_rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><div class='small'>Code Runner</div></div>", unsafe_allow_html=True)
    code_input = st.text_area("Python snippet", value="print('Hello from Sleek Pro')", height=150)
    if st.session_state.enable_code:
        if st.button("Run Code"):
            out, err = run_code(code_input, timeout=5)
            if out:
                st.code(out)
            if err:
                st.error(err)
    else:
        st.info("Enable 'Enable code execution' in the sidebar to run snippets (unsafe).")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'><div class='small'>Quick Quiz</div></div>", unsafe_allow_html=True)
    top = st.session_state.courses.loc[st.session_state.courses['Completion'].idxmax()]["Course"]
    st.markdown(f"Suggested: **{top}**")
    if st.button("Generate 3-question quiz"):
        q = [
            {"q":f"What data structure is FIFO commonly implemented with in {top}?", "a":"queue"},
            {"q":"Which Python keyword defines a function?", "a":"def"},
            {"q":"What is the Big-O for binary search (average)?", "a":"logarithmic"}
        ]
        st.session_state.current_quiz = q
        st.experimental_rerun()
    if st.session_state.get("current_quiz"):
        answers = []
        for i,qa in enumerate(st.session_state.current_quiz):
            answers.append(st.text_input(f"Q{i+1}: {qa['q']}", key=f"quiz_{i}"))
        if st.button("Submit Quiz"):
            score = sum(1 for i,qa in enumerate(st.session_state.current_quiz) if answers[i] and qa["a"] in answers[i].lower())
            st.session_state.quiz_scores.setdefault(top,[]).append({"score":score,"ts":now_iso()})
            save_state()
            st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
            del st.session_state["current_quiz"]
            st.experimental_rerun()
    if st.session_state.quiz_scores:
        st.markdown("### Past Scores")
        st.write(st.session_state.quiz_scores)

# -------------- footer --------------
st.markdown("<div style='text-align:center; color:#9aa6b2; padding:14px'>Sleek Pro • Moscifer — Built 2025</div>", unsafe_allow_html=True)
