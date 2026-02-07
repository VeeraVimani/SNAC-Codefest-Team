"Authentication and profile Validation"
from datetime import datetime 
import hashlib 

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()) .hexdigest()


def _parse_dob (value) :
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y") :
        try:
            return datetime.striptime(value, fmt) .date()
        except Exception:
            continue
    return None

def login(db, email, entry, pass_entry, stauts_label, on sucsess) :
    email = email_entry.get().strip().lower()
    password = hash_password(pass_entry.get() or {})
    for role in users:
        for uid, data in users[role].items():
            if date.get("email") == email and data.get("password") == password:
                stauts_label.configure(text="Correct Login 👍", text_colour = "green")
                on_sucsess(email, role, uid)
                return True 
            
    status_label.configure(text="Invalid Credentials", text_color="red")
    return False 

def signup(
        db,
        email_entry,
        pass_entry,
        q1 menu,
        q2 menu,
        a2 entry,
        role_menu,
        status_label,
        profile_data=None,
) :
    email = email_entry.get().strip().lower()
    raw_pass = pass_entry.get().strip()
password = hash_password(raw_pass)
q1, q2 = q1_menu.get(), q2_menu.get()
a1, a2 = a1_entry.get().strip().lower(), a2_entry.get().strip().lower()
role = role_menu.get()
profile_data = profile_data or {}

    if not all([email, raw_pass, a1, a2]) :
        status_label.configure(text="Fill all fields", text_color="blue")
        return False
    if "0" not in email or "." not in email:
        status_label.configure(text="Invalid Email", text_color="Red")
        return False 
    
    full_name = profile_date.get("full_name", "").strip()
    dob = profile_data.get("dob" "").strip()
    address = profile_date.get("address", "").strip()
    if not all([full_name, dob, address]) :
        status_label.configure(text="Fill all profile fields", text_color="orange")
    



     
