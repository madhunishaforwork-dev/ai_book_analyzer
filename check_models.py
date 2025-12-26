
import requests
import re

try:
    api_key = None
    with open(".streamlit/secrets.toml", "r") as f:
        content = f.read()
        match = re.search(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
        if match:
            api_key = match.group(1)

    if not api_key:
        print("No API Key found in secrets.")
        exit()

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        with open("models.txt", "w") as f:
            for m in models:
                if "generateContent" in m.get('supportedGenerationMethods', []):
                    f.write(f"{m['name']}\n")
        print("Models written to models.txt")
    else:
        print(f"Error listing models: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Script error: {e}")
