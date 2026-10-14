import urllib.request
import json

with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    tabs = json.loads(res.read().decode())

print(f"Total tabs: {len(tabs)}")
for i, t in enumerate(tabs):
    print(f"{i}: id={t.get('id')} | title={t.get('title')} | url={t.get('url')[:60]}")
