import hashlib
from datetime import datetime
from firebase import get_ref

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    users_ref = get_ref("users")
    if users_ref.child(username).get():
        return False

    users_ref.child(username).set({
        "password": hash_password(password),
        "created_at": str(datetime.now()),
        "balance": 0
    })
    return True

def verify_login(username, password):
    user = get_ref("users").child(username).get()
    if not user:
        return False

    return user["password"] == hash_password(password)