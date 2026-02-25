import os
from flask import Flask
from dotenv import load_dotenv

from .extensions import db, login_manager
from .shared_constants import CATEGORIES, CATEGORY_TITLES, STATUS_LABELS


def create_app():
    load_dotenv()
    app = Flask(__name__)
    # Construct absolute path to database file
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    @app.context_processor
    def inject_ui_constants():
        return {
            "categories": CATEGORIES,
            "category_titles": CATEGORY_TITLES,
            "status_labels": STATUS_LABELS,
        }

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # register models
    from . import models

    # register bps
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.lists import bp as lists_bp
    from .routes.catalog import bp as catalog_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(catalog_bp)

    with app.app_context():
        db.create_all()

    return app
