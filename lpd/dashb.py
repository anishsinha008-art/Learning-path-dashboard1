# app_superior.py
"""
CSE Learning Path — AI Mentor (Ultimate)
Features:
- UI: Neon/dark themes, course management, charts
- AI: DeepSeek/OpenAI scaffold + offline simulator + modes
- TTS via gTTS
- Notes, quizzes, code runner (toggle), Spectorial Mode
- Persistence (local JSON), secrets/env support for API keys

Setup:
pip install streamlit pandas plotly numpy requests gTTS
(install openai package if you want OpenAI integration)
Use .streamlit/secrets.toml or environment variables for keys:
DEEPSEEK_API_KEY, OPENAI_API_KEY
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import json
import random
import requests
from io import BytesIO
import subprocess
import shlex

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Learning Path Dashboard", layout="wide")

# ------------------ Persistence ------------------
PERSIST_FILE = "cse_dashboard_state.json"

def save_state_local():
    state = {
        "chat_history": st.session_state.chat_history,
        "topic_memory": st.session_state.topic_memory,
        "chat_summary": st.session_state.chat_summary,
        "courses": st.session_state.courses.to_dict(orient="records") if st.session_state.courses is not None else None,
        "notes": st.session_state.notes,
        "quiz_scores": st.session_state.quiz_scores,
    }
    try:
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def make_course_df():
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

def now_iso():
    return pd.Timestamp.utcnow().isoformat()

init_session_state()
if st.session_state.courses is None:
    st.session_state.courses = make_course_df()
load_state_local()

# ------------------ TTS ------------------
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

def tts_speak(text: str):
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

# ------------------ Summarizer & Simulated LLM ------------------
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

def build_system_prompt(mode, course_ctx, chat_summary):
    base = {
        "Tutor": "You are a helpful computer science tutor. Give concise steps and small exercises.",
        "Code Helper": "You are a pragmatic code assistant. Provide runnable examples and debugging tips.",
        "Motivator": "You are a short, encouraging mentor. Provide micro-action prompts.",
    }.get(mode, "You are a helpful assistant.")
    ctx = ""
    if course_ctx:
        ctx += f" Learner context: {course_ctx}."
    if chat_summary and st.session_state.use_memory:
        ctx += f" Memory: {chat_summary}."
    return base + ctx

def simulated_llm_reply(user_msg, mode):
    df = st.session_state.courses
    try:
        top = df.loc[df['Completion'].idxmax()]
        top_hint = f"{top['Course']} ({top['Completion']}%)"
    except Exception:
        top_hint = "none"
    summary = st.session_state.chat_summary or summarize_memory()
    msg = user_msg.lower()
    # Code helper
    if mode == "Code Helper":
        if any(kw in msg for kw in ["bug","error","traceback","fix"]):
            return "Please paste the minimal error or code snippet. I can propose a fix and a runnable example."
        if "streamlit" in msg:
            return "Tip: use st.form to group inputs and st.session_state to persist values. Want a small snippet?"
        return "Describe the issue or desired feature and I'll return a short runnable example."
    # Tutor
    if mode == "Tutor":
        for c in st.session_state.courses['Course'].tolist():
            if c.lower() in msg:
                comp = int(st.session_state.courses.loc[st.session_state.courses['Course']==c, 'Completion'].values[0])
                if comp < 50:
                    return f"You're {comp}% through {c}. Suggestion: 2 sessions of focused review (25min) + 3 practice problems. Want 2 problems now?"
                else:
                    return f"At {comp}% in {c}, try a mini-project (1–2 hours). Want a project idea?"
        if "exercise" in msg or "problem" in msg:
            return "Mini exercise: write a function that reverses words in a sentence while preserving whitespace. Want solution in Python?"
        return "Short plan: (1) 25m review (2) 45m practice (3) 10m reflect. Want me to make a 7-day plan?"
    # Motivator
    if mode == "Motivator":
        choices = [
            "Small wins matter — start with a 25-min pomodoro and log one takeaway.",
            "Consistency > intensity. Pick a micro-goal and do it today.",
            "Stuck? Take a 5-min break, then try again with the rubber-duck technique."
        ]
        return random.choice(choices)
    return "How can I help — study plan, code snippet, or motivation?"

# ------------------ External API scaffolds ------------------
def call_openai_chat(api_key, system_prompt, user_prompt):
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if False else "gpt-4o-mini",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            max_tokens=450, temperature=0.5
        )
        return resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.warning(f"OpenAI call failed or openai lib missing: {e}")
        return None

def call_deepseek(api_key, user_prompt):
    # key can be None -> we will use secrets/env before calling
    key = api_key or None
    if not key:
        try:
            key = st.secrets.get("DEEPSEEK_API_KEY")
        except Exception:
            key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        st.warning("DeepSeek API key not found. Add it to .streamlit/secrets.toml or set DEEPSEEK_API_KEY env var.")
        return None
    try:
        endpoint = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model":"deepseek-reasoner",
            "messages":[{"role":"system","content":"You are a helpful AI mentor for CSE students."},
                        {"role":"user","content":user_prompt}],
            "temperature":0.7,"max_tokens":400
        }
        r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        # handle common shapes
        if isinstance(data, dict):
            choices = data.get("choices")
            if choices and isinstance(choices, list) and len(choices)>0:
                first = choices[0]
                # try message.content
                if isinstance(first.get("message"), dict):
                    return first.get("message").get("content")
                if first.get("text"):
                    return first.get("text")
            if data.get("text"):
                return data.get("text")
            if data.get("output"):
                return data.get("output")
        st.warning("DeepSeek returned unexpected shape.")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"DeepSeek request failed: {e}")
        return None
    except Exception as e:
        st.warning(f"DeepSeek call failed: {e}")
        return None

# ------------------ Main generator ------------------
def generate_bot_reply(user_msg: str, mode: str = None) -> str:
    if mode is None:
        mode = st.session_state.assistant_mode
    st.session_state.typing = True
    time.sleep(np.random.uniform(0.2, 0.9))
    st.session_state.typing = False
    if st.session_state.use_memory:
        st.session_state.chat_summary = summarize_memory()
    provider = st.session_state.api_provider
    # OpenAI
    if provider == "OpenAI":
        key = st.session_state.api_key or (st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY"))
        if key:
            sys = build_system_prompt(mode, course_ctx="", chat_summary=st.session_state.chat_summary)
            txt = call_openai_chat(key, sys, user_msg)
            if txt:
                return txt
    # DeepSeek
    if provider == "DeepSeek":
        key = st.session_state.deepseek_key or None
        txt = call_deepseek(key, user_msg)
        if txt:
            return txt
    # fallback
    return simulated_llm_reply(user_msg, mode)

# ------------------ Code runner (safe-ish) ------------------
def run_code_snippet(code: str, timeout=5):
    """
    Run python code in a subprocess for safety. Returns (stdout, stderr, timed_out_flag).
    ⚠️ WARNING: this executes code on the host machine. Only enable in trusted environments.
    """
    # create a temporary file and run it with python -c
    try:
        # Using subprocess with shell disabled and timeout
        proc = subprocess.run(
            [shlex.split("python -c")[0], "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        return "", "Execution timed out.", True
    except Exception as e:
        return "", f"Execution failed: {e}", False

# ------------------ UI Styles ------------------
NEON_CSS = """
<style>
.stApp { background: #000; color: #bfffc2; }
.card { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 12px; border: 1px solid rgba(0,255,127,0.06); }
.chat-area { background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border-radius: 12px; padding: 12px; max-height:56vh; overflow-y:auto; border:1px solid rgba(0,255,127,0.03); }
.bubble-user { background: linear-gradient(90deg,#003e13,#1b5e20); color:#eafff0; padding:10px; border-radius:12px; margin:8px 0; text-align:right; display:inline-block; max-width:82%; }
.bubble-bot { background: linear-gradient(90deg,#134b2b,#2e7d32); color:#eafff0; padding:10px; border-radius:12px; margin:8px 0; text-align:left; display:inline-block; max-width:82%; }
.memory-badge { background: rgba(0,255,127,0.08); color:#bfffc2; padding:7px 10px; border-radius:10px; display:inline-block; margin-bottom:8px; }
.small-muted { font-size:12px; color:#8fffbf; }
</style>
"""
DARK_CSS = """
<style>
.stApp { background: #0b0b0b; color: #e6eef1; }
.card { background: rgba(255,255,255,0.02); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.03); }
</style>
"""
if st.session_state.theme == "neon":
    st.markdown(NEON_CSS, unsafe_allow_html=True)
else:
    st.markdown(DARK_CSS, unsafe_allow_html=True)

# ------------------ Sidebar ------------------
with st.sidebar:
    st.title("☰ Menu")
    page = st.radio("Navigate:", ["🏠 Dashboard", "🤖 AI Mentor", "📝 Notes", "🧪 Quizzes", "🧪 Code Runner", "🌌 Spectorial"])
    st.markdown("---")
    st.selectbox("Theme:", ["neon", "dark"], index=0 if st.session_state.theme=="neon" else 1, key="theme_select", on_change=lambda: st.session_state.update({"theme":st.session_state.theme_select}))
    st.markdown("---")
    st.header("AI Settings")
    st.session_state.assistant_mode = st.selectbox("Mode:", ["Tutor","Code Helper","Motivator"], index=["Tutor","Code Helper","Motivator"].index(st.session_state.assistant_mode) if st.session_state.assistant_mode in ["Tutor","Code Helper","Motivator"] else 0)
    st.session_state.use_memory = st.checkbox("Use short-term memory", value=st.session_state.use_memory)
    st.session_state.use_tts = st.checkbox("Enable TTS (gTTS)", value=st.session_state.use_tts)
    st.session_state.enable_code_exec = st.checkbox("Enable Code Execution (unsafe)", value=st.session_state.enable_code_exec)
    st.markdown("Optional: connect to LLM provider (keys via secrets/env recommended).")
    provider = st.selectbox("Provider:", ["None","OpenAI","DeepSeek"], index=0)
    if provider != "None":
        st.session_state.api_provider = provider
        if provider == "OpenAI":
            st.session_state.api_key = st.text_input("OpenAI API Key (paste here)", type="password")
        elif provider == "DeepSeek":
            st.session_state.deepseek_key = st.text_input("DeepSeek API Key (paste here)", type="password")
    else:
        st.session_state.api_provider = None
        st.session_state.api_key = None
        st.session_state.deepseek_key = None
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

# ------------------ Dashboard Page ------------------
if page == "🏠 Dashboard":
    st.title("📚Learning Path")
    st.markdown("<div class='card'>Fusion of learning, AI mentor, and creative Spectorial mode. Track progress, ask the AI, take quizzes, run code (if enabled).</div>", unsafe_allow_html=True)

    # top metrics
    c1,c2,c3 = st.columns([1.2,1,1])
    with c1:
        overall = int(st.session_state.courses["Completion"].mean())
        fig = go.Figure(go.Indicator(mode="gauge+number", value=overall, title={'text':"Total Completion"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':'#00FF7F'}}))
        fig.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2')
        st.plotly_chart(fig, use_container_width=True)
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

    # weekly progress
    st.subheader("📆 Weekly Progress")
    weeks = [f"Week {i+1}" for i in range(4)]
    cols = st.columns(len(weeks))
    week_vals=[]
    for i,col in enumerate(cols):
        v = col.slider(weeks[i],0,100,int(np.clip((st.session_state.courses["Completion"].mean()+(i-1)*5),0,100)))
        week_vals.append(v)
    b = go.Figure(go.Bar(x=weeks, y=week_vals, text=week_vals, textposition='auto'))
    b.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(b, use_container_width=True)

    st.markdown("---")

    # courses list with smart actions
    st.subheader("📚 Courses & Actions")
    search = st.text_input("Search courses (name/status)")
    df = st.session_state.courses.copy()
    if search:
        mask = df["Course"].str.contains(search, case=False, na=False) | df["Status"].str.contains(search, case=False, na=False)
        df = df[mask]
    for idx,row in df.reset_index(drop=False).iterrows():
        col1,col2,col3 = st.columns([3,1,1])
        with col1:
            st.markdown(f"<div class='card'><b>{row['Course']}</b> — <small>{row['Status']}</small><br>Completion: {row['Completion']}%</div>", unsafe_allow_html=True)
        with col2:
            new = st.slider(f"prog_{row['index']}",0,100,int(row['Completion']))
            if new != int(row['Completion']):
                st.session_state.courses.at[row['index'],'Completion']=int(new)
                st.session_state.courses.at[row['index'],'Status']= 'Completed' if new==100 else ('Not Started' if new==0 else 'In Progress')
                save_state_local()
                st.experimental_rerun()
        with col3:
            if st.button(f"Ask AI about {row['Course']}", key=f"ask_{row['index']}"):
                prompt = f"Give a short study plan for {row['Course']} at {row['Completion']}% completion."
                st.session_state.chat_history.append({"sender":"user","message":prompt,"ts":now_iso()})
                reply = generate_bot_reply(prompt, mode=st.session_state.assistant_mode)
                st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
                if st.session_state.use_tts and TTS_AVAILABLE:
                    audio = tts_speak(reply)
                    if audio:
                        st.audio(audio, format='audio/mp3')
                save_state_local()
                st.experimental_rerun()

    st.markdown("---")

    # table + export
    st.subheader("📈 Detailed Course Progress")
    try:
        st.dataframe(st.session_state.courses.style.format({'Completion':'{:.0f}'}), use_container_width=True)
    except Exception:
        st.dataframe(st.session_state.courses, use_container_width=True)

    dl1,dl2 = st.columns([1,1])
    with dl1:
        if st.button("Export CSV"):
            csv = st.session_state.courses.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv, file_name="courses.csv", mime="text/csv")
    with dl2:
        if st.button("Export JSON"):
            j = st.session_state.courses.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button("⬇️ Download JSON", data=j, file_name="courses.json", mime="application/json")

    st.markdown("---")
    st.markdown("<div style='color:#bfffc2'>Developed by Anish • AI Mentor (Ultimate) © 2025</div>", unsafe_allow_html=True)

# ------------------ AI Mentor Page ------------------
elif page == "🤖 AI Mentor":
    st.markdown("<h2 class='neon-header'>🤖 AI Mentor</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Ask the mentor, choose modes, and use quick actions. Offline fallback active if no API is configured.</div>", unsafe_allow_html=True)

    # quick starters
    q1,q2,q3,q4 = st.columns(4)
    if q1.button("💪 Motivate Me"): 
        st.session_state.chat_history.append({"sender":"user","message":"motivate me","ts":now_iso()})
        r = generate_bot_reply("motivate me", mode="Motivator")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q2.button("🐍 Python Tip"):
        st.session_state.chat_history.append({"sender":"user","message":"tell me about python","ts":now_iso()})
        r = generate_bot_reply("tell me about python", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q3.button("🧠 AI Info"):
        st.session_state.chat_history.append({"sender":"user","message":"tell me about ai","ts":now_iso()})
        r = generate_bot_reply("tell me about ai", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()
    if q4.button("🌐 Web Help"):
        st.session_state.chat_history.append({"sender":"user","message":"help with web dev","ts":now_iso()})
        r = generate_bot_reply("help with web dev", mode="Tutor")
        st.session_state.chat_history.append({"sender":"bot","message":r,"ts":now_iso()})
        save_state_local(); st.experimental_rerun()

    st.markdown("")
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history=[]; st.session_state.topic_memory=None; st.session_state.chat_summary=None
        save_state_local(); st.success("Cleared chat.")

    # chat area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.chat_summary and st.session_state.use_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Memory: {st.session_state.chat_summary}</div>", unsafe_allow_html=True)
    for m in st.session_state.chat_history:
        sender=m.get("sender"); msg=m.get("message"); ts=m.get("ts")
        tstr = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender=="user":
            st.markdown(f"<div style='text-align:right'><div class='bubble-user'><b>You:</b> {msg}</div><div class='small-muted' style='text-align:right'>{tstr}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'><div class='bubble-bot'><b>Assistant:</b> {msg}</div><div class='small-muted'>{tstr}</div></div>", unsafe_allow_html=True)
    if st.session_state.typing:
        st.markdown("<div class='small-muted'>Assistant is typing...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # input form
    with st.form("chat_form", clear_on_submit=True):
        user_text = st.text_input("Ask the AI mentor (type 'bye' to clear memory)")
        submitted = st.form_submit_button("Send")
        if submitted and user_text and user_text.strip():
            st.session_state.chat_history.append({"sender":"user","message":user_text.strip(),"ts":now_iso()})
            reply = generate_bot_reply(user_text.strip(), mode=st.session_state.assistant_mode)
            st.session_state.chat_history.append({"sender":"bot","message":reply,"ts":now_iso()})
            if st.session_state.use_tts and TTS_AVAILABLE:
                audio = tts_speak(reply)
                if audio: st.audio(audio, format='audio/mp3')
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
    st.markdown("<h2 class='neon-header'>📝 Notes</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Quick note-taking. Notes persist to local JSON.</div>", unsafe_allow_html=True)
    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("Title")
        body = st.text_area("Body")
        s = st.form_submit_button("Add Note")
        if s and (title.strip() or body.strip()):
            st.session_state.notes.append({"title":title,"body":body,"ts":now_iso()})
            save_state_local(); st.success("Note saved."); st.experimental_rerun()
    if st.session_state.notes:
        for i,n in enumerate(reversed(st.session_state.notes)):
            st.markdown(f"**{n['title']}** — <span class='small-muted'>{n['ts']}</span>", unsafe_allow_html=True)
            st.write(n['body'])
            st.markdown("---")
    else:
        st.info("No notes yet.")

# ------------------ Quizzes Page ------------------
elif page == "🧪 Quizzes":
    st.markdown("<h2 class='neon-header'>🧪 Quizzes</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Short quizzes are generated from your courses. Try one and save your score.</div>", unsafe_allow_html=True)
    top_course = st.session_state.courses.loc[st.session_state.courses['Completion'].idxmax()]['Course']
    st.markdown(f"**Suggested course for quiz:** {top_course}")
    if st.button("Generate 3-question quiz"):
        # simple fixed templates (you can expand)
        quiz = [
            {"q":f"What is a common data structure used in {top_course} to implement FIFO?", "a":"queue"},
            {"q":f"In {top_course}, which keyword defines a function in Python?", "a":"def"},
            {"q":f"What complexity (big-O) is average-case for binary search?", "a":"logarithmic"}
        ]
        st.session_state.current_quiz = quiz
        st.experimental_rerun()
    if st.session_state.get("current_quiz"):
        answers = []
        for i,qa in enumerate(st.session_state.current_quiz):
            ans = st.text_input(f"Q{i+1}: {qa['q']}", key=f"quiz_in_{i}")
            answers.append(ans)
        if st.button("Submit Quiz"):
            score=0
            for i,qa in enumerate(st.session_state.current_quiz):
                if answers[i] and qa['a'] in answers[i].lower():
                    score+=1
            st.session_state.quiz_scores[top_course]=st.session_state.quiz_scores.get(top_course,[])+[{"score":score,"ts":now_iso()}]
            save_state_local()
            st.success(f"Score: {score}/{len(st.session_state.current_quiz)}")
            del st.session_state.current_quiz
            st.experimental_rerun()
    if st.session_state.quiz_scores:
        st.markdown("### Past Scores")
        st.write(st.session_state.quiz_scores)

# ------------------ Code Runner Page ------------------
elif page == "🧪 Code Runner":
    st.markdown("<h2 class='neon-header'>🧪 Code Runner</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Run short Python snippets on this machine. ⚠️ Enable only in trusted environments.</div>", unsafe_allow_html=True)
    st.markdown("**Enable execution toggle** in sidebar to run code.")
    code = st.text_area("Enter Python code", value='print(\"Hello, world!\")', height=200)
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
        st.info("Code execution is disabled. Please toggle 'Enable Code Execution' in the sidebar if you understand the risks.")

# ------------------ Spectorial Mode ------------------
elif page == "🌌 Spectorial":
    st.markdown("<h2 class='neon-header'>🌌 Spectorial Mode</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>A reflective journaling and creativity interface inspired by 'Spectorial Consciousness'. Use prompts to explore ideas.</div>", unsafe_allow_html=True)
    prompt = st.selectbox("Prompt", ["Free write","What did I learn today?","Ideas for a creative project","What meaning did I find in my studies?"])
    entry = st.text_area("Write your reflective entry here", height=240)
    if st.button("Save Entry"):
        st.session_state.spectorial_entries.append({"prompt":prompt,"entry":entry,"ts":now_iso()})
        save_state_local(); st.success("Saved.")
    if st.session_state.spectorial_entries:
        st.markdown("### Past Entries")
        for e in reversed(st.session_state.spectorial_entries[-10:]):
            st.markdown(f"**{e['prompt']}** — <span class='small-muted'>{e['ts']}</span>", unsafe_allow_html=True)
            st.write(e['entry']); st.markdown("---")

# ------------------ Footer ------------------
st.markdown("<div style='text-align:center; color:#bfffc2; margin-top:20px'>Moscifer • CSE Mentor — Built 2025</div>", unsafe_allow_html=True)
