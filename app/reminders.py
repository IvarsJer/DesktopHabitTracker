# app/reminders.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from sqlalchemy.exc import OperationalError, ProgrammingError
from flask import current_app
from .models import db, Reminder
import requests, os

def check_due():
    # ensure we have an app context for DB
    with current_app.app_context():
        try:
            now = datetime.now(timezone.utc)
            due = Reminder.query.filter(
                Reminder.when_due <= now, Reminder.is_sent.is_(False)
            ).all()
        except (OperationalError, ProgrammingError):
            # e.g., table not created yet; just skip this tick
            return

        for r in due:
            try:
                requests.post(
                    os.getenv("SHELL_NOTIFY_URL", "http://127.0.0.1:8787/notify"),
                    json={"title": "HabitFlow",
                          "body": r.message or f"Reminder for {r.habit.name}",
                          "habit_id": r.habit_id},
                    timeout=2
                )
            except Exception:
                pass
            r.is_sent = True

        if due:
            db.session.commit()

def init_scheduler(app):
    sched = BackgroundScheduler(daemon=True, timezone="UTC")
    # run the job with app context every minute
    sched.add_job(check_due, "interval", minutes=1, id="check_due")
    sched.start()

    @app.teardown_appcontext
    def _shutdown_scheduler(exc):
        if sched.running:
            sched.shutdown(wait=False)
