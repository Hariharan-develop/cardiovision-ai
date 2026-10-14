import json
import base64
import time
import urllib.request
import websocket
import os
import re

print("Connecting to Chrome CDP...")
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
send_cmd("Runtime.enable")

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
    resp = send_cmd("Runtime.evaluate", {
        "expression": wrapper, "returnByValue": True, "awaitPromise": True
    })
    return resp.get("result", {}).get("result", {}).get("value")

report_html = eval_in_iframe("return win.exportClinicalReport();")
assert report_html and not report_html.startswith('ERROR')
print(f"Got current report HTML: {len(report_html)} bytes")

# Test modifying CSS for footer positioning
# We want to test heights: 275mm, 276mm, 277mm, etc.
for test_height in ["272mm", "274mm", "275mm", "276mm"]:
    # Replace in CSS
    modified_html = report_html.replace(
        "height: 100%;",
        f"height: {test_height} !important; max-height: {test_height} !important; min-height: {test_height} !important;"
    )
    # Also change Confidential Prototype Record to Research Prototype Record
    modified_html = modified_html.replace(
        "Confidential Prototype Record", "Research Prototype Record"
    )

    # Create target tab
    new_target_resp = send_cmd("Target.createTarget", {"url": "about:blank"})
    new_target_id = new_target_resp.get("result", {}).get("targetId")

    with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
        all_tabs = json.loads(res.read().decode())

    tab_target = [t for t in all_tabs if t.get("id") == new_target_id][0]
    tab_ws = websocket.create_connection(tab_target.get("webSocketDebuggerUrl"), timeout=30, suppress_origin=True)

    t_id = 0
    def tab_cmd(method, params=None):
        global t_id
        t_id += 1
        req = {"id": t_id, "method": method}
        if params: req["params"] = params
        tab_ws.send(json.dumps(req))
        while True:
            resp = json.loads(tab_ws.recv())
            if resp.get("id") == t_id: return resp

    tab_cmd("Page.enable")
    tab_cmd("Runtime.enable")
    tab_cmd("Runtime.evaluate", {"expression": f"document.open(); document.write({json.dumps(modified_html)}); document.close();"})
    time.sleep(0.5)

    pdf_resp = tab_cmd("Page.printToPDF", {
        "paperWidth": 8.27, "paperHeight": 11.69,
        "marginTop": 0.39, "marginBottom": 0.39,
        "marginLeft": 0.55, "marginRight": 0.55,
        "printBackground": True, "preferCSSPageSize": True
    })
    pdf_bytes = base64.b64decode(pdf_resp.get("result", {}).get("data"))
    pages = len(re.findall(rb'/Type\s*/Page\b', pdf_bytes))
    print(f"Height {test_height}: Generated PDF size = {len(pdf_bytes)} bytes, Pages = {pages}")

    tab_ws.close()
    send_cmd("Target.closeTarget", {"targetId": new_target_id})

ws.close()
