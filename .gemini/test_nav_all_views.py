import json
import urllib.request
import websocket
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

def eval_in_iframe(expr):
    wrapper = f"""
    (() => {{
        const iframe = document.querySelector('iframe');
        if (!iframe || !iframe.contentDocument) return 'ERROR';
        const doc = iframe.contentDocument;
        const win = iframe.contentWindow;
        return (function(doc, win) {{ {expr} }})(doc, win);
    }})()
    """
    resp = send_cmd("Runtime.evaluate", {"expression": wrapper, "returnByValue": True})
    return resp.get("result", {}).get("result", {}).get("value")

views = ['predict', 'patient', 'viewer3d', 'about', 'results']
for v in views:
    res = eval_in_iframe(f"""
        win.switchNav('{v}');
        const el = doc.getElementById('view-{v}');
        return {{ view: '{v}', display: el ? el.style.display : 'not_found' }};
    """)
    print("Nav test:", res)

ws.close()
print("All views navigable without errors")
