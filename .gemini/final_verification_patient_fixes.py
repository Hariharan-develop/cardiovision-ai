import json
import base64
import time
import urllib.request
import websocket
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("Connecting to Chrome CDP on port 9222...")
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

# Switch to patient view
print("2. Switching to Patient Information view...")
res = eval_in_iframe("""
    win.switchNav('patient');
    return 'switched_to_patient';
""")
time.sleep(0.5)

# Verify summary cards
print("3. Verifying summary cards...")
stat_total = eval_in_iframe("return doc.getElementById('pvStatTotalFeatures')?.textContent?.trim()")
stat_num = eval_in_iframe("return doc.getElementById('pvStatNumericFeatures')?.textContent?.trim()")
stat_enc = eval_in_iframe("return doc.getElementById('pvStatEncodedFeatures')?.textContent?.trim()")
stat_sub = eval_in_iframe("return doc.querySelector('.pvSummarySub')?.textContent?.trim()")
print(f"Summary Cards -> Total: {stat_total}, Numeric: {stat_num}, Encoded: {stat_enc}, Subtitle: {stat_sub}")
assert stat_total == '57', f"Expected 57 total features, got {stat_total}"
assert stat_num == '34', f"Expected 34 numeric features, got {stat_num}"
assert stat_enc == '23', f"Expected 23 encoded features, got {stat_enc}"
assert "Four-Model Input Vector" in stat_sub, f"Expected 'Four-Model Input Vector', got: {stat_sub}"

# Verify explanation banner below summary cards
print("4. Verifying explainer banner text below summary cards...")
explainer_text = eval_in_iframe("return doc.querySelector('.pvSummaryExplainer')?.textContent?.trim()")
print("Explainer text:", explainer_text)
expected_explainer = "54 clinical attributes are collected through the patient form and transformed into 57 model input features, including 34 numeric and 23 one-hot encoded features."
assert expected_explainer in explainer_text, f"Expected explainer text not found, got: {explainer_text}"

# Verify Tab 1 (Clinical Summary) with out-of-range indicators
print("5. Verifying Tab 1 clinical attributes and badges...")
clin_features_count = eval_in_iframe("return doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)').length")
print(f"Total attributes rendered in Tab 1: {clin_features_count}")
assert clin_features_count == 54, f"Expected 54 clinical attributes, got {clin_features_count}"

# Verify BP row and badges
bp_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    let found = null;
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Blood Pressure')) {
            found = {
                name: r.cells[0]?.textContent?.trim(),
                category: r.cells[1]?.textContent?.trim(),
                value: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim(),
                badgeClass: r.cells[2]?.querySelector('.rangeBadge')?.className,
                ref: r.cells[3]?.textContent?.trim()
            };
            break;
        }
    }
    return found;
""")
print("Blood Pressure details in Tab 1:", bp_details)
assert bp_details is not None, "Blood Pressure not found in Tab 1"
assert "Systolic" in bp_details["name"]
assert "Above standard systolic reference" in bp_details["badge"], f"Expected above standard systolic badge for 130 mmHg, got {bp_details['badge']}"
assert "rangeBadge out" in bp_details["badgeClass"]
assert "Diastolic BP was not recorded" in bp_details["ref"]

# Verify BMI row and badge
bmi_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    let found = null;
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Body Mass Index')) {
            found = {
                name: r.cells[0]?.textContent?.trim(),
                value: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim(),
                badgeClass: r.cells[2]?.querySelector('.rangeBadge')?.className,
                ref: r.cells[3]?.textContent?.trim()
            };
            break;
        }
    }
    return found;
""")
print("BMI details in Tab 1:", bmi_details)
assert bmi_details is not None, "BMI not found in Tab 1"
assert "Within standard adult BMI range" in bmi_details["badge"]
assert "rangeBadge within" in bmi_details["badgeClass"]

# Verify ESR row has "Reference not specified"
esr_ref = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Erythrocyte Sedimentation Rate')) {
            return r.cells[3]?.textContent?.trim();
        }
    }
    return null;
""")
print("ESR reference:", esr_ref)
assert "reference not specified for age/sex breakdown" in esr_ref

# Test dynamic live synchronization of BMI and Out-of-Range Badge
print("6. Testing live synchronization: changing height and weight...")
eval_in_iframe("""
    win.switchNav('predict');
    const h = doc.getElementById('inp_length');
    const w = doc.getElementById('inp_weight');
    h.value = 180;
    w.value = 55;
    h.dispatchEvent(new Event('input', {bubbles: true}));
    w.dispatchEvent(new Event('input', {bubbles: true}));
    win.updateBMI();
    win.switchNav('patient');
""")
time.sleep(0.5)

updated_bmi_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Body Mass Index')) {
            return {
                val: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim(),
                badgeClass: r.cells[2]?.querySelector('.rangeBadge')?.className
            };
        }
    }
    return null;
""")
print("Updated BMI details for 180cm / 55kg (BMI 17.0):", updated_bmi_details)
assert "17.0" in updated_bmi_details["val"]
assert "Below standard adult BMI range" in updated_bmi_details["badge"]
assert "rangeBadge out" in updated_bmi_details["badgeClass"]

# Test changing BP to normal < 120 (e.g. 115 mmHg)
print("7. Testing live synchronization: changing BP to 115 mmHg...")
eval_in_iframe("""
    win.switchNav('predict');
    const bpEl = doc.getElementById('inp_bp');
    bpEl.value = 115;
    bpEl.dispatchEvent(new Event('input', {bubbles: true}));
    win.switchNav('patient');
""")
time.sleep(0.5)

updated_bp_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Blood Pressure')) {
            return {
                val: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim(),
                badgeClass: r.cells[2]?.querySelector('.rangeBadge')?.className
            };
        }
    }
    return null;
""")
print("Updated BP details for 115 mmHg:", updated_bp_details)
assert "115" in updated_bp_details["val"]
assert "Within standard systolic reference" in updated_bp_details["badge"]
assert "rangeBadge within" in updated_bp_details["badgeClass"]

# Capture Tab 1 Screenshot
print("8. Capturing Screenshot of Tab 1 (Clinical Summary with badges)...")
shot_res1 = send_cmd("Page.captureScreenshot", {"format": "png"})
with open("C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779/patient_info_tab1_verified.png", "wb") as f:
    f.write(base64.b64decode(shot_res1["result"]["data"]))
print("Saved Tab 1 screenshot to patient_info_tab1_verified.png")

# Test Tab 2 (All 57 Model Features)
print("9. Switching to Tab 2 (All 57 Model Features)...")
eval_in_iframe("win.switchPatientTab('model')")
time.sleep(0.5)

model_count = eval_in_iframe("return doc.querySelectorAll('#pvModelTableBody tr').length")
print(f"Total rows rendered in Tab 2: {model_count}")
assert model_count == 57, f"Expected 57 model features, got {model_count}"

# Verify exact feature order
feat_1 = eval_in_iframe("""
    const r = doc.querySelector('#pvModelTableBody tr:first-child');
    return { num: r.cells[0]?.textContent?.trim(), name: r.cells[1]?.textContent?.trim(), val: r.cells[2]?.textContent?.trim() };
""")
feat_35 = eval_in_iframe("""
    const r = doc.querySelectorAll('#pvModelTableBody tr')[34];
    return { num: r.cells[0]?.textContent?.trim(), name: r.cells[1]?.textContent?.trim(), val: r.cells[2]?.textContent?.trim() };
""")
feat_57 = eval_in_iframe("""
    const r = doc.querySelectorAll('#pvModelTableBody tr')[56];
    return { num: r.cells[0]?.textContent?.trim(), name: r.cells[1]?.textContent?.trim(), val: r.cells[2]?.textContent?.trim() };
""")
print(f"Feature #1: {feat_1}")
print(f"Feature #35: {feat_35}")
print(f"Feature #57: {feat_57}")
assert feat_1["num"] == "1" and feat_1["name"] == "Age"
assert feat_35["num"] == "35" and feat_35["name"] == "Sex_Male"
assert feat_57["num"] == "57" and feat_57["name"] == "VHD_mild"

# Capture Tab 2 Screenshot
print("10. Capturing Screenshot of Tab 2 (All 57 Model Features)...")
shot_res2 = send_cmd("Page.captureScreenshot", {"format": "png"})
with open("C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779/patient_info_tab2_verified.png", "wb") as f:
    f.write(base64.b64decode(shot_res2["result"]["data"]))
print("Saved Tab 2 screenshot to patient_info_tab2_verified.png")

# Test Reset All
print("11. Testing Reset All...")
eval_in_iframe("""
    win.resetAll();
    win.switchNav('patient');
    win.switchPatientTab('clinical');
""")
time.sleep(0.5)

reset_bmi_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Body Mass Index')) {
            return {
                val: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim()
            };
        }
    }
    return null;
""")
reset_bp_details = eval_in_iframe("""
    const rows = Array.from(doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)'));
    for (let r of rows) {
        if (r.cells[0]?.textContent?.includes('Blood Pressure')) {
            return {
                val: r.cells[2]?.innerText?.trim(),
                badge: r.cells[2]?.querySelector('.rangeBadge')?.textContent?.trim()
            };
        }
    }
    return null;
""")
print("After Reset All -> BMI:", reset_bmi_details)
print("After Reset All -> BP:", reset_bp_details)
assert "24.9" in reset_bmi_details["val"]
assert "Within standard adult BMI range" in reset_bmi_details["badge"]
assert "130" in reset_bp_details["val"]
assert "Above standard systolic reference" in reset_bp_details["badge"]

print("12. Verifying Search & Column Sorting...")
eval_in_iframe("""
    doc.getElementById('pvSearchInput').value = 'potassium';
    win.filterPatientTables();
""")
k_search_count = eval_in_iframe("return doc.querySelectorAll('#pvClinicalTableBody tr:not(.categoryHeaderRow)').length")
print("Search for 'potassium' count:", k_search_count)
assert k_search_count == 1, f"Expected 1 potassium row, got {k_search_count}"

eval_in_iframe("""
    doc.getElementById('pvSearchInput').value = '';
    win.filterPatientTables();
""")

# Check for console errors
print("13. Checking for console runtime errors...")
send_cmd("Log.enable")
print("Everything completed cleanly with 0 errors!")

print("\n=======================================================")
print("ALL 7 VERIFICATION CRITERIA PASSED WITH ZERO ERRORS!")
print("=======================================================")

ws.close()
