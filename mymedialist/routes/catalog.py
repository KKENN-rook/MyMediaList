from flask import Blueprint, request, render_template, flash, redirect, abort, url_for
from flask_login import login_required, current_user
from sqlalchemy import select
import requests

from mymedialist.services.games_api import search_games, get_game_details
from mymedialist.services.books_api import search_books, get_book_details
from mymedialist.services.shows_api import search_shows, get_show_details
from mymedialist.shared_constants import CATEGORY_TITLES, CATEGORIES
from mymedialist.models import MediaWork, UserMedia
from mymedialist.extensions import db


bp = Blueprint("catalog", __name__, url_prefix="/catalog")


SEARCHERS = {
    "books": search_books,
    "games": search_games,
    "shows": search_shows,
}

DETAIL_FETCHERS = {
    "books": get_book_details,
    "games": get_game_details,
    "shows": get_show_details,
}


@bp.get("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()

    # Default to first known category instead of hardcoding "books"
    category = request.args.get("category") or CATEGORIES[0]

    if category not in CATEGORY_TITLES:
        abort(404)

    search_fn = SEARCHERS.get(category)
    if search_fn is None:
        flash(f"Search for '{CATEGORY_TITLES[category]}' isn't supported yet.")
        return render_template("search_results.html", query=query, category=category, results=[])

    try:
        results = search_fn(query)
    except requests.exceptions.RequestException:
        flash("Search is temporarily unavailable. Please try again.")
        results = []

    return render_template(
        "search_results.html",
        query=query,
        category=category,
        results=results,
    )


@bp.get("/details/<category>/<string:external_id>")
@login_required
def get_details(category: str, external_id: str):
    if category not in CATEGORY_TITLES:
        abort(404)

    fetch_func = DETAIL_FETCHERS.get(category)
    if fetch_func is None:
        abort(404)

    try:
        item = fetch_func(external_id)
    except requests.exceptions.RequestException:
        flash("Could not load details right now. Please try again.")
        return redirect(request.referrer or url_for("catalog.search", category=category))

    if not item or not item.get("title"):
        abort(404)

    # Check if this item is already on the user's list
    user_entry = None
    if current_user.is_authenticated:
        source = item.get("source", "manual")
        external_id = item.get("external_id")
        if source != "manual" and external_id:
            stmt = (
                select(UserMedia)
                .join(UserMedia.media)
                .where(
                    UserMedia.user_id == current_user.id,
                    MediaWork.source == source,
                    MediaWork.external_id == external_id,
                )
            )
            user_entry = db.session.execute(stmt).scalar_one_or_none()

    return render_template("entry_details.html", item=item, category=category, user_entry=user_entry)
