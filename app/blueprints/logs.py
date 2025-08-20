from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from .. import db
from ..models import Habit, HabitLog

bp = Blueprint("logs", __name__)


@bp.route("/new", methods=["GET", "POST"])
@bp.route("/<int:log_id>/edit", methods=["GET", "POST"])
def upsert(log_id=None):
    log = HabitLog.query.get(log_id) if log_id else None
    habits = Habit.query.order_by(Habit.name).all()

    if request.method == "POST":
        habit_id = int(request.form["habit_id"]) if request.form.get("habit_id") else None
        log_date = request.form.get("log_date") or date.today().isoformat()
        value = request.form.get("value")
        note = request.form.get("note")

        if not habit_id:
            flash("Please choose a habit.", "danger")
            return render_template("logs/form.html", log=log, habits=habits)

        if log is None:
            log = HabitLog(habit_id=habit_id, log_date=log_date, value=value, note=note)
        else:
            log.habit_id = habit_id
            log.log_date = log_date
            log.value = value
            log.note = note

        try:
            db.session.add(log)
            db.session.commit()
            flash("Log saved.", "success")
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")

    return render_template("logs/form.html", log=log, habits=habits)
