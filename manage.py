from app import create_app, db
from flask_migrate import upgrade
from app.seeds import seed_example_data
import os

app = create_app()


@app.cli.command("seed")
def seed():
    """Seed database with example habits and logs."""
    seed_example_data()
    print("Seeded example data.")


if __name__ == "__main__":
    # Allow `python manage.py run`
    port = int(os.getenv("PORT", 5001))
    app.run(host="127.0.0.1", port=port, debug=True)
