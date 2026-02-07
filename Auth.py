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
        return False 
dob_date = _parse_dob(dob)
if not dob_date:
    status_label.configure(text="DOB format invalid (YYYY-MM-DD ",
text_color = "red") 
    return False 
if role == "parent":
    today = datetime.today() .date()
    age = (today - dob_date) .days // 365
    if age < 18
       status_label.configure(text="Parent Must be 18 or above", text_color = "red"):
       return False 
    
    company_name = profile_data.get("compamy_name", "").strip()
    companies = profile_data.get("comapnies", [])
    store_type = profile_data.get("store_type", "").strip()


    store_other = profile_data.get("store_other", "").strip()
    if role =="vendor":
        if not company_name:
            status_label.configure(text="Company name required", text_color="orange")
            return False
        if store_type:
            status_label.configure(text="Store type required", text_color="orange")
            return False 
        if store_type == "Other", and not store_other:
            status_label.congfigure(text="Enter Store Type", text_color="orange")
            return False 
        
        users = db.reference(f"users/{role}").get() or ()
        if any(u.get("email") == email for u in users.values()):
            return False 
        
    uid = email.replace("@", "_").replace(".", "_")
    user_payload = {
        "email": email,
        "password": password,
        "security": {
           "q1": {"question": q1, "answer": a1},
           "q2": {"question": q2, "answer": a2},
       },
       "profile": {
           "full_name": full_name,
           "dob": dob,
           "address": address,
       },
   }
   if role == "vendor":
       company_list = [company_name] + [c for c in companies if c]
       user_payload["profile"]["company_name"] = company_name
       user_payload["profile"]["companies"] = company_list
       user_payload["profile"]["store_type"] = store_type
       user_payload["profile"]["store_other"] = store_other


     db.reference(f"users/{role}/{uid}").set(user_payload)
        status_label.configure(text="Account created ✔", text_color="green")
        return True




def find_account(db, email_entry, q1_label, q2_label, status_label, found_user):
   email = email_entry.get().strip().lower()
   users = db.reference("users/parent").get() or {}
   for uid, data in users.items():
       if data.get("email") == email:
           found_user.clear()
           found_user["uid"] = uid
           found_user["security"] = data["security"]
           q1_label.configure(text=data["security"]["q1"]["question"])
           q2_label.configure(text=data["security"]["q2"]["question"])
           status_label.configure(text="")
           return True


     status_label.configure(text="Email not found", text_color="red")
   return False




def reset_password(db, a1_entry, a2_entry, new_pass_entry, status_label, found_user):
   a1 = a1_entry.get().strip().lower()
   a2 = a2_entry.get().strip().lower()
   new_pass = hash_password(new_pass_entry.get().strip())
   sec = found_user.get("security")
   if not sec:
       return False


   if a1 == sec["q1"]["answer"] and a2 == sec["q2"]["answer"]:
       db.reference(f"users/parent/{found_user['uid']}/password").set(new_pass)
       status_label.configure(text="Password reset ✔", text_color="green")
       return True


   status_label.configure(text="Wrong answers", text_color="red")
   return False




    }




     
