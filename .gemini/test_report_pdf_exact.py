import re
import json
import base64
import urllib.request
import websocket
import time

# 1. Read cardiovision_exact_dashboard.html and extract reportHtml template
with open('c:/Users/hario/Downloads/CardioVision-AI/cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find exportClinicalReport function body
idx = content.find('function exportClinicalReport()')
assert idx != -1
report_fn = content[idx:idx+35000]

# Extract the template string inside reportHtml = `...`;
m = re.search(r'const reportHtml = `(.*?)`;', report_fn, re.DOTALL)
assert m, "Could not find reportHtml template"
raw_html = m.group(1)

# Replace template interpolation variables with realistic patient values
replacements = {
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

sample_html = raw_html
for k, v in replacements.items():
    sample_html = sample_html.replace(k, v)

# Update Confidential to Research Prototype Record
sample_html = sample_html.replace('Confidential Prototype Record', 'Research Prototype Record')

# Remove window.print auto script so test tab doesn't block
sample_html = re.sub(r'<script>\s*window\.onload\s*=\s*function\(\)\s*\{.*?\}\s*;\s*</script>', '', sample_html, flags=re.DOTALL)

# Wrap page-1 and page-2 content in sheetBody if not already wrapped
if 'class="sheetBody"' not in sample_html:
    # Page 1: wrap from after <div class="reportSheet page-1"> to before <!-- Page 1 Footer -->
    sample_html = sample_html.replace(
        '<div class="reportSheet page-1">\n  <div>',
        '<div class="reportSheet page-1">\n  <div class="sheetBody">'
    )
    # Page 2: wrap from after <div class="reportSheet page-2"> to before <!-- Page 2 Footer -->
    sample_html = sample_html.replace(
        '<div class="reportSheet page-2">\n  <div>',
        '<div class="reportSheet page-2">\n  <div class="sheetBody">'
    )

print("Sample HTML length:", len(sample_html))

# Connect to Chrome browser CDP
ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

def b_cmd(method, params=None):
    b_ws.send(json.dumps({'id': 999, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(b_ws.recv())
        if resp.get('id') == 999:
            return resp

test_heights = ["270mm", "272mm", "274mm", "275mm", "276mm", "277mm"]
for h in test_heights:
    # Prepare CSS with height h
    css_override = f"""
    <style id="test-override">
    @media print {{
      html, body {{
        margin: 0 !important;
        padding: 0 !important;
        background: #fff !important;
      }}
      .reportSheet {{
        width: 100% !important;
        height: {h} !important;
        max-height: {h} !important;
        min-height: {h} !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
      }}
      .sheetBody {{
        flex: 0 0 auto !important;
      }}
      .pageFooter {{
        margin-top: auto !important;
        flex-shrink: 0 !important;
      }}
      .page-2 {{
        page-break-before: always !important;
        break-before: page !important;
        padding-top: 0 !important;
      }}
      .noPrint, .noPrintBar {{
        display: none !important;
      }}
    }}
    </style>
    """
    html_variant = sample_html.replace('</head>', f'{css_override}</head>')

    # Create new target tab
    new_t = b_cmd("Target.createTarget", {"url": "about:blank"})
    target_id = new_t['result']['targetId']

    # Connect to target
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target_tab = [t for t in tabs if t.get('id') == target_id][0]
    t_ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)

    global t_id
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
    t_cmd("Runtime.evaluate", {
        "expression": f"document.open(); document.write({json.dumps(html_variant)}); document.close();"
    })
    time.sleep(0.3)

    pdf_res = t_cmd("Page.printToPDF", {
        "paperWidth": 8.27, "paperHeight": 11.69,
        "marginTop": 0.39, "marginBottom": 0.39,
        "marginLeft": 0.55, "marginRight": 0.55,
        "printBackground": True, "preferCSSPageSize": True
    })
    pdf_b64 = pdf_res.get("result", {}).get("data")
    pdf_bytes = base64.b64decode(pdf_b64)
    page_count = len(re.findall(rb'/Type\s*/Page\b', pdf_bytes))

    print(f"Height: {h:6s} -> PDF size: {len(pdf_bytes):6d} bytes, Page count: {page_count}")

    # Save 274mm and 275mm for visual inspection
    if h in ["274mm", "275mm"]:
        pdf_path = f"c:/Users/hario/Downloads/CardioVision-AI/.gemini/report_{h}.pdf"
        with open(pdf_path, "wb") as pf:
            pf.write(pdf_bytes)
        print(f"  Saved test PDF to {pdf_path}")

    t_ws.close()
    b_cmd("Target.closeTarget", {"targetId": target_id})

b_ws.close()
print("Done testing heights!")
