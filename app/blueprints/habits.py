# app/blueprints/habits.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date, timedelta
from .. import db
from ..models import Habit, HabitLog
from ..utils import calc_streak

bp = Blueprint("habits", __name__)


@bp.route("/")
def index():
    """Daily checklist-like view of habits with quick 'done today' controls."""
    habits = Habit.query.order_by(Habit.name).all()

    today = date.today()
    start = today - timedelta(days=6)  # last 7 days inclusive

    # Pull last 7 days of logs for all habits once
    logs = (
        HabitLog.query.filter(
            HabitLog.log_date >= start,
            HabitLog.log_date <= today,
        ).all()
    )
    by_key = {(lg.habit_id, lg.log_date): (lg.value or 0) for lg in logs}

    # Also get last 90d to compute streaks
    start_90 = today - timedelta(days=89)
    logs_90 = (
        HabitLog.query.filter(
            HabitLog.log_date >= start_90,
            HabitLog.log_date <= today,
        ).all()
    )

    active_days = {}
    for lg in logs_90:
        if (lg.value or 0) > 0:
            active_days.setdefault(lg.habit_id, set()).add(lg.log_date)

    vm = []
    for h in habits:
        week = []
        for i in range(7):
            d = start + timedelta(days=i)
            v = float(by_key.get((h.id, d), 0) or 0)
            week.append({"date": d, "value": v})
        today_total = week[-1]["value"]
        streak = calc_streak(active_days.get(h.id, set()))
        vm.append(
            {"habit": h, "week": week, "today_total": today_total, "streak": streak}
        )

    # Single-letter weekday labels Mon..Sun for each row block
    week_labels = [(start + timedelta(days=i)).strftime("%a")[0] for i in range(7)]

    return render_template("habits/index.html", rows=vm, week_labels=week_labels)


@bp.route("/new", methods=["GET", "POST"])
@bp.route("/<int:habit_id>/edit", methods=["GET", "POST"])
def upsert(habit_id=None):
    habit = Habit.query.get(habit_id) if habit_id else Habit()
    if request.method == "POST":
        habit.name = request.form.get("name", "").strip()
        habit.kind = request.form.get("kind")
        habit.unit = request.form.get("unit") or ""
        # daily_target is optional; store as float or None
        dt = request.form.get("daily_target", "").strip()
        habit.daily_target = float(dt) if dt else None
        habit.color = request.form.get("color") or "#3b82f6"

        if not habit.name:
            flash("Name is required.", "danger")
            return render_template("habits/form.html", habit=habit)

        db.session.add(habit)
        db.session.commit()
        flash("Habit saved.", "success")
        return redirect(url_for("habits.index"))

    return render_template("habits/form.html", habit=habit)


@bp.route("/<int:habit_id>/delete", methods=["POST"])
def delete(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    flash("Habit deleted.", "success")
    return redirect(url_for("habits.index"))


# ---------- Quick actions (used by the Habits list) ----------

@bp.post("/today/toggle")
def toggle_today():
    """
    Toggle today's completion for a boolean habit.
    Expects: habit_id (form or JSON). Returns JSON {ok: true, today_total: 0|1}
    """
    habit_id = request.values.get("habit_id") or (request.json or {}).get("habit_id")
    if not habit_id:
        return jsonify({"ok": False, "error": "habit_id required"}), 400

    habit = Habit.query.get_or_404(int(habit_id))
    if habit.kind != "boolean":
        return jsonify({"ok": False, "error": "Only boolean habits can be toggled."}), 400

    today = date.today()
    log = HabitLog.query.filter_by(habit_id=habit.id, log_date=today).first()

    if log and (log.value or 0) > 0:
        # Uncheck -> remove the log (cleaner DB than storing 0)
        db.session.delete(log)
        today_total = 0
    else:
        if not log:
            log = HabitLog(habit_id=habit.id, log_date=today, value=1)
            db.session.add(log)
        else:
            log.value = 1
        today_total = 1

    db.session.commit()
    return jsonify({"ok": True, "today_total": today_total})


@bp.post("/quick_add")
def quick_add():
    """
    Increment today's value for numeric habits.
    Expects: habit_id, amount (form or JSON). Returns JSON {ok: true, today_total: N}
    """
    data = request.json or request.form
    try:
        habit_id = int(data.get("habit_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "habit_id required"}), 400

    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "amount must be a number"}), 400

    if amount <= 0:
        return jsonify({"ok": False, "error": "amount must be > 0"}), 400

    habit = Habit.query.get_or_404(habit_id)
    if habit.kind == "boolean":
        return jsonify({"ok": False, "error": "boolean habits cannot quick-add"}), 400

    # normalize amount for integer-ish kinds
    if habit.kind in ("count", "duration"):
        amount = int(round(amount))

    today = date.today()
    log = HabitLog.query.filter_by(habit_id=habit.id, log_date=today).first()
    if not log:
        log = HabitLog(habit_id=habit.id, log_date=today, value=amount)
        db.session.add(log)
        today_total = amount
    else:
        log.value = float(log.value or 0) + amount
        today_total = log.value

    db.session.commit()
    return jsonify({"ok": True, "today_total": today_total})
