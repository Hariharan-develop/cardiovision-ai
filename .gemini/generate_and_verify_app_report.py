import json
import base64
import urllib.request
import websocket
import time
import re

print("=== Starting CardioVision AI Report PDF Verification ===")

# 1. Connect to Chrome CDP
ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

b_id = 0
def b_cmd(method, params=None):
    global b_id
    b_id += 1
    b_ws.send(json.dumps({'id': b_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(b_ws.recv())
        if resp.get('id') == b_id:
            return resp

# 2. Extract the actual report HTML from the iframe in localhost:8501
tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
app_tab = [x for x in tabs if '8501' in x.get('url', '')][0]
a_ws = websocket.create_connection(app_tab['webSocketDebuggerUrl'], suppress_origin=True)

extract_script = """
(() => {
    const iframe = document.querySelector('iframe');
    const win = iframe.contentWindow;
    const doc = iframe.contentDocument;

    // Temporarily mock window.open to intercept reportHtml
    let capturedHtml = null;
    const origOpen = win.open;
    win.open = function() {
        return {
            document: {
                open: function() {},
                write: function(content) { capturedHtml = content; },
                close: function() {}
            }
        };
    };

    try {
        win.exportClinicalReport();
    } finally {
        win.open = origOpen;
    }

    return capturedHtml;
})()
"""

a_ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': extract_script, 'returnByValue': True}}))
extract_res = json.loads(a_ws.recv())
report_html = extract_res.get('result', {}).get('result', {}).get('value')
a_ws.close()

assert report_html, "Failed to capture reportHtml from exportClinicalReport!"
print(f"Successfully captured report HTML ({len(report_html)} bytes) directly from live app!")

# Remove automatic window.print() timer from the captured HTML for headless testing
test_report_html = re.sub(
    r'<script>\s*window\.onload\s*=\s*function\(\)\s*\{.*?\}\s*;\s*</script>',
    '',
    report_html,
    flags=re.DOTALL
)

# 3. Create a clean test tab
new_t = b_cmd("Target.createTarget", {"url": "about:blank"})
target_id = new_t['result']['targetId']

tabs_list = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
target_tab = [t for t in tabs_list if t.get('id') == target_id][0]
t_ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)

t_id = 0
def t_cmd(method, params=None):
    global t_id
    t_id += 1
    t_ws.send(json.dumps({'id': t_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(t_ws.recv())
        if resp.get('id') == t_id:
            return resp

t_cmd("Page.enable")
t_cmd("Runtime.enable")

# Write report HTML
t_cmd("Runtime.evaluate", {
    "expression": f"document.open(); document.write({json.dumps(test_report_html)}); document.close();"
})
time.sleep(0.5)

# 4. Generate PDF using Chrome Page.printToPDF
print("\n--- Generating PDF via Chrome Page.printToPDF (A4 Portrait) ---")
pdf_res = t_cmd("Page.printToPDF", {
    "paperWidth": 8.27, "paperHeight": 11.69,
    "marginTop": 0.39, "marginBottom": 0.39,
    "marginLeft": 0.55, "marginRight": 0.55,
    "printBackground": True,
    "preferCSSPageSize": True
})

pdf_data = base64.b64decode(pdf_res['result']['data'])
pages = len(re.findall(rb'/Type\s*/Page\b', pdf_data))
print(f"PDF Generated! Size: {len(pdf_data)} bytes. Number of A4 Pages: {pages}")
assert pages == 2, f"FAILED: Expected 2 pages, got {pages}"

pdf_out = 'c:/Users/hario/Downloads/CardioVision-AI/.gemini/CardioVision_Research_Report.pdf'
with open(pdf_out, 'wb') as f:
    f.write(pdf_data)
print(f"Saved PDF to {pdf_out}")

# 5. Measure layout geometry and footer alignment
print("\n--- Evaluating Layout Geometry & Footer Alignment ---")
t_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1050, "height": 2600, "deviceScaleFactor": 1, "mobile": False
})
time.sleep(0.3)

metrics_js = """
(() => {
    const p1 = document.querySelector('.page-1');
    const p2 = document.querySelector('.page-2');
    const b1 = p1.querySelector('.sheetBody');
    const b2 = p2.querySelector('.sheetBody');
    const f1 = p1.querySelector('.pageFooter');
    const f2 = p2.querySelector('.pageFooter');

    const rP1 = p1.getBoundingClientRect();
    const rP2 = p2.getBoundingClientRect();
    const rB1 = b1.getBoundingClientRect();
    const rB2 = b2.getBoundingClientRect();
    const rF1 = f1.getBoundingClientRect();
    const rF2 = f2.getBoundingClientRect();

    return {
        page1: {
            heightPx: Math.round(rP1.height),
            contentHeightPx: Math.round(rB1.height),
            footerGapBelowPx: Math.round(rP1.bottom - rF1.bottom),
            footerText: f1.innerText.replace(/\\s+/g, ' ').trim()
        },
        page2: {
            heightPx: Math.round(rP2.height),
            contentHeightPx: Math.round(rB2.height),
            emptySpaceBeforeFooterPx: Math.round(rF2.top - rB2.bottom),
            footerGapBelowPx: Math.round(rP2.bottom - rF2.bottom),
            footerText: f2.innerText.replace(/\\s+/g, ' ').trim()
        }
    };
})()
"""

metrics_res = t_cmd("Runtime.evaluate", {"expression": metrics_js, "returnByValue": True})
m = metrics_res['result']['result']['value']
print(json.dumps(m, indent=2))

# Assertions
assert "Research Prototype Record" in m['page1']['footerText'], "Page 1 footer missing 'Research Prototype Record'"
assert "Confidential Prototype Record" not in m['page1']['footerText'], "Page 1 footer still has 'Confidential Prototype Record'"
assert "Page 1 of 2" in m['page1']['footerText']
assert "Page 2 of 2" in m['page2']['footerText']

# Page 2 footer must be at the bottom (gap below is exactly the padding ~38px = 10mm)
assert m['page2']['footerGapBelowPx'] == 38, f"Footer on Page 2 not at bottom! Gap below: {m['page2']['footerGapBelowPx']}"

# Page 2 content must not be stretched: empty space before footer must be substantial (~450px)
assert m['page2']['emptySpaceBeforeFooterPx'] > 200, "Content seems stretched!"
print(f"\nVerification Success: Page 2 footer sits at bottom with {m['page2']['emptySpaceBeforeFooterPx']}px empty space above it without stretching content!")

# 6. Capture screenshots of Page 1 and Page 2
p1_box = t_cmd("Runtime.evaluate", {
    "expression": "(() => { const r = document.querySelector('.page-1').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()",
    "returnByValue": True
})['result']['result']['value']

p2_box = t_cmd("Runtime.evaluate", {
    "expression": "(() => { const r = document.querySelector('.page-2').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()",
    "returnByValue": True
})['result']['result']['value']

ss1 = t_cmd("Page.captureScreenshot", {"clip": {**p1_box, "scale": 1}})
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/page1_final.png', 'wb') as pf:
    pf.write(base64.b64decode(ss1['result']['data']))

ss2 = t_cmd("Page.captureScreenshot", {"clip": {**p2_box, "scale": 1}})
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/page2_final.png', 'wb') as pf:
    pf.write(base64.b64decode(ss2['result']['data']))

print("Screenshots saved: page1_final.png and page2_final.png")

t_ws.close()
b_cmd("Target.closeTarget", {"targetId": target_id})
b_ws.close()

print("\n=== ALL VERIFICATIONS PASSED 100% ===")
