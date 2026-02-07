import customtkinter as ctk
from auth2 import verify_login, signup
from PIL import Image, ImageTk, ImageSequence

def clear(w):
    for i in w.winfo_children():
        i.destroy()

def add_hover_zoom(btn, width, height, zoom=1.2):
    def on_enter(_e):
        btn.configure(width=int(width * zoom), height=int(height * zoom))

    def on_leave(_e):
        btn.configure(width=width, height=height)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def image_button(app, image_path, size, command, zoom=1.12):
    base_img = Image.open(image_path).resize(size)
    zoom_size = (int(size[0] * zoom), int(size[1] * zoom))
    zoom_img = Image.open(image_path).resize(zoom_size)

    base_photo = ImageTk.PhotoImage(base_img)
    zoom_photo = ImageTk.PhotoImage(zoom_img)

    btn = ctk.CTkButton(
        app,
        image=base_photo,
        text="",
        command=command,
        width=size[0],
        height=size[1],
        fg_color="transparent",
        hover=False,
        border_width=0,
        corner_radius=0,
    )

    btn.image = base_photo
    btn._hover_image = zoom_photo

    def on_enter(_e):
        btn.configure(image=btn._hover_image, width=zoom_size[0], height=zoom_size[1])

    def on_leave(_e):
        btn.configure(image=btn.image, width=size[0], height=size[1])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def splash_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="SNAC Wallet", font=("Arial",50,"bold")).pack(pady=120)

    # continue image logic
    continue_img = Image.open("continue.webp").resize((230,50))
    continue_photo = ImageTk.PhotoImage(continue_img)

    btn = ctk.CTkButton(
        app,
        image=continue_photo,
        text="",
        command=lambda: login_screen(app),
        width=230,
        height=50,
        fg_color="transparent",
        hover=False,
        border_width=0,
        corner_radius=0,
    )
    btn.pack(pady=10)
    btn.image = continue_photo  # the image which we made as button
    add_hover_zoom(btn, 230, 50)

#logginnnnn
def login_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="Login", font=("Arial",28,"bold")).pack(pady=40)
    user = ctk.CTkEntry(app, placeholder_text="Username"); user.pack(pady=10)
    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*"); pwd.pack(pady=10)
    msg = ctk.CTkLabel(app, text=""); msg.pack(pady=10)
    
    def do_login():
        if verify_login(user.get(), pwd.get()): loading_screen(app, user.get())
        else: msg.configure(text="Invalid credentials ❌")

    login_btn = image_button(
        app,
        "login.webp",
        (220, 60),
        command=do_login,
        zoom=1.12,
    )
    login_btn.pack(pady=10)

    signup_btn = image_button(
        app,
        "signup.png",
        (220, 60),
        command=lambda: signup_screen(app),
        zoom=1.12,
    )
    signup_btn.pack(pady=5)

# signup stuff
def signup_screen(app):
    clear(app)
    ctk.CTkLabel(app, text="Signup", font=("Arial",28,"bold")).pack(pady=40)
    user = ctk.CTkEntry(app, placeholder_text="Username"); user.pack(pady=10)
    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*"); pwd.pack(pady=10)
    msg = ctk.CTkLabel(app, text=""); msg.pack(pady=10)
    
    def do_signup():
        if signup(user.get(), pwd.get()): msg.configure(text="Account created ✅")
        else: msg.configure(text="User already exists ❌")

    create_btn = image_button(
        app,
        "signup.png",
        (240, 60),
        command=do_signup,
        zoom=1.12,
    )
    create_btn.pack(pady=10)

    back_btn = ctk.CTkButton(app, text="Back to Login", command=lambda: login_screen(app), width=200, height=50)
    back_btn.pack(pady=5)
    add_hover_zoom(back_btn, 200, 50)

# gif animationnnn less goo
def loading_screen(app, username):
    clear(app)
    label = ctk.CTkLabel(app); label.pack(fill="both", expand=True)

    # playing the giff
    im = Image.open("loading.gif")
    frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(im)]

    loop_count = frame_index = 0
    max_loops = 3  

    def animate():
        nonlocal frame_index, loop_count
        label.configure(image=frames[frame_index])
        frame_index += 1

        if frame_index >= len(frames):
            frame_index = 0
            loop_count += 1
            if loop_count >= max_loops:
                dashboard_screen(app, username)
                return

        app.after(100, animate)  

    animate()

# the begining scren after logginn 
def dashboard_screen(app, username):
    clear(app)
    ctk.CTkLabel(app, text=f"Hello, {username} 👋 welcome back", font=("Arial",28,"bold")).pack(pady=80)
    ctk.CTkLabel(app, text="Balance: ₹0", font=("Arial",20)).pack(pady=10)

    logout_btn = ctk.CTkButton(app, text="Logout", command=lambda: splash_screen(app), width=200, height=50)
    logout_btn.pack(pady=40)
    add_hover_zoom(logout_btn, 200, 50)
