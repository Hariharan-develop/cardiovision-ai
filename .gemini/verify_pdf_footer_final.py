import json
import base64
import urllib.request
import websocket
import time
import re
import os

print("--- Step 1: Connecting to Chrome CDP ---")
ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

msg_id = 0
def b_cmd(method, params=None):
    global msg_id
    msg_id += 1
    b_ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(b_ws.recv())
        if resp.get('id') == msg_id:
            return resp

# Find localhost:8501 tab
tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
app_tab = next((t for t in tabs if 'localhost:8501' in t.get('url', '')), None)
assert app_tab, "localhost:8501 tab not found!"

tab_ws = websocket.create_connection(app_tab['webSocketDebuggerUrl'], suppress_origin=True)
tab_msg_id = 0
def app_cmd(method, params=None):
    global tab_msg_id
    tab_msg_id += 1
    tab_ws.send(json.dumps({'id': tab_msg_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(tab_ws.recv())
        if resp.get('id') == tab_msg_id:
            return resp

app_cmd("Page.enable")
app_cmd("Runtime.enable")

print("--- Step 2: Reloading Streamlit tab ---")
app_cmd("Page.reload", {"ignoreCache": True})
time.sleep(3.0)

# Evaluate in iframe to get report HTML directly without opening print dialog
get_report_js = """
(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe || !iframe.contentDocument) return { error: 'No iframe' };
    const win = iframe.contentWindow;
    const doc = iframe.contentDocument;

    // Call exportClinicalReport logic to construct reportHtml without window.open
    const pat = win.getPatientDetails ? win.getPatientDetails() : { id: 'CV-2024-8841', displayName: 'Jane Doe' };
    const age = doc.getElementById('inp_age')?.value || 58;
    const sex = doc.getElementById('inp_sex')?.value || 'Male';
    const length = doc.getElementById('inp_length')?.value || 170;
    const weight = doc.getElementById('inp_weight')?.value || 72;
    const bmi = doc.getElementById('inp_bmi')?.value || '24.9';
    const bp = doc.getElementById('inp_bp')?.value || 130;
    const pr = doc.getElementById('inp_pr')?.value || 70;
    const ef = doc.getElementById('inp_ef_tte')?.value || 50;
    const fbs = doc.getElementById('inp_fbs')?.value || 98;
    const cr = doc.getElementById('inp_cr')?.value || 1.0;
    const ldl = doc.getElementById('inp_ldl')?.value || 100;
    const hdl = doc.getElementById('inp_hdl')?.value || 39;
    const tg = doc.getElementById('inp_tg')?.value || 122;

    const cadRisk = doc.getElementById('cadRiskNum')?.textContent || '78.4%';
    const cadLbl = doc.getElementById('cadLabelText')?.textContent || 'High Risk';
    const ladRisk = doc.getElementById('ladRiskNum')?.textContent || '62.1%';
    const ladLbl = doc.getElementById('ladLabelText')?.textContent || 'Elevated';
    const lcxRisk = doc.getElementById('lcxRiskNum')?.textContent || '41.3%';
    const lcxLbl = doc.getElementById('lcxLabelText')?.textContent || 'Moderate';
    const rcaRisk = doc.getElementById('rcaRiskNum')?.textContent || '35.0%';
    const rcaLbl = doc.getElementById('rcaLabelText')?.textContent || 'Low Risk';

    // Verify what exportClinicalReport contains
    const fnStr = win.exportClinicalReport ? win.exportClinicalReport.toString() : '';
    return {
        hasFn: !!win.exportClinicalReport,
        hasResearchPrototype: fnStr.includes('Research Prototype Record'),
        hasConfidential: fnStr.includes('Confidential Prototype Record'),
        hasSheetBody: fnStr.includes('sheetBody'),
        hasHeight274: fnStr.includes('height: 274mm'),
        fnLength: fnStr.length
    };
})()
"""

print("--- Step 2: Waiting for Streamlit iframe to mount ---")
diag = {}
for i in range(25):
    time.sleep(1.0)
    res = app_cmd("Runtime.evaluate", {"expression": get_report_js, "returnByValue": True})
    val = res.get('result', {}).get('result', {}).get('value', {})
    if val and 'error' not in val:
        diag = val
        print(f"Iframe ready after {i+1}s")
        break

print("Iframe diagnosis:", diag)

assert diag.get('hasFn'), "exportClinicalReport function not found in iframe!"
assert diag.get('hasResearchPrototype'), "Research Prototype Record not found in exportClinicalReport!"
assert not diag.get('hasConfidential'), "Confidential Prototype Record still present in exportClinicalReport!"
assert diag.get('hasSheetBody'), "sheetBody wrapper not found in exportClinicalReport!"
assert diag.get('hasHeight274'), "height: 274mm not found in exportClinicalReport!"

print("--- Step 3: Extract report HTML directly from template ---")
with open('c:/Users/hario/Downloads/CardioVision-AI/cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

m = re.search(r'const reportHtml = `(.*?)`;', html_text, re.DOTALL)
assert m, "Could not extract reportHtml template from HTML file"
raw_report_html = m.group(1)

# Substitute real values for testing
subs = {
    '${pat.id}': 'CV-2024-8841',
    '${pat.displayName}': 'Jane Doe',
    '${age}': '58',
    '${sex}': 'Female',
    '${length}': '165',
    '${weight}': '68',
    '${bmi}': '25.0',
    '${bp}': '130',
    '${pr}': '72',
    '${ef}': '55',
    '${fbs}': '105',
    '${cr}': '1.0',
    '${crStatus}': 'Within displayed adult reference range (Informational)',
    '${ldl}': '112',
    '${hdl}': '48',
    '${tg}': '135',
    '${cadRisk}': '78.4%',
    '${cadLbl}': 'High Risk',
    '${ladRisk}': '62.1%',
    '${ladLbl}': 'Elevated',
    '${lcxRisk}': '41.3%',
    '${lcxLbl}': 'Moderate',
    '${rcaRisk}': '35.0%',
    '${rcaLbl}': 'Low Risk',
    '${reportDateTime}': 'Fri, Oct 10, 2026, 09:00 AM',
}
for k, v in subs.items():
    raw_report_html = raw_report_html.replace(k, v)

# Evaluate simple inline ternaries for realistic table layout
raw_report_html = re.sub(
    r"\$\{parseFloat\(bp\) >= 130 \? 'Above standard systolic reference \(≥ 130 mmHg, Informational\)' : [^}]+\}",
    "Above standard systolic reference (≥ 130 mmHg, Informational)",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(pr\) >= 60 && parseFloat\(pr\) <= 100 \? 'Within standard resting range' : [^}]+\}",
    "Within standard resting range",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(ef\) >= 50 \? 'LVEF ≥ 50% — interpret in clinical context' : [^}]+\}",
    "LVEF ≥ 50% — interpret in clinical context",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(fbs\) >= 126 \? [^:]+ : parseFloat\(fbs\) >= 100 \? 'Above standard fasting range \(100–125 mg/dL, Informational\)' : [^}]+\}",
    "Above standard fasting range (100–125 mg/dL, Informational)",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(ldl\) >= 100 \? 'Above standard reference \(≥ 100 mg/dL, Informational\)' : [^}]+\}",
    "Above standard reference (≥ 100 mg/dL, Informational)",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(hdl\) < 40 \? 'Below standard reference \(Informational\)' : [^}]+\}",
    "Within standard reference",
    raw_report_html
)
raw_report_html = re.sub(
    r"\$\{parseFloat\(tg\) >= 150 \? 'Above standard reference \(Informational\)' : [^}]+\}",
    "Within standard reference",
    raw_report_html
)

# Remove window.print() timeout script so test tab doesn't prompt dialog
clean_html = re.sub(r'<script>\s*window\.onload\s*=\s*function\(\)\s*\{.*?\}\s*;\s*</script>', '', raw_report_html, flags=re.DOTALL)

# Write clean report HTML to artifact file
report_out_path = 'c:/Users/hario/Downloads/CardioVision-AI/.gemini/verified_report.html'
with open(report_out_path, 'w', encoding='utf-8') as f:
    f.write(clean_html)
print(f"Wrote report HTML ({len(clean_html)} bytes) to {report_out_path}")

print("--- Step 4: Rendering in test tab & printing to PDF ---")
new_t = b_cmd("Target.createTarget", {"url": f"file:///{report_out_path}"})
t_id = new_t['result']['targetId']

tabs_list = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
target_tab = [t for t in tabs_list if t.get('id') == t_id][0]
t_ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)

test_msg_id = 0
def t_cmd(method, params=None):
    global test_msg_id
    test_msg_id += 1
    t_ws.send(json.dumps({'id': test_msg_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(t_ws.recv())
        if resp.get('id') == test_msg_id:
            return resp

t_cmd("Page.enable")
t_cmd("Runtime.enable")
time.sleep(0.5)

# A4 print to PDF
pdf_res = t_cmd("Page.printToPDF", {
    "paperWidth": 8.27, "paperHeight": 11.69,
    "marginTop": 0.39, "marginBottom": 0.39,
    "marginLeft": 0.55, "marginRight": 0.55,
    "printBackground": True, "preferCSSPageSize": True
})
pdf_bytes = base64.b64decode(pdf_res['result']['data'])
page_matches = re.findall(rb'/Type\s*/Page\b', pdf_bytes)
page_count = len(page_matches)
print(f"Generated PDF Size: {len(pdf_bytes)} bytes")
print(f"Total Page Count: {page_count} (Expected: exactly 2)")
assert page_count == 2, f"Expected exactly 2 pages, got {page_count}!"

pdf_save_path = 'c:/Users/hario/Downloads/CardioVision-AI/.gemini/CardioVision_Research_Report_Final.pdf'
with open(pdf_save_path, 'wb') as pf:
    pf.write(pdf_bytes)
print(f"Successfully saved final PDF to {pdf_save_path}")

print("--- Step 5: Screen Preview Evaluation & Visual Metric Checks ---")
# Check metrics in Screen Preview mode
t_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1050, "height": 2600, "deviceScaleFactor": 1, "mobile": False
})
time.sleep(0.3)

metrics = t_cmd("Runtime.evaluate", {
    "expression": """
    (() => {
        const p1 = document.querySelector('.page-1');
        const p2 = document.querySelector('.page-2');
        const f1 = p1.querySelector('.pageFooter');
        const f2 = p2.querySelector('.pageFooter');
        const rP1 = p1.getBoundingClientRect();
        const rP2 = p2.getBoundingClientRect();
        const rF1 = f1.getBoundingClientRect();
        const rF2 = f2.getBoundingClientRect();

        return {
            page1Height: rP1.height,
            page2Height: rP2.height,
            footer1Text: f1.innerText,
            footer2Text: f2.innerText,
            footer1GapBelow: Math.round(rP1.bottom - rF1.bottom),
            footer2GapBelow: Math.round(rP2.bottom - rF2.bottom),
            page2ContentBottom: Math.round(p2.querySelector('.sheetBody').getBoundingClientRect().bottom - rP2.top),
            page2FooterTop: Math.round(rF2.top - rP2.top)
        };
    })()
    """,
    "returnByValue": True
})
m_val = metrics['result']['result']['value']
print("Metrics analysis:", json.dumps(m_val, indent=2))

# Verify footers
assert "Research Prototype Record" in m_val['footer1Text'], "Page 1 footer missing 'Research Prototype Record'!"
assert "Page 1 of 2" in m_val['footer1Text']
assert "Page 2 of 2" in m_val['footer2Text']
assert m_val['footer2GapBelow'] == 38, f"Expected 38px (10mm) bottom padding on Page 2, got {m_val['footer2GapBelow']}"

# Capture screenshots of both pages
p1_box = t_cmd("Runtime.evaluate", {
    "expression": "(() => { const r = document.querySelector('.page-1').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()",
    "returnByValue": True
})['result']['result']['value']

p2_box = t_cmd("Runtime.evaluate", {
    "expression": "(() => { const r = document.querySelector('.page-2').getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })()",
    "returnByValue": True
})['result']['result']['value']

ss1 = t_cmd("Page.captureScreenshot", {"clip": {**p1_box, "scale": 1}})
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/final_page1_preview.png', 'wb') as pf:
    pf.write(base64.b64decode(ss1['result']['data']))

ss2 = t_cmd("Page.captureScreenshot", {"clip": {**p2_box, "scale": 1}})
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/final_page2_preview.png', 'wb') as pf:
    pf.write(base64.b64decode(ss2['result']['data']))

print("Saved final_page1_preview.png and final_page2_preview.png")

t_ws.close()
b_cmd("Target.closeTarget", {"targetId": t_id})
tab_ws.close()
b_ws.close()

print("\n=== ALL PDF FOOTER VERIFICATION CHECKS PASSED PERFECTLY ===")
