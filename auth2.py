import hashlib
from datetime import datetime
from firebase import get_ref


def hash_password(password):
    """Hash a raw password with SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def signup(username, password, role, profile, security):
    """Create a new user with role, profile, and security answers."""
    users_ref = get_ref("users")
    if users_ref.child(username).get():
        return False

    users_ref.child(username).set(
        {
            "password": hash_password(password),
            "created_at": str(datetime.now()),
            "balance": 0,
            "role": role,
            "profile": profile,
            "security": security,
        }
    )
    return True


def verify_login(username, password):
    """Check provided login credentials."""
    user = get_ref("users").child(username).get()
    if not user:
        return False

    return user["password"] == hash_password(password)


def verify_security_answers(username, a1, a2):
    """Validate security answers for password reset or child linking."""
    user = get_ref("users").child(username).get()
    if not user or "security" not in user:
        return False
    sec = user["security"]
    return sec.get("a1", "").lower() == a1.lower() and sec.get("a2", "").lower() == a2.lower()


def reset_password(username, new_password):
    """Update a user's password after successful verification."""
    get_ref("users").child(username).child("password").set(hash_password(new_password))
    return True


def get_security_questions(username):
    """Fetch the stored security questions for a user."""
    user = get_ref("users").child(username).get()
    if not user or "security" not in user:
        return None
    sec = user["security"]
    return sec.get("q1"), sec.get("q2")


def get_user_role(username):
    """Fetch the saved role for a user."""
    user = get_ref("users").child(username).get()
    if not user:
        return None
    return user.get("role")


def get_user_profile(username):
    """Fetch the profile object for a user."""
    user = get_ref("users").child(username).get()
    if not user:
        return None
    return user.get("profile", {})


def add_child_to_parent(parent_username, child_username):
    """Link a child to a parent account."""
    user_ref = get_ref("users").child(parent_username).child("profile").child("children")
    current = user_ref.get() or []
    if child_username not in current:
        current.append(child_username)
        user_ref.set(current)
    get_ref("users").child(child_username).child("profile").child("parent").set(parent_username)
    return True
