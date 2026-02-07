from datetime import datetime
from firebase import get_ref


def get_user(username):
    return get_ref("users").child(username).get()


def ensure_balance(username, default_balance=500.0):
    ref = get_ref("users").child(username).child("balance")
    bal = ref.get()
    if bal is None:
        ref.set(default_balance)
        return float(default_balance)
    try:
        return float(bal)
    except Exception:
        ref.set(default_balance)
        return float(default_balance)


def set_balance(username, amount):
    get_ref("users").child(username).child("balance").set(round(float(amount), 2))


def record_payment(payload):
    get_ref("payments").push(payload)


def pay_by_username(from_user, to_user, amount):
    if amount <= 0:
        return False, "Amount must be positive"

    sender = get_user(from_user)
    receiver = get_user(to_user)
    if not receiver:
        return False, "Recipient not found"

    sender_bal = ensure_balance(from_user)
    if sender_bal < amount:
        return False, "Insufficient balance"

    receiver_bal = ensure_balance(to_user)

    new_sender = sender_bal - amount
    new_receiver = receiver_bal + amount

    set_balance(from_user, new_sender)
    set_balance(to_user, new_receiver)

    record_payment(
        {
            "from": from_user,
            "to": to_user,
            "amount": round(amount, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return True, "Payment successful"


def get_payments_for_user(username):
    data = get_ref("payments").get() or {}
    items = []
    for _pid, p in data.items():
        if p.get("from") == username or p.get("to") == username:
            items.append(p)
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return items
