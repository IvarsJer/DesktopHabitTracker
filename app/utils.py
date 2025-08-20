from datetime import date, timedelta
from collections import defaultdict


def daterange(start, end):
    """Yield dates from start..end inclusive."""
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def start_of_week(d):
    return d - timedelta(days=d.weekday())  # Monday


def start_of_month(d):
    return d.replace(day=1)


def aggregate_logs(logs, granularity="daily"):
    """Aggregate HabitLog rows (already filtered by habit or not) by day/week/month.
    Returns dict[date, float]
    """
    buckets = defaultdict(float)
    for log in logs:
        d = log.log_date
        if granularity == "weekly":
            key = start_of_week(d)
        elif granularity == "monthly":
            key = start_of_month(d)
        else:
            key = d
        buckets[key] += float(log.value or 0)
    return dict(sorted(buckets.items()))


def calc_streak(dates_set):
    """Given a set of dates with activity, return current streak length (days)."""
    streak = 0
    today = date.today()
    d = today
    while d in dates_set:
        streak += 1
        d = d - timedelta(days=1)
    return streak
