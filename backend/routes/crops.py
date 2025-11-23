from flask import Blueprint, request, jsonify
from firebase_app import db
from utils.utils import get_uid, resolve_references_one_level
import traceback

crop_bp = Blueprint("crop", __name__)


@crop_bp.get("/")
def get_my_crops():
    uid = get_uid()
    crops = db.collection("crops").where("userId", "==", uid).stream()

    result = []
    for c in crops:
        item = c.to_dict()
        item["id"] = c.id
        result.append(item)

    return jsonify(result)

@crop_bp.post("/")
def create_crop():
    uid = get_uid()
    data = request.json
    data["userId"] = uid

    ref = db.collection("crops").add(data)[1]

    return jsonify({"id": ref.id, **data})

@crop_bp.delete("/<crop_id>")
def delete_crop(crop_id):
    uid = get_uid()

    doc = db.collection("crops").document(crop_id).get()
    if not doc.exists or doc.to_dict().get("userId") != uid:
        return jsonify({"error": "Unauthorized"}), 403

    db.collection("crops").document(crop_id).delete()
    return jsonify({"success": True})