import customtkinter as ctk
from screens import splash_screen
from auth2 import signup, verify_login

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("900x1000")
app.title("SNAC Wallet")

def login_screen():
    from screens import clear
    clear(app)
    ctk.CTkLabel(app, text="Login Screen", font=("Arial", 30, "bold")).pack(pady=200)

# Pass the login_screen function as the continue_command
splash_screen(app, continue_command=login_screen)

app.mainloop()
