from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# extensions (initialized without app, then "init_app" later)
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object("app.config.Config")

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from .blueprints.main import bp as main_bp
    from .blueprints.habits import bp as habits_bp
    from .blueprints.logs import bp as logs_bp
    from .blueprints.api import bp as api_bp
    from . import models

    app.register_blueprint(main_bp)
    app.register_blueprint(habits_bp, url_prefix="/habits")
    app.register_blueprint(logs_bp, url_prefix="/logs")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.shell_context_processor
    def make_shell_context():
        from . import models
        return {"db": db, **models.__dict__}

    return app
