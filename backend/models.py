# backend/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AgentConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topics = db.Column(db.String, default="")
    behavior = db.Column(db.String, default="")  # JSON string

    @staticmethod
    def get_current():
        config = AgentConfig.query.first()
        if not config:
            config = AgentConfig()
            db.session.add(config)
            db.session.commit()
        return config

    @staticmethod
    def update_from_json(data):
        config = AgentConfig.get_current()
        config.topics = data.get("topics", config.topics)
        config.behavior = data.get("behavior", config.behavior)
        db.session.add(config)
        db.session.commit()

class AgentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String)
    target = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    extra = db.Column(db.String, default="")