from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for login sessions

# -------------------------
# DATABASE SIMULATION
# -------------------------
users = {
    "grandma": {"password": "password123", "balance": 5000, "transactions": []},
    "demo": {"password": "demo123", "balance": 1000, "transactions": []},
}

# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid login, try again."
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user = users[username]
    return render_template(
        "dashboard.html",
        username=username,
        balance=user["balance"],
        transactions=user["transactions"]
    )


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
