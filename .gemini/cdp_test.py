import json
import urllib.request
import websocket

with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    tabs = json.loads(res.read().decode())

target = None
for t in tabs:
    if 'localhost:8501' in t.get('url', ''):
        target = t
        break

print("Target tab:", target.get('url') if target else "None")
ws_url = target.get('webSocketDebuggerUrl')
print("Connecting to ws:", ws_url)

ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)

req = {
    "id": 1,
    "method": "Runtime.evaluate",
    "params": {
        "expression": "document.title"
    }
}
ws.send(json.dumps(req))
resp = json.loads(ws.recv())
print("Response:", resp)

ws.close()
