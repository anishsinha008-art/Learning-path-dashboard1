# streamlit_learning_dashboard.py
# Enhanced Learning Path Dashboard — Cyber Blue theme
# Debugged and fixed version

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import io
import random
import json
import os
from datetime import datetime, timedelta, date
from pathlib import Path

# Optional imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_KEY = os.getenv('OPENAI_API_KEY', '')
USE_OPENAI = bool(OPENAI_KEY)

# persistent storage file
DATA_FILE = Path('./dashboard_data.json')

st.set_page_config(page_title="CSE Learning Path — Cyber Blue", layout="wide")

# -------------------- Styling & small animations --------------------
st.markdown(
    """
<style>
/* Cyber-blue theme */
body { background: linear-gradient(180deg, #031023 0%, #071b2b 100%); color: #e6f7ff; }
.section-card { background: rgba(255,255,255,0.02); padding: 16px; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.45); }
.h-title { color: #9fe8ff; font-size:28px; margin:0 }
.small { color:#bfeeff }
.button-glow { border-radius:12px; padding:8px 12px; background:linear-gradient(90deg,#00b4d8,#0077b6); color:white; box-shadow: 0 6px 20px rgba(0,180,216,0.18); }
.fade-in { animation: fadeIn 0.9s ease-in-out; }
@keyframes fadeIn { from {opacity:0; transform: translateY(6px)} to {opacity:1; transform: none} }
.chat-bubble { background: rgba(255,255,255,0.04); padding:10px; border-radius:10px; margin-bottom:8px; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- Helpers --------------------


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Use st.error only if Streamlit is running (safe here)
        try:
            st.error(f'Failed to save data: {e}')
        except Exception:
            pass


def default_state():
    return {
        'courses': {
            'Python Basics': {
                'modules': [
                    {'title': 'Intro & Setup', 'duration_min': 30, 'done': False},
                    {'title': 'Data Types', 'duration_min': 45, 'done': False},
                    {'title': 'Control Flow', 'duration_min': 40, 'done': False},
                    {'title': 'Functions', 'duration_min': 60, 'done': False},
                ],
                'color': '#0f52ba',
                'materials': [],
            },
            'Web Development': {
                'modules': [
                    {'title': 'HTML & CSS', 'duration_min': 50, 'done': False},
                    {'title': 'JavaScript Basics', 'duration_min': 60, 'done': False},
                    {'title': 'Deploying Sites', 'duration_min': 30, 'done': False},
                ],
                'color': '#0077b6',
                'materials': [],
            },
            'Data Structures': {
                'modules': [
                    {'title': 'Arrays & Lists', 'duration_min': 40, 'done': False},
                    {'title': 'Stacks & Queues', 'duration_min': 45, 'done': False},
                    {'title': 'Trees', 'duration_min': 70, 'done': False},
                ],
                'color': '#00b4d8',
                'materials': [],
            },
        },
        'active_course': 'Python Basics',
        'chat_history': [],
        'planner': {},
        'pomodoro': {'running': False, 'end_time': None, 'duration': 25 * 60},
        'quiz_history': [],
    }


def ensure_state():
    data = load_data()
    if not data:
        data = default_state()
        save_data(data)
    # minimal repairs
    if 'courses' not in data:
        data['courses'] = default_state()['courses']
    if 'active_course' not in data:
        data['active_course'] = list(data['courses'].keys())[0]
    if 'chat_history' not in data:
        data['chat_history'] = []
    if 'planner' not in data:
        data['planner'] = {}
    if 'pomodoro' not in data:
        data['pomodoro'] = {'running': False, 'end_time': None, 'duration': 25 * 60}
    if 'quiz_history' not in data:
        data['quiz_history'] = []
    save_data(data)
    return data


def course_progress(data, course_name):
    modules = data['courses'][course_name]['modules']
    if len(modules) == 0:
        return 0
    done = sum(1 for m in modules if m.get('done'))
    return int(done / len(modules) * 100)


def plot_gauge(percent, title='Progress'):
    fig = go.Figure(
        go.Indicator(
            mode='gauge+number',
            value=percent,
            number={'font': {'size': 40}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#00B4D8', 'thickness': 0.25},
                'steps': [
                    {'range': [0, 33], 'color': '#2b2b2b'},
                    {'range': [33, 66], 'color': '#124559'},
                    {'range': [66, 100], 'color': '#013a63'},
                ],
            },
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
        )
    )
    fig.update_layout(height=260, margin={'t': 10, 'b': 10, 'l': 10, 'r': 10}, paper_bgcolor='rgba(0,0,0,0)')
    return fig


# local motivator function (used as fallback and default)
def local_motivator(msg):
    msg = msg.lower()
    quotes = [
        "Small progress is still progress. Keep going!",
        "You are capable of more than you think.",
        "Consistency beats intensity. Study a little every day.",
        "Remember why you started — and show up for yourself today.",
    ]
    if any(x in msg for x in ['tired', 'give up', 'stuck', 'frustrat']):
        return random.choice(
            [
                "Take a short break — 5 minutes away from the screen can change your focus.",
                "Try breaking the task into 10-minute chunks — you'll be surprised how much you finish.",
                random.choice(quotes),
            ]
        )
    if msg.endswith('?'):
        return random.choice(
            [
                "That's a good question — try searching a concise answer and summarize it.",
                random.choice(quotes),
            ]
        )
    if 'progress' in msg:
        # course_progress requires STATE, we will handle where called
        return None
    if 'motivate' in msg or 'encour' in msg:
        return random.choice(quotes)
    return random.choice(quotes)


# -------------------- Init persistent state --------------------
ensure_state()
STATE = load_data()

# make sure active_course exists (safety)
if STATE['active_course'] not in STATE['courses']:
    STATE['active_course'] = list(STATE['courses'].keys())[0]
    save_data(STATE)

# -------------------- Top bar --------------------
st.markdown(
    f"""
<div class='section-card fade-in' style='display:flex;justify-content:space-between;align-items:center'>
  <div>
    <h1 class='h-title'>CSE Learning Path</h1>
    <div class='small'>Cyber Blue — interactive dashboard with motivator chatbot</div>
  </div>
  <div style='text-align:right'>
    <div class='small'>Status: <strong>{'OpenAI API' if USE_OPENAI else 'Local Motivator'}</strong></div>
    <div style='margin-top:6px'><small class='small'>Data file: <code>{DATA_FILE}</code></small></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.header('Controls')
    course_list = list(STATE['courses'].keys())
    # protect against empty courses
    if not course_list:
        course_list = ['(no courses)']
    try:
        index = course_list.index(STATE.get('active_course', course_list[0]))
    except ValueError:
        index = 0
    active = st.selectbox('Active course', course_list, index=index)
    STATE['active_course'] = active

    st.markdown('---')
    st.subheader('Create Course')
    new_course = st.text_input('Course name', '')
    coln = st.columns([2, 1])
    with coln[1]:
        color = st.color_picker('Accent', value='#00b4d8')
    if st.button('Add Course') and new_course.strip():
        if new_course in STATE['courses']:
            st.warning('Course already exists')
        else:
            STATE['courses'][new_course.strip()] = {'modules': [], 'color': color, 'materials': []}
            save_data(STATE)
            st.experimental_rerun()

    st.markdown('---')
    st.subheader('Quick Actions')
    if st.button('Export progress CSV'):
        rows = []
        for c, d in STATE['courses'].items():
            for m in d['modules']:
                rows.append({'course': c, 'module': m['title'], 'duration_min': m['duration_min'], 'done': m['done']})
        df = pd.DataFrame(rows)
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        st.download_button('Download CSV', buf.getvalue(), file_name='learning_progress.csv', mime='text/csv')

    if st.button('Reset to demo'):
        try:
            DATA_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        st.success('Reset. Reloading...')
        st.experimental_rerun()

    st.markdown('---')
    st.subheader('Pomodoro')
    pmin = st.number_input('Minutes', min_value=5, max_value=60, value=int(STATE['pomodoro']['duration'] // 60))
    if st.button('Start Pomodoro'):
        STATE['pomodoro']['duration'] = int(pmin * 60)
        STATE['pomodoro']['end_time'] = time.time() + STATE['pomodoro']['duration']
        STATE['pomodoro']['running'] = True
        save_data(STATE)
    if st.button('Stop Pomodoro'):
        STATE['pomodoro']['running'] = False
        STATE['pomodoro']['end_time'] = None
        save_data(STATE)

# -------------------- Main layout --------------------
left, right = st.columns([2.5, 1.2])

with left:
    st.subheader(f"Course — {STATE['active_course']}")
    course = STATE['courses'][STATE['active_course']]

    # Modules list
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write('**Modules**')
    for i, mod in enumerate(course['modules']):
        cols = st.columns([0.05, 0.6, 0.15, 0.2])
        chk = cols[0].checkbox('', value=mod.get('done', False), key=f"chk_{STATE['active_course']}_{i}")
        if chk != mod.get('done', False):
            course['modules'][i]['done'] = chk
            save_data(STATE)
        cols[1].markdown(
            f"**{mod.get('title','Untitled')}**\n\n<small class='small'>Est: {mod.get('duration_min',0)} min</small>",
            unsafe_allow_html=True,
        )
        if cols[2].button('Add +10min', key=f'add_{i}'):
            course['modules'][i]['duration_min'] = int(course['modules'][i].get('duration_min', 0)) + 10
            save_data(STATE)
        if cols[3].button('Remove', key=f'rem_{i}'):
            # remove safely
            course['modules'].pop(i)
            save_data(STATE)
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Add module
    st.markdown('<div class="section-card" style="margin-top:12px">', unsafe_allow_html=True)
    st.write('Add Module')
    with st.form('add_mod_form'):
        mtitle = st.text_input('Module title')
        mdur = st.number_input('Duration (min)', min_value=5, value=30)
        sub = st.form_submit_button('Add Module')
        if sub and mtitle.strip():
            course['modules'].append({'title': mtitle.strip(), 'duration_min': int(mdur), 'done': False})
            save_data(STATE)
            st.success('Module added')
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Materials: upload per course
    st.markdown('<div class="section-card" style="margin-top:12px">', unsafe_allow_html=True)
    st.write('Course Materials')
    uploaded = st.file_uploader('Upload material (PDF / Image / ZIP)', type=['pdf', 'png', 'jpg', 'jpeg', 'zip'], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            content = f.read()
            filename = f.name
            # save material to local folder for this course
            mat_dir = Path('./materials') / STATE['active_course']
            mat_dir.mkdir(parents=True, exist_ok=True)
            filepath = mat_dir / filename
            with open(filepath, 'wb') as fh:
                fh.write(content)
            course['materials'].append(str(filepath))
            save_data(STATE)
            st.success(f'Uploaded {filename}')
    if course.get('materials'):
        for m in course['materials']:
            st.write(f'- {m}')
            # provide download
            try:
                with open(m, 'rb') as fh:
                    data = fh.read()
                st.download_button(f'Download {Path(m).name}', data, file_name=Path(m).name)
            except Exception:
                st.write('(file missing)')
    st.markdown('</div>', unsafe_allow_html=True)

    # Planner with ICS export
    st.markdown('<div class="section-card" style="margin-top:12px">', unsafe_allow_html=True)
    st.write('Study Planner & Calendar')
    plan_date = st.date_input('Pick date', value=date.today())
    plan_task = st.text_input('Task (e.g., Study Module 2)')
    plan_time = st.time_input('Time', value=datetime.now().time())
    if st.button('Add to Planner') and plan_task.strip():
        k = plan_date.isoformat()
        if k not in STATE['planner']:
            STATE['planner'][k] = []
        STATE['planner'][k].append({'task': plan_task, 'time': plan_time.strftime('%H:%M'), 'course': STATE['active_course']})
        save_data(STATE)
        st.success('Planned')
    # show today's plans
    plans = STATE['planner'].get(plan_date.isoformat(), [])
    if plans:
        for p in plans:
            st.write(f"- [{p['course']}] {p['task']} at {p['time']}")
    else:
        st.info('No plans for this date')

    # ICS export (simple)
    if st.button('Export selected date (.ics)'):
        try:
            from ics import Calendar, Event

            cal = Calendar()
            for p in plans:
                e = Event()
                e.name = f"{p['course']}: {p['task']}"
                dt = datetime.combine(plan_date, datetime.strptime(p['time'], '%H:%M').time())
                e.begin = dt
                e.duration = timedelta(minutes=30)
                cal.events.add(e)
            ics_bytes = cal.serialize().encode('utf-8')
            st.download_button('Download ICS', ics_bytes, file_name=f'planner_{plan_date}.ics', mime='text/calendar')
        except Exception:
            st.error('Install package "ics" to enable calendar export')
    st.markdown('</div>', unsafe_allow_html=True)

    # Mini Quiz Engine
    st.markdown('<div class="section-card" style="margin-top:12px">', unsafe_allow_html=True)
    st.write('Quiz Center')
    st.write('Create a quick multiple-choice quiz for self-check (saved to history)')
    with st.form('quiz_form'):
        qtxt = st.text_input('Question')
        opt1 = st.text_input('Option 1')
        opt2 = st.text_input('Option 2')
        opt3 = st.text_input('Option 3')
        opt4 = st.text_input('Option 4')
        ans = st.selectbox('Correct option', ('Option 1', 'Option 2', 'Option 3', 'Option 4'))
        qsub = st.form_submit_button('Add & Take Quiz')
        if qsub and qtxt.strip():
            qobj = {'question': qtxt, 'options': [opt1, opt2, opt3, opt4], 'answer': ans, 'course': STATE['active_course'], 'time': datetime.now().isoformat()}
            STATE['quiz_history'].append({'quiz': qobj, 'result': None})
            save_data(STATE)
            st.success('Quiz created — answering below')
            st.experimental_rerun()
    # If there are pending quizzes (most recent created), show attempt
    if STATE['quiz_history']:
        last = STATE['quiz_history'][-1]
        if last['result'] is None:
            q = last['quiz']
            st.markdown('**Take latest quiz**')
            # filter out empty options
            options = [o if o else "(empty)" for o in q['options']]
            chosen = st.radio(q['question'], options, key='attempt_latest')
            if st.button('Submit Answer'):
                correct = options[['Option 1', 'Option 2', 'Option 3', 'Option 4'].index(q['answer'])]
                score = 1 if chosen == correct else 0
                last['result'] = {'chosen': chosen, 'correct': correct, 'score': score, 'time': datetime.now().isoformat()}
                save_data(STATE)
                if score:
                    st.success('Correct ✅')
                else:
                    st.error(f'Incorrect — correct: {correct}')
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.subheader('Overview')
    prog = course_progress(STATE, STATE['active_course'])
    st.plotly_chart(plot_gauge(prog, title='Course Progress'), use_container_width=True)
    st.metric('Completion', f"{prog}%")

    st.markdown('---')
    st.write('Quick Analytics')
    nmods = len(course.get('modules', []))
    total_min = sum(m.get('duration_min', 0) for m in course.get('modules', []))
    rem_min = sum(m.get('duration_min', 0) for m in course.get('modules', []) if not m.get('done', False))
    st.write(f'Modules: {nmods}')
    st.write(f'Total est. time: {total_min} min')
    st.write(f'Remaining: {rem_min} min')

    st.markdown('---')
    st.subheader('Motivator Chatbot')
    st.write('Use the built-in motivator or connect to OpenAI (set OPENAI_API_KEY env var).')
    chat_in = st.text_input('Talk to motivator', key='chat_in')
    if st.button('Send') and chat_in.strip():
        # produce response
        bot = None
        if USE_OPENAI:
            try:
                import openai

                openai.api_key = OPENAI_KEY
                # Use completion endpoint carefully; model name may vary on your account.
                resp = openai.ChatCompletion.create(
                    model='gpt-4o',
                    messages=[
                        {'role': 'system', 'content': 'You are a short, encouraging study motivator. Keep answers under 40 words.'},
                        {'role': 'user', 'content': chat_in},
                    ],
                    max_tokens=100,
                )
                bot = resp.choices[0].message.content.strip()
            except Exception:
                # fallback to local motivator
                bot_local = local_motivator(chat_in)
                if bot_local is None:
                    bot = f"Your active course '{STATE['active_course']}' is {course_progress(STATE, STATE['active_course'])}% complete. Keep it up!"
                else:
                    bot = bot_local
        else:
            bot_local = local_motivator(chat_in)
            if bot_local is None:
                bot = f"Your active course '{STATE['active_course']}' is {course_progress(STATE, STATE['active_course'])}% complete. Keep it up!"
            else:
                bot = bot_local

        STATE['chat_history'].append({'user': chat_in, 'bot': bot, 'time': datetime.now().isoformat()})
        save_data(STATE)
        st.experimental_rerun()

    # show latest chat entries
    if STATE.get('chat_history'):
        for m in STATE['chat_history'][-6:][::-1]:
            st.markdown(
                f"<div class='chat-bubble'><strong>You</strong> <small class='small'>({m['time']})</small><br>{m['user']}<br><strong>Motivator:</strong> {m['bot']}</div>",
                unsafe_allow_html=True,
            )

    st.markdown('---')
    st.subheader('Course Progress Table')
    ctitles = []
    cprogress = []
    for c in STATE['courses']:
        ctitles.append(c)
        cprogress.append(course_progress(STATE, c))
    df = pd.DataFrame({'course': ctitles, 'progress': cprogress})
    st.dataframe(df)

# -------------------- Footer actions --------------------
st.markdown('---')
cols = st.columns([1, 1, 1])
with cols[0]:
    if st.button('Save Snapshot'):
        save_data(STATE)
        st.success('Saved to dashboard_data.json')
with cols[1]:
    # provide a persistent download button every run (so button UI shows)
    j = json.dumps(STATE, indent=2)
    st.download_button('Download Snapshot (JSON)', j.encode('utf-8'), file_name='dashboard_snapshot.json', mime='application/json')
with cols[2]:
    if st.button('Get Motivational Tip'):
        tips = ['Use Pomodoro: 25/5.', 'Break tasks into 10-minute chunks.', 'Celebrate micro wins each session.']
        st.balloons()
        st.success(random.choice(tips))

# Pomodoro non-blocking display
if STATE.get('pomodoro', {}).get('running') and STATE.get('pomodoro', {}).get('end_time'):
    try:
        remaining = int(STATE['pomodoro']['end_time'] - time.time())
    except Exception:
        remaining = 0
    if remaining <= 0:
        STATE['pomodoro']['running'] = False
        STATE['pomodoro']['end_time'] = None
        save_data(STATE)
        st.success('Pomodoro finished! Take a break 🎉')
    else:
        mleft = remaining // 60
        sleft = remaining % 60
        st.info(f'Pomodoro — time left: {mleft:02d}:{sleft:02d}')

# Small analytics for quiz history
if STATE.get('quiz_history'):
    scores = [q['result']['score'] for q in STATE['quiz_history'] if q.get('result')]
    if scores:
        avg = sum(scores) / len(scores)
        try:
            st.sidebar.metric('Avg quiz score', f"{avg:.2f}")
        except Exception:
            pass

st.markdown(
    """
---
*Made with ❤️ — enhanced interactive dashboard. Customize further? Tell me what else to add: syncing to Google Calendar, richer LLM replies, or multi-user support.*
"""
)
