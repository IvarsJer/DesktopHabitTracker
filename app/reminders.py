# app/reminders.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from flask import current_app
from .models import db, Reminder
import requests, os, atexit

def check_due():
    """Runs inside an app context (see init_scheduler)."""
    now = datetime.now(timezone.utc)
    due = Reminder.query.filter(
        Reminder.when_due <= now, Reminder.is_sent.is_(False)
    ).all()

    for r in due:
        try:
            requests.post(
                os.getenv("SHELL_NOTIFY_URL", "http://127.0.0.1:8787/notify"),
                json={
                    "title": "HabitFlow",
                    "body": r.message or f"Reminder for {r.habit.name}",
                    "habit_id": r.habit_id,
                },
                timeout=2,
            )
        except Exception:
            # swallow notification transport errors; keep marking sent
            pass
        r.is_sent = True

    if due:
        db.session.commit()


def init_scheduler(app):
    """
    Create & start a single BackgroundScheduler.
    - Runs jobs inside app.app_context()
    - Stores scheduler in app.extensions['scheduler']
    - Shuts down on teardown and process exit
    - Guards against double-start under the reloader
    """
    # Avoid duplicate schedulers if Flask debug reloader is on
    if app.extensions.get("scheduler_started"):
        return

    sched = BackgroundScheduler(daemon=True, timezone="UTC")

    # Wrap the job so it always has an app context
    def job_wrapper():
        with app.app_context():
            check_due()

    sched.add_job(job_wrapper, "interval", minutes=1, id="check_due")
    sched.start()

    # Keep references for cleanup
    app.extensions["scheduler"] = sched
    app.extensions["scheduler_started"] = True

    # Clean shutdown on Flask app teardown
    @app.teardown_appcontext
    def _shutdown_scheduler(_exc=None):
        s = app.extensions.get("scheduler")
        if s and s.running:
            try:
                s.shutdown(wait=False)
            except Exception:
                pass

    # Extra safety: also stop on process exit
    atexit.register(lambda: sched.shutdown(wait=False) if sched.running else None)
