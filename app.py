from flask import Flask, render_template, request, flash, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = "development_build"

# Temporary user database
users = {}

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
    return render_template("profile.html", user=session["user"])


@app.route("/<category>")
def media_list(category):
    selected = data.get(category)
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
    app.run(debug=True)
