from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)
app.secret_key = 'studyplanner_secret_2024'

# In-memory data store (simulates a database)
DATA_FILE = 'data/user_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'tasks': [],
        'sessions': [],
        'schedule': [],
        'analytics': {
            'total_study_time': 0,
            'tasks_completed': 0,
            'streak': 0,
            'last_study_date': None
        }
    }

def save_data(data):
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    data = load_data()
    return jsonify(data['tasks'])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = load_data()
    task = request.json
    task['id'] = str(uuid.uuid4())
    task['created_at'] = datetime.now().isoformat()
    task['completed'] = False
    task['progress'] = 0
    data['tasks'].append(task)
    save_data(data)
    return jsonify(task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = load_data()
    for i, task in enumerate(data['tasks']):
        if task['id'] == task_id:
            data['tasks'][i].update(request.json)
            if request.json.get('completed') and not task.get('completed'):
                data['analytics']['tasks_completed'] += 1
            save_data(data)
            return jsonify(data['tasks'][i])
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    data = load_data()
    data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/generate-schedule', methods=['POST'])
def generate_schedule():
    """AI-powered schedule generation"""
    body = request.json
    subjects = body.get('subjects', [])
    hours_per_day = body.get('hours_per_day', 4)
    start_date = body.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    exam_date = body.get('exam_date', '')
    priority = body.get('priority', 'balanced')

    data = load_data()

    # AI Schedule Generation Logic
    schedule = generate_ai_schedule(subjects, hours_per_day, start_date, exam_date, priority)
    data['schedule'] = schedule
    save_data(data)
    return jsonify(schedule)

def generate_ai_schedule(subjects, hours_per_day, start_date, exam_date, priority):
    """Simulate AI-based schedule generation"""
    schedule = []
    tips_pool = [
        "Use the Pomodoro technique: 25 min study, 5 min break.",
        "Review previous day's notes before starting new topics.",
        "Practice active recall — close the book and recall key concepts.",
        "Interleave subjects for better long-term retention.",
        "Get 7-9 hours of sleep; memory consolidation happens at night.",
        "Teach the concept to someone else to test understanding.",
        "Use mind maps for complex topics.",
        "Set a clear goal for each study session.",
    ]

    if not subjects:
        subjects = [{"name": "General Study", "difficulty": "medium", "hours": hours_per_day}]

    try:
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(exam_date, '%Y-%m-%d') if exam_date else current + timedelta(days=14)
    except Exception:
        current = datetime.now()
        end = current + timedelta(days=14)

    day = 0
    total_days = max((end - current).days, 1)

    while current <= end:
        day_plan = {
            'date': current.strftime('%Y-%m-%d'),
            'day_name': current.strftime('%A'),
            'sessions': [],
            'tip': random.choice(tips_pool),
            'total_hours': 0
        }

        remaining_hours = hours_per_day
        if current.weekday() == 6:  # Sunday = rest/review
            remaining_hours = max(1, hours_per_day // 2)

        # Distribute subjects using AI weighting
        days_left = max((end - current).days, 1)
        for subj in subjects:
            if remaining_hours <= 0:
                break
            subj_hours = float(subj.get('hours', 1))
            difficulty = subj.get('difficulty', 'medium')

            # Weight by difficulty and days left
            weight = 1.0
            if difficulty == 'hard':
                weight = 1.4
            elif difficulty == 'easy':
                weight = 0.7

            if priority == 'deadline':
                weight *= (1 + 1 / days_left)

            allocated = min(round(subj_hours * weight, 1), remaining_hours)
            if allocated <= 0:
                allocated = 0.5

            topics = subj.get('topics', ['Core concepts', 'Practice problems', 'Review'])
            topic = topics[day % len(topics)] if topics else 'Study session'

            day_plan['sessions'].append({
                'subject': subj['name'],
                'hours': allocated,
                'topic': topic,
                'difficulty': difficulty,
                'type': 'focused' if difficulty == 'hard' else 'normal'
            })
            remaining_hours -= allocated
            day_plan['total_hours'] += allocated

        schedule.append(day_plan)
        current += timedelta(days=1)
        day += 1

    return schedule

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    data = load_data()
    return jsonify(data.get('schedule', []))

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    data = load_data()
    return jsonify(data.get('sessions', []))

@app.route('/api/sessions', methods=['POST'])
def log_session():
    data = load_data()
    session_data = request.json
    session_data['id'] = str(uuid.uuid4())
    session_data['logged_at'] = datetime.now().isoformat()
    data['sessions'].append(session_data)

    # Update analytics
    duration = session_data.get('duration', 0)
    data['analytics']['total_study_time'] += duration

    today = datetime.now().strftime('%Y-%m-%d')
    last = data['analytics'].get('last_study_date')
    if last:
        last_dt = datetime.strptime(last, '%Y-%m-%d')
        if (datetime.now() - last_dt).days == 1:
            data['analytics']['streak'] += 1
        elif (datetime.now() - last_dt).days > 1:
            data['analytics']['streak'] = 1
    else:
        data['analytics']['streak'] = 1
    data['analytics']['last_study_date'] = today

    save_data(data)
    return jsonify(session_data), 201

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    data = load_data()
    sessions = data.get('sessions', [])
    tasks = data.get('tasks', [])

    # Build weekly data
    weekly = {}
    for s in sessions:
        try:
            dt = datetime.fromisoformat(s['logged_at'])
            day_key = dt.strftime('%a')
            weekly[day_key] = weekly.get(day_key, 0) + s.get('duration', 0)
        except Exception:
            pass

    days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekly_chart = [{'day': d, 'hours': round(weekly.get(d, 0) / 60, 1)} for d in days_order]

    # Subject breakdown
    subject_hours = {}
    for s in sessions:
        subj = s.get('subject', 'General')
        subject_hours[subj] = subject_hours.get(subj, 0) + s.get('duration', 0)

    subject_chart = [{'subject': k, 'hours': round(v / 60, 1)} for k, v in subject_hours.items()]

    completed = sum(1 for t in tasks if t.get('completed'))
    total = len(tasks)

    return jsonify({
        'total_study_time': data['analytics']['total_study_time'],
        'tasks_completed': completed,
        'total_tasks': total,
        'streak': data['analytics']['streak'],
        'weekly_chart': weekly_chart,
        'subject_chart': subject_chart,
        'completion_rate': round((completed / total * 100) if total else 0, 1),
        'avg_session': round(data['analytics']['total_study_time'] / max(len(sessions), 1), 0)
    })

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    """Smart reminders based on schedule and tasks"""
    data = load_data()
    reminders = []
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')

    # Check overdue tasks
    for task in data['tasks']:
        if not task.get('completed') and task.get('deadline'):
            try:
                dl = datetime.strptime(task['deadline'], '%Y-%m-%d')
                if dl.date() <= now.date():
                    reminders.append({
                        'type': 'deadline',
                        'priority': 'high',
                        'message': f"⚠️ '{task['title']}' is due today!",
                        'action': 'Start Now'
                    })
                elif (dl - now).days <= 2:
                    reminders.append({
                        'type': 'upcoming',
                        'priority': 'medium',
                        'message': f"📅 '{task['title']}' is due in {(dl - now).days} day(s).",
                        'action': 'Review'
                    })
            except Exception:
                pass





    # Today's schedule
    for day in data.get('schedule', []):
        if day['date'] == today:
            for s in day['sessions']:
                reminders.append({
                    'type': 'study',
                    'priority': 'normal',
                    'message': f"📚 Time to study {s['subject']} — {s['hours']}h on '{s['topic']}'",
                    'action': 'Start Session'
                })

    # Break reminder
    sessions_today = [s for s in data.get('sessions', []) if s.get('logged_at', '').startswith(today)]
    total_today = sum(s.get('duration', 0) for s in sessions_today)
    if total_today >= 90:
        reminders.append({
            'type': 'break',
            'priority': 'low',
            'message': f"☕ You've studied {total_today // 60}h {total_today % 60}m today. Take a break!",
            'action': 'Take Break'
        })

    if not reminders:
        reminders.append({
            'type': 'motivation',
            'priority': 'low',
            'message': "🌟 No urgent tasks! Great time to get ahead on your schedule.",
            'action': 'View Schedule'
        })

    return jsonify(reminders)

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, port=5000)
