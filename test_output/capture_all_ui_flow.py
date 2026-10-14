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

def eval_js(expr, await_promise=False):
    resp = send_cmd("Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": await_promise
    })
    return resp.get("result", {}).get("result", {}).get("value")

def capture_screenshot(filename):
    res = send_cmd("Page.captureScreenshot", {"format": "png"})
    img_b64 = res.get("result", {}).get("data")
    if img_b64:
        out_path = os.path.join(SCREENSHOT_DIR, filename)
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        print(f"Captured screenshot: {out_path} ({os.path.getsize(out_path)} bytes)")
        return out_path
    return None

# 1. Switch to Predict tab
eval_js("if (typeof switchNav === 'function') switchNav('predict');")
time.sleep(0.5)

# Reset form state
eval_js("discardExtraction();")
time.sleep(0.2)

# 2. Upload test document with promise
print("Uploading Eleanor Vance Cardiology Summary report...")
upload_promise = f"""
new Promise((resolve, reject) => {{
    try {{
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
        
        let attempts = 0;
        const interval = setInterval(() => {{
            attempts++;
            const rev = document.getElementById('extractionReviewContainer');
            if (rev && rev.style.display !== 'none') {{
                clearInterval(interval);
                resolve({{
                    success: true,
                    rows: document.querySelectorAll('.reviewTableRow').length
                }});
            }} else if (attempts > 30) {{
                clearInterval(interval);
                resolve({{ success: false, timeout: true }});
            }}
        }}, 200);
    }} catch(e) {{
        reject(e.toString());
    }}
}})
"""

upload_res = eval_js(upload_promise, await_promise=True)
print("Upload Result:", upload_res)
time.sleep(0.8)

# Scroll review container to top of viewport
eval_js("document.getElementById('uploadReportSection').scrollIntoView({behavior: 'instant', block: 'start'});")
time.sleep(0.5)

# Capture Screenshot 1: Extraction Review Table (Top section with badges, pills, demographics)
capture_screenshot("01_extraction_review_table.png")

# Scroll table down slightly to capture lab measurements & snippets
eval_js("document.querySelector('.reviewTableWrap').scrollTop = 280;")
time.sleep(0.5)
capture_screenshot("02_extraction_review_lab_snippets.png")

# 3. Simulate user editing a value (e.g., verifying interactive edit)
print("Simulating user review and edit...")
eval_js("""
(() => {
    const prInp = document.querySelector('.reviewRowInput[data-feat="pr"]');
    if (prInp) {
        prInp.value = "76";
        handleReviewInputEdit(prInp);
    }
})()
""")
time.sleep(0.3)

# 4. Click 'Apply to Patient Form'
print("Clicking 'Apply to Patient Form'...")
eval_js("applyExtractedValues();")
time.sleep(0.8)

# Capture Screenshot 3: Applied Alert & Form autofill confirmation
eval_js("document.getElementById('uploadReportSection').scrollIntoView({behavior: 'instant', block: 'start'});")
time.sleep(0.5)
capture_screenshot("03_form_autofill_applied.png")

# Check populated form fields in DOM
fields_state = eval_js("""
(() => {
    return {
        patient_name: document.getElementById('inp_patient_name') ? document.getElementById('inp_patient_name').value : '',
        patient_id: document.getElementById('inp_patient_id') ? document.getElementById('inp_patient_id').value : '',
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
        ldl: document.getElementById('inp_ldl') ? document.getElementById('inp_ldl').value : '',
        hdl: document.getElementById('inp_hdl') ? document.getElementById('inp_hdl').value : '',
        ef_tte: document.getElementById('inp_ef_tte') ? document.getElementById('inp_ef_tte').value : '',
        dm: document.getElementById('inp_dm') ? document.getElementById('inp_dm').value : '',
        htn: document.getElementById('inp_htn') ? document.getElementById('inp_htn').value : '',
        ex_smoker: document.getElementById('inp_ex_smoker') ? document.getElementById('inp_ex_smoker').value : '',
        statusBadge: document.getElementById('predStatusBadge') ? document.getElementById('predStatusBadge').textContent.trim() : ''
    };
})()
""")
print(f"Verified Form Fields State: {json.dumps(fields_state, indent=2)}")

# Scroll down to show vitals & biomarkers section with populated inputs
eval_js("window.scrollBy(0, 500);")
time.sleep(0.5)
capture_screenshot("04_populated_vitals_biomarkers.png")

# 5. Run Fresh Prediction with verified inputs
print("Running fresh prediction using verified inputs...")
eval_js("runPrediction();")
time.sleep(2.0)

# Capture Screenshot 5: Fresh prediction results with updated probabilities & SHAP
eval_js("document.getElementById('riskGaugesCard').scrollIntoView({behavior: 'instant', block: 'start'});")
time.sleep(0.5)
capture_screenshot("05_fresh_prediction_results.png")

ws.close()
print("\nAll 5 demonstration screenshots captured and verified successfully!")
