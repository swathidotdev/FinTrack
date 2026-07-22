from flask import Flask
from app.db import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key-change-in-production"

    init_db()  # ensure tables exist every time the app starts

    from app.routes import bp
    from app.auth_routes import auth_bp
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp, url_prefix="")  # Auth routes at root level

    return app