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

# 5. Extract generated report HTML
print("\n--- Extracting Generated Report HTML ---")
report_html = eval_in_iframe("""
    if (typeof win.exportClinicalReport === 'function') {
        return win.exportClinicalReport();
    }
    return 'ERROR: exportClinicalReport not found';
""")

assert report_html and not report_html.startswith('ERROR'), f"Failed to get report HTML: {report_html[:200]}"
print(f"Retrieved report HTML: {len(report_html)} bytes")

# Verify Terminology in report HTML
print("\n--- Verifying Medical Terminology in Exported Report ---")
checks = {
    "1. Heading: Model-Estimated Coronary Outcome Probabilities": "Model-Estimated Coronary Outcome Probabilities" in report_html,
    "2. Card Note: These are model-estimated probabilities...": "These are model-estimated probabilities, not clinically calibrated risk estimates or measured coronary artery narrowing percentages." in report_html,
    "3. Table Header: General Adult Reference (Informational)": "General Adult Reference (Informational)" in report_html,
    "4. Feature note: 57-feature input vector": "Machine learning prediction models evaluate the full standardized 57-feature input vector." in report_html,
    "5. LVEF label: LVEF ≥ 50% — interpret in clinical context": "LVEF ≥ 50% — interpret in clinical context" in report_html,
    "6. Renal marker: Serum creatinine — kidney function marker": "Serum creatinine — kidney function marker" in report_html,
    "7. Validation Section on Page 2 (keepTogether)": "keepTogether" in report_html and "Model Validation Performance &amp; Reliability" in report_html,
    "8. LCX/RCA Reliability Notice": "LCX and RCA models have limited predictive discrimination in current validation results" in report_html,
    "9. Disclaimer: RESEARCH PROTOTYPE — NOT A MEDICAL DEVICE": "RESEARCH PROTOTYPE — NOT A MEDICAL DEVICE" in report_html,
    "10. Page 1 Footer: Page 1 of 2": "Page 1 of 2" in report_html,
    "11. Page 2 Footer: Page 2 of 2": "Page 2 of 2" in report_html,
    "12. Unit nowrap: kg/m²": "kg/m²" in report_html and "nowrap" in report_html,
    "13. Time nowrap: non-breaking space": "&nbsp;" in report_html,
}

for name, passed in checks.items():
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    assert passed, f"Failed check: {name}"

# Save report HTML to artifact directory
artifact_dir = "C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779"
html_path = os.path.join(artifact_dir, "cardiovision_research_evaluation_report.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(report_html)
print(f"Report HTML saved to: {html_path}")

# 6. Render report in a target tab and print to PDF via CDP
print("\n--- Printing to PDF via Chrome DevTools Protocol (A4) ---")
# Create a new tab via Target.createTarget
new_target_resp = send_cmd("Target.createTarget", {"url": "about:blank"})
new_target_id = new_target_resp.get("result", {}).get("targetId")
print("Created target tab:", new_target_id)

# Connect to new target tab
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

# Set the document content to report_html
set_doc_expr = f"""
    document.open();
    document.write({json.dumps(report_html)});
    document.close();
"""
tab_cmd("Runtime.evaluate", {"expression": set_doc_expr})
time.sleep(1.0)

# Capture Page 1 screenshot
tab_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1200, "height": 950, "deviceScaleFactor": 1, "mobile": False
})
shot_resp = tab_cmd("Page.captureScreenshot", {"format": "png"})
shot_data = shot_resp.get("result", {}).get("data")
if shot_data:
    with open(os.path.join(artifact_dir, "report_preview_page1.png"), "wb") as f:
        f.write(base64.b64decode(shot_data))
    print("Page 1 preview screenshot saved")

# Scroll down to Page 2 and capture Page 2 screenshot
tab_cmd("Runtime.evaluate", {"expression": "window.scrollTo(0, document.body.scrollHeight / 2 + 100);"})
time.sleep(0.5)
shot_resp2 = tab_cmd("Page.captureScreenshot", {"format": "png"})
shot_data2 = shot_resp2.get("result", {}).get("data")
if shot_data2:
    with open(os.path.join(artifact_dir, "report_preview_page2.png"), "wb") as f:
        f.write(base64.b64decode(shot_data2))
    print("Page 2 preview screenshot saved")

# Print to PDF using A4 parameters
# A4 size: 8.27 in x 11.69 in (210mm x 297mm)
# Margins: 10mm top/bottom = 0.39 in; 14mm left/right = 0.55 in
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
print(f"PDF successfully generated and saved to: {pdf_path} ({len(pdf_bytes)} bytes)")

# Count pages in PDF
page_matches = re.findall(rb'/Type\s*/Page\b', pdf_bytes)
page_count = len(page_matches)
print(f"PDF Page Count: {page_count} pages")
assert page_count == 2, f"Expected exactly 2 pages, got {page_count} pages!"

# Close tab
tab_ws.close()
send_cmd("Target.closeTarget", {"targetId": new_target_id})
ws.close()

print("\n=== ALL PDF VERIFICATION CHECKS PASSED: EXACTLY 2 PAGES ===")
