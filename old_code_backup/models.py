import json
import os
from tempfile import NamedTemporaryFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "users.json")


def default_users():
    return {
        "john": {
            "username": "john",
            "password": "1234",
            "name": "John Doe",
            "balance": 1000.0,
            "transactions": [],
            "notifications": [],
        },
        "Aaron1": {
            "username": "Aaron1",
            "password": "password123",
            "name": "Aaron James Dacombe",
            "balance": 250000.0,
            "transactions": [],
            "notifications": [],
        },
        "Rbrown1": {
            "username": "Rbrown1",
            "password": "password123",
            "name": "Robert Brown",
            "balance": 1250.0,
            "transactions": [],
            "notifications": [],
        },
    }


def _is_empty_file(path):
    return os.path.exists(path) and os.path.getsize(path) == 0


def _ensure_user_shape(data):
    for username, user in data.items():
        user.setdefault("username", username)
        user.setdefault("name", username)
        user.setdefault("balance", 0.0)
        user.setdefault("transactions", [])
        user.setdefault("notifications", [])
    return data


def load_users():
    if not os.path.exists(DATA_FILE) or _is_empty_file(DATA_FILE):
        users_data = default_users()
        save_users(users_data)
        return users_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict) or not data:
                users_data = default_users()
                save_users(users_data)
                return users_data
            return _ensure_user_shape(data)
        except json.JSONDecodeError:
            users_data = default_users()
            save_users(users_data)
            return users_data


def save_users(users_data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with NamedTemporaryFile("w", delete=False, dir=os.path.dirname(DATA_FILE), encoding="utf-8") as tmp:
        json.dump(users_data, tmp, indent=4)
        temp_name = tmp.name
    os.replace(temp_name, DATA_FILE)


users = load_users()
admin = {"username": "admin", "password": "admin123"}


def add_transaction(user, description, amount, status):
    txn = {"description": description, "amount": amount, "status": status}
    user.setdefault("transactions", []).insert(0, txn)
    user.setdefault("notifications", [])
    save_users(users)


def update_balance(user, new_balance, reason=None):
    old_balance = user.get("balance", 0.0)
    delta = new_balance - old_balance
    user["balance"] = new_balance

    if delta > 0:
        description = "Deposit Successful"
    elif delta < 0:
        description = "Withdraw Successful"
    else:
        description = reason or "Balance Unchanged"

    add_transaction(user, description, delta, "APPROVED")
