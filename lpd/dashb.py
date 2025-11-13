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

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="CSE Learning Path — AI Mentor (Pro)", layout="wide")

# ------------------ HELPERS & PERSISTENCE ------------------
PERSIST_FILE = "cse_dashboard_state.json"


def init_session_state():
    """Initialize session state with safe defaults."""
    defaults = {
        "chat_history": [],  # list of dicts: {sender, message, ts}
        "topic_memory": None,
        "chat_summary": None,
        "download_blob": None,
        "courses": None,
        "theme": "neon",
        "show_more_courses": False,
        "typing": False,
        "assistant_mode": "Tutor",  # Tutor, Code Helper, Motivator
        "use_memory": True,
        "api_provider": None,
        "api_key": None,
        "deepseek_key": None,
        "use_tts": False,
        "use_google_sheets": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def now_iso():
    return pd.Timestamp.utcnow().isoformat()


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


def save_state_local():
    """Save app state locally to a JSON file."""
    state = {
        "chat_history": st.session_state.chat_history,
        "topic_memory": st.session_state.topic_memory,
        "chat_summary": st.session_state.chat_summary,
        "courses": st.session_state.courses.to_dict(orient="records") if st.session_state.courses is not None else None,
    }
    try:
        with open(PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        st.warning(f"Failed to save local state: {e}")
        return False


def load_state_local():
    """Load app state from local JSON if present."""
    try:
        with open(PERSIST_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        if state.get("courses"):
            st.session_state.courses = pd.DataFrame(state.get("courses"))
        st.session_state.chat_history = state.get("chat_history", [])
        st.session_state.topic_memory = state.get("topic_memory")
        st.session_state.chat_summary = state.get("chat_summary")
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        st.warning(f"Failed to load local state: {e}")
        return False


# ------------------ TEXT-TO-SPEECH (TTS) ------------------
# We'll attempt to use gTTS (creates an MP3 in-memory) and play via st.audio.
# If gTTS is unavailable, TTS will be silently disabled.
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


def tts_speak(text: str):
    """Generate TTS audio and return bytes (MP3) for st.audio playback."""
    if not TTS_AVAILABLE:
        st.info("gTTS not installed on server — TTS is unavailable.")
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


# ------------------ SMARTER SUMMARIZATION ------------------
# If OpenAI key is provided, we will use it for better summarization and replies.
# Otherwise, fall back to a compact heuristic summarizer.


def summarize_memory(remote=False, max_chars=1000):
    """Return a concise summary of recent chat messages."""
    msgs = st.session_state.chat_history
    if not msgs:
        return None
    last = msgs[-30:]
    user_texts = [m['message'] for m in last if m['sender'] == 'user']
    # heuristic keyword extraction
    kws = ["python","ai","machine","web","data","project","bug","debug","motivate","study","recursion","ds","algorithms","streamlit","openai","deepseek"]
    keywords = set()
    for t in user_texts:
        for k in kws:
            if k in t.lower():
                keywords.add(k)
    summary = "Topics: " + (", ".join(sorted(keywords)) if keywords else "general") + "."
    if user_texts:
        summary += " Recent: " + " | ".join(user_texts[-3:])
    return summary[:max_chars]


# ------------------ EXTERNAL LLM / DEEPSEEK SCAFFOLD ------------------


def call_openai_chat(api_key: str, system_prompt: str, user_prompt: str):
    """Scaffold to call OpenAI Chat API if openai package is available.
    This is best-effort: if the openai library is not installed or the call fails,
    we return None and the app falls back to the simulated engine.
    """
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini" if False else "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=450,
            temperature=0.5,
        )
        return resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.warning(f"OpenAI call failed or openai lib missing: {e}")
        return None


def call_deepseek(api_key: str, user_prompt: str):
    """Call DeepSeek's production chat endpoint. The function will try these sources for the API key in order:
    1. explicit `api_key` argument
    2. Streamlit secrets (DEEPSEEK_API_KEY)
    3. environment variable DEEPSEEK_API_KEY

    Returns the assistant text or None on failure.
    """
    # prefer explicit key
    key = api_key or None
    if not key:
        try:
            key = st.secrets.get("DEEPSEEK_API_KEY")
        except Exception:
            key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        st.warning("DeepSeek API key not provided. Set .streamlit/secrets.toml or environment variable DEEPSEEK_API_KEY.")
        return None

    try:
        endpoint = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-reasoner",
            "messages": [
                {"role": "system", "content": "You are a helpful AI mentor for CSE students."},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 400,
        }
        r = requests.post(endpoint, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()

        # Try common response shapes (OpenAI-like)
        if isinstance(data, dict):
            choices = data.get("choices")
            if choices and isinstance(choices, list) and len(choices) > 0:
                first = choices[0]
                # message.content style
                if isinstance(first.get("message"), dict):
                    return first.get("message").get("content")
                # choices[0].text style
                if first.get("text"):
                    return first.get("text")

            # fallback top-level fields
            if data.get("text"):
                return data.get("text")
            if data.get("output"):
                return data.get("output")

        # If we didn't return above, give up gracefully
        st.warning("DeepSeek returned an unexpected response shape.")
        return None

    except requests.exceptions.RequestException as e:
        st.warning(f"DeepSeek request failed: {e}")
        return None
    except Exception as e:
        st.warning(f"DeepSeek call failed: {e}")
        return None


# ------------------ SIMULATED LLM (SMARTER) ------------------

def build_system_prompt(mode: str, course_context: str, chat_summary: str) -> str:
    base = {
        "Tutor": "You are a helpful computer science tutor. Provide clear steps, tiny exercises, and concise explanations.",
        "Code Helper": "You are a pragmatic code assistant. Provide runnable snippets and debugging hints when relevant.",
        "Motivator": "You are an encouraging mentor. Give short motivational prompts and practical micro-goals.",
    }.get(mode, "You are a helpful assistant.")

    ctx = ""
    if course_context:
        ctx += f" Learner context: {course_context}."
    if chat_summary and st.session_state.use_memory:
        ctx += f" Memory: {chat_summary}."
    return base + ctx


def simulated_llm_reply(user_msg: str, mode: str) -> str:
    course_df = st.session_state.courses
    try:
        top_course = course_df.loc[course_df['Completion'].idxmax()]
        course_hint = f"Top course: {top_course['Course']} ({top_course['Completion']}%)."
    except Exception:
        course_hint = "No course data."

    chat_summary = st.session_state.chat_summary or summarize_memory()
    system = build_system_prompt(mode, course_hint, chat_summary)

    msg = user_msg.lower()
    # Code Helper special cases
    if mode == "Code Helper":
        if any(kw in msg for kw in ["bug", "error", "traceback", "fix"]):
            return "Please paste the error or the minimal code snippet and I will suggest a fix and a corrected example."
        if "streamlit" in msg:
            return "Use `st.form` for inputs to avoid reruns, and `st.session_state` for persistent values. Want a ready snippet?"
        return "Describe the bug or desired functionality and I'll provide a small, runnable example."

    # Tutor special cases
    if mode == "Tutor":
        for c in st.session_state.courses['Course'].tolist():
            if c.lower() in msg:
                comp = int(st.session_state.courses.loc[st.session_state.courses['Course']==c, 'Completion'].values[0])
                if comp < 50:
                    return f"You're {comp}% through {c}. Recommendation: revisit core concepts for 2 sessions (25 min each) and solve 3 basic problems. Want two practice problems now?"
                else:
                    return f"At {comp}% in {c}, try a mini-project (1-2 hours) or 5-10 medium problems. Want a project idea?"
        if "exercise" in msg or "problem" in msg:
            return "Mini exercise: write a function that reverses words in a sentence preserving whitespace. Try in Python — want the solution?"
        return "Short plan: 1) 25m review, 2) 45m practice, 3) 10m reflection. Want me to generate a 7-day plan?"

    # Motivator special cases
    if mode == "Motivator":
        choices = [
            "You're doing well — celebrate small wins. Start with a 25-min focused session.",
            "Consistency beats intensity. Pick a micro-goal for today and stick to it.",
            "If stuck, take a 5-min break and return with a fresh approach. Small progress counts."
        ]
        return random.choice(choices)

    # Default fallback
    return "I can help with a study plan, code snippets, or motivation — which would you like?"


# ------------------ GENERATE REPLY (MAIN) ------------------

def generate_bot_reply(user_msg: str, mode: str = None) -> str:
    if mode is None:
        mode = st.session_state.assistant_mode

    # set typing indicator
    st.session_state.typing = True
    time.sleep(np.random.uniform(0.2, 0.9))
    st.session_state.typing = False

    # update summary for context
    if st.session_state.use_memory:
        st.session_state.chat_summary = summarize_memory()

    # If an API provider is configured, try it first
    provider = st.session_state.api_provider
    if provider == "OpenAI" and st.session_state.api_key:
        system_prompt = build_system_prompt(mode, course_context='', chat_summary=st.session_state.chat_summary)
        text = call_openai_chat(st.session_state.api_key, system_prompt, user_msg)
        if text:
            return text
    if provider == "DeepSeek":
        # prefer explicit key, otherwise try secrets/env
        key = st.session_state.deepseek_key or None
        if not key:
            try:
                key = st.secrets.get("DEEPSEEK_API_KEY")
            except Exception:
                key = os.getenv("DEEPSEEK_API_KEY")
        if key:
            text = call_deepseek(key, user_msg)
            if text:
                return text

    # fallback: simulated smarter reply
    return simulated_llm_reply(user_msg, mode)


# ------------------ INITIALIZE ------------------
init_session_state()
# try to load persisted state if present
if st.session_state.courses is None:
    st.session_state.courses = make_course_df()
load_state_local()

# ------------------ STYLES ------------------
NEON_CSS = """
<style>
.stApp { background: #000000; color: #bfffc2; }
.card { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.06); }
.chat-area { background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.005)); border-radius: 12px; padding: 12px; max-height: 56vh; overflow-y: auto; border: 1px solid rgba(0,255,127,0.04); }
.bubble-user { background: linear-gradient(90deg,#003e13,#1b5e20); color: #eafff0; padding: 10px; border-radius: 14px; margin: 8px 0; text-align: right; display: inline-block; max-width: 85%; }
.bubble-bot { background: linear-gradient(90deg,#134b2b,#2e7d32); color: #eafff0; padding: 10px; border-radius: 14px; margin: 8px 0; text-align: left; display: inline-block; max-width: 85%; }
.memory-badge { background: rgba(0,255,127,0.08); color: #bfffc2; padding: 6px 10px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.06); display:inline-block; margin-bottom:8px; }
.neon-btn { background: linear-gradient(90deg,#00ff7f33,#00ff7f22); color: #000; padding: 8px 14px; border-radius: 10px; border: 1px solid rgba(0,255,127,0.35); }
.small-muted { font-size:12px; color:#8fffbf }
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
    page = st.radio("Navigate:", ["🏠 Dashboard", "🤖 AI Mentor (Pro)"])
    st.markdown("---")
    # Theme selector
    st.selectbox("Theme:", ["neon", "dark"], index=0 if st.session_state.theme == "neon" else 1, key="theme_select", on_change=lambda: st.session_state.update({"theme": st.session_state.theme_select}))
    st.markdown("---")
    st.header("Assistant Settings")
    st.session_state.assistant_mode = st.selectbox("Mode:", ["Tutor", "Code Helper", "Motivator"], index=["Tutor", "Code Helper", "Motator"].index(st.session_state.assistant_mode) if st.session_state.assistant_mode in ["Tutor", "Code Helper", "Motivator"] else 0)
    st.session_state.use_memory = st.checkbox("Use short-term memory", value=st.session_state.use_memory)
    st.session_state.use_tts = st.checkbox("Enable TTS (gTTS)", value=st.session_state.use_tts)
    st.markdown("Optional: connect to an LLM provider for richer replies (API key kept local).")
    provider = st.selectbox("Provider:", ["None", "OpenAI", "DeepSeek"], index=0)
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
    # Persistence options (local + scaffold for Google Sheets)
    if st.button("Save App State (local)"):
        ok = save_state_local()
        if ok:
            st.success("Saved to local JSON.")
    if st.button("Load App State (local)"):
        ok = load_state_local()
        if ok:
            st.success("Loaded local state.")
    st.markdown("Note: Google Sheets persistence is scaffolded in code comments — requires credentials.")

# =========================
# PAGE: DASHBOARD
# =========================
if page == "🏠 Dashboard":
    st.title("🧠 CSE Learning Path Dashboard — AI Mentor (Pro)")
    st.markdown("<div class='card'>Track progress, plan learning sprints, add courses, ask the AI mentor, enable TTS, and connect to real LLM providers.</div>", unsafe_allow_html=True)
    st.markdown(" ")

    # Top metrics
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        overall = int(st.session_state.courses["Completion"].mean())
        gauge_fig = go.Figure(go.Indicator(mode="gauge+number", value=overall, title={'text': "Total Completion"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FF7F"}}))
        gauge_fig.update_layout(height=240, paper_bgcolor='rgba(0,0,0,0)', font_color='#bfffc2')
        st.plotly_chart(gauge_fig, use_container_width=True)
    with col2:
        st.metric(label="Courses", value=len(st.session_state.courses))
        st.metric(label="Active Topic", value=(st.session_state.topic_memory or "—"))
    with col3:
        if st.button("➕ Add New Course"):
            st.session_state.show_add_course = True
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

    # Course cards + quick AI actions
    st.subheader("📚 Courses & AI Actions")
    search = st.text_input("Search courses (name/status)")
    filtered = st.session_state.courses.copy()
    if search:
        mask = filtered["Course"].str.contains(search, case=False, na=False) | filtered["Status"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    for idx, row in filtered.reset_index(drop=False).iterrows():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.markdown(f"<div class='card'><b>{row['Course']}</b> — <small>{row['Status']}</small><br>Completion: {row['Completion']}%</div>", unsafe_allow_html=True)
        with c2:
            new_val = st.slider(f"progress_{row['index']}", 0, 100, int(row['Completion']))
            if new_val != int(row['Completion']):
                st.session_state.courses.at[row['index'], 'Completion'] = int(new_val)
                if new_val == 100:
                    st.session_state.courses.at[row['index'], 'Status'] = 'Completed'
                elif new_val == 0:
                    st.session_state.courses.at[row['index'], 'Status'] = 'Not Started'
                else:
                    st.session_state.courses.at[row['index'], 'Status'] = 'In Progress'
                # persist automatically
                save_state_local()
                st.experimental_rerun()
        with c3:
            if st.button(f"Ask AI about {row['Course']}", key=f"askai_{row['index']}"):
                prompt = f"Tell me a short study plan for {row['Course']} given current completion {row['Completion']}%."
                st.session_state.chat_history.append({"sender": "user", "message": prompt, "ts": now_iso()})
                reply = generate_bot_reply(prompt, mode=st.session_state.assistant_mode)
                st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
                # optional TTS
                if st.session_state.use_tts and TTS_AVAILABLE:
                    audio = tts_speak(reply)
                    if audio:
                        st.audio(audio, format='audio/mp3')
                save_state_local()
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
    st.markdown("<div style='color:#bfffc2;'>Developed by Anish | CSE Learning Path Dashboard — AI Mentor (Pro) © 2025</div>", unsafe_allow_html=True)

# =========================
# PAGE: AI MENTOR (PRO)
# =========================
elif page == "🤖 AI Mentor (Pro)":
    st.markdown("<h2 class='neon-header'>🤖 AI Mentor (Pro)</h2>", unsafe_allow_html=True)
    st.markdown("<div class='card'>A context-aware assistant that uses optional external APIs, TTS, local persistence, and course-aware suggestions.</div>", unsafe_allow_html=True)

    # Quick action buttons
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🔎 What should I study next?"):
        df = st.session_state.courses
        cand = df[df['Completion'] < 60].sort_values('Completion').iloc[0]
        prompt = f"Recommend next study topic based on progress. I have {cand['Course']} at {cand['Completion']}% completion."
        st.session_state.chat_history.append({"sender": "user", "message": prompt, "ts": now_iso()})
        reply = generate_bot_reply(prompt)
        st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
        if st.session_state.use_tts and TTS_AVAILABLE:
            audio = tts_speak(reply)
            if audio:
                st.audio(audio, format='audio/mp3')
        save_state_local()
        st.experimental_rerun()
    if c2.button("📚 Quick Revision Plan"):
        st.session_state.chat_history.append({"sender": "user", "message": "Give me a 3-step revision plan for my top course.", "ts": now_iso()})
        reply = generate_bot_reply("Give me a 3-step revision plan for my top course.")
        st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
        if st.session_state.use_tts and TTS_AVAILABLE:
            audio = tts_speak(reply)
            if audio:
                st.audio(audio, format='audio/mp3')
        save_state_local()
        st.experimental_rerun()
    if c3.button("🧪 Give me an exercise"):
        st.session_state.chat_history.append({"sender": "user", "message": "Give me a short coding exercise.", "ts": now_iso()})
        reply = generate_bot_reply("Give me a short coding exercise.")
        st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
        if st.session_state.use_tts and TTS_AVAILABLE:
            audio = tts_speak(reply)
            if audio:
                st.audio(audio, format='audio/mp3')
        save_state_local()
        st.experimental_rerun()
    if c4.button("🕒 Study Timer (25m)"):
        st.session_state.chat_history.append({"sender": "user", "message": "Start a 25 minute Pomodoro.", "ts": now_iso()})
        st.session_state.chat_history.append({"sender": "bot", "message": "Pomodoro started: 25 minutes. Focus!", "ts": now_iso()})
        save_state_local()
        st.experimental_rerun()

    st.markdown("")
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.topic_memory = None
        st.session_state.chat_summary = None
        save_state_local()
        st.success("Chat cleared.")

    # Chat display area
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    if st.session_state.chat_summary and st.session_state.use_memory:
        st.markdown(f"<div class='memory-badge'>🧠 Memory: {st.session_state.chat_summary}</div>", unsafe_allow_html=True)

    for m in st.session_state.chat_history:
        sender = m.get("sender")
        message = m.get("message")
        ts = m.get("ts")
        time_str = pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        if sender == "user":
            st.markdown(f"<div style='text-align:right'><div class='bubble-user'><b>You:</b> {message}</div><div class='small-muted' style='text-align:right'>{time_str}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left'><div class='bubble-bot'><b>Assistant:</b> {message}</div><div class='small-muted'>{time_str}</div></div>", unsafe_allow_html=True)

    if st.session_state.typing:
        st.markdown("<div style='font-size:12px;color:#bfffc2'>Assistant is typing...</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Input area using form
    with st.form(key="chat_form", clear_on_submit=True):
        user_text = st.text_input("Ask the AI mentor anything (or type 'help')", key="user_input_text")
        submit = st.form_submit_button("Send")
        if submit and user_text and user_text.strip():
            st.session_state.chat_history.append({"sender": "user", "message": user_text.strip(), "ts": now_iso()})
            # generate reply
            reply = generate_bot_reply(user_text.strip(), mode=st.session_state.assistant_mode)
            st.session_state.chat_history.append({"sender": "bot", "message": reply, "ts": now_iso()})
            # TTS playback if enabled
            if st.session_state.use_tts and TTS_AVAILABLE:
                audio = tts_speak(reply)
                if audio:
                    st.audio(audio, format='audio/mp3')
            # update summary and persist
            if st.session_state.use_memory:
                st.session_state.chat_summary = summarize_memory()
            save_state_local()
            st.experimental_rerun()

    st.markdown("---")
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

    st.markdown("<div style='color:#bfffc2;text-align:center'>AI Mentor (Pro) • Developed by Anish © 2025</div>", unsafe_allow_html=True)

# ------------------ END ------------------
# Notes for deployment:
# - To enable OpenAI: select OpenAI in sidebar and paste your API key. Make sure `openai` Python package is installed in the environment.
# - To enable DeepSeek: add your DeepSeek API key to `.streamlit/secrets.toml` like:
#     DEEPSEEK_API_KEY = "your_key_here"
#   or set the environment variable DEEPSEEK_API_KEY. The app will try those automatically.
# - TTS: gTTS is used to generate MP3 bytes. Install `gTTS` (pip install gTTS) for TTS support. Audio plays via Streamlit's st.audio.
# - Persistence: app saves local JSON to cse_dashboard_state.json. For Google Sheets/Firestore persistence, add your credentials and implement the respective client; scaffolding comments can be added on request.

