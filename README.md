# HabitFlow


A minimal, extensible habit tracker for your workouts, cold swims, coding practice, cybersecurity study, healthy eating, and more.


## Features
- Create habits with kind (count / duration / distance / boolean), unit, target, and color
- Log daily activity quickly
- Dashboard with streak + mini chart per habit
- JSON stats API for daily/weekly/monthly aggregations (used by charts)
- PostgreSQL via SQLAlchemy + Flask‑Migrate
- Run as a desktop window with `pywebview`


## Running locally
See the main instructions in the root of this document.


## Next ideas
- Habit detail page with weekly & monthly charts + calendar heatmap
- Per-habit reminders & notifications
- Multi-user auth with Flask‑Login
- Import/Export (CSV/JSON)
- Mobile‑friendly quick logging