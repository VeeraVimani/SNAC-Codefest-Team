import time
import threading
from services import get_rate


def ensure_balance(db, role, uid, default_balance=500):
    ref = db.reference(f"users/{role}/{uid}/balance")
    bal = ref.get()
    if bal is None:
        ref.set(default_balance)
        return default_balance
    try:
        return float(bal)
    except Exception:
        ref.set(default_balance)
        return default_balance


def set_balance(db, role, uid, -new_balance):
    db.reference(f"users/{role}/{uid}/balance").set(round(float(new_balance), 2))


def find_user_by_email(db, email):
    users = db.reference("users").get() or {}
    for role, group in users.items():
        for uid, data in group.items():
            if data.get("email") == email:
                return role, uid, data
    return None, None, None


def parse_amount(text):
    try:
        return float(text)
    except Exception:
        return None


def run_conversion(app, amount, target_currency, label):
    if amount is None or amount <= 0:
        label.configure(text="")
        return

    def worker():
        try:
            rate = get_rate("USD", target_currency)
            converted = amount * rate
            app.after(0, lambda: label.configure(text=f"Converted: {converted:.2f} {target_currency}"))
        except Exception:
            app.after(0, lambda: label.configure(text="Conversion failed"))

    threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()


def setup_currency_controls(app, amount_entry, currency_menu, converted_label):
    timer = {"id": None}

    def trigger(_event=None):
        if timer["id"] is not None:
            app.after_cancel(timer["id"])
        timer["id"] = app.after(
            400,
            lambda: run_conversion(
                app,
                parse_amount(amount_entry.get()),
                currency_menu.get(),
                converted_label,
            ),
        )

    amount_entry.bind("<KeyRelease>", trigger)
    currency_menu.configure(command=lambda _v=None: trigger())
    return trigger


def toggle_currency(menu):
    if menu.winfo_ismapped():
        menu.pack_forget()
    else:
        menu.pack(pady=4)


def handle_pay(
    db,
    app,
    current_user,
    current_role,
    current_uid,
    current_balance,
    set_current_balance,
    update_balance_labels,
    show_loading,
    recipient_email,
    amount,
    currency,
    status_label,
    require_reason=False,
    reason_text="",
    category=None,
):
    recipient_email = recipient_email.strip().lower()
    if not recipient_email or amount is None or amount <= 0:
        status_label.configure(text="Enter email and valid amount", text_color="orange")
        return
    if require_reason and not reason_text.strip():
        status_label.configure(text="Reason required", text_color="orange")
        return

    to_role, to_uid, _to_data = find_user_by_email(db, recipient_email)
    if not to_uid:
        status_label.configure(text="User not found", text_color="red")
        return

    sender_balance = ensure_balance(db, current_role, current_uid)
    if sender_balance < amount:
        status_label.configure(text="Insufficient balance", text_color="red")
        return

    receiver_balance = ensure_balance(db, to_role, to_uid)

    payload = {
        "from": current_user,
        "from_role": current_role,
        "to": recipient_email,
        "to_role": to_role,
        "amount_usd": round(amount, 2),
        "currency": currency,
        "timestamp": time.time(),
    }
    if require_reason:
        payload["reason"] = reason_text.strip()
    if category:
        payload["category"] = category

    db.reference("payments").push(payload)

    new_balance = round(sender_balance - amount, 2)
    set_current_balance(new_balance)
    set_balance(db, current_role, current_uid, new_balance)
    set_balance(db, to_role, to_uid, receiver_balance + amount)

    update_balance_labels()
    status_label.configure(text="Payment successful ✔", text_color="green")
    show_loading()


def update_spending_chart(db, current_user, canvas):
    payments = db.reference("payments").get() or {}
    totals = {}
    for _pid, data in payments.items():
        if data.get("from") == current_user and data.get("from_role") == "child":
            category = data.get("category", "Other")
            totals[category] = totals.get(category, 0) + float(data.get("amount_usd", 0))
    canvas.delete("all")
    if not totals:
        canvas.create_text(260, 70, text="No spending yet", fill="white")
        return
    max_amt = max(totals.values()) if totals else 1
    x = 20
    bar_w = 60
    gap = 20
    for cat, amt in sorted(totals.items(), key=lambda x: -x[1])[:6]:
        h = int((amt / max_amt) * 90) + 5
        y0 = 120 - h
        canvas.create_rectangle(x, y0, x + bar_w, 120, fill="#2E86DE", outline="")
        canvas.create_text(x + bar_w / 2, 130, text=cat[:6], fill="white")
        canvas.create_text(x + bar_w / 2, y0 - 8, text=f"${amt:.0f}", fill="white")
        x += bar_w + gap


def refresh_history(db, current_user, current_role, box, direction, category):
    payments = db.reference("payments").get() or {}
    lines = []
    for _pid, data in payments.items():
        is_sent = data.get("from") == current_user
        is_recv = data.get("to") == current_user
        if direction == "Sent" and not is_sent:
            continue
        if direction == "Received" and not is_recv:
            continue
        if direction == "All" and not (is_sent or is_recv):
            continue
        cat = data.get("category", "Other")
        if category != "All" and cat != category:
            continue
        ts = data.get("timestamp", 0)
        try:
            ts_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
        except Exception:
            ts_str = "unknown"
        amount = data.get("amount_usd", 0)
        cur = data.get("currency", "USD")
        to_user = data.get("to", "")
        from_user = data.get("from", "")
        line = f"{ts_str} | {from_user} -> {to_user} | ${amount} {cur} | {cat}"
        lines.append((ts, line))

    lines.sort(key=lambda x: x[0], reverse=True)
    text = "\n".join([l[1] for l in lines]) if lines else "No payments yet"
    box.configure(state="normal")
    box.delete("1.0", "end")
    box.insert("end", text)
    box.configure(state="disabled")
app.main