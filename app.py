import customtkinter as ctk
from auth import verify_login

ctk.set_appearance_mode("dark")
ctk.set_default_colour_theme("blue")

class SnacWalletApp(ctk.CTk):
    def _init_(self):
        def _init_ (self):
            super()._init_()
            self.title("Snac Wallet")
            self.geometry("400x300")
            self.show_lpgin()

#login screen
def show login(self):
self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="
                                   