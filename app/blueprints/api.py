from flask import Blueprint, jsonify, request
from datetime import date, timedelta
from ..models import Habit, HabitLog
from ..utils import aggregate_logs

bp = Blueprint("api", __name__)

# ... your existing /stats route remains unchanged ...


@bp.post("/toggle_today")
def toggle_today():
    """Toggle today's completion for boolean habits.
    Body: { habit_id:int }
    If a log for today exists -> delete it. Else create value=1.
    """
    habit_id = request.json.get("habit_id")
    if not habit_id:
        return jsonify({"error": "habit_id is required"}), 400

    h = Habit.query.get_or_404(habit_id)
    if h.kind != "boolean":
        return jsonify({"error": "only boolean habits can be toggled"}), 400

    today = date.today()
    log = HabitLog.query.filter_by(habit_id=h.id, log_date=today).first()
    if log:
        # Untick = delete
        from .. import db
        db.session.delete(log)
        db.session.commit()
        return jsonify({"done": False, "total": 0})
    else:
        # Tick = create
        from .. import db
        db.session.add(HabitLog(habit_id=h.id, log_date=today, value=1))
        db.session.commit()
        return jsonify({"done": True, "total": 1})


@bp.post("/quick_add")
def quick_add():
    """Quick-add a numeric amount to today's log.
    Body: { habit_id:int, delta:number }
    If a log exists today, increment its value; else create.
    """
    habit_id = request.json.get("habit_id")
    delta = request.json.get("delta", 0)
    if not habit_id:
        return jsonify({"error": "habit_id is required"}), 400
    try:
        delta = float(delta)
    except Exception:
        return jsonify({"error": "delta must be a number"}), 400

    h = Habit.query.get_or_404(habit_id)
    if h.kind == "boolean":
        return jsonify({"error": "boolean habits use toggle_today"}), 400

    today = date.today()
    from .. import db
    log = HabitLog.query.filter_by(habit_id=h.id, log_date=today).first()
    if log:
        log.value = float(log.value or 0) + delta
    else:
        log = HabitLog(habit_id=h.id, log_date=today, value=delta)
        db.session.add(log)
    db.session.commit()
    return jsonify({"total": float(log.value or 0)})


@bp.get("/week")
def week():
    """Return last 7 days (inclusive) for a habit:
       [{date:'YYYY-MM-DD', value:number}, ...]
       Any value>0 counts as 'done'.
       Query: ?habit_id=<id>
    """
    habit_id = request.args.get("habit_id", type=int)
    if not habit_id:
        return jsonify({"error": "habit_id is required"}), 400

    today = date.today()
    start = today - timedelta(days=6)
    logs = HabitLog.query.filter(
        HabitLog.habit_id == habit_id,
        HabitLog.log_date >= start,
        HabitLog.log_date <= today,
    ).all()
    by_day = {lg.log_date: float(lg.value or 0) for lg in logs}
    series = []
    for i in range(7):
        d = start + timedelta(days=i)
        series.append({"date": d.isoformat(), "value": by_day.get(d, 0.0)})
    return jsonify(series)
