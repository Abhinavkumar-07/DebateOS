import os
import sys
import json
import urllib.request
from config import settings

print(f"API KEY IN CONFIG: {settings.OPENAI_API_KEY[:15]}...")

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Say hello"}]
}

req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers)

try:
    with urllib.request.urlopen(req) as response:
        result = response.read().decode("utf-8")
        print("SUCCESS:")
        print(result)
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code} {e.reason}")
    print("DETAILS:", e.read().decode("utf-8"))
except Exception as e:
    print(f"OTHER ERROR: {e}")
