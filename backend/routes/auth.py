from flask import Blueprint, request, jsonify
import requests
from config import API_KEY
from firebase_app import auth
import traceback

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/send-otp")
def send_otp():
    try:
        data = request.json
        phone = data.get("phone")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode?key={API_KEY}"

        payload = {
            "phoneNumber": phone
        }

        res = requests.post(url, json=payload)
        return jsonify(res.json())

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@auth_bp.post("/verify-otp")
def verify_otp():
    try:
        data = request.json
        session = data.get("sessionInfo")
        code = data.get("code")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPhoneNumber?key={API_KEY}"

        payload = {
            "sessionInfo": session,
            "code": code
        }

        res = requests.post(url, json=payload)
        r = res.json()

        if "localId" not in r:
            return jsonify({"error": "Invalid OTP"}), 400

        uid = r["localId"]
        custom_token = auth.create_custom_token(uid).decode() #used for authorization

        return jsonify({
            "uid": uid,
            "idToken": r.get("idToken"),
            "customToken": custom_token
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
