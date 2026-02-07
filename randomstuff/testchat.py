import customtkinter as ctk
import firebase_admin
from firebase_admin import credentials, db
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://snac-codefest-db-default-rtdb.firebaseio.com/'
})

app = ctk.CTk()
app.title("Chat Window")
app.geometry("500x500")

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

# Frame to hold chat display and scrollbar
chat_frame = ctk.CTkFrame(app)
chat_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
chat_frame.grid_rowconfigure(0, weight=1)
chat_frame.grid_columnconfigure(0, weight=1)

scrollbar = ctk.CTkScrollbar(chat_frame, orientation="vertical")
scrollbar.grid(row=0, column=1, sticky="ns", padx=(0,5))

display_box = ctk.CTkTextbox(chat_frame, wrap="word", state="normal", yscrollcommand=scrollbar.set)
display_box.grid(row=0, column=0, sticky="nsew")
scrollbar.configure(command=display_box.yview)
display_box.configure(state="disabled")  # make it read-only

input_frame = ctk.CTkFrame(app)
input_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
input_frame.grid_columnconfigure(0, weight=1)

entry_field = ctk.CTkEntry(input_frame, placeholder_text="Type your message...")
entry_field.grid(row=0, column=0, padx=(0,5), pady=5, sticky="ew")

send_button = ctk.CTkButton(input_frame, text="Send")
send_button.grid(row=0, column=1, pady=5, sticky="ew")

username = "You"

def display_message(user, text):
    display_box.configure(state="normal")
    if user == username:
        display_box.insert(ctk.END, f"{user}: {text}\n", "right")
    else:
        display_box.insert(ctk.END, f"{user}: {text}\n")
    display_box.configure(state="disabled")
    display_box.see(ctk.END)

def send_message(event=None):
    message = entry_field.get().strip()
    if not message:
        return
    display_message(username, message)
    ref = db.reference("/messages")
    ref.push({
        "user": username,
        "text": message
    })
    entry_field.delete(0, ctk.END)
    entry_field.focus_set()

def fetch_messages():
    ref = db.reference("/messages")
    displayed_keys = set()
    while True:
        messages = ref.get() or {}
        for key, msg in messages.items():
            if key not in displayed_keys:
                displayed_keys.add(key)
                if msg["user"] != username:
                    display_message(msg["user"], msg["text"])
        time.sleep(1)

send_button.configure(command=send_message)
entry_field.bind("<Return>", send_message)
entry_field.focus_set()

threading.Thread(target=fetch_messages, daemon=True).start()
app.mainloop()