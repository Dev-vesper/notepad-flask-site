import os
import hashlib
from functools import wraps
from flask import redirect, url_for, session

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_folder(username):
    user_folder = f"users/{username}"
    os.makedirs(user_folder, exist_ok=True)

    # ایجاد فایل‌های اولیه
    if not os.path.exists(f"{user_folder}/notes.json"):
        with open(f"{user_folder}/notes.json", 'w') as f:
            f.write('[]')

    if not os.path.exists(f"{user_folder}/profile.json"):
        with open(f"{user_folder}/profile.json", 'w') as f:
            f.write('{"username": "' + username + '", "joined_at": "' + datetime.now().isoformat() + '"}')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
