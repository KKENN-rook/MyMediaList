from flask import Flask, render_template, request, flash, redirect, url_for, session

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
    return redirect(url_for('home'))

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

@app.route("/booklist")
def booklist():
    return render_template("booklist.html")

@app.route("/gamelist")
def gamelist():
    return render_template("gamelist.html")

@app.route("/showlist")
def showlist():
    return render_template("film.html")


if __name__ == "__main__":
    app.run(debug=True)
