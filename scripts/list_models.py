import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("No API Key found")
    exit(1)

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

if response.status_code == 200:
    models = response.json()["data"]
    gemini_models = [m["id"] for m in models if "gemini" in m["id"].lower()]
    print("Available Gemini Models:")
    for m in sorted(gemini_models):
        print(m)
else:
    print(f"Error: {response.status_code} - {response.text}")
