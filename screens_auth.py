from datetime import datetime
import customtkinter as ctk
from auth2 import (
    verify_login,
    signup,
    verify_security_answers,
    reset_password,
    get_security_questions,
    get_user_role,
)
from screens_common import clear, image_button, image_path, add_hover_zoom


def login_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="SNAC Wallet", font=("Arial", 26, "bold")).pack(pady=(24, 4))
    ctk.CTkLabel(app, text="Smart money management for families", font=("Arial", 14)).pack(pady=(0, 16))

    card = ctk.CTkFrame(app, width=560, height=600, corner_radius=18)
    card.pack(pady=8)
    card.pack_propagate(False)

    ctk.CTkLabel(card, text="Login", font=("Arial", 30, "bold")).pack(pady=(28, 6))
    ctk.CTkLabel(card, text="Welcome back. Continue where you left off.", font=("Arial", 13)).pack(pady=(0, 14))

    user = ctk.CTkEntry(card, placeholder_text="Username", font=("Arial", 19), height=48, width=360)
    user.pack(pady=8)
    pwd = ctk.CTkEntry(card, placeholder_text="Password", show="*", font=("Arial", 19), height=48, width=360)
    pwd.pack(pady=8)
    msg = ctk.CTkLabel(card, text="")
    msg.pack(pady=10)

    def do_login():
        if verify_login(user.get(), pwd.get()):
            role = get_user_role(user.get())
            from screens_dashboard import loading_screen
            loading_screen(app, user.get(), role)
        else:
            msg.configure(text="Invalid credentials ❌")

    login_btn = image_button(card, image_path("login.webp"), (240, 64), command=do_login, zoom=1.12)
    login_btn.pack(pady=(16, 8))

    signup_btn = image_button(card, image_path("signup.png"), (240, 64), command=lambda: signup_screen(app), zoom=1.12)
    signup_btn.pack(pady=6)

    forgot_btn = image_button(card, image_path("resetpassword.png"), (240, 64), command=lambda: reset_password_screen(app), zoom=1.12)
    forgot_btn.pack(pady=6)


def signup_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="Signup", font=("Arial", 28, "bold")).pack(pady=20)
    user = ctk.CTkEntry(app, placeholder_text="Username", font=("Arial", 22), height=50)
    user.pack(pady=4)
    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*", font=("Arial", 22), height=50)
    pwd.pack(pady=4)

    role_label = ctk.CTkLabel(app, text="Account Type", font=("Arial", 14, "bold"))
    role_label.pack(pady=(8, 2))
    role_menu = ctk.CTkOptionMenu(app, values=["Parent", "Child", "Vendor"])
    role_menu.set("Parent")
    role_menu.pack(pady=4)

    dob = ctk.CTkEntry(app, placeholder_text="Date of Birth (YYYY-MM-DD)")
    dob.pack(pady=4)

    sec_label = ctk.CTkLabel(app, text="Security Questions (answer 2)", font=("Arial", 14, "bold"))
    sec_label.pack(pady=(8, 2))
    q_values = [
        "What is your favorite color?",
        "What is the name of your first pet?",
        "What city were you born in?",
        "What is your mother's maiden name?",
        "What was the name of your first school?",
        "What is your favorite food?",
    ]
    q1_menu = ctk.CTkOptionMenu(app, values=q_values)
    q1_menu.set(q_values[0])
    q1_menu.pack(pady=3)
    a1_entry = ctk.CTkEntry(app, placeholder_text="Answer 1")
    a1_entry.pack(pady=3)
    q2_menu = ctk.CTkOptionMenu(app, values=q_values)
    q2_menu.set(q_values[1])
    q2_menu.pack(pady=3)
    a2_entry = ctk.CTkEntry(app, placeholder_text="Answer 2")
    a2_entry.pack(pady=3)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=8)

    def validate_basic_fields():
        username = user.get().strip()
        password = pwd.get().strip()
        role = role_menu.get()
        dob_value = dob.get().strip()

        if not username or not password:
            msg.configure(text="Username and password required ❌")
            return None

        profile = {"dob": dob_value}

        if role == "Parent":
            try:
                dob_date = datetime.strptime(dob_value, "%Y-%m-%d").date()
                age = (datetime.today().date() - dob_date).days // 365
                if age < 18:
                    msg.configure(text="Parent must be 18+ ❌")
                    return None
            except Exception:
                msg.configure(text="Invalid DOB format (YYYY-MM-DD) ❌")
                return None

        a1 = a1_entry.get().strip()
        a2 = a2_entry.get().strip()
        if not a1 or not a2:
            msg.configure(text="Answer both security questions ❌")
            return None

        security = {"q1": q1_menu.get(), "a1": a1, "q2": q2_menu.get(), "a2": a2}
        return username, password, role, profile, security

    def do_signup():
        data = validate_basic_fields()
        if not data:
            return
        username, password, role, profile, security = data
        if signup(username, password, role, profile, security):
            msg.configure(text="Account created ✅")
        else:
            msg.configure(text="User already exists ❌")

    def go_vendor_details():
        data = validate_basic_fields()
        if not data:
            return
        username, password, role, profile, security = data
        from screens_dashboard import vendor_details_screen
        vendor_details_screen(app, username, password, role, profile, security)

    primary_btn = image_button(app, image_path("continue.webp"), (240, 60), command=go_vendor_details, zoom=1.12)
    primary_btn.pack(pady=10)

    def refresh_primary():
        if role_menu.get() == "Vendor":
            primary_btn.configure(command=go_vendor_details)
        else:
            primary_btn.configure(command=do_signup)

    role_menu.configure(command=lambda _v: refresh_primary())
    refresh_primary()

    back_btn = ctk.CTkButton(app, text="Back", command=lambda: login_screen(app), width=200, height=40)
    back_btn.pack(pady=6)
    add_hover_zoom(back_btn, 200, 40)


def reset_password_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="Reset Password", font=("Arial", 28, "bold")).pack(pady=30)
    user = ctk.CTkEntry(app, placeholder_text="Email / Username", font=("Arial", 18), height=50)
    user.pack(pady=6)

    q1_label = ctk.CTkLabel(app, text="")
    q1_label.pack(pady=4)
    q1 = ctk.CTkEntry(app, placeholder_text="Answer 1")
    q1.pack(pady=4)

    q2_label = ctk.CTkLabel(app, text="")
    q2_label.pack(pady=4)
    q2 = ctk.CTkEntry(app, placeholder_text="Answer 2")
    q2.pack(pady=4)

    new_pwd = ctk.CTkEntry(app, placeholder_text="New Password", show="*", font=("Arial", 18), height=50)
    new_pwd.pack(pady=6)
    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=8)

    def load_questions(_event=None):
        username = user.get().strip()
        if not username:
            msg.configure(text="Enter email/username ❌")
            return
        questions = get_security_questions(username)
        if not questions:
            msg.configure(text="Account not found ❌")
            return
        q1_label.configure(text=questions[0])
        q2_label.configure(text=questions[1])
        msg.configure(text="")

    user.bind("<FocusOut>", load_questions)
    user.bind("<Return>", load_questions)

    def do_reset():
        username = user.get().strip()
        a1 = q1.get().strip()
        a2 = q2.get().strip()
        np = new_pwd.get().strip()
        if not username or not a1 or not a2 or not np:
            msg.configure(text="Fill all fields ❌")
            return
        if not verify_security_answers(username, a1, a2):
            msg.configure(text="Security answers incorrect ❌")
            return
        reset_password(username, np)
        msg.configure(text="Password reset ✅")

    reset_btn = image_button(app, image_path("resetpassword.png"), (220, 60), command=do_reset, zoom=1.12)
    reset_btn.pack(pady=10)
    ctk.CTkButton(app, text="Back to Login", command=lambda: login_screen(app), width=200, height=40).pack(pady=6)
