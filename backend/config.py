# backend/config.py

import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///linkedin_agent.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key")
    LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD", "")