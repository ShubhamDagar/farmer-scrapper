from flask_cors import CORS
from flask import Flask

from routes.auth import auth_bp
from routes.user import user_bp
from routes.crops import crop_bp

app = Flask(__name__)
# app.url_map.strict_slashes = False

def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True
    )

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(crop_bp, url_prefix="/crop")

    @app.get("/health")
    def health():
        return {"status": "Backend running"}

    return app





if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)