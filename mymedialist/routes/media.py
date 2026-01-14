from flask import render_template, request, flash, redirect, url_for, abort, Blueprint
from sqlalchemy import select
from flask_login import login_required, current_user

from ..extensions import db
from ..models import MediaItem

# Valid Categories : Their page title
CATEGORY_TITLES = {"books": "Books", "games": "Games", "shows": "Shows & Film"}

bp = Blueprint("media", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@bp.route("/<category>")
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


@bp.route("/add/<category>", methods=["POST"])
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
    return redirect(url_for("media.media_list", category=category))


@bp.route("/edit/<category>", methods=["POST"])
@login_required
def edit_entry(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    old_title = request.form["old_title"]
    title = request.form["title"]
    rating = int(request.form["rating"]) if request.form["rating"] else None
    status = request.form["status"]
    notes = request.form.get("notes") or None

    stmt = select(MediaItem).where(
        MediaItem.category == category,
        MediaItem.user_id == current_user.id,
        MediaItem.title == old_title,
    )
    item = db.session.execute(stmt).scalars().first()

    if not item:
        flash("Item not found or you don't have permission to edit it.")
        return redirect(url_for("media.media_list", category=category))

    item.title = title
    item.rating = rating
    item.status = status
    item.notes = notes
    db.session.commit()

    flash(f"Updated '{title}' in your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("media.media_list", category=category))


@bp.route("/delete/<category>", methods=["POST"])
@login_required
def delete_entry(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    title = request.form["title"]

    stmt = select(MediaItem).where(
        MediaItem.category == category,
        MediaItem.user_id == current_user.id,
        MediaItem.title == title,
    )
    item = db.session.execute(stmt).scalars().first()

    if not item:
        flash("Item not found or you don't have permission to delete it.")
        return redirect(url_for("media.media_list", category=category))

    db.session.delete(item)
    db.session.commit()

    flash(f"Deleted '{title}' from your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("media.media_list", category=category))
