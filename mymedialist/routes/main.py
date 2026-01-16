from flask import render_template, Blueprint
from flask_login import login_required


bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
