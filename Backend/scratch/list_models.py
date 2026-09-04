import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Cannot list models: No API key found in .env")
    exit(1)

print(f"API Key found: Yes (length: {len(api_key)})")
print("Fetching models directly from Google API...\n")

try:
    response = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
    response.raise_for_status()
    data = response.json()
    
    print("Available models:")
    for model in data.get("models", []):
        name = model.get("name")
        methods = model.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            print(f" - {name}")
            
except Exception as e:
    print(f"Error fetching models: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response data: {e.response.text}")
