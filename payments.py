import threading 
import time 

from services import get_rate

def ensure_balance(db, role, uid, default_balance=500):
    ref = db.reference(f"users/{role}/{uid}/balance")
    if bal is None
    ref.set(default_balance)
    return default_balance
try:
    return float(bal)
except ():
