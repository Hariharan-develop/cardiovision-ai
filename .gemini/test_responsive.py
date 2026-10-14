import json
import base64
import time
import urllib.request
import websocket
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    tabs = json.loads(res.read().decode())

target = None
for t in tabs:
    if 'localhost:8501' in t.get('url', ''):
        target = t
        break

ws_url = target.get('webSocketDebuggerUrl')
ws = websocket.create_connection(ws_url, timeout=30, suppress_origin=True)

msg_id = 0
def send_cmd(method, params=None):
    global msg_id
    msg_id += 1
    req = {"id": msg_id, "method": method}
    if params:
        req["params"] = params
    ws.send(json.dumps(req))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == msg_id:
            return resp

send_cmd("Page.enable")
send_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 820,
    "height": 1080,
    "deviceScaleFactor": 1,
    "mobile": False
})
time.sleep(0.8)

artifact_dir = "C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779"
resp = send_cmd("Page.captureScreenshot", {"format": "png"})
data = resp.get("result", {}).get("data")
if data:
    with open(os.path.join(artifact_dir, "results_screen_tablet.png"), "wb") as f:
        f.write(base64.b64decode(data))
    print("Tablet screenshot saved")

# Mobile width (414px)
send_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 414,
    "height": 896,
    "deviceScaleFactor": 1,
    "mobile": True
})
time.sleep(0.8)

resp = send_cmd("Page.captureScreenshot", {"format": "png"})
data = resp.get("result", {}).get("data")
if data:
    with open(os.path.join(artifact_dir, "results_screen_mobile.png"), "wb") as f:
        f.write(base64.b64decode(data))
    print("Mobile screenshot saved")

# Reset viewport back to desktop
send_cmd("Emulation.clearDeviceMetricsOverride")
time.sleep(0.5)

ws.close()
print("Responsive checks complete")
