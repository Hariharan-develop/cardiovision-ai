import json
import base64
import time
import urllib.request
import websocket
import os
import sys

# Ensure UTF-8 output on Windows consoles
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

# 1. Reload the page to ensure freshest Streamlit / iframe load
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

# 3. Switch to Results & Analysis view
print("\n--- Navigating to Results View ---")
nav_res = eval_in_iframe("""
    if (typeof win.switchNav === 'function') {
        win.switchNav('results');
        return {
            switched: true,
            resultsDisplay: doc.getElementById('view-results')?.style.display,
            activeNav: doc.querySelector('.navItem.active')?.dataset?.view
        };
    }
    return { switched: false };
""")
print("Nav result:", nav_res)
time.sleep(0.8)

# 4. Verify all Elements in Results & Analysis View
print("\n--- Verifying Results & Analysis Screen Content ---")
verification = eval_in_iframe("""
    const resView = doc.getElementById('view-results');
    if (!resView) return { error: 'view-results not found' };

    // 1. Header
    const h2 = resView.querySelector('.viewTitleBox h2')?.textContent?.trim();
    const sub = resView.querySelector('.viewTitleBox p')?.textContent?.trim();
    const exportBtn = !!doc.querySelector('.exportReportBtn');

    // 2. Patient Summary Bar
    const patName = doc.getElementById('resPatientName')?.textContent?.trim();
    const patId = doc.getElementById('resPatientId')?.textContent?.trim();
    const patDemo = doc.getElementById('resDemographics')?.textContent?.trim();
    const patDate = doc.getElementById('resDate')?.textContent?.trim();
    const patCad = doc.getElementById('resRiskSummary')?.textContent?.trim();

    // 3. Four Prediction Cards
    const cadCard = {
        pct: doc.getElementById('resCadCardPct')?.textContent?.trim(),
        label: doc.getElementById('resCadClassBadge')?.textContent?.trim(),
        tier: doc.getElementById('resCadTierBadge')?.textContent?.trim(),
        tierClass: doc.getElementById('resCadTierBadge')?.className,
        offset: doc.getElementById('resCadCircleBar')?.style?.strokeDashoffset
    };
    const ladCard = {
        pct: doc.getElementById('resLadCardPct')?.textContent?.trim(),
        label: doc.getElementById('resLadClassBadge')?.textContent?.trim(),
        tier: doc.getElementById('resLadTierBadge')?.textContent?.trim(),
        tierClass: doc.getElementById('resLadTierBadge')?.className,
        offset: doc.getElementById('resLadCircleBar')?.style?.strokeDashoffset
    };
    const lcxCard = {
        pct: doc.getElementById('resLcxCardPct')?.textContent?.trim(),
        label: doc.getElementById('resLcxClassBadge')?.textContent?.trim(),
        tier: doc.getElementById('resLcxTierBadge')?.textContent?.trim(),
        tierClass: doc.getElementById('resLcxTierBadge')?.className,
        offset: doc.getElementById('resLcxCircleBar')?.style?.strokeDashoffset
    };
    const rcaCard = {
        pct: doc.getElementById('resRcaCardPct')?.textContent?.trim(),
        label: doc.getElementById('resRcaClassBadge')?.textContent?.trim(),
        tier: doc.getElementById('resRcaTierBadge')?.textContent?.trim(),
        tierClass: doc.getElementById('resRcaTierBadge')?.className,
        offset: doc.getElementById('resRcaCircleBar')?.style?.strokeDashoffset
    };

    // 4. Comparison Bar Chart
    const chartBars = {
        cad: { val: doc.getElementById('chartCadVal')?.textContent?.trim(), height: doc.getElementById('chartCadBar')?.style?.height },
        lad: { val: doc.getElementById('chartLadVal')?.textContent?.trim(), height: doc.getElementById('chartLadBar')?.style?.height },
        lcx: { val: doc.getElementById('chartLcxVal')?.textContent?.trim(), height: doc.getElementById('chartLcxBar')?.style?.height },
        rca: { val: doc.getElementById('chartRcaVal')?.textContent?.trim(), height: doc.getElementById('chartRcaBar')?.style?.height }
    };

    // 5. Interpretation & Educational Guidance
    const stenosisTitle = resView.querySelector('.resTwoColGrid .tableCard:first-child h3')?.textContent?.trim();
    const guidanceTitle = resView.querySelector('.resTwoColGrid .tableCard:nth-child(2) h3')?.textContent?.trim();
    const multiVesselTitle = doc.getElementById('resMultiVesselTitle')?.textContent?.trim();
    const multiVesselText = doc.getElementById('resMultiVesselText')?.textContent?.trim();

    // 6. Model Performance Table
    const perfRows = Array.from(doc.querySelectorAll('.perfTable tbody tr')).map(tr => {
        const tds = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
        return { model: tds[0], target: tds[1], acc: tds[2], f1: tds[3], auc: tds[4] };
    });
    const cautionText = doc.querySelector('.cautionNotice')?.textContent?.trim();

    // 7. Explainability Section
    const explainTitle = doc.querySelector('.explainCard .resSectionTitle')?.textContent?.trim();
    const explainStatus = doc.querySelector('.explainStatusDesc')?.textContent?.trim();

    // 8. Stale Warning Notice
    const staleDisplay = doc.getElementById('resStaleNotice')?.style?.display;

    return {
        header: { h2, sub, exportBtn },
        patientBar: { patName, patId, patDemo, patDate, patCad },
        cards: { cadCard, ladCard, lcxCard, rcaCard },
        chart: chartBars,
        stenosisTitle,
        guidanceTitle,
        multiVesselAlert: { title: multiVesselTitle, text: multiVesselText },
        perfRows,
        cautionText,
        explainability: { title: explainTitle, status: explainStatus },
        staleDisplay
    };
""")

print("\n--- VERIFICATION RESULTS ---")
print(json.dumps(verification, indent=2))

# Capture full desktop screenshot
artifact_dir = "C:/Users/hario/.gemini/antigravity-ide/brain/10a2f2a8-1e30-4f80-bb7e-ccaa5ea8f779"
shot1 = os.path.join(artifact_dir, "results_screen_initial.png")
capture_screenshot(shot1)

# 5. Test Stale State: modify an input and verify warning
print("\n--- Testing Stale State Notification ---")
stale_test = eval_in_iframe("""
    // Modify age input
    const ageInp = doc.getElementById('inp_age');
    if (ageInp) {
        ageInp.value = '64';
        ageInp.dispatchEvent(new Event('input', { bubbles: true }));
        ageInp.dispatchEvent(new Event('change', { bubbles: true }));
    }
    const resNotice = doc.getElementById('resStaleNotice');
    return {
        modifiedAge: ageInp?.value,
        resNoticeDisplay: resNotice?.style?.display,
        resNoticeVisible: resNotice && resNotice.style.display !== 'none',
        noticeText: resNotice?.textContent?.trim()
    };
""")
print("Stale test result:", stale_test)
shot2 = os.path.join(artifact_dir, "results_screen_stale_warning.png")
capture_screenshot(shot2)

# 6. Test Prediction Recalculation
print("\n--- Testing Prediction Recalculation ---")
eval_in_iframe("""
    if (typeof win.predictRisk === 'function') {
        win.predictRisk();
    }
""")
time.sleep(1.8)

pred_updated = eval_in_iframe("""
    const resNotice = doc.getElementById('resStaleNotice');
    return {
        resNoticeDisplay: resNotice?.style?.display,
        cadPct: doc.getElementById('resCadCardPct')?.textContent?.trim(),
        cadBar: doc.getElementById('chartCadBar')?.style?.height,
        chartCadVal: doc.getElementById('chartCadVal')?.textContent?.trim(),
        cadTier: doc.getElementById('resCadTierBadge')?.textContent?.trim(),
        patCad: doc.getElementById('resRiskSummary')?.textContent?.trim()
    };
""")
print("Prediction update result:", pred_updated)
shot3 = os.path.join(artifact_dir, "results_screen_after_predict.png")
capture_screenshot(shot3)

# 7. Test Reset All (Awaiting State)
print("\n--- Testing Reset All (Awaiting State) ---")
eval_in_iframe("""
    if (typeof win.resetAll === 'function') {
        win.resetAll();
    }
""")
time.sleep(0.5)

awaiting_state = eval_in_iframe("""
    return {
        resCadPct: doc.getElementById('resCadCardPct')?.textContent?.trim(),
        resLadPct: doc.getElementById('resLadCardPct')?.textContent?.trim(),
        resLcxPct: doc.getElementById('resLcxCardPct')?.textContent?.trim(),
        resRcaPct: doc.getElementById('resRcaCardPct')?.textContent?.trim(),
        resCadBadge: doc.getElementById('resCadClassBadge')?.textContent?.trim(),
        resCadTier: doc.getElementById('resCadTierBadge')?.textContent?.trim(),
        chartCadHeight: doc.getElementById('chartCadBar')?.style?.height,
        resRiskSummary: doc.getElementById('resRiskSummary')?.textContent?.trim(),
        alertTitle: doc.getElementById('resMultiVesselTitle')?.textContent?.trim()
    };
""")
print("Awaiting state result:", awaiting_state)
shot4 = os.path.join(artifact_dir, "results_screen_after_reset.png")
capture_screenshot(shot4)

# 8. Re-predict to leave the screen in a clean evaluated state
print("\n--- Re-predicting to restore fresh active prediction ---")
eval_in_iframe("""
    if (typeof win.predictRisk === 'function') {
        win.predictRisk();
    }
""")
time.sleep(1.8)
shot5 = os.path.join(artifact_dir, "results_screen_final_verified.png")
capture_screenshot(shot5)

print("\n=== ALL RESULTS SCREEN AUTOMATED TESTS COMPLETE ===")
ws.close()
