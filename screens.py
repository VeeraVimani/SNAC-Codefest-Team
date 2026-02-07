import os
from datetime import datetime
import customtkinter as ctk
import threading
from auth2 import (
    verify_login,
    signup,
    verify_security_answers,
    reset_password,
    get_security_questions,
    get_user_role,
    get_user_profile,
    add_child_to_parent,
)
from PIL import Image, ImageTk, ImageSequence


def clear(w):
    """Remove all child widgets from the given container."""
    for i in w.winfo_children():
        i.destroy()


def add_hover_zoom(btn, width, height, zoom=1.2): #hover efect stuff for buttons
    def on_enter(_e):
        btn.configure(width=int(width * zoom), height=int(height * zoom))

    def on_leave(_e):
        btn.configure(width=width, height=height)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def image_path(name):
    return os.path.join(BASE_DIR, name)


def image_button(app, image_path_value, size, command, zoom=1.12): #image button but like with hover.
   
    base_img = Image.open(image_path_value).resize(size)
    zoom_size = (int(size[0] * zoom), int(size[1] * zoom))
    zoom_img = Image.open(image_path_value).resize(zoom_size)

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


def splash_screen(app): #lading screen with continnue buttonnn
    
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


# loginnnnn
def login_screen(app): #login ui with username password and resett password
    
    clear(app)
    ctk.CTkLabel(app, text="Login", font=("Arial", 28, "bold")).pack(pady=40)
    user = ctk.CTkEntry(app, placeholder_text="Username", font=("Arial", 15), height=30)
    user.pack(pady=10)
    pwd = ctk.CTkEntry(app, placeholder_text="Password", show="*", font=("Arial", 15), height=30)
    pwd.pack(pady=10)
    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=10)

    def do_login():
        if verify_login(user.get(), pwd.get()):
            role = get_user_role(user.get())
            loading_screen(app, user.get(), role)
        else:
            msg.configure(text="Invalid credentials ❌")

    login_btn = image_button(
        app,
        image_path("login.webp"),
        (220, 60),
        command=do_login,
        zoom=1.12,
    )
    login_btn.pack(pady=10)

    signup_btn = image_button(
        app,
        image_path("signup.png"),
        (220, 60),
        command=lambda: signup_screen(app),
        zoom=1.12,
    )
    signup_btn.pack(pady=5)

    forgot_btn = image_button(
        app,
        image_path("resetpassword.png"),
        (220, 60),
        command=lambda: reset_password_screen(app),
        zoom=1.12,
    )
    forgot_btn.pack(pady=5)


# signup stuff
def signup_screen(app): #sign in ui with like different role stuff lkke if u that role then its like that
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

    vendor_frame = ctk.CTkFrame(app, fg_color="transparent")
    vendor_frame.pack(pady=4)

    company_label = ctk.CTkLabel(vendor_frame, text="Company Name (Vendor only)")
    company_entry = ctk.CTkEntry(vendor_frame, placeholder_text="Company Name")

    companies_frame = ctk.CTkFrame(vendor_frame, fg_color="transparent")
    company_entries = []

    def add_company():
        entry = ctk.CTkEntry(companies_frame, placeholder_text="Additional Company")
        entry.pack(pady=4)
        company_entries.append(entry)

    add_company_btn = ctk.CTkButton(vendor_frame, text="Add Another Company", command=add_company, width=220, height=32)

    store_label = ctk.CTkLabel(vendor_frame, text="Store Type (Vendor only)")
    store_menu = ctk.CTkOptionMenu(vendor_frame, values=["Toys", "Entertainment", "Other"])
    store_menu.set("Toys")
    store_other = ctk.CTkEntry(vendor_frame, placeholder_text="If Other, specify")

    def set_vendor_visibility(is_vendor):
        if is_vendor:
            company_label.pack(pady=(6, 2))
            company_entry.pack(pady=4)
            companies_frame.pack(pady=4)
            add_company_btn.pack(pady=4)
            store_label.pack(pady=(6, 2))
            store_menu.pack(pady=4)
            store_other.pack(pady=4)
        else:
            company_label.pack_forget()
            company_entry.pack_forget()
            companies_frame.pack_forget()
            add_company_btn.pack_forget()
            store_label.pack_forget()
            store_menu.pack_forget()
            store_other.pack_forget()

    set_vendor_visibility(False)

    def on_role_change(_value):
        set_vendor_visibility(role_menu.get() == "Vendor")

    role_menu.configure(command=on_role_change)

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

    def do_signup():
        username = user.get().strip()
        password = pwd.get().strip()
        role = role_menu.get()
        dob_value = dob.get().strip()

        if not username or not password:
            msg.configure(text="Username and password required ❌")
            return

        profile = {"dob": dob_value}

        if role == "Parent":
            try:
                dob_date = datetime.strptime(dob_value, "%Y-%m-%d").date()
                age = (datetime.today().date() - dob_date).days // 365
                if age < 18:
                    msg.configure(text="Parent must be 18+ ❌")
                    return
            except Exception:
                msg.configure(text="Invalid DOB format (YYYY-MM-DD) ❌")
                return

        if role == "Vendor":
            company = company_entry.get().strip()
            if not company:
                msg.configure(text="Company name required ❌")
                return
            companies = [company]
            for e in company_entries:
                val = e.get().strip()
                if val:
                    companies.append(val)
            store_type = store_menu.get()
            other = store_other.get().strip()
            if store_type == "Other" and not other:
                msg.configure(text="Please specify store type ❌")
                return
            profile.update(
                {
                    "company_name": company,
                    "companies": companies,
                    "store_type": store_type,
                    "store_other": other,
                }
            )

        a1 = a1_entry.get().strip()
        a2 = a2_entry.get().strip()
        if not a1 or not a2:
            msg.configure(text="Answer both security questions ❌")
            return

        security = {"q1": q1_menu.get(), "a1": a1, "q2": q2_menu.get(), "a2": a2}

        if signup(username, password, role, profile, security):
            msg.configure(text="Account created ✅")
        else:
            msg.configure(text="User already exists ❌")

    create_btn = image_button(
        app,
        image_path("signup.png"),
        (240, 60),
        command=do_signup,
        zoom=1.12,
    )
    create_btn.pack(pady=10)

    back_btn = ctk.CTkButton(
        app,
        text="Back to Login",
        command=lambda: login_screen(app),
        width=200,
        height=50,
    )
    back_btn.pack(pady=5)
    add_hover_zoom(back_btn, 200, 50)


def reset_password_screen(app): #reset password flow and then all that
    
    clear(app)
    ctk.CTkLabel(app, text="Reset Password", font=("Arial", 28, "bold")).pack(pady=30)
    user = ctk.CTkEntry(app, placeholder_text="Email / Username", font=("Arial", 22), height=50)
    user.pack(pady=6)

    q1_label = ctk.CTkLabel(app, text="")
    q1_label.pack(pady=4)
    q1 = ctk.CTkEntry(app, placeholder_text="Answer 1")
    q1.pack(pady=4)

    q2_label = ctk.CTkLabel(app, text="")
    q2_label.pack(pady=4)
    q2 = ctk.CTkEntry(app, placeholder_text="Answer 2")
    q2.pack(pady=4)

    new_pwd = ctk.CTkEntry(app, placeholder_text="New Password", show="*", font=("Arial", 22), height=50)
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

    user.bind("<FocusOut>", load_questions)
    user.bind("<Return>", load_questions)
    reset_btn = image_button(
        app,
        image_path("resetpassword.png"),
        (220, 60),
        command=do_reset,
        zoom=1.12,
    )
    reset_btn.pack(pady=10)
    ctk.CTkButton(app, text="Back to Login", command=lambda: login_screen(app), width=200, height=40).pack(pady=6)


def add_child_screen(app, parent_username, role): #linking the child account to parent
    clear(app)
    ctk.CTkLabel(app, text="Add Child Account", font=("Arial", 28, "bold")).pack(pady=30)
    child_user = ctk.CTkEntry(app, placeholder_text="Child Username", font=("Arial", 18), height=50)
    child_user.pack(pady=6)

    q1_label = ctk.CTkLabel(app, text="")
    q1_label.pack(pady=4)
    a1 = ctk.CTkEntry(app, placeholder_text="Answer 1")
    a1.pack(pady=4)

    q2_label = ctk.CTkLabel(app, text="")
    q2_label.pack(pady=4)
    a2 = ctk.CTkEntry(app, placeholder_text="Answer 2")
    a2.pack(pady=4)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=8)

    def load_questions(_e=None):
        username = child_user.get().strip()
        if not username:
            msg.configure(text="Enter child username ❌")
            return
        questions = get_security_questions(username)
        if not questions:
            msg.configure(text="Child account not found ❌")
            return
        q1_label.configure(text=questions[0])
        q2_label.configure(text=questions[1])
        msg.configure(text="")

    child_user.bind("<FocusOut>", load_questions)
    child_user.bind("<Return>", load_questions)

    def do_add():
        username = child_user.get().strip()
        if not username:
            msg.configure(text="Enter child username ❌")
            return
        if not verify_security_answers(username, a1.get().strip(), a2.get().strip()):
            msg.configure(text="Security answers incorrect ❌")
            return
        add_child_to_parent(parent_username, username)
        msg.configure(text="Child linked ✅")

    ctk.CTkButton(app, text="Add Child", command=do_add, width=200, height=50).pack(pady=10)
    ctk.CTkButton(
        app,
        text="Back",
        command=lambda: dashboard_screen(app, parent_username, role),
        width=200,
        height=40,
    ).pack(pady=6)


def generate_qr_screen(app, username, role): # like generating the qr for vendors andchild
    
    clear(app)
    ctk.CTkLabel(app, text="Generate QR", font=("Arial", 28, "bold")).pack(pady=30)
    ctk.CTkLabel(app, text=f"QR will encode: {username}", font=("Arial", 16)).pack(pady=6)

    qr_label = ctk.CTkLabel(app, text="")
    qr_label.pack(pady=10)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=6)

    def do_generate():
        try:
            import qrcode
        except Exception:
            msg.configure(text="qrcode library not installed ❌")
            return
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(username)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(220, 220))
        qr_label.configure(image=ctk_img)
        qr_label._image = ctk_img
        msg.configure(text="QR generated ✅")

    ctk.CTkButton(app, text="Generate", command=do_generate, width=200, height=50).pack(pady=10)
    ctk.CTkButton(
        app,
        text="Back",
        command=lambda: dashboard_screen(app, username, role),
        width=200,
        height=40,
    ).pack(pady=6)


# gif animationnnn less goo
def loading_screen(app, username, role): #loading animation 
   
    clear(app)
    label = ctk.CTkLabel(app)
    label.pack(fill="both", expand=True)

    im = Image.open(image_path("loading.gif"))
    frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(im)]

    loop_count = 0
    frame_index = 0
    max_loops = 3

    def animate():
        nonlocal frame_index, loop_count
        label.configure(image=frames[frame_index])
        frame_index += 1

        if frame_index >= len(frames):
            frame_index = 0
            loop_count += 1
            if loop_count >= max_loops:
                dashboard_screen(app, username, role)
                return

        app.after(100, animate)

    animate()


# the begining scren after logginn
def dashboard_screen(app, username, role): # this thingy like the dashboard with the buttons to scan qrr and that stuff
    
    clear(app)
    ctk.CTkLabel(app, text=f"Hello, {username} 👋 welcome back", font=("Arial", 28, "bold")).pack(
        pady=80
    )
    ctk.CTkLabel(app, text="Balance: ₹0", font=("Arial", 20)).pack(pady=10)

    def on_qr_detected(data):
        clear(app)
        ctk.CTkLabel(app, text="QR Detected", font=("Arial", 26, "bold")).pack(pady=30)
        ctk.CTkLabel(app, text=data, font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(
            app,
            text="Back",
            command=lambda: dashboard_screen(app, username, role),
            width=200,
            height=50,
        ).pack(pady=20)

    if role != "Parent":
        scan_btn = ctk.CTkButton(
            app,
            text="Scan QR",
            command=lambda: scan_qr(app, on_qr_detected, on_cancel=lambda: dashboard_screen(app, username, role)),
            width=200,
            height=50,
        )
        scan_btn.pack(pady=10)
        add_hover_zoom(scan_btn, 200, 50)

    if role == "Vendor":
        gen_btn = ctk.CTkButton(
            app,
            text="Generate QR",
            command=lambda: generate_qr_screen(app, username, role),
            width=200,
            height=50,
        )
        gen_btn.pack(pady=10)
        add_hover_zoom(gen_btn, 200, 50)

    if role == "Parent":
        add_child_btn = ctk.CTkButton(
            app,
            text="link child account",
            command=lambda: add_child_screen(app, username, role),
            width=200,
            height=50,
        )
        add_child_btn.pack(pady=10)
        add_hover_zoom(add_child_btn, 200, 50)

        profile = get_user_profile(username) or {}
        children = profile.get("children", [])
        children_text = ", ".join(children) if children else "None"
        ctk.CTkLabel(app, text=f"Children: {children_text}", font=("Arial", 16)).pack(pady=10)

    if role == "Child":
        profile = get_user_profile(username) or {}
        parent_name = profile.get("parent", "Not linked")
        ctk.CTkLabel(app, text=f"Parent: {parent_name}", font=("Arial", 16)).pack(pady=10)

    logout_btn = ctk.CTkButton(app, text="Logout", command=lambda: splash_screen(app), width=200, height=50)
    logout_btn.pack(pady=40)
    add_hover_zoom(logout_btn, 200, 50)


def scan_qr(app, on_detected, on_cancel=None): #webcame qr display and scan for qr codes shown
   
    import cv2
    from collections import deque
    try:
        from pyzbar import pyzbar
        use_pyzbar = True
    except Exception:
        pyzbar = None
        use_pyzbar = False
        detector = cv2.QRCodeDetector()

    clear(app)
    status = ctk.CTkLabel(app, text="Point the camera at a QR code", font=("Arial", 16))
    status.pack(pady=10)
    scan_label = ctk.CTkLabel(app)
    scan_label.pack(pady=10)

    frame_queue = deque(maxlen=1)
    stop_flag = {"stop": False}

    def camera_loop():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            app.after(0, lambda: status.configure(text="Error: Cannot open camera"))
            return

        while not stop_flag["stop"]:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (420, 315))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, _ = frame_rgb.shape
            cv2.line(frame_rgb, (0, h // 2), (w, h // 2), (0, 255, 0), 2)

            qr_data = None
            if use_pyzbar:
                decoded_objs = pyzbar.decode(frame_rgb)
                if decoded_objs:
                    qr_data = decoded_objs[0].data.decode("utf-8")
            else:
                data, _points, _ = detector.detectAndDecode(frame_rgb)
                if data:
                    qr_data = data

            if qr_data:
                stop_flag["stop"] = True
                cap.release()
                app.after(0, lambda: on_detected(qr_data))
                return

            frame_queue.append(frame_rgb)

        cap.release()

    def ui_loop():
        if stop_flag["stop"]:
            return
        if frame_queue:
            img = Image.fromarray(frame_queue[-1])
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(420, 315))
            scan_label.configure(image=ctk_img)
            scan_label._image = ctk_img
        app.after(30, ui_loop)

    ctk.CTkButton(
        app,
        text="Cancel",
        command=lambda: (stop_flag.update({"stop": True}), on_cancel() if on_cancel else None),
        width=160,
        height=40,
    ).pack(pady=10)

    threading.Thread(target=camera_loop, daemon=True).start()
    ui_loop()
