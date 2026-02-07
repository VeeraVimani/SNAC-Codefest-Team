import customtkinter as ctk
from screens_common import clear, image_button, image_path
from screens_auth import login_screen, signup_screen, reset_password_screen
from screens_dashboard import (
    loading_screen,
    dashboard_screen,
    scan_qr,
    payment_screen,
    history_screen,
    group_chat_screen,
    add_child_screen,
    generate_qr_screen,
    group_wallets_screen,
    notifications_screen,
    group_wallet_detail_screen,
    vendor_details_screen,
)


def splash_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="SNAC Wallet", font=("Arial", 50, "bold")).pack(pady=120)

    continue_btn = image_button(
        app,
        image_path("continue.webp"),
        (230, 50),
        command=lambda: login_screen(app),
        zoom=1.12,
    )
    continue_btn.pack(pady=10)

__all__ = [
    "splash_screen",
    "login_screen",
    "signup_screen",
    "reset_password_screen",
    "loading_screen",
    "dashboard_screen",
    "scan_qr",
    "payment_screen",
    "history_screen",
    "group_chat_screen",
    "add_child_screen",
    "generate_qr_screen",
    "group_wallets_screen",
    "notifications_screen",
    "group_wallet_detail_screen",
    "vendor_details_screen",
]
