from flask import Blueprint, request, jsonify
from firebase_app import db
from utils.utils import get_uid, resolve_references_one_level
import traceback

user_bp = Blueprint("user", __name__)


@user_bp.post("/signup")
def signup():
    try:
        data = request.json
        uid = data.get("uid")

        user_data = {
            "name": data.get("name"),
            "phone": data.get("number"),
            "aadharNumber": data.get("aadhar"),
            "address": data.get("address"),
            "type": data.get("type"),
        }


        db.collection("users").document(uid).set(user_data)

        return jsonify({"message": "Signup successful", "user": {**user_data, "uid": uid}})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@user_bp.get("/profile")
def profile():
    uid = get_uid()

    user = db.collection("users").document(uid).get()
    return jsonify({"user": resolve_references_one_level(user.to_dict())})


@user_bp.post("/check-user")
def check_user():
    phone = request.json.get("phone")
    query = db.collection("users").where("phone", "==", phone).get()

    if query:
        return jsonify({"exists": True})
    return jsonify({"exists": False})