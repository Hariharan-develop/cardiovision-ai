import json
import base64
import time
import urllib.request
import websocket
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("Connecting to Chrome CDP on 127.0.0.1:9222...")
with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    tabs = json.loads(res.read().decode())

target = None
for t in tabs:
    if 'localhost:8501' in t.get('url', ''):
        target = t
        break

if not target:
    raise RuntimeError("Could not find localhost:8501 tab")

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
        if (!iframe || !iframe.contentDocument) {{
            return 'ERROR: iframe not accessible';
        }}
        const doc = iframe.contentDocument;
        const win = iframe.contentWindow;
        try {{
            return (function(doc, win) {{ {expr} }})(doc, win);
        }} catch(e) {{
            return 'ERROR: ' + e.toString() + '\\n' + e.stack;
        }}
    }})()
    """
    resp = send_cmd("Runtime.evaluate", {
        "expression": wrapper,
        "returnByValue": True,
        "awaitPromise": True
    })
    return resp.get("result", {}).get("result", {}).get("value")

# 1. Reload page
print("\n--- Reloading Page ---")
send_cmd("Page.reload", {"ignoreCache": True})
time.sleep(3.0)

# 2. Wait for iframe
print("\n--- Waiting for iframe ---")
for attempt in range(15):
    res = eval_in_iframe("return !!doc.getElementById('view-results');")
    if res is True:
        print(f"Iframe ready on attempt {attempt+1}")
        break
    time.sleep(1.0)
else:
    raise RuntimeError("Iframe did not become ready")

# 3. Switch to Results view
print("\n--- Switching to Results View ---")
eval_in_iframe("win.switchNav('results');")
time.sleep(0.8)

# 4. Trigger Predict to ensure active predictions
print("\n--- Running Prediction Calculation ---")
eval_in_iframe("if (typeof win.predictRisk === 'function') win.predictRisk();")
time.sleep(1.8)

# 5. Extract report HTML with default creatinine (1.0 mg/dL)
print("\n--- Verifying Default Creatinine (1.0 mg/dL) and Validation Terminology ---")
report_html_1 = eval_in_iframe("""
    if (typeof win.exportClinicalReport === 'function') {
        return win.exportClinicalReport();
    }
    return 'ERROR';
""")

assert "Within displayed adult reference range (Informational)" in report_html_1, "Failed: CR 1.0 mg/dL not marked as within reference range!"
print("[PASS] Serum Creatinine 1.0 mg/dL correctly classified: 'Within displayed adult reference range (Informational)'")

assert "Retrospective model evaluation metrics recorded during development using held-out test data." in report_html_1, "Failed: Held-out validation terminology missing!"
print("[PASS] Model Validation Terminology correctly updated: 'Retrospective model evaluation metrics recorded during development using held-out test data.'")

# 6. Test Elevated Creatinine (2.2 mg/dL) dynamic status
print("\n--- Testing Dynamic Creatinine Status with Elevated Value (2.2 mg/dL) ---")
report_html_elevated = eval_in_iframe("""
    const crInp = doc.getElementById('inp_cr');
    if (crInp) crInp.value = '2.2';
    if (typeof win.exportClinicalReport === 'function') {
        const html = win.exportClinicalReport();
        if (crInp) crInp.value = '1.0'; // restore
        return html;
    }
    return 'ERROR';
""")

assert "Outside displayed adult reference range (Informational)" in report_html_elevated, "Failed: CR 2.2 mg/dL not marked as outside reference range!"
print("[PASS] Elevated Serum Creatinine (2.2 mg/dL) correctly classified: 'Outside displayed adult reference range (Informational)'")

# 7. Render report in a target tab and print to PDF via CDP
print("\n--- Printing to PDF via Chrome DevTools Protocol (A4) ---")
artifact_dir = "C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779"

new_target_resp = send_cmd("Target.createTarget", {"url": "about:blank"})
new_target_id = new_target_resp.get("result", {}).get("targetId")

with urllib.request.urlopen('http://127.0.0.1:9222/json') as res:
    all_tabs = json.loads(res.read().decode())

tab_target = None
for t in all_tabs:
    if t.get("id") == new_target_id:
        tab_target = t
        break

assert tab_target, "Could not find created tab in tabs list"
tab_ws = websocket.create_connection(tab_target.get("webSocketDebuggerUrl"), timeout=30, suppress_origin=True)

t_id = 0
def tab_cmd(method, params=None):
    global t_id
    t_id += 1
    req = {"id": t_id, "method": method}
    if params:
        req["params"] = params
    tab_ws.send(json.dumps(req))
    while True:
        resp = json.loads(tab_ws.recv())
        if resp.get("id") == t_id:
            return resp

tab_cmd("Page.enable")
tab_cmd("Runtime.enable")

set_doc_expr = f"""
    document.open();
    document.write({json.dumps(report_html_1)});
    document.close();
"""
tab_cmd("Runtime.evaluate", {"expression": set_doc_expr})
time.sleep(1.0)

# Capture Page 1 screenshot
tab_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1200, "height": 980, "deviceScaleFactor": 1, "mobile": False
})
shot_resp = tab_cmd("Page.captureScreenshot", {"format": "png"})
shot_data = shot_resp.get("result", {}).get("data")
if shot_data:
    with open(os.path.join(artifact_dir, "report_refined_page1.png"), "wb") as f:
        f.write(base64.b64decode(shot_data))
    print("Page 1 preview screenshot saved")

# Scroll down to Page 2 and capture Page 2 screenshot
tab_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, document.body.scrollHeight / 2 + 100);"})
time.sleep(0.5)
shot_resp2 = tab_cmd("Page.captureScreenshot", {"format": "png"})
shot_data2 = shot_resp2.get("result", {}).get("data")
if shot_data2:
    with open(os.path.join(artifact_dir, "report_refined_page2.png"), "wb") as f:
        f.write(base64.b64decode(shot_data2))
    print("Page 2 preview screenshot saved")

# Print to PDF using A4 parameters
pdf_resp = tab_cmd("Page.printToPDF", {
    "paperWidth": 8.27,
    "paperHeight": 11.69,
    "marginTop": 0.39,
    "marginBottom": 0.39,
    "marginLeft": 0.55,
    "marginRight": 0.55,
    "printBackground": True,
    "preferCSSPageSize": True
})

pdf_data = pdf_resp.get("result", {}).get("data")
assert pdf_data, "Failed to get PDF data from Page.printToPDF"

pdf_bytes = base64.b64decode(pdf_data)
pdf_path = os.path.join(artifact_dir, "CardioVision_Research_Evaluation_Report.pdf")
with open(pdf_path, "wb") as f:
    f.write(pdf_bytes)
print(f"PDF successfully saved to: {pdf_path} ({len(pdf_bytes)} bytes)")

# Count pages in PDF
page_matches = re.findall(rb'/Type\s*/Page\b', pdf_bytes)
page_count = len(page_matches)
print(f"PDF Page Count: {page_count} pages")
assert page_count == 2, f"Expected exactly 2 pages, got {page_count} pages!"
print("[PASS] PDF Page count is EXACTLY 2 pages!")

# Close tab
tab_ws.close()
send_cmd("Target.closeTarget", {"targetId": new_target_id})
ws.close()

print("\n=== ALL FINAL PDF REFINEMENT TESTS COMPLETED WITH 100% SUCCESS ===")
