from datetime import date, timedelta
from . import db
from .models import Habit, HabitLog
import random


def seed_example_data():
    # clear tables (idempotent seed for dev)
    HabitLog.query.delete()
    Habit.query.delete()
    db.session.commit()

    habits = [
        Habit(name="Push-ups", kind="count", unit="reps", daily_target=50, color="#3b82f6"),
        Habit(name="Pull-ups", kind="count", unit="reps", daily_target=10, color="#8b5cf6"),
        Habit(name="Crunches", kind="count", unit="reps", daily_target=50, color="#ef4444"),
        Habit(name="Plank", kind="duration", unit="min", daily_target=5, color="#22c55e"),
        Habit(name="Running", kind="distance", unit="km", daily_target=3, color="#06b6d4"),
        Habit(name="Cold Swim", kind="boolean", unit="yes/no", color="#0ea5e9"),
        Habit(name="Practice Coding", kind="duration", unit="min", daily_target=60, color="#f59e0b"),
        Habit(name="Cyber Security", kind="duration", unit="min", daily_target=30, color="#a3e635"),
        Habit(name="Eat Healthy", kind="boolean", unit="yes/no", color="#10b981"),
    ]
    db.session.add_all(habits)
    db.session.commit()

    # create 60 days of randomish logs as a demo
    start = date.today() - timedelta(days=60)
    for i in range(60):
        day = start + timedelta(days=i)
        for h in habits:
            r = random.random()
            if h.kind == "boolean":
                if r < 0.6:
                    db.session.add(HabitLog(habit_id=h.id, log_date=day, value=1))
            elif h.kind == "count":
                if r < 0.8:
                    val = int(random.uniform(0.5, 1.2) * (h.daily_target or 30))
                    db.session.add(HabitLog(habit_id=h.id, log_date=day, value=val))
            elif h.kind == "duration":
                if r < 0.75:
                    val = int(random.uniform(0.4, 1.1) * (h.daily_target or 20))
                    db.session.add(HabitLog(habit_id=h.id, log_date=day, value=val))
            elif h.kind == "distance":
                if r < 0.5:
                    val = round(random.uniform(2.0, 6.0), 2)
                    db.session.add(HabitLog(habit_id=h.id, log_date=day, value=val))

    db.session.commit()
