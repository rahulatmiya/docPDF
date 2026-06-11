import requests
import json

prompt = "A futuristic sneaker ad"

print("Sending POST request to SubNP...")
try:
    response = requests.post(
        "https://subnp.com/api/free/generate",
        json={"prompt": prompt, "model": "magic"},
        stream=True,
        timeout=60
    )
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print("Raw Line:", decoded_line)
            if decoded_line.startswith('data: '):
                data_str = decoded_line[6:]
                try:
                    data = json.loads(data_str)
                    print("Parsed JSON:", data)
                except json.JSONDecodeError:
                    print("Failed to parse JSON.")
                    
except Exception as e:
    print("Request failed:", e)
