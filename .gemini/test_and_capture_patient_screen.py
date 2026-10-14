import json
import base64
import time
import urllib.request
import websocket

# Connect to Chrome CDP
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

def eval_js(expr):
    resp = send_cmd("Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    })
    return resp.get("result", {}).get("result", {}).get("value")

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
    return eval_js(wrapper)

print("1. Reloading page...")
send_cmd("Page.reload")

def wait_for_iframe(timeout=25):
    t0 = time.time()
    while time.time() - t0 < timeout:
        ok = eval_js("Boolean(document.querySelector('iframe') && document.querySelector('iframe').contentDocument && document.querySelector('iframe').contentDocument.getElementById('view-patient'))")
        if ok:
            return True
        time.sleep(0.5)
    return False

print("Waiting for iframe...")
if not wait_for_iframe():
    raise TimeoutError("iframe not ready within timeout")
print("Iframe ready!")

print("2. Checking Streamlit & Dashboard load...")
title = eval_js("document.title")
print("Document title:", title)

# Switch to patient view
print("3. Switching to Patient Information view...")
res = eval_in_iframe("""
    win.switchNav('patient');
    return 'switched_to_patient';
""")
print("Switch nav result:", res)
time.sleep(0.5)

# Check summary cards
print("4. Verifying summary cards...")
stat_total = eval_in_iframe("return doc.getElementById('pvStatTotalFeatures')?.textContent")
stat_num = eval_in_iframe("return doc.getElementById('pvStatNumericFeatures')?.textContent")
stat_enc = eval_in_iframe("return doc.getElementById('pvStatEncodedFeatures')?.textContent")
print(f"Summary Cards -> Total: {stat_total}, Numeric: {stat_num}, Encoded: {stat_enc}")
assert stat_total == '57', f"Expected 57 total features, got {stat_total}"
assert stat_num == '34', f"Expected 34 numeric features, got {stat_num}"
assert stat_enc == '23', f"Expected 23 encoded features, got {stat_enc}"

# Check Patient Identification strip
print("5. Verifying Patient Identification strip...")
pat_name = eval_in_iframe("return doc.getElementById('pvPatientNameDisplay')?.textContent")
pat_id = eval_in_iframe("return doc.getElementById('pvPatientIdDisplay')?.textContent")
pat_age = eval_in_iframe("return doc.getElementById('pvAgeDisplay')?.textContent")
pat_sex = eval_in_iframe("return doc.getElementById('pvSexDisplay')?.textContent")
print(f"Patient Strip -> Name: {pat_name}, ID: {pat_id}, Age: {pat_age}, Sex: {pat_sex}")
assert pat_id and 'CV-2026-' in pat_id, f"Invalid patient ID: {pat_id}"
assert '58' in pat_age, f"Expected 58 years, got {pat_age}"
assert pat_sex in ['Male', 'Female'], f"Unexpected sex: {pat_sex}"

# Check Tab 1 (Clinical Summary)
print("6. Verifying Tab 1 (Clinical Summary)...")
bp_info = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr'));
    let bpRow = null;
    for (let r of rows) {
        if (r.textContent.includes('Blood Pressure')) {
            bpRow = {
                name: r.cells[0]?.textContent?.trim(),
                category: r.cells[1]?.textContent?.trim(),
                value: r.cells[2]?.textContent?.trim(),
                ref: r.cells[3]?.textContent?.trim()
            };
            break;
        }
    }
    return bpRow;
""")
print("BP Row in Clinical Summary:", bp_info)
assert bp_info is not None, "Blood Pressure row not found in Tab 1"
assert "120/80" not in bp_info.get("ref", ""), f"Two-number 120/80 reference found in BP row: {bp_info}"
assert "Systolic" in bp_info.get("name", ""), f"BP not labeled with Systolic: {bp_info}"

# Test search filtering
print("7. Testing search filter...")
eval_in_iframe("""
    const inp = doc.getElementById('pvSearchInput');
    inp.value = 'systolic';
    win.filterPatientTables();
""")
search_count = eval_in_iframe("""
    const visible = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    return visible.length;
""")
print("Rows matching 'systolic':", search_count)
assert search_count > 0, "Search for 'systolic' returned 0 rows"

eval_in_iframe("""
    const inp = doc.getElementById('pvSearchInput');
    inp.value = '';
    win.filterPatientTables();
""")

# Test category filtering
print("8. Testing category dropdown filter...")
eval_in_iframe("""
    const sel = doc.getElementById('pvCategorySelect');
    sel.value = 'Vital Signs';
    win.filterPatientTables();
""")
vitals_count = eval_in_iframe("""
    const visible = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    return visible.length;
""")
print("Rows in category 'Vital Signs':", vitals_count)
assert vitals_count == 3, f"Expected 3 Vital Signs rows, got {vitals_count}"

eval_in_iframe("""
    const sel = doc.getElementById('pvCategorySelect');
    sel.value = 'ALL';
    win.filterPatientTables();
""")

# Capture Tab 1 Screenshot
print("9. Capturing Screenshot of Tab 1...")
shot_res1 = send_cmd("Page.captureScreenshot", {"format": "png"})
with open("C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779/patient_info_tab1_verified.png", "wb") as f:
    f.write(base64.b64decode(shot_res1["result"]["data"]))
print("Saved Tab 1 screenshot to patient_info_tab1_verified.png")

# Switch to Tab 2
print("10. Switching to Tab 2 (All 57 Model Features)...")
eval_in_iframe("win.switchPatientTab('model')")
time.sleep(0.5)

model_count = eval_in_iframe("""
    return doc.querySelectorAll('#pvModelTableBody tr').length;
""")
print("Total rows in Tab 2:", model_count)
assert model_count == 57, f"Expected 57 rows in Tab 2, got {model_count}"

# Check first and encoded features
first_feat = eval_in_iframe("""
    const r = doc.querySelector('#pvModelTableBody tr:first-child');
    return { num: r.cells[0]?.textContent, name: r.cells[1]?.textContent, val: r.cells[2]?.textContent, type: r.cells[3]?.textContent };
""")
print("Feature #1:", first_feat)
assert "Age" in first_feat.get("name", "")
assert "Numeric" in first_feat.get("type", "")

feat_35 = eval_in_iframe("""
    const rows = doc.querySelectorAll('#pvModelTableBody tr');
    const r = rows[34]; // index 34 is feature 35
    return { num: r.cells[0]?.textContent, name: r.cells[1]?.textContent, val: r.cells[2]?.textContent, type: r.cells[3]?.textContent };
""")
print("Feature #35:", feat_35)
assert "Sex_Male" in feat_35.get("name", "")
assert "One-Hot Encoded" in feat_35.get("type", "")

feat_57 = eval_in_iframe("""
    const rows = doc.querySelectorAll('#pvModelTableBody tr');
    const r = rows[56]; // index 56 is feature 57
    return { num: r.cells[0]?.textContent, name: r.cells[1]?.textContent, val: r.cells[2]?.textContent, type: r.cells[3]?.textContent };
""")
print("Feature #57:", feat_57)
assert "VHD_mild" in feat_57.get("name", "")
assert "One-Hot Encoded" in feat_57.get("type", "")

# Capture Tab 2 Screenshot
print("11. Capturing Screenshot of Tab 2...")
shot_res2 = send_cmd("Page.captureScreenshot", {"format": "png"})
with open("C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779/patient_info_tab2_verified.png", "wb") as f:
    f.write(base64.b64decode(shot_res2["result"]["data"]))
print("Saved Tab 2 screenshot to patient_info_tab2_verified.png")

# Test synchronization
print("12. Testing live input synchronization...")
eval_in_iframe("""
    win.switchNav('predict');
    doc.getElementById('inp_age').value = 65;
    doc.getElementById('inp_pr').value = 85;
    // trigger input
    doc.getElementById('inp_age').dispatchEvent(new Event('input', {bubbles: true}));
    doc.getElementById('inp_pr').dispatchEvent(new Event('input', {bubbles: true}));
    win.switchNav('patient');
""")
time.sleep(0.5)

sync_age = eval_in_iframe("return doc.getElementById('pvAgeDisplay')?.textContent")
print("Synchronized Age Display:", sync_age)
assert "65" in sync_age, f"Expected 65 years after live update, got {sync_age}"

# Test Reset All
print("13. Testing Reset All...")
eval_in_iframe("""
    win.resetAll();
""")
time.sleep(0.5)
reset_age = eval_in_iframe("return doc.getElementById('pvAgeDisplay')?.textContent")
reset_pr = eval_in_iframe("return doc.getElementById('inp_pr')?.value")
print(f"After Reset All -> Age: {reset_age}, PR: {reset_pr}")
assert "58" in reset_age, f"Expected 58 years after reset, got {reset_age}"
assert reset_pr == '70', f"Expected PR 70 after reset, got {reset_pr}"

print("14. ALL AUTOMATED PATIENT INFORMATION VERIFICATIONS PASSED SUCCESSFULLY!")
ws.close()
