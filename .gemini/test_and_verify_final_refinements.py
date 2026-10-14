import json
import base64
import time
import urllib.request
import websocket
import os
import sys

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

def capture_screenshot(filename):
    resp = send_cmd("Page.captureScreenshot", {"format": "png"})
    data = resp.get("result", {}).get("data")
    if data:
        with open(filename, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"Screenshot saved: {filename}")
        return True
    return False

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

# 4. Trigger Predict to test active prediction display
print("\n--- Running Prediction Calculation ---")
eval_in_iframe("if (typeof win.predictRisk === 'function') win.predictRisk();")
time.sleep(1.8)

# 5. Verify all refinements
print("\n--- Verifying Refined Elements in Results & Analysis View ---")
verification = eval_in_iframe("""
    const resView = doc.getElementById('view-results');
    if (!resView) return { error: 'view-results not found' };

    // 1. Header & Subtitle
    const h2 = resView.querySelector('.viewTitleBox h2')?.textContent?.trim();
    const sub = resView.querySelector('.viewTitleBox p')?.textContent?.trim();
    const exportBtnText = resView.querySelector('.exportReportBtn span')?.textContent?.trim();

    // 2. Chart Note Clarification
    const chartNoteText = doc.querySelector('.chartNote span')?.textContent?.trim();

    // 3. Stenosis Interpretation
    const cadStenosisText = doc.querySelector('#view-results .tableCard ul li:first-child')?.textContent?.trim();
    const stenosisNoteText = doc.querySelector('#view-results .tableCard div[style*=\"background:#f0f6fc\"]')?.textContent?.trim();

    // 4. Understanding the Prediction - 7 Categories
    const explainBox = doc.querySelector('.explainBox');
    const introText = explainBox?.querySelector('div')?.textContent?.trim();
    const catItems = Array.from(explainBox?.querySelectorAll('ul li') || []).map(li => li.textContent.trim());

    // 5. Explainability Notice
    const explainDesc = doc.querySelector('.explainStatusDesc')?.textContent?.trim();

    // 6. Four Cards Values
    const cadPct = doc.getElementById('resCadCardPct')?.textContent?.trim();
    const ladPct = doc.getElementById('resLadCardPct')?.textContent?.trim();
    const lcxPct = doc.getElementById('resLcxCardPct')?.textContent?.trim();
    const rcaPct = doc.getElementById('resRcaCardPct')?.textContent?.trim();

    // 7. Chart Values
    const chartCad = doc.getElementById('chartCadVal')?.textContent?.trim();
    const chartLad = doc.getElementById('chartLadVal')?.textContent?.trim();
    const chartLcx = doc.getElementById('chartLcxVal')?.textContent?.trim();
    const chartRca = doc.getElementById('chartRcaVal')?.textContent?.trim();

    // 8. Performance Table Rows
    const perfRows = Array.from(doc.querySelectorAll('.perfTable tbody tr')).map(tr => {
        const tds = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
        return { model: tds[0], target: tds[1], acc: tds[2], f1: tds[3], auc: tds[4] };
    });
    const cautionText = doc.querySelector('.cautionNotice')?.textContent?.trim();

    return {
        header: { h2, sub, exportBtnText },
        chartNoteText,
        stenosis: { cadStenosisText, stenosisNoteText },
        explainability: { introText, catCount: catItems.length, catItems, explainDesc },
        cards: { cadPct, ladPct, lcxPct, rcaPct },
        chart: { chartCad, chartLad, chartLcx, chartRca },
        perfRows,
        cautionText
    };
""")

print("\n--- VERIFICATION OUTPUT ---")
print(json.dumps(verification, indent=2))

# Assertions
header = verification['header']
assert header['h2'] == "Coronary Artery Risk & Prediction Analysis", f"Wrong title: {header['h2']}"
assert header['sub'] == "Multi-vessel model probability assessment and cardiovascular risk visualization.", f"Wrong sub: {header['sub']}"
assert header['exportBtnText'] == "Export Research Evaluation Report", f"Wrong export btn: {header['exportBtnText']}"
print("[PASS] Screen Header, Subtitle, and Export Button Label verified.")

chartNote = verification['chartNoteText']
assert "Probability categories and the 50% reference line are visualization aids only." in chartNote, f"Wrong chart note: {chartNote}"
assert "Clinical probability calibration has not been established." in chartNote, f"Missing calibration note: {chartNote}"
print("[PASS] Comparison Chart Note clarification verified.")

stenosis = verification['stenosis']
assert "Model-estimated likelihood of overall coronary artery disease." in stenosis['cadStenosisText'], f"Wrong CAD stenosis text: {stenosis['cadStenosisText']}"
assert "Model-estimated probabilities are statistical outputs, not measured anatomical stenosis percentages, confirmed disease severity, or validated clinical diagnostic findings." in stenosis['stenosisNoteText'], f"Wrong stenosis note: {stenosis['stenosisNoteText']}"
print("[PASS] Coronary Stenosis Interpretation panel text verified.")

exp = verification['explainability']
assert exp['catCount'] == 7, f"Expected 7 categories, got {exp['catCount']}"
assert "Basic Information" in exp['catItems'][0]
assert "Medical History" in exp['catItems'][1]
assert "Symptoms" in exp['catItems'][2]
assert "Vital Signs" in exp['catItems'][3]
assert "Laboratory Results" in exp['catItems'][4]
assert "ECG & Cardiac Findings" in exp['catItems'][5]
assert "Additional Clinical Findings" in exp['catItems'][6]
assert "Patient-specific feature attribution is not currently available. SHAP or other local explanation methods have not been computed." in exp['explainDesc'], f"Wrong explainDesc: {exp['explainDesc']}"
print("[PASS] All 7 feature categories and exact explainability notice verified.")

cards = verification['cards']
chart = verification['chart']
assert cards['cadPct'] == chart['chartCad'], f"CAD mismatch: card={cards['cadPct']}, chart={chart['chartCad']}"
assert cards['ladPct'] == chart['chartLad'], f"LAD mismatch: card={cards['ladPct']}, chart={chart['chartLad']}"
assert cards['lcxPct'] == chart['chartLcx'], f"LCX mismatch: card={cards['lcxPct']}, chart={chart['chartLcx']}"
assert cards['rcaPct'] == chart['chartRca'], f"RCA mismatch: card={cards['rcaPct']}, chart={chart['chartRca']}"
print(f"[PASS] Probability cards and chart values match exactly: CAD={cards['cadPct']}, LAD={cards['ladPct']}, LCX={cards['lcxPct']}, RCA={cards['rcaPct']}")

# Capture screenshots
artifact_dir = "C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779"
shot1 = os.path.join(artifact_dir, "results_screen_refined_active.png")
capture_screenshot(shot1)

# Test Stale warning
print("\n--- Testing Inputs Modified Warning ---")
eval_in_iframe("""
    const ageInp = doc.getElementById('inp_age');
    if (ageInp) {
        ageInp.value = '65';
        ageInp.dispatchEvent(new Event('input', { bubbles: true }));
        ageInp.dispatchEvent(new Event('change', { bubbles: true }));
    }
""")
stale_vis = eval_in_iframe("return doc.getElementById('resStaleNotice')?.style?.display !== 'none';")
assert stale_vis is True, "Stale warning banner not visible after input change!"
print("[PASS] Inputs Modified warning banner correctly displayed.")

shot2 = os.path.join(artifact_dir, "results_screen_refined_stale.png")
capture_screenshot(shot2)

# Test Reset All
print("\n--- Testing Reset All ---")
eval_in_iframe("if (typeof win.resetAll === 'function') win.resetAll();")
time.sleep(0.5)

reset_state = eval_in_iframe("""
    return {
        cadCardPct: doc.getElementById('resCadCardPct')?.textContent?.trim(),
        chartCadHeight: doc.getElementById('chartCadBar')?.style?.height,
        alertTitle: doc.getElementById('resMultiVesselTitle')?.textContent?.trim()
    };
""")
assert reset_state['cadCardPct'] == '—', f"Expected '—', got {reset_state['cadCardPct']}"
assert reset_state['chartCadHeight'] == '0%', f"Expected '0%', got {reset_state['chartCadHeight']}"
assert reset_state['alertTitle'] == 'Awaiting Model Prediction', f"Expected 'Awaiting Model Prediction', got {reset_state['alertTitle']}"
print("[PASS] Reset All correctly restores Awaiting Prediction state across all cards and chart.")

shot3 = os.path.join(artifact_dir, "results_screen_refined_awaiting.png")
capture_screenshot(shot3)

# Re-predict to leave clean active state
eval_in_iframe("if (typeof win.predictRisk === 'function') win.predictRisk();")
time.sleep(1.8)
shot4 = os.path.join(artifact_dir, "results_screen_refined_final.png")
capture_screenshot(shot4)

print("\n=== ALL FINAL REFINEMENT TESTS PASSED PERFECTLY ===")
ws.close()
