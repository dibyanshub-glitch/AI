import json
import os
import bcrypt

USERS_FILE = "Data/users.json"


def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users):
    os.makedirs("Data", exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(email, password):
    users = _load_users()

    if email in users:
        return {"ok": False, "msg": "User already exists"}

    users[email] = {
        "password": hash_password(password)
    }

    _save_users(users)
    return {"ok": True}


def login_user(email, password):
    users = _load_users()

    if email not in users:
        return {"ok": False, "msg": "User not found"}

    if not verify_password(password, users[email]["password"]):
        return {"ok": False, "msg": "Wrong password"}

    return {"ok": True}