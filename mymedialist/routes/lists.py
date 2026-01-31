from flask import render_template, request, flash, redirect, url_for, abort, Blueprint
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from flask_login import login_required, current_user

from ..extensions import db
from ..models import UserMedia, MediaWork
from ..shared_constants import CATEGORY_TITLES, STATUSES, get_status_labels

bp = Blueprint("lists", __name__)


@bp.route("/<category>")
@login_required
def media_list(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    stmt = (
        select(UserMedia)
        .join(UserMedia.media)
        .where(
            UserMedia.user_id == current_user.id,
            MediaWork.category == category,
        )
        .options(selectinload(UserMedia.media))
        .order_by(MediaWork.title)
    )
    entries = db.session.execute(stmt).scalars().all()

    return render_template(
        "media_list.html", 
        category=category, 
        title=CATEGORY_TITLES[category], 
        entries=entries,
        statuses=STATUSES,
        status_labels=get_status_labels(category))


@bp.route("/add/<category>", methods=["POST"])
@login_required
def add_entry(category):
    if category not in CATEGORY_TITLES:
        abort(404)

    title = request.form["title"].strip()
    rating = int(request.form["rating"]) if request.form["rating"] else None  # returns "" if "-" option is selected
    status = request.form["status"]
    notes = request.form.get("notes") or None
    progress_value = int(request.form.get("progress_value") or 0) or None

    if not title or not category or not status:
        flash("Title, category, and status are required.")
        return redirect(url_for("lists.media_list", category=category))

    # Manual entry always adds a new MediaWork **Placeholder until APIs are implemented
    media = MediaWork(title=title, category=category, source="manual")

    new_entry = UserMedia(
        user_id=current_user.id,
        media=media,
        status=status,
        rating=rating,
        notes=notes,
        progress_value=progress_value,
    )
    db.session.add(new_entry)  # Cascades and saves media too due to the relationship
    db.session.commit()

    flash(f"Added '{title}' to your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("lists.media_list", category=category))


@bp.route("/edit/<category>/<int:entry_id>", methods=["POST"])
@login_required
def edit_entry(category, entry_id):
    if category not in CATEGORY_TITLES:
        abort(404)

    entry = db.session.get(UserMedia, entry_id)
    if entry is None or entry.user_id != current_user.id:
        flash("Item not found or you don't have permission to edit it.")
        return redirect(url_for("lists.media_list", category=category))

    title = request.form["title"]
    rating = int(request.form["rating"]) if request.form["rating"] else None
    status = request.form["status"]
    notes = request.form.get("notes") or None
    progress_value = int(request.form.get("progress_value") or 0) or None

    entry.media.title = title
    entry.rating = rating
    entry.status = status
    entry.notes = notes
    entry.progress_value = progress_value

    db.session.commit()
    flash(f"Updated '{title}' in your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("lists.media_list", category=category))


@bp.route("/delete/<category>/<int:entry_id>", methods=["POST"])
@login_required
def delete_entry(category, entry_id):
    if category not in CATEGORY_TITLES:
        abort(404)

    entry = db.session.get(UserMedia, entry_id)
    if entry is None or entry.user_id != current_user.id:
        flash("Item not found or you don't have permission to delete it.")
        return redirect(url_for("lists.media_list", category=category))
    
    title = entry.media.title # Capture the title to display it after delete

    db.session.delete(entry)
    db.session.commit()
    flash(f"Deleted '{title}' from your {CATEGORY_TITLES[category]} list.")
    return redirect(url_for("lists.media_list", category=category))
