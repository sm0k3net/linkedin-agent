# backend/app.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from backend.config import Config
from backend.routes import bp as routes_bp
from backend.logging_setup import setup_logging

db = SQLAlchemy()
socketio = SocketIO(async_mode="threading")

def create_app():
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app)
    app.register_blueprint(routes_bp)
    setup_logging()
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)