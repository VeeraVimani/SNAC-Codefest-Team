from datetime import datetime
import threading
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
from auth2 import get_user_profile, add_child_to_parent, verify_security_answers, get_security_questions
from payments import ensure_balance, pay_by_username, get_payments_for_user
from firebase import get_ref
from screens_common import clear, add_hover_zoom, image_path


def loading_screen(app, username, role):
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


def dashboard_screen(app, username, role):
    clear(app)
    balance = ensure_balance(username, default_balance=500.0)
    if balance == 0:
        from payments import set_balance
        set_balance(username, 500.0)
        balance = 500.0

    ctk.CTkLabel(app, text="Balance", font=("Arial", 14)).pack(pady=(18, 2))
    ctk.CTkLabel(app, text=f"₹{balance:.2f}", font=("Arial", 32, "bold")).pack(pady=(0, 6))
    ctk.CTkLabel(app, text=f"{username}", font=("Arial", 14)).pack(pady=(0, 14))

    actions = ctk.CTkFrame(app, width=520, height=520, corner_radius=18)
    actions.pack(pady=10)
    actions.pack_propagate(False)
    ctk.CTkLabel(actions, text="Actions", font=("Arial", 18, "bold")).pack(pady=(18, 12))

    def on_qr_detected(data):
        clear(app)
        ctk.CTkLabel(app, text="QR Detected", font=("Arial", 26, "bold")).pack(pady=30)
        ctk.CTkLabel(app, text=data, font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=50).pack(pady=20)

    if role != "Parent":
        scan_btn = ctk.CTkButton(actions, text="Scan QR", command=lambda: scan_qr(app, on_qr_detected, on_cancel=lambda: dashboard_screen(app, username, role)), width=360, height=54)
        scan_btn.pack(pady=8)
        add_hover_zoom(scan_btn, 360, 54)

    if role == "Vendor":
        gen_btn = ctk.CTkButton(actions, text="Generate QR", command=lambda: generate_qr_screen(app, username, role), width=360, height=54)
        gen_btn.pack(pady=8)
        add_hover_zoom(gen_btn, 360, 54)

    if role in ("Child", "Vendor"):
        pay_btn = ctk.CTkButton(actions, text="Pay by Username", command=lambda: payment_screen(app, username, role), width=360, height=54)
        pay_btn.pack(pady=8)
        add_hover_zoom(pay_btn, 360, 54)

    history_btn = ctk.CTkButton(actions, text="Transaction History", command=lambda: history_screen(app, username, role), width=360, height=54)
    history_btn.pack(pady=8)
    add_hover_zoom(history_btn, 360, 54)

    chat_btn = ctk.CTkButton(actions, text="Group Chat", command=lambda: group_chat_screen(app, username, role), width=360, height=54)
    chat_btn.pack(pady=8)
    add_hover_zoom(chat_btn, 360, 54)

    if role == "Parent":
        add_child_btn = ctk.CTkButton(actions, text="Link Child Account", command=lambda: add_child_screen(app, username, role), width=360, height=54)
        add_child_btn.pack(pady=8)
        add_hover_zoom(add_child_btn, 360, 54)

        profile = get_user_profile(username) or {}
        children = profile.get("children", [])
        children_text = ", ".join(children) if children else "None"
        ctk.CTkLabel(actions, text=f"Children: {children_text}", font=("Arial", 14)).pack(pady=(10, 0))

    if role == "Child":
        profile = get_user_profile(username) or {}
        parent_name = profile.get("parent", "Not linked")
        ctk.CTkLabel(actions, text=f"Parent: {parent_name}", font=("Arial", 14)).pack(pady=(10, 0))

    group_btn = ctk.CTkButton(actions, text="Group Wallets", command=lambda: group_wallets_screen(app, username, role), width=360, height=54)
    group_btn.pack(pady=8)
    add_hover_zoom(group_btn, 360, 54)

    notif_btn = ctk.CTkButton(actions, text="Notifications", command=lambda: notifications_screen(app, username, role), width=360, height=54)
    notif_btn.pack(pady=8)
    add_hover_zoom(notif_btn, 360, 54)

    from screens import splash_screen
    logout_btn = ctk.CTkButton(app, text="Logout", command=lambda: splash_screen(app), width=360, height=54)
    logout_btn.pack(pady=18)
    add_hover_zoom(logout_btn, 360, 54)


def scan_qr(app, on_detected, on_cancel=None):
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

    ctk.CTkButton(app, text="Cancel", command=lambda: (stop_flag.update({"stop": True}), on_cancel() if on_cancel else None), width=160, height=40).pack(pady=10)

    threading.Thread(target=camera_loop, daemon=True).start()
    ui_loop()


def payment_screen(app, from_user, role):
    clear(app)
    ctk.CTkLabel(app, text="Make Payment", font=("Arial", 28, "bold")).pack(pady=(24, 8))
    ctk.CTkLabel(app, text="Send money using a username", font=("Arial", 13)).pack(pady=(0, 14))

    card = ctk.CTkFrame(app, width=520, height=360, corner_radius=18)
    card.pack(pady=10)
    card.pack_propagate(False)

    ctk.CTkLabel(card, text="Payment Details", font=("Arial", 16, "bold")).pack(pady=(18, 10))

    to_entry = ctk.CTkEntry(card, placeholder_text="Recipient Username", font=("Arial", 18), height=48, width=360)
    to_entry.pack(pady=8)

    amount_entry = ctk.CTkEntry(card, placeholder_text="Amount (₹)", font=("Arial", 18), height=48, width=360)
    amount_entry.pack(pady=8)

    msg = ctk.CTkLabel(card, text="")
    msg.pack(pady=10)

    def do_pay():
        to_user = to_entry.get().strip()
        try:
            amount = float(amount_entry.get().strip())
        except Exception:
            msg.configure(text="Enter a valid amount ❌")
            return
        if not to_user:
            msg.configure(text="Recipient required ❌")
            return
        ok, text = pay_by_username(from_user, to_user, amount)
        msg.configure(text=("✅ " + text) if ok else ("❌ " + text))
        if ok:
            payment_success_screen(app, from_user, role, to_user, amount)

    ctk.CTkButton(card, text="Pay", command=do_pay, width=240, height=50).pack(pady=10)
    ctk.CTkButton(card, text="Back", command=lambda: dashboard_screen(app, from_user, role), width=240, height=40).pack(pady=6)


def payment_success_screen(app, from_user, role, to_user, amount):
    clear(app)
    ctk.CTkLabel(app, text="Payment Success", font=("Arial", 28, "bold")).pack(pady=(24, 8))
    ctk.CTkLabel(app, text=f"Sent ₹{amount:.2f} to {to_user}", font=("Arial", 14)).pack(pady=(0, 14))

    label = ctk.CTkLabel(app)
    label.pack(pady=10)

    try:
        import subprocess
        audio_path = image_path("payment.mp3")
        subprocess.Popen(["afplay", audio_path])
    except Exception:
        pass

    try:
        im = Image.open(image_path("coins.gif"))
        frames = [ImageTk.PhotoImage(f.copy().convert("RGBA")) for f in ImageSequence.Iterator(im)]
    except Exception:
        frames = []

    frame_index = 0
    max_loops = 2
    loop_count = 0

    def animate():
        nonlocal frame_index, loop_count
        if frames:
            label.configure(image=frames[frame_index])
            frame_index += 1
            if frame_index >= len(frames):
                frame_index = 0
                loop_count += 1
        if loop_count >= max_loops:
            dashboard_screen(app, from_user, role)
            return
        app.after(80, animate)

    animate()


def history_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Transaction History", font=("Arial", 28, "bold")).pack(pady=20)

    box = ctk.CTkTextbox(app, width=560, height=360)
    box.pack(pady=10)
    box.configure(state="disabled")

    items = get_payments_for_user(username)
    lines = []
    for p in items:
        direction = "Sent" if p.get("from") == username else "Received"
        other = p.get("to") if direction == "Sent" else p.get("from")
        amt = p.get("amount", 0)
        ts = p.get("timestamp", "")
        lines.append(f"{ts} | {direction} | {other} | ₹{amt}")
    text = "\n".join(lines) if lines else "No transactions yet"

    box.configure(state="normal")
    box.insert("end", text)
    box.configure(state="disabled")

    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=40).pack(pady=6)


def group_chat_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Group Chat", font=("Arial", 28, "bold")).pack(pady=20)

    chat_box = ctk.CTkTextbox(app, width=520, height=320)
    chat_box.pack(pady=10)
    chat_box.configure(state="disabled")

    msg_entry = ctk.CTkEntry(app, placeholder_text="Type a message...", font=("Arial", 16), height=44)
    msg_entry.pack(pady=6)

    last_ids = {"seen": set()}

    def fetch_messages():
        try:
            data = get_ref("chat/group").get() or {}
        except Exception:
            return []
        items = []
        for mid, msg in data.items():
            ts = msg.get("ts", "")
            items.append((ts, mid, msg))
        items.sort(key=lambda x: x[0])
        return items

    def render():
        items = fetch_messages()
        new_lines = []
        for _ts, mid, msg in items:
            if mid in last_ids["seen"]:
                continue
            last_ids["seen"].add(mid)
            line = f"{msg.get('user','')}: {msg.get('text','')}"
            new_lines.append(line)
        if new_lines:
            chat_box.configure(state="normal")
            chat_box.insert("end", "\n".join(new_lines) + "\n")
            chat_box.configure(state="disabled")
            chat_box.see("end")
        app.after(1500, render)

    def send_msg():
        text = msg_entry.get().strip()
        if not text:
            return
        get_ref("chat/group").push({"user": username, "text": text, "ts": datetime.utcnow().isoformat()})
        msg_entry.delete(0, "end")

    ctk.CTkButton(app, text="Send", command=send_msg, width=200, height=44).pack(pady=6)
    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=40).pack(pady=6)

    render()


def add_child_screen(app, parent_username, role):
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
    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, parent_username, role), width=200, height=40).pack(pady=6)


def generate_qr_screen(app, username, role):
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
    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=40).pack(pady=6)


def group_wallets_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Group Wallets", font=("Arial", 28, "bold")).pack(pady=(20, 6))
    ctk.CTkLabel(app, text="Create, join, and manage shared balances", font=("Arial", 13)).pack(pady=(0, 12))

    list_card = ctk.CTkFrame(app, width=560, height=300, corner_radius=16)
    list_card.pack(pady=10)
    list_card.pack_propagate(False)

    list_box = ctk.CTkTextbox(list_card, width=520, height=240)
    list_box.pack(pady=18)
    list_box.configure(state="disabled")

    groups = get_ref("group_wallets").get() or {}
    user_groups = []
    for gid, g in groups.items():
        members = g.get("members", {}) or {}
        if members.get(username):
            user_groups.append((gid, g))

    list_box.configure(state="normal")
    if user_groups:
        for gid, g in user_groups:
            list_box.insert("end", f"{g.get('name','Group')} | Balance ₹{g.get('balance',0)} | id: {gid}\n")
    else:
        list_box.insert("end", "No group wallets yet")
    list_box.configure(state="disabled")

    ctk.CTkButton(app, text="Create Group Wallet", command=lambda: create_group_wallet_screen(app, username, role), width=280, height=50).pack(pady=8)
    ctk.CTkButton(app, text="Open Group by ID", command=lambda: open_group_by_id_screen(app, username, role), width=280, height=50).pack(pady=6)
    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=40).pack(pady=6)


def open_group_by_id_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Open Group", font=("Arial", 26, "bold")).pack(pady=20)
    gid_entry = ctk.CTkEntry(app, placeholder_text="Group ID", font=("Arial", 16), height=44, width=320)
    gid_entry.pack(pady=8)
    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=6)

    def open_group():
        gid = gid_entry.get().strip()
        if not gid:
            msg.configure(text="Enter group id ❌")
            return
        g = get_ref("group_wallets").child(gid).get()
        if not g:
            msg.configure(text="Group not found ❌")
            return
        members = g.get("members", {}) or {}
        if not members.get(username):
            msg.configure(text="You are not a member ❌")
            return
        group_wallet_detail_screen(app, username, role, gid)

    ctk.CTkButton(app, text="Open", command=open_group, width=200, height=44).pack(pady=8)
    ctk.CTkButton(app, text="Back", command=lambda: group_wallets_screen(app, username, role), width=200, height=40).pack(pady=6)


def create_group_wallet_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Create Group Wallet", font=("Arial", 28, "bold")).pack(pady=20)

    name_entry = ctk.CTkEntry(app, placeholder_text="Group Name", font=("Arial", 16), height=44, width=360)
    name_entry.pack(pady=8)
    member_entry = ctk.CTkEntry(app, placeholder_text="Invite Username", font=("Arial", 16), height=44, width=360)
    member_entry.pack(pady=8)
    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=6)

    def create_and_invite():
        name = name_entry.get().strip() or "Group Wallet"
        invite_user = member_entry.get().strip()
        gid_ref = get_ref("group_wallets").push({"name": name, "owner": username, "balance": 0, "members": {username: True}})
        gid = gid_ref.key
        if invite_user:
            get_ref("group_requests").child(invite_user).push({"from": username, "group_id": gid, "group_name": name, "ts": datetime.utcnow().isoformat()})
            msg.configure(text=f"Invite sent to {invite_user} ✅")
        else:
            msg.configure(text="Group created ✅")

    ctk.CTkButton(app, text="Create", command=create_and_invite, width=220, height=44).pack(pady=8)
    ctk.CTkButton(app, text="Back", command=lambda: group_wallets_screen(app, username, role), width=200, height=40).pack(pady=6)


def notifications_screen(app, username, role):
    clear(app)
    ctk.CTkLabel(app, text="Notifications", font=("Arial", 28, "bold")).pack(pady=20)

    requests = get_ref("group_requests").child(username).get() or {}
    items = list(requests.items())

    if not items:
        ctk.CTkLabel(app, text="No requests", font=("Arial", 14)).pack(pady=10)
    else:
        for rid, req in items:
            row = ctk.CTkFrame(app, corner_radius=12)
            row.pack(pady=6, padx=20, fill="x")
            text = f"{req.get('from')} invited you to {req.get('group_name')}"
            ctk.CTkLabel(row, text=text, font=("Arial", 14)).pack(side="left", padx=10, pady=8)

            def accept(req=req, rid=rid):
                gid = req.get("group_id")
                get_ref("group_wallets").child(gid).child("members").child(username).set(True)
                get_ref("group_requests").child(username).child(rid).delete()
                notifications_screen(app, username, role)

            def decline(rid=rid):
                get_ref("group_requests").child(username).child(rid).delete()
                notifications_screen(app, username, role)

            ctk.CTkButton(row, text="Accept", command=accept, width=90, height=32).pack(side="right", padx=6)
            ctk.CTkButton(row, text="Decline", command=decline, width=90, height=32).pack(side="right", padx=6)

    ctk.CTkButton(app, text="Back", command=lambda: dashboard_screen(app, username, role), width=200, height=40).pack(pady=10)


def group_wallet_detail_screen(app, username, role, group_id):
    clear(app)
    g = get_ref("group_wallets").child(group_id).get() or {}
    name = g.get("name", "Group Wallet")
    balance = float(g.get("balance", 0))
    members = g.get("members", {}) or {}

    ctk.CTkLabel(app, text=name, font=("Arial", 28, "bold")).pack(pady=(20, 6))
    ctk.CTkLabel(app, text=f"Group Balance", font=("Arial", 13)).pack(pady=(0, 2))
    ctk.CTkLabel(app, text=f"₹{balance:.2f}", font=("Arial", 24, "bold")).pack(pady=(0, 10))

    members_card = ctk.CTkFrame(app, width=560, height=160, corner_radius=16)
    members_card.pack(pady=10)
    members_card.pack_propagate(False)
    ctk.CTkLabel(members_card, text="Members", font=("Arial", 14, "bold")).pack(pady=(12, 6))
    members_text = ", ".join(members.keys()) if members else "None"
    ctk.CTkLabel(members_card, text=members_text, font=("Arial", 13)).pack(pady=(0, 10))

    add_card = ctk.CTkFrame(app, width=560, height=140, corner_radius=16)
    add_card.pack(pady=10)
    add_card.pack_propagate(False)
    ctk.CTkLabel(add_card, text="Add Money", font=("Arial", 14, "bold")).pack(pady=(12, 6))
    amt_entry = ctk.CTkEntry(add_card, placeholder_text="Amount", font=("Arial", 16), height=44, width=280)
    amt_entry.pack(pady=6)
    msg = ctk.CTkLabel(add_card, text="")
    msg.pack(pady=4)

    def add_money():
        try:
            amt = float(amt_entry.get().strip())
        except Exception:
            msg.configure(text="Enter a valid amount ❌")
            return
        new_bal = balance + amt
        get_ref("group_wallets").child(group_id).child("balance").set(round(new_bal, 2))
        msg.configure(text="Added ✅")
        group_wallet_detail_screen(app, username, role, group_id)

    ctk.CTkButton(app, text="Add Money", command=add_money, width=220, height=44).pack(pady=8)
    ctk.CTkButton(app, text="Back", command=lambda: group_wallets_screen(app, username, role), width=200, height=40).pack(pady=6)


def vendor_details_screen(app, username, password, role, profile, security):
    clear(app)
    ctk.CTkLabel(app, text="Vendor Details", font=("Arial", 28, "bold")).pack(pady=20)

    company_label = ctk.CTkLabel(app, text="Company Name")
    company_label.pack(pady=(6, 2))
    company_entry = ctk.CTkEntry(app, placeholder_text="Company Name")
    company_entry.pack(pady=4)

    companies_frame = ctk.CTkFrame(app, fg_color="transparent")
    companies_frame.pack(pady=4)
    company_entries = []

    def add_company():
        entry = ctk.CTkEntry(companies_frame, placeholder_text="Additional Company")
        entry.pack(pady=4)
        company_entries.append(entry)

    add_company_btn = ctk.CTkButton(app, text="Add Another Company", command=add_company, width=220, height=32)
    add_company_btn.pack(pady=6)

    store_label = ctk.CTkLabel(app, text="Store Type")
    store_label.pack(pady=(6, 2))
    store_menu = ctk.CTkOptionMenu(app, values=["Toys", "Entertainment", "Other"])
    store_menu.set("Toys")
    store_menu.pack(pady=4)
    store_other = ctk.CTkEntry(app, placeholder_text="If Other, specify")
    store_other.pack(pady=4)

    msg = ctk.CTkLabel(app, text="")
    msg.pack(pady=8)

    def do_vendor_signup():
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

        profile.update({"company_name": company, "companies": companies, "store_type": store_type, "store_other": other})

        from auth2 import signup
        if signup(username, password, role, profile, security):
            msg.configure(text="Account created ✅")
        else:
            msg.configure(text="User already exists ❌")

    from screens_common import image_button
    from screens_auth import login_screen
    image_button(app, image_path("signup.png"), (240, 60), command=do_vendor_signup, zoom=1.12).pack(pady=10)
    ctk.CTkButton(app, text="Back", command=lambda: login_screen(app), width=200, height=40).pack(pady=6)
