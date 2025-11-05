from flask import Flask, render_template, request, flash, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = "development_build"

# Temporary user database
users = {}


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.get(username) == password:
            session["user"] = username
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You are now logged out.")
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            flash("Username already exists.")
        else:
            users[username] = password
            flash("Registered successfully! Please log in.")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("profile.html", user=session["user"])


@app.route("/<category>")
def media_list(category):
    if "user" not in session:
        return redirect(url_for("home"))

    data = {
        "books": {
            "title": "Books",
            "headers": ["Title", "Rating"],
            "statuses": ["All", "Completed", "In Progress", "Plan to Read", "Dropped"],
            "items": [
                {"Title": "The Outsiders", "Rating": 10, "Status": "Completed"},
                {"Title": "Moby Dick", "Rating": 6, "Status": "Completed"},
                {"Title": "To Kill a Mockingbird", "Rating": 7, "Status": "Completed"},
                {"Title": "The Metamorphosis", "Rating": None , "Status": "Plan to Read"},
            ],
        },
        "games": {
            "title": "Games",
            "headers": ["Title", "Rating"],
            "statuses": ["All", "Completed", "In Progress", "Plan to Play", "Dropped"],
            "items": [
                {"Title": "Hades", "Rating": 10, "Status": "Completed"},
                {"Title": "Final Fantasy VII", "Rating": None, "Status": "Playing"},
            ],
        },
        "shows": {
            "title": "Shows & Films",
            "headers": ["Title", "Rating"],
            "statuses": ["All", "Completed", "In Progress", "Plan to Watch", "Dropped"],
            "items": [
                {"Title": "Demon Slayer", "Rating": 7, "Status": "Completed"},
                {"Title": "Toy Story", "Rating": 9, "Status": "Completed"},
                {"Title": "One Piece", "Rating": None, "Status": "Dropped"},
            ],
        },
    }

    selected = data.get(category)
    if not selected:
        abort(404)
    
    return render_template("media_list.html", **selected)



if __name__ == "__main__":
    app.run(debug=True)
