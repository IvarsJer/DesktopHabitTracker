from datetime import date, datetime
from . import db
from sqlalchemy import UniqueConstraint


class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    # kind controls how values are interpreted (display + validation)
    # count (reps), duration (minutes), distance (km), boolean (0/1)
    kind = db.Column(db.String(20), nullable=False, default="count")
    unit = db.Column(db.String(20), nullable=False, default="reps")
    color = db.Column(db.String(7), nullable=False, default="#3b82f6")  # hex
    daily_target = db.Column(db.Float, nullable=True)  # optional goal per day
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    logs = db.relationship("HabitLog", backref="habit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Habit {self.name} ({self.kind})>"


class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Float, nullable=True)  # minutes/reps/km/1
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("habit_id", "log_date", name="uq_habit_date"),
    )

    def as_dict(self):
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "log_date": self.log_date.isoformat(),
            "value": self.value,
            "note": self.note,
        }
