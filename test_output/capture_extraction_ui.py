import json
import base64
import time
import urllib.request
import websocket
import os

BASE_DIR = r"c:\Users\hario\Downloads\CardioVision-AI"
TEST_PDF_PATH = os.path.join(BASE_DIR, "test_output", "extraction_tests", "test1_text_medical.pdf")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "test_output", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

with open(TEST_PDF_PATH, "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

# Connect to Chrome CDP
with urllib.request.urlopen("http://127.0.0.1:9222/json") as res:
    tabs = json.loads(res.read().decode())

target = next((t for t in tabs if "8502" in t.get("url", "") or "dashboard" in t.get("url", "")), None)
if not target:
    target = tabs[0]

ws_url = target.get("webSocketDebuggerUrl")
print(f"Connecting to CDP: {ws_url} (tab: {target.get('title')})")
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

def eval_js(expr):
    resp = send_cmd("Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    })
    return resp.get("result", {}).get("result", {}).get("value")

def capture_screenshot(filename, clip=None):
    params = {"format": "png"}
    if clip:
        params["clip"] = clip
    res = send_cmd("Page.captureScreenshot", params)
    img_b64 = res.get("result", {}).get("data")
    if img_b64:
        out_path = os.path.join(SCREENSHOT_DIR, filename)
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f"Captured screenshot: {out_path}")
        return out_path
    return None

# 1. Reload the dashboard
print("Reloading dashboard...")
send_cmd("Page.reload")
time.sleep(2.0)

# Switch to Predict Risk tab if needed
eval_js("if (typeof switchNav === 'function') switchNav('predict');")
time.sleep(0.5)

# 2. Upload test PDF via JavaScript File & FileReader
print("Triggering document upload via UI client engine...")
upload_script = f"""
(() => {{
    const b64 = "{pdf_b64}";
    const byteChars = atob(b64);
    const byteNumbers = new Array(byteChars.length);
    for (let i = 0; i < byteChars.length; i++) {{
        byteNumbers[i] = byteChars.charCodeAt(i);
    }}
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], {{type: 'application/pdf'}});
    const file = new File([blob], 'Eleanor_Vance_Cardiology_Summary.pdf', {{type: 'application/pdf'}});
    uploadPatientReportFile(file);
    return true;
}})()
"""
eval_js(upload_script)

# Wait for extraction review table to render
print("Waiting for extraction review table...")
review_visible = False
for _ in range(20):
    time.sleep(0.5)
    review_visible = eval_js("document.getElementById('extractionReviewContainer') && document.getElementById('extractionReviewContainer').style.display !== 'none'")
    if review_visible:
        break

print(f"Extraction review container visible: {review_visible}")

# Scroll review container into view
eval_js("document.getElementById('extractionReviewContainer').scrollIntoView({behavior: 'instant', block: 'start'});")
time.sleep(0.8)

# Capture Review Table Screenshot
shot1 = capture_screenshot("01_extraction_review_table.png")

# 3. Check review items count
items_info = eval_js("""
(() => {
    const rows = document.querySelectorAll('.reviewTableRow');
    const pills = {
        all: document.getElementById('pillCountAll') ? document.getElementById('pillCountAll').textContent : '0',
        extracted: document.getElementById('pillCountExtracted') ? document.getElementById('pillCountExtracted').textContent : '0',
        calculated: document.getElementById('pillCountCalculated') ? document.getElementById('pillCountCalculated').textContent : '0',
        needsReview: document.getElementById('pillCountNeedsReview') ? document.getElementById('pillCountNeedsReview').textContent : '0',
        notFound: document.getElementById('pillCountNotFound') ? document.getElementById('pillCountNotFound').textContent : '0',
    };
    return { rowCount: rows.length, pills: pills };
})()
""")
print(f"Review Items rendered: {items_info}")

# 4. Click 'Apply to Patient Form'
print("Clicking Apply to Patient Form...")
eval_js("applyExtractedValues();")
time.sleep(1.0)

# Check populated form values
populated_vals = eval_js("""
(() => {
    return {
        patient_id: document.getElementById('inp_patient_id') ? document.getElementById('inp_patient_id').value : '',
        patient_name: document.getElementById('inp_patient_name') ? document.getElementById('inp_patient_name').value : '',
        age: document.getElementById('inp_age') ? document.getElementById('inp_age').value : '',
        sex: document.getElementById('inp_sex') ? document.getElementById('inp_sex').value : '',
        length: document.getElementById('inp_length') ? document.getElementById('inp_length').value : '',
        weight: document.getElementById('inp_weight') ? document.getElementById('inp_weight').value : '',
        bmi: document.getElementById('inp_bmi') ? document.getElementById('inp_bmi').value : '',
        bp: document.getElementById('inp_bp') ? document.getElementById('inp_bp').value : '',
        pr: document.getElementById('inp_pr') ? document.getElementById('inp_pr').value : '',
        fbs: document.getElementById('inp_fbs') ? document.getElementById('inp_fbs').value : '',
        cr: document.getElementById('inp_cr') ? document.getElementById('inp_cr').value : '',
        tg: document.getElementById('inp_tg') ? document.getElementById('inp_tg').value : '',
        ef_tte: document.getElementById('inp_ef_tte') ? document.getElementById('inp_ef_tte').value : '',
        dm: document.getElementById('inp_dm') ? document.getElementById('inp_dm').value : '',
        htn: document.getElementById('inp_htn') ? document.getElementById('inp_htn').value : '',
        statusBadge: document.getElementById('predStatusBadge') ? document.getElementById('predStatusBadge').textContent.trim() : ''
    };
})()
""")
print(f"Populated Form Values: {json.dumps(populated_vals, indent=2)}")

# Capture Form with Applied Banner Screenshot
eval_js("document.getElementById('uploadReportSection').scrollIntoView({behavior: 'instant', block: 'start'});")
time.sleep(0.5)
shot2 = capture_screenshot("02_applied_form_fields.png")

# Also scroll down to basic info / vitals
eval_js("window.scrollBy(0, 450);")
time.sleep(0.5)
shot3 = capture_screenshot("03_populated_vitals_biomarkers.png")

ws.close()
print("Screenshot capture and browser verification completed successfully!")
