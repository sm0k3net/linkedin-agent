# backend/automation/deepseek_integration.py

import requests
from backend.config import Config

def generate_content(prompt):
    headers = {"Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"}
    data = {"prompt": prompt}
    response = requests.post("https://api.deepseek.com/generate", headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("result", "")
    return ""