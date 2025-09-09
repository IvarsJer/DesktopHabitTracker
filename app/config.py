import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # DATABASE_URL should be full SQLAlchemy URI e.g. postgresql+psycopg2://user:pass@localhost:5432/habitflow
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        "postgresql+psycopg2://habitflow:habitflow@127.0.0.1:5433/habitflow"
    )
    PORT = int(os.getenv("PORT", 5001))
