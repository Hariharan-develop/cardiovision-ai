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

assert target, "No localhost:8501 tab"
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
print(f"Retrieved report HTML: {len(report_html)} bytes")

# Test heights from 270mm to 276mm
results = []
for h in ["268mm", "270mm", "272mm", "274mm", "275mm"]:
    css_override = f"""
    @media print {{
      html, body {{ margin: 0 !important; padding: 0 !important; background: #fff !important; }}
      .reportSheet {{
        width: 100% !important;
        height: {h} !important;
        max-height: {h} !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
      }}
      .page-2 {{
        page-break-before: always !important;
        break-before: page !important;
      }}
      .noPrint, .noPrintBar {{ display: none !important; }}
    }}
    """
    # inject into report_html
    test_html = report_html.replace("</style>", f"{css_override}</style>")
    test_html = test_html.replace("Confidential Prototype Record", "Research Prototype Record")

    # Create target tab
    new_t = send_cmd("Target.createTarget", {"url": "about:blank"})
    t_id = new_t.get("result", {}).get("targetId")

    with urllib.request.urlopen('http://127.0.0.1:9222/json') as r:
        tabs_list = json.loads(r.read().decode())
    target_tab = [x for x in tabs_list if x.get("id") == t_id][0]

    tab_ws = websocket.create_connection(target_tab.get("webSocketDebuggerUrl"), timeout=30, suppress_origin=True)
    tab_msg_id = 0
    def t_cmd(m, p=None):
        global tab_msg_id
        tab_msg_id += 1
        q = {"id": tab_msg_id, "method": m}
        if p: q["params"] = p
        tab_ws.send(json.dumps(q))
        while True:
            res_obj = json.loads(tab_ws.recv())
            if res_obj.get("id") == tab_msg_id: return res_obj

    t_cmd("Page.enable")
    t_cmd("Runtime.enable")
    t_cmd("Runtime.evaluate", {"expression": f"document.open(); document.write({json.dumps(test_html)}); document.close();"})
    time.sleep(0.5)

    pdf_res = t_cmd("Page.printToPDF", {
        "paperWidth": 8.27, "paperHeight": 11.69,
        "marginTop": 0.39, "marginBottom": 0.39,
        "marginLeft": 0.55, "marginRight": 0.55,
        "printBackground": True, "preferCSSPageSize": True
    })
    pdf_bytes = base64.b64decode(pdf_res.get("result", {}).get("data"))
    pages = len(re.findall(rb'/Type\s*/Page\b', pdf_bytes))
    results.append((h, len(pdf_bytes), pages))
    print(f"Height {h}: Pages = {pages}, Size = {len(pdf_bytes)} bytes")

    tab_ws.close()
    send_cmd("Target.closeTarget", {"targetId": t_id})

ws.close()
print("\nResults:", results)
