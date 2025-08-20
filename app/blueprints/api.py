from flask import Blueprint, jsonify, request
from datetime import date, timedelta
from ..models import Habit, HabitLog
from ..utils import aggregate_logs

bp = Blueprint("api", __name__)


@bp.get("/stats")
def stats():
    """Return aggregated timeseries for a habit.
    Query params: habit_id=<id>&range=daily|weekly|monthly&days=<n>
    """
    habit_id = request.args.get("habit_id", type=int)
    gran = request.args.get("range", default="daily")
    days = request.args.get("days", default=30, type=int)

    if not habit_id:
        return jsonify({"error": "habit_id is required"}), 400

    today = date.today()
    start = today - timedelta(days=days - 1)

    logs = HabitLog.query.filter(
        HabitLog.habit_id == habit_id,
        HabitLog.log_date >= start,
        HabitLog.log_date <= today,
    ).all()

    series = aggregate_logs(logs, gran)
    points = [{"date": d.isoformat(), "value": v} for d, v in series.items()]
    habit = Habit.query.get(habit_id)
    return jsonify({
        "habit": {
            "id": habit.id,
            "name": habit.name,
            "unit": habit.unit,
            "kind": habit.kind,
            "daily_target": habit.daily_target,
            "color": habit.color,
        },
        "granularity": gran,
        "points": points,
    })
