from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select
from werkzeug.security import generate_password_hash, check_password_hash
import os


# Set up Flask and connect SQLAlchemy to the SQLite database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mymedialist.db"
db = SQLAlchemy(app)

# Initialize for client side sessions
app.secret_key = "development_build"

# Temporary database (shared between all users for now while a database isn't implemented)
data = {
    "books": {
        "title": "Books",
        "headers": ["Title", "Rating"],
        "statuses": ["All", "Completed", "Reading", "Plan to Read", "Dropped"],
        "items": [
            {"Title": "The Outsiders", "Rating": 10, "Status": "Completed"},
            {"Title": "Moby Dick", "Rating": 6, "Status": "Completed"},
            {"Title": "To Kill a Mockingbird", "Rating": 7, "Status": "Completed"},
            {"Title": "The Metamorphosis", "Rating": None, "Status": "Plan to Read"},
        ],
    },
    "games": {
        "title": "Games",
        "headers": ["Title", "Rating"],
        "statuses": ["All", "Completed", "Playing", "Plan to Play", "Dropped"],
        "items": [
            {"Title": "Hades", "Rating": 10, "Status": "Completed"},
            {"Title": "Final Fantasy VII", "Rating": None, "Status": "Playing"},
            {"Title": "Ocarina of Time", "Rating": None, "Status": "Plan to Play"},
            {"Title": "Halo Reach", "Rating": None, "Status": "Dropped"},
        ],
    },
    "shows": {
        "title": "Shows & Films",
        "headers": ["Title", "Rating"],
        "statuses": ["All", "Completed", "Watching", "Plan to Watch", "Dropped"],
        "items": [
            {"Title": "Demon Slayer", "Rating": 7, "Status": "Completed"},
            {"Title": "Toy Story", "Rating": 9, "Status": "Completed"},
            {"Title": "One Piece", "Rating": None, "Status": "Dropped"},
        ],
    },
}


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Hash could use many chars

    def set_password(self, password: str):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Verify login information
    if request.method == "POST":
        form_username = request.form["username"]
        form_password = request.form["password"]
        stmt = select(User).filter_by(username=form_username)
        user = db.session.execute(stmt).scalar()
        if user and user.check_password(form_password):
            session["user"] = user.username
            flash("Login Successful!")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You are now logged out.")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_username = request.form["username"]
        form_password = request.form["password"]

        # Verify inputted username does not already exist
        stmt = select(User).filter_by(username=form_username)
        existing_user = db.session.execute(stmt).scalar()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for("register"))

        # Create and Save new user
        user = User(username=form_username)
        user.set_password(form_password)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/profile")
def profile():
    return render_template("profile.html", user=session["user"])


@app.route("/<category>")
def media_list(category):
    selected = data.get(category)

    if selected is None:
        abort(404)
    return render_template("media_list.html", category=category, **selected)


@app.route("/add/<category>", methods=["POST"])
def add_entry(category):
    title = request.form["title"]
    rating = request.form["rating"] or None  # Used to account for "-" entries (It's value is set to "" in media_list)
    status = request.form["status"]
    data[category]["items"].append({"Title": title, "Rating": rating, "Status": status})

    flash(f"Added '{title}' to your {category.capitalize()} list.")
    return redirect(url_for("media_list", category=category))


@app.route("/edit/<category>", methods=["POST"])
def edit_entry(category):
    old_title = request.form["old_title"]
    title = request.form["title"]
    rating = request.form["rating"] or None
    status = request.form["status"]

    for item in data[category]["items"]:
        if item["Title"] == old_title:
            item["Title"] = title
            item["Rating"] = rating
            item["Status"] = status
            break

    flash(f"Updated '{title}' in your {category.capitalize()} list.")
    return redirect(url_for("media_list", category=category))


@app.route("/delete/<category>", methods=["POST"])
def delete_entry(category):
    title = request.form["title"]
    data[category]["items"] = [i for i in data[category]["items"] if i["Title"] != title]
    flash(f"Deleted '{title}' from your {category.capitalize()} list.")
    return redirect(url_for("media_list", category=category))


if __name__ == "__main__":
    # create_all() requires application context
    with app.app_context():
        db.create_all()
    app.run(debug=True)
