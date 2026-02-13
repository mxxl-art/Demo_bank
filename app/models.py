import json
import os

DATA_FILE = "app/users.json"

# ---------------- Load Users ---------------- #
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # If file is empty, return default users
                return default_users()
    else:
        return default_users()

def default_users():
    return {
        "john": {"username": "john", "password": "1234", "name": "John Doe", "balance": 1000.0, "transactions": [], "notifications": []},
        "Aaron1": {"username": "Aaron1", "password": "password123", "name": "Aaron James Dacombe", "balance": 250000.0, "transactions": [], "notifications": []},
        "Rbrown1": {"username": "Rbrown1", "password": "password123", "name": "Robert Brown", "balance": 1250.0, "transactions": [], "notifications": []}
    }

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- Users & Admin ---------------- #
users = load_users()
admin = {"username": "admin", "password": "admin123"}

# ---------------- Helper Functions ---------------- #
def add_transaction(user, description, amount, status):
    txn = {"description": description, "amount": amount, "status": status}
    user.setdefault("transactions", []).insert(0, txn)
    # Initialize notifications list if missing
    user.setdefault("notifications", [])
    save_users(users)  # persist immediately

def update_balance(user, new_balance, reason="Admin Balance Adjustment"):
    delta = new_balance - user["balance"]
    user["balance"] = new_balance
    add_transaction(user, reason, delta, "APPROVED")
    save_users(users)
