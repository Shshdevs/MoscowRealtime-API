import firebase_admin
from firebase_admin import credentials, firestore

from app.shared.config import Settings


def get_firestore_client(settings: Settings):
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred)

    return firestore.client()
