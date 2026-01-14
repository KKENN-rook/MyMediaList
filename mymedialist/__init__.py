from flask import Flask

from .extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mymedialist.db"
    app.secret_key = "development_build"

    db.init_app(app)
    login_manager.init_app(app)

    print("login_view =", login_manager.login_view)
    print("has login endpoint =", "login" in app.view_functions)
    print("has auth.login endpoint =", "auth.login" in app.view_functions)

    # register models
    from . import models

    from .routes.auth import bp as auth_bp
    from .routes.media import bp as media_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(media_bp)

    with app.app_context():
        db.create_all()

    return app
