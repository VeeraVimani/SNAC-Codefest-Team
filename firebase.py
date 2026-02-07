import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("key.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://snac-codefest-db-default-rtdb.firebaseio.com/"
})

def get_ref(path):
    return db.reference(path)
