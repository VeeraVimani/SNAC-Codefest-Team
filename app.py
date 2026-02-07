import customtkinter as ctk
from screens import splash_screen
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("900x1000")
app.title("SNAC Wallet")
splash_screen(app)
app.mainloop()
