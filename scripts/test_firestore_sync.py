import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import firebase_admin
from firebase_admin import credentials, firestore

def test_firestore():
    cred_path = "serviceAccountKey.json"
    if not os.path.exists(cred_path):
        print(f"[ERROR] Service account file '{cred_path}' not found.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    print("[1] Initialized Firebase Admin SDK successfully.")
    
    try:
        fs = firestore.client()
        print("[2] Attempting to write test token to Cloud Firestore (collection: 'users', doc: 'health_check')...")
        doc_ref = fs.collection("users").document("health_check")
        doc_ref.set({
            "test": True,
            "status": "connected",
            "updatedAt": firestore.SERVER_TIMESTAMP
        })
        print("[SUCCESS] Cloud Firestore is active and writable!")
    except Exception as e:
        print(f"\n[FIRESTORE NOT READY] Cloud Firestore rejected write request with error:")
        print(f"  --> {e}\n")
        print("ACTION REQUIRED:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/project/onfood-8ff37/firestore")
        print("2. Click 'Create database'")
        print("3. Select your location and start mode (Production or Test)")
        print("4. Click 'Enable'")

if __name__ == "__main__":
    test_firestore()
