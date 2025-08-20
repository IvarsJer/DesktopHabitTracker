from flask import Blueprint, render_template
from datetime import date, timedelta
from ..models import Habit, HabitLog
from ..utils import aggregate_logs, calc_streak

bp = Blueprint("main", __name__)


@bp.route("/")
def dashboard():
    habits = Habit.query.order_by(Habit.name).all()

    # build quick dashboard metrics per habit
    today = date.today()
    start_90 = today - timedelta(days=89)

    summaries = []
    for h in habits:
        logs = HabitLog.query.filter(
            HabitLog.habit_id == h.id,
            HabitLog.log_date >= start_90,
            HabitLog.log_date <= today,
        ).all()
        by_day = aggregate_logs(logs, "daily")
        streak = calc_streak(set(by_day.keys()))
        total = sum(by_day.values())
        summaries.append({
            "habit": h,
            "by_day": by_day,
            "streak": streak,
            "total": total,
        })

    return render_template("dashboard.html", summaries=summaries)
