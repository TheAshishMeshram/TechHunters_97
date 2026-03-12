# 📚 StudyFlow AI — Smart Study Planner & Productivity Coach

An AI-powered study planner with personalized scheduling, task management, productivity tracking, smart reminders, and performance analytics.

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| ⚡ AI Schedule Generator | Input subjects, difficulty, and deadline — AI builds your optimal daily plan |
| ✅ Task & Deadline Manager | Add, track, filter, and complete tasks with priorities |
| ⏱️ Study Timer | Pomodoro, Short Break, Long Break & Deep Work modes with session logging |
| 🔔 Smart Reminders | AI-generated nudges for deadlines, study time, and breaks |
| 📊 Performance Analytics | Weekly charts, subject breakdown, completion rate, streaks |

---

## 🛠️ Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js
- **Fonts**: Google Fonts (Syne + DM Sans)
- **Data**: JSON file-based storage (easily swappable for SQLite/PostgreSQL)

---

## 📦 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
study-planner/
├── app.py                  # Flask backend + AI schedule logic
├── requirements.txt        # Python dependencies
├── README.md
├── data/
│   └── user_data.json      # Auto-generated data store
├── templates/
│   └── index.html          # Main SPA template
└── static/
    ├── css/
    │   └── style.css       # Full design system
    └── js/
        └── app.js          # Frontend application logic
```

---

## 🤖 AI Schedule Algorithm

The scheduler uses a weighted allocation system:
- **Difficulty weighting**: Hard subjects get 40% more time
- **Deadline proximity**: More time allocated as exam approaches
- **Priority modes**: Balanced, Deadline-Driven, or Difficulty-First
- **Weekly rhythm**: Sundays are auto-set to review/rest mode
- **Study tips**: Randomized from a curated evidence-based pool

---

## 📊 Analytics Tracked

- Total study time (all-time)
- Study streak (consecutive days)
- Task completion rate
- Average session length
- Per-subject hour breakdown
- Weekly study hours bar chart

---

## 💡 Usage Tips

1. **Generate a schedule first** — Go to "AI Schedule", fill in your subjects and exam date
2. **Add your tasks** — Break down assignments into trackable tasks with deadlines
3. **Use the timer** — Log real study sessions to feed the analytics dashboard
4. **Check reminders** — Smart alerts are generated based on your schedule and tasks
5. **Review analytics weekly** — Adjust your schedule based on performance data
