from flask import Flask
from app.db import init_db


def create_app():
    app = Flask(__name__)

    init_db()  # ensure tables exist every time the app starts

    from app.routes import bp
    app.register_blueprint(bp)

    return app