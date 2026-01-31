from flask import render_template, Blueprint
from flask_login import login_required, current_user

from ..extensions import db
from ..services.stats import get_category_stats
from ..shared_constants import CATEGORY_TITLES, STATUS_LABELS, STATUSES

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/profile")
@login_required
def profile():
    stats_by_category = {}

    for category in CATEGORY_TITLES.keys():
        stats_by_category[category] = get_category_stats(db.session, user_id=current_user.id, category=category)
    return render_template(
        "profile.html", stats_by_category=stats_by_category, category_titles=CATEGORY_TITLES, status_labels=STATUS_LABELS,
        statuses=STATUSES
    )
