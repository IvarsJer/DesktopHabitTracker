from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Habit

bp = Blueprint("habits", __name__)


@bp.route("/")
def index():
    habits = Habit.query.order_by(Habit.name).all()
    return render_template("habits/index.html", habits=habits)


@bp.route("/new", methods=["GET", "POST"])
@bp.route("/<int:habit_id>/edit", methods=["GET", "POST"])
def upsert(habit_id=None):
    habit = Habit.query.get(habit_id) if habit_id else Habit()
    if request.method == "POST":
        habit.name = request.form.get("name", "").strip()
        habit.kind = request.form.get("kind")
        habit.unit = request.form.get("unit")
        habit.daily_target = request.form.get("daily_target") or None
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
