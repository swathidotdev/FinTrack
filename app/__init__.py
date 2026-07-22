from flask import Flask
from app.db import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key-change-in-production"

    init_db()

    from app.routes import bp
    from app.auth_routes import auth_bp
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp, url_prefix="")

    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = "0"
        response.headers["Pragma"] = "no-cache"
        return response

    return app