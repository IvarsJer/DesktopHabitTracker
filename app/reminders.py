# app/reminders.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from .models import db, Reminder  # your new model
import requests, os

def check_due():
    now = datetime.now(timezone.utc)
    due = Reminder.query.filter(
        Reminder.when_due <= now, Reminder.is_sent == False
    ).all()
    for r in due:
        # Notify the desktop shell (Electron/Tauri)
        try:
            requests.post(os.getenv("SHELL_NOTIFY_URL", "http://127.0.0.1:8787/notify"), json={
                "title": "HabitFlow",
                "body": r.message or f"Reminder for {r.habit.name}",
                "habit_id": r.habit_id
            }, timeout=2)
        except Exception:
            pass
        r.is_sent = True
    if due:
        db.session.commit()

def init_scheduler(app):
    sched = BackgroundScheduler(daemon=True, timezone="UTC")
    sched.add_job(check_due, "interval", minutes=1, id="check_due")
    sched.start()
