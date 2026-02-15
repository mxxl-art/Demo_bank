from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import users, admin, add_transaction, update_balance, save_users

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("main.dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]

        if not full_name or not username or not password:
            return render_template("signup.html", error="All fields are required")

        if username in users:
            return render_template("signup.html", error="Username already exists")

        users[username] = {
            "username": username,
            "password": password,
            "name": full_name,
            "balance": 0.0,
            "transactions": [],
            "notifications": [],
        }
        save_users(users)

        session["user"] = username
        return redirect(url_for("main.dashboard"))

    return render_template("signup.html")


@main.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("main.login"))

    username = session["user"]
    if username not in users:
        session.pop("user", None)
        return redirect(url_for("main.login"))

    user = users[username]
    notifications = user.get("notifications", []).copy()
    user["notifications"] = []
    save_users(users)

    return render_template("dashboard.html", user=user, notifications=notifications)


@main.route("/dashboard/deposit", methods=["POST"])
def dashboard_deposit():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json()
    amount = float(data["amount"])
    note = data.get("note", "Deposit Request")
    user = users[session["user"]]
    add_transaction(user, note, amount, "PENDING")
    return jsonify({"status": "success"})


@main.route("/dashboard/withdraw", methods=["POST"])
def dashboard_withdraw():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json()
    amount = float(data["amount"])
    note = data.get("note", "Withdraw Request")
    user = users[session["user"]]
    add_transaction(user, note, -amount, "PENDING")
    return jsonify({"status": "success"})


@main.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.login"))


@main.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == admin["username"] and password == admin["password"]:
            session["admin"] = username
            return redirect(url_for("main.admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")


@main.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("main.admin_login"))
    return render_template("admin_dashboard.html", users=users)


@main.route("/admin/update_balance", methods=["POST"])
def admin_update_balance():
    username = request.form["username"].strip()
    new_balance = float(request.form["balance"])
    user = users.get(username)
    if user:
        update_balance(user, new_balance)
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/edit_txn_description", methods=["POST"])
def admin_edit_txn_description():
    if "admin" not in session:
        return redirect(url_for("main.admin_login"))

    username = request.form.get("username", "").strip()
    txn_index = int(request.form.get("txn_index"))
    new_description = request.form.get("description", "").strip()

    if username in users and new_description:
        transactions = users[username].get("transactions", [])
        if 0 <= txn_index < len(transactions):
            transactions[txn_index]["description"] = new_description
            save_users(users)

    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/approve_txn", methods=["POST"])
def admin_approve_txn():
    username = request.form.get("username")
    txn_index = int(request.form.get("txn_index"))

    if username in users:
        txn = users[username]["transactions"][txn_index]
        if txn["status"] == "PENDING":
            txn["status"] = "APPROVED"
            users[username]["balance"] += txn["amount"]
            txn_type = "Deposit" if txn["amount"] > 0 else "Withdraw"
            users[username].setdefault("notifications", []).insert(0, f"{txn_type} Approved")
            save_users(users)
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/reject_txn", methods=["POST"])
def admin_reject_txn():
    username = request.form.get("username")
    txn_index = int(request.form.get("txn_index"))

    if username in users:
        txn = users[username]["transactions"][txn_index]
        if txn["status"] == "PENDING":
            txn["status"] = "REJECTED"
            txn_type = "Deposit" if txn["amount"] > 0 else "Withdraw"
            users[username].setdefault("notifications", []).insert(0, f"{txn_type} Rejected")
            save_users(users)
    return redirect(url_for("main.admin_dashboard"))
