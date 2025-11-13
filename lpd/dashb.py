# streamlit_learning_dashboard.py
# Learning Path Dashboard with multiple courses, interactive features and a motivator chatbot
# Single-file Streamlit app. Save as streamlit_learning_dashboard.py and run with:
#    pip install streamlit pandas numpy plotly
#    streamlit run streamlit_learning_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import io
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="CSE Learning Path Dashboard", layout="wide")

# ---------------------- Helpers ----------------------
def init_state():
    if 'courses' not in st.session_state:
        # sample starter courses
        st.session_state.courses = {
            'Python Basics': {
                'modules': [
                    {'title':'Intro & Setup', 'duration_min':30, 'done':False},
                    {'title':'Data Types', 'duration_min':45, 'done':False},
                    {'title':'Control Flow', 'duration_min':40, 'done':False},
                    {'title':'Functions', 'duration_min':60, 'done':False}
                ],
                'color':'#0f52ba'
            },
            'Web Development': {
                'modules': [
                    {'title':'HTML & CSS', 'duration_min':50, 'done':False},
                    {'title':'JavaScript Basics', 'duration_min':60, 'done':False},
                    {'title':'Deploying Sites', 'duration_min':30, 'done':False}
                ],
                'color':'#0077b6'
            },
            'Data Structures': {
                'modules': [
                    {'title':'Arrays & Lists', 'duration_min':40, 'done':False},
                    {'title':'Stacks & Queues', 'duration_min':45, 'done':False},
                    {'title':'Trees', 'duration_min':70, 'done':False}
                ],
                'color':'#00b4d8'
            }
        }
    if 'active_course' not in st.session_state:
        st.session_state.active_course = list(st.session_state.courses.keys())[0]
    if 'motivation_history' not in st.session_state:
        st.session_state.motivation_history = []
    if 'pomodoro' not in st.session_state:
        st.session_state.pomodoro = {'running':False, 'end_time':None, 'duration':25*60}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def save_state_to_csv():
    rows = []
    for course, data in st.session_state.courses.items():
        for m in data['modules']:
            rows.append({'course':course,'module':m['title'],'duration_min':m['duration_min'],'done':m['done']})
    df = pd.DataFrame(rows)
    return df


def course_progress(course_name):
    modules = st.session_state.courses[course_name]['modules']
    if len(modules)==0:
        return 0
    done = sum(1 for m in modules if m.get('done'))
    return int(done/len(modules)*100)


def plot_center_gauge(percent, title="Progress"):
    # Plotly gauge with centered percentage text
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        number = {'valueformat': "d", 'font': {'size':36}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#00B4D8", 'thickness':0.25},
            'bgcolor':'white',
            'steps': [
                {'range':[0,33], 'color':'#ffcccc'},
                {'range':[33,66], 'color':'#ffe699'},
                {'range':[66,100], 'color':'#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': percent
            }
        }
    ))
    fig.update_layout(margin={'t':10,'b':10,'l':10,'r':10}, height=300)
    return fig


# ---------------------- Init ----------------------
init_state()

# ---------------------- Layout ----------------------
st.markdown('<div style="background:#071b2b;padding:18px;border-radius:12px">', unsafe_allow_html=True)
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://raw.githubusercontent.com/streamlit/brand/master/streamlit-logo-primary-colormark-darktext.png", width=80)
    st.title('Learning Path')
with col2:
    st.markdown('<h2 style="color:#9fe8ff">Cyber Blue Dashboard</h2>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header('Courses')
    # course selector
    course_names = list(st.session_state.courses.keys())
    selected = st.selectbox('Active Course', course_names, index=course_names.index(st.session_state.active_course))
    st.session_state.active_course = selected

    st.markdown('---')
    new_course = st.text_input('Add Course')
    if st.button('Create Course') and new_course.strip():
        if new_course in st.session_state.courses:
            st.warning('Course already exists')
        else:
            st.session_state.courses[new_course] = {'modules':[], 'color':'#00b4d8'}
            st.success(f'Created course: {new_course}')

    st.markdown('---')
    st.header('Quick Actions')
    if st.button('Export progress CSV'):
        df = save_state_to_csv()
        towrite = io.BytesIO()
        df.to_csv(towrite, index=False)
        towrite.seek(0)
        st.download_button('Download CSV', towrite, file_name='learning_progress.csv', mime='text/csv')

    if st.button('Reset demo data'):
        for c in list(st.session_state.courses.keys()):
            del st.session_state.courses[c]
        init_state()
        st.experimental_rerun()

    st.markdown('---')
    st.subheader('Pomodoro')
    pmin = st.number_input('Minutes', min_value=5, max_value=60, value=int(st.session_state.pomodoro['duration']/60))
    if st.button('Start Pomodoro'):
        st.session_state.pomodoro['duration'] = pmin*60
        st.session_state.pomodoro['end_time'] = time.time() + st.session_state.pomodoro['duration']
        st.session_state.pomodoro['running'] = True
    if st.button('Stop Pomodoro'):
        st.session_state.pomodoro['running'] = False

# Main area
left, right = st.columns([2,1])

with left:
    st.subheader(f"{st.session_state.active_course}")
    course = st.session_state.courses[st.session_state.active_course]

    # modules table with checkboxes
    for i, module in enumerate(course['modules']):
        cols = st.columns([0.05, 0.65, 0.15, 0.15])
        with cols[0]:
            chk = st.checkbox('', value=module.get('done', False), key=f"chk_{st.session_state.active_course}_{i}")
            if chk != module.get('done', False):
                module['done'] = chk
        with cols[1]:
            st.markdown(f"**{module['title']}**")
            st.caption(f"Estimated: {module['duration_min']} min")
        with cols[2]:
            if st.button('Add Time', key=f'addtime_{st.session_state.active_course}_{i}'):
                module['duration_min'] += 10
        with cols[3]:
            if st.button('Remove', key=f'remove_{st.session_state.active_course}_{i}'):
                course['modules'].pop(i)
                st.experimental_rerun()

    st.markdown('---')
    st.subheader('Add Module')
    with st.form('add_module'):
        mtitle = st.text_input('Module title')
        mdur = st.number_input('Duration (min)', min_value=5, value=30)
        submitted = st.form_submit_button('Add Module')
        if submitted and mtitle.strip():
            course['modules'].append({'title':mtitle.strip(),'duration_min':int(mdur),'done':False})
            st.success('Module added')
            st.experimental_rerun()

    st.markdown('---')
    st.subheader('Mini Quiz (Self-check)')
    q1 = st.radio('1) Which data type is immutable in Python?', ('List','Tuple','Dict','Set'), key='q1')
    if st.button('Submit Quiz'):
        score = 0
        if q1 == 'Tuple': score += 1
        st.success(f'You scored {score}/1 — keep going!')

    st.markdown('---')
    st.subheader('Study Planner (Quick)')
    today = datetime.now().date()
    planner_date = st.date_input('Pick date', value=today)
    task = st.text_input('Task (what will you study?)')
    if st.button('Plan Task') and task.strip():
        key = f'plan_{planner_date}'
        if key not in st.session_state:
            st.session_state[key] = []
        st.session_state[key].append({'task':task,'time':datetime.now().strftime('%H:%M')})
        st.success('Planned')
    # show today's plans
    plans_for_date = st.session_state.get(f'plan_{planner_date}', [])
    if plans_for_date:
        for p in plans_for_date:
            st.write(f"- {p['task']} (added {p['time']})")
    else:
        st.info('No plans for this date')

with right:
    # Progress gauge
    prog = course_progress(st.session_state.active_course)
    st.plotly_chart(plot_center_gauge(prog, title='Course Progress'), use_container_width=True)
    st.metric('Overall course completion', f"{prog}%")

    # Course summary
    st.markdown('---')
    st.subheader('Course Summary')
    total_min = sum(m['duration_min'] for m in course['modules'])
    remaining_min = sum(m['duration_min'] for m in course['modules'] if not m.get('done'))
    st.write(f"Modules: {len(course['modules'])}")
    st.write(f"Estimated total time: {total_min} min")
    st.write(f"Remaining time: {remaining_min} min")

    # Motivator Chatbot (simple, built-in)
    st.markdown('---')
    st.subheader('Motivator Chatbot')
    chat_input = st.text_input('Say something to your motivator', key='chat_input')
    def motivator_response(user_msg):
        user_msg = user_msg.lower().strip()
        # rules + random encouraging quotes
        quotes = [
            "Small progress is still progress. Keep going!",
            "You are capable of more than you think.",
            "Consistency beats intensity. Study a little every day.",
            "Remember why you started — and show up for yourself today."
        ]
        if any(word in user_msg for word in ['tired','give up','stuck','frustrat']):
            return random.choice([
                "Take a short break — 5 minutes away from the screen can change your focus.",
                "Try breaking the task into 10-minute chunks — you'll be surprised how much you finish.",
                random.choice(quotes)
            ])
        if user_msg.endswith('?'):
            return random.choice(["That's a good question — try searching a concise answer and summarize it.", random.choice(quotes)])
        if 'progress' in user_msg:
            return f"Your active course '{st.session_state.active_course}' is {course_progress(st.session_state.active_course)}% complete. Keep it up!"
        return random.choice(quotes)

    if st.button('Send to Motivator') and chat_input.strip():
        resp = motivator_response(chat_input)
        st.session_state.chat_history.append({'user':chat_input, 'bot':resp, 'time':datetime.now().strftime('%H:%M')})

    # show chat history
    for msg in st.session_state.chat_history[::-1]:
        st.markdown(f"**You** ({msg['time']}): {msg['user']}")
        st.info(f"Motivator: {msg['bot']}")

    # Quick analytics
    st.markdown('---')
    st.subheader('Quick Analytics')
    # show progress across courses
    course_names = list(st.session_state.courses.keys())
    progress_list = [course_progress(c) for c in course_names]
    df = pd.DataFrame({'course':course_names,'progress':progress_list})
    st.dataframe(df)

# Footer controls
st.markdown('---')
cols = st.columns([1,1,1])
with cols[0]:
    if st.button('Save Snapshot'):
        df = save_state_to_csv()
        st.session_state['last_snapshot'] = df
        st.success('Snapshot saved to session state')
with cols[1]:
    if st.button('Load Snapshot'):
        if 'last_snapshot' in st.session_state:
            df = st.session_state['last_snapshot']
            # attempt to load back
            st.success('Snapshot loaded (preview)')
            st.dataframe(df)
        else:
            st.warning('No snapshot found')
with cols[2]:
    if st.button('Get Motivational Tip'):
        tips = [
            'Use the Pomodoro: 25 minutes focused, 5 minutes break.',
            'Turn goals into specific tasks: "Read chapter 3" not just "Study Python".',
            'Celebrate micro wins: mark 1 module as done each study session.'
        ]
        st.balloons()
        st.success(random.choice(tips))

# Pomodoro display (non-blocking)
if st.session_state.pomodoro['running'] and st.session_state.pomodoro['end_time']:
    remaining = int(st.session_state.pomodoro['end_time'] - time.time())
    if remaining <= 0:
        st.session_state.pomodoro['running'] = False
        st.success('Pomodoro finished! Take a break 🎉')
    else:
        minutes = remaining//60
        seconds = remaining%60
        st.info(f'Pomodoro running — time left: {minutes:02d}:{seconds:02d}')

# End of app
st.markdown('\n---\n*Made with ❤️ — interactive dashboard with multiple courses, progress tracking, planner, quizzes, and a friendly motivator chatbot.*')
