from firebase_admin import auth
from flask import request, abort
from firebase_admin import firestore

def get_uid():
    header = request.headers.get("Authorization")
    if not header:
        abort(401, description="Missing Authorization header")
    token = header.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except:
        abort(401, description="Invalid or expired token")


def resolve_references_one_level(data):
    for key, value in data.items():
        if isinstance(value, firestore.DocumentReference):
            data[key] = value.path
        
        elif isinstance(value, list) and value and \
                isinstance(value[0], firestore.DocumentReference):
            
            data[key] = [ref.path for ref in value]
    
    return data