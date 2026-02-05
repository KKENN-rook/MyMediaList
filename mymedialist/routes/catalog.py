from flask import Blueprint, request, render_template, flash, redirect, abort, url_for
from flask_login import login_required
import requests

from mymedialist.services.books_api import search_books, get_book_details
from mymedialist.shared_constants import CATEGORY_TITLES, CATEGORIES


bp = Blueprint("catalog", __name__, url_prefix="/catalog")


SEARCHERS = {
    "books": search_books,
    # "games": search_games,
    # "shows": search_shows,
}

DETAIL_FETCHERS = {
    "books": get_book_details,
    # "games": get_game_details,
    # "shows": get_show_details,
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

    fetch_fn = DETAIL_FETCHERS.get(category)
    if fetch_fn is None:
        abort(404)

    try:
        item = fetch_fn(external_id)
    except requests.exceptions.RequestException:
        flash("Could not load details right now. Please try again.")
        return redirect(request.referrer or url_for("catalog.search", category=category))

    if not item or not item.get("title"):
        abort(404)

    # Ensure category is available to template even if service doesn't include it
    item["category"] = category

    return render_template("entry_details.html", item=item)
