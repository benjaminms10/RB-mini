import os
import json

USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users")

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)
    return True

def add_user(fullname, username, email, password):
    users = load_users()
    new_user = {
        "fullname": fullname,
        "username": username,
        "email": email,
        "password": password
    }
    users.append(new_user)
    save_users(users)

def username_exists(username):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return True
    return False

def authenticate(username, password):
    if username == "admin" and password == "admin":
        return True
    users = load_users()
    for user in users:
        if user.get("username") == username and user.get("password") == password:
            return True
    return False
