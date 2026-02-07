import customtkinter as ctk
from auth2 import verify_login, signup


def clear(window):
    for w in window.winfo_children():
        w.destroy()


def splash_screen(app):
    clear(app)

    title = ctk.CTkLabel(app, text="SNAC Wallet", font=("Arial", 50, "bold"))
    title.pack(pady=120)

    btn = ctk.CTkButton(
        app,
        text="Continue",
        command=lambda: login_screen(app),
        width=230,
        height=50,
        font=("Arial", 20, )
    )
    btn.pack(pady=10)


def login_screen(app):
    clear(app)

    title = ctk.CTkLabel(app, text="Login", font=("Arial", 28, "bold"))
    title.pack(pady=40)

    user = ctk.CTkEntry(app, placeholder_text="Username")
    user.pack(pady=10)

    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*")
    pwd.pack(pady=10)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=10)

    def do_login():
        if verify_login(user.get(), pwd.get()):
            dashboard_screen(app, user.get())
        else:
            msg.configure(text="Invalid credentials ❌")

    ctk.CTkButton(app, text="Login", command=do_login).pack(pady=10)
    ctk.CTkButton(app, text="Signup", command=lambda: signup_screen(app)).pack(pady=5)

def signup_screen(app):
    clear(app)

    title = ctk.CTkLabel(app, text="Signup", font=("Arial", 28, "bold"))
    title.pack(pady=40)

    user = ctk.CTkEntry(app, placeholder_text="Username")
    user.pack(pady=10)

    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*")
    pwd.pack(pady=10)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=10)

    def do_signup():
        if signup(user.get(), pwd.get()):
            msg.configure(text="Account created ✅")
        else:
            msg.configure(text="User already exists ❌")

    ctk.CTkButton(app, text="Create Account", command=do_signup).pack(pady=10)
    ctk.CTkButton(app, text="Back to Login", command=lambda: login_screen(app)).pack(pady=5)

def dashboard_screen(app, username):
    clear(app)

    title = ctk.CTkLabel(app, text=f"Welcome {username}", font=("Arial", 24))
    title.pack(pady=40)

    ctk.CTkLabel(app, text="Balance: ₹0").pack(pady=10)

    ctk.CTkButton(app, text="Logout", command=lambda: splash_screen(app)).pack(pady=20)
