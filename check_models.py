import requests

try:
    response = requests.get("https://subnp.com/api/free/models")
    print(response.json())
except Exception as e:
    print(e)
