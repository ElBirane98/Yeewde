import json
import urllib.request

url = "http://127.0.0.1:8000/health"
with urllib.request.urlopen(url, timeout=10) as response:
    body = response.read().decode("utf-8")
    print(body)
    payload = json.loads(body)
    assert payload.get("status") == "ok", payload
