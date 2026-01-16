from flask import Flask

from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mymedialist.db"
    app.secret_key = "development_build"

    db.init_app(app)
    login_manager.init_app(app)

    # register models
    from . import models

    # register bps 
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.lists import bp as lists_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(lists_bp)

    with app.app_context():
        db.create_all()

    return app
