# app/blueprints/main.py
from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify, request
from ..models import db, Habit, HabitLog

bp = Blueprint("main", __name__)

def _calc_streak(active_dates: set[date]) -> int:
    """Count consecutive active days ending today."""
    if not active_dates:
        return 0
    streak = 0
    d = date.today()
    while d in active_dates:
        streak += 1
        d -= timedelta(days=1)
    return streak

@bp.get("/")
def dashboard():
    today = date.today()
    start_90 = today - timedelta(days=89)

    habits = Habit.query.order_by(Habit.name).all()

    # Pull last 90 days of logs for all habits once
    logs = HabitLog.query.filter(
        HabitLog.log_date >= start_90,
        HabitLog.log_date <= today,
    ).all()

    # Aggregate per habit
    totals = {}
    active_days = {}
    for lg in logs:
        v = float(lg.value or 0)
        totals[lg.habit_id] = totals.get(lg.habit_id, 0.0) + v
        if v > 0:
            active_days.setdefault(lg.habit_id, set()).add(lg.log_date)

    summaries = []
    for h in habits:
        total = totals.get(h.id, 0.0)
        streak = _calc_streak(active_days.get(h.id, set()))
        summaries.append({
            "habit": h,
            "total": total,
            "streak": streak,
        })

    return render_template("dashboard.html", summaries=summaries)

@bp.get("/api/stats")
def api_stats():
    habit_id = request.args.get("habit_id", type=int)
    days = request.args.get("days", default=90, type=int)
    if not habit_id:
        return jsonify({"points": []})

    end = date.today()
    start = end - timedelta(days=days - 1)

    rows = (HabitLog.query
            .filter(HabitLog.habit_id == habit_id,
                    HabitLog.log_date >= start,
                    HabitLog.log_date <= end)
            .all())

    by_date = {r.log_date: float(r.value or 0) for r in rows}

    points = [{
        "date": (start + timedelta(days=i)).isoformat(),
        "value": by_date.get(start + timedelta(days=i), 0.0),
    } for i in range(days)]

    return jsonify({"points": points})
