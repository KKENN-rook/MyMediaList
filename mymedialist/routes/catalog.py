from flask import Blueprint, request, render_template
from flask_login import login_required
from mymedialist.services.books_api import search_books

bp = Blueprint("catalog", __name__, url_prefix="/catalog")

@bp.get("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "books")

    results = []
    if category == "books" and q:
        results = search_books(q)

    return render_template(
        "catalog_search.html",
        q=q,
        category=category,
        results=results,
    )