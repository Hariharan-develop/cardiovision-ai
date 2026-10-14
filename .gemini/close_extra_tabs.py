import urllib.request
import json

with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    tabs = json.loads(res.read().decode())

for t in tabs:
    t_id = t.get('id')
    url = t.get('url', '')
    if 'localhost:8501' not in url and 'cardiovision_exact_dashboard' not in url:
        try:
            req = urllib.request.Request(f'http://127.0.0.1:9222/json/close/{t_id}')
            with urllib.request.urlopen(req) as resp:
                print(f"Closed tab {t_id} ({url})")
        except Exception as e:
            print(f"Could not close {t_id}: {e}")
