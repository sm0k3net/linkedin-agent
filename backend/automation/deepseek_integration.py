# backend/automation/deepseek_integration.py

import requests
from backend.config import Config

def generate_content(prompt, min_words=600, max_words=1200):
    headers = {"Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"}
    data = {
        "prompt": prompt,
        "min_words": min_words,
        "max_words": max_words
    }
    response = requests.post("https://api.deepseek.com/generate", headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("result", "")
    return ""