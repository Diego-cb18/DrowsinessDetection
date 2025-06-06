import requests

try:
    response = requests.get("https://vigiadrowsyapp.duckdns.org/", timeout=5)
    print(response.status_code)
except requests.exceptions.SSLError as e:
    print("SSL ERROR:", e)
except Exception as e:
    print("OTHER ERROR:", e)
