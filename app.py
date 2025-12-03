from flask import Flask, render_template, request, flash, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, select, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Valid Categories : Their page title
CATEGORY_TITLES = {"books": "Books", "games": "Games", "shows": "Shows & Film"}


# Set up Flask and connect SQLAlchemy to the SQLite database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mymedialist.db"
db = SQLAlchemy(app)

# Initialize for client side sessions
app.secret_key = "development_build"

# Flask-login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    pw_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # Hash could use many chars
    media_items: Mapped[list["MediaItem"]] = relationship(back_populates="user")  # 1:M -- User:Media Items

    def set_password(self, password: str):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class MediaItem(db.Model):
    __tablename__ = "media_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Generic progress tracking
    total_units: Mapped[int | None] = mapped_column(nullable=True)
    completed_units: Mapped[int | None] = mapped_column(nullable=True)
    unit_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="media_items")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
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
            return redirect(next_page or url_for("profile"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("You are now logged out.")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form_username = request.form["username"].strip().lower()  # Usernames are case insensitive
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
@login_required
def profile():
    return render_template("profile.html", user=current_user.username)


@app.route("/<category>")
@login_required
def media_list(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    stmt = (
        select(MediaItem)
        .where(MediaItem.category == category, MediaItem.user_id == current_user.id)
        .order_by(MediaItem.title)
    )
    items = db.session.execute(stmt).scalars().all()

    return render_template("media_list.html", category=category, title=CATEGORY_TITLES[category], items=items)


@app.route("/add/<category>", methods=["POST"])
@login_required
def add_entry(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    title = request.form["title"].strip()
    rating = int(request.form["rating"]) if request.form["rating"] else None  # returns "" if "-" option is selected
    status = request.form["status"]
    notes = request.form.get("notes") or None

    new_item = MediaItem(
        title=title,
        category=category,
        status=status,
        rating=rating,
        notes=notes,
        user_id=current_user.id,
    )
    db.session.add(new_item)
    db.session.commit()

    flash(f"Added '{title}' to your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("media_list", category=category))


@app.route("/edit/<category>", methods=["POST"])
def edit_entry(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    old_title = request.form["old_title"]
    title = request.form["title"]
    rating = int(request.form["rating"]) if request.form["rating"] else None
    status = request.form["status"]

    stmt = select(MediaItem).where(
        MediaItem.category == category,
        MediaItem.user_id == current_user.id,
        MediaItem.title == old_title,
    )
    item = db.session.execute(stmt).scalar_one_or_none()

    if not item:
        flash("Item not found or you don't have permission to edit it.")
        return redirect(url_for("media_list", category=category))

    item.title = title
    item.rating = rating
    item.status = status
    db.session.commit()

    flash(f"Updated '{title}' in your {CATEGORY_TITLES[category]} list.")
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
