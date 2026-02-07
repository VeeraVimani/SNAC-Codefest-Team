import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")
DB_URL = os.getenv("FIREBASE_DB_URL")
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": DB_URL
})
ref = db.reference("test")
def test_connection():
    ref.set({
        "message": "Snac Wallet Firebase Connected!"
    })
    print(" Firebase Connected and Data Written!")
