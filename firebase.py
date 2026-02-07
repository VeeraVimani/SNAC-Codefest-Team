import os
import firebase_admin
from firebase_admin import credentials, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "key.json")

cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://snac-codefest-db-default-rtdb.firebaseio.com/"
})

def get_ref(path):
    return db.reference(path)
