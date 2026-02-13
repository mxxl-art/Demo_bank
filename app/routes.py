from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import users, admin, add_transaction, update_balance, save_users

main = Blueprint("main", __name__)

# ---------------- User Login ---------------- #
@main.route("/", methods=["GET", "POST"])
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("main.dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# ---------------- User Dashboard ---------------- #
@main.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("main.login"))
    user = users[session["user"]]

    # Copy notifications to show in template
    notifications = user.get("notifications", []).copy()

    # Clear notifications after showing
    user["notifications"] = []
    save_users(users)

    return render_template("dashboard.html", user=user, notifications=notifications)

# ---------------- User Deposit Modal ---------------- #
@main.route("/dashboard/deposit", methods=["POST"])
def dashboard_deposit():
    data = request.get_json()
    amount = float(data["amount"])
    note = data.get("note", "Deposit Request")
    user = users[session["user"]]
    add_transaction(user, note, amount, "PENDING")
    return jsonify({"status": "success"})

# ---------------- User Withdraw Modal ---------------- #
@main.route("/dashboard/withdraw", methods=["POST"])
def dashboard_withdraw():
    data = request.get_json()
    amount = float(data["amount"])
    note = data.get("note", "Withdraw Request")
    user = users[session["user"]]
    add_transaction(user, note, -amount, "PENDING")
    return jsonify({"status": "success"})

# ---------------- User Logout ---------------- #
@main.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.login"))

# ---------------- Admin Login ---------------- #
@main.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == admin["username"] and password == admin["password"]:
            session["admin"] = username
            return redirect(url_for("main.admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

# ---------------- Admin Dashboard ---------------- #
@main.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("main.admin_login"))
    return render_template("admin_dashboard.html", users=users)

# ---------------- Admin Update Balance ---------------- #
@main.route("/admin/update_balance", methods=["POST"])
def admin_update_balance():
    username = request.form["username"]
    new_balance = float(request.form["balance"])
    user = users.get(username)
    if user:
        update_balance(user, new_balance)
    return redirect(url_for("main.admin_dashboard"))

# ---------------- Admin Approve / Reject Transactions ---------------- #
@main.route("/admin/approve_txn", methods=["POST"])
def admin_approve_txn():
    username = request.form.get("username")
    txn_index = int(request.form.get("txn_index"))

    if username in users:
        txn = users[username]["transactions"][txn_index]
        if txn["status"] == "PENDING":
            txn["status"] = "APPROVED"
            users[username]["balance"] += txn["amount"]

            # Update description to Deposit/Withdraw only
            txn["description"] = "Deposit" if txn["amount"] > 0 else "Withdraw"

            # Add notification for user
            users[username].setdefault("notifications", []).insert(0, f"{txn['description']} Approved")

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

            # Update description to Deposit/Withdraw only
            txn["description"] = "Deposit" if txn["amount"] > 0 else "Withdraw"

            # Add notification for user
            users[username].setdefault("notifications", []).insert(0, f"{txn['description']} Rejected")

            save_users(users)
    return redirect(url_for("main.admin_dashboard"))
