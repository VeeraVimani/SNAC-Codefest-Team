import customtkinter as ctk
from screens import splash_screen

# App theme configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Root window setup
app = ctk.CTk()
app.geometry("900x1000")
app.title("SNAC Wallet")

# Start at the splash screen
splash_screen(app)

# Enter the Tk event loop
app.mainloop()
