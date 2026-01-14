from flask import Blueprint, request, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required
from sqlalchemy import select

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    # Verify login information
    if request.method == "POST":
        form_username = request.form["username"].strip().lower()
        form_password = request.form["password"]
        stmt = select(User).filter_by(username=form_username)
        user = db.session.execute(stmt).scalar()
        if user and user.check_password(form_password):
            login_user(user)
            flash("Login Successful!")
            # If a user tries to access a protected page w/o being logged in
            # they will be redirected to login and the page tried will be stored under the key "next"
            next_page = request.args.get("next")
            return redirect(next_page or url_for("media.profile"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.")
    return redirect(url_for("media.home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_username = request.form["username"].strip().lower()  # Usernames are case insensitive
        form_password = request.form["password"]

        # Verify inputted username does not already exist
        stmt = select(User).filter_by(username=form_username)
        existing_user = db.session.execute(stmt).scalar()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for("auth.register"))

        # Create and Save new user
        user = User(username=form_username)
        user.set_password(form_password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")
