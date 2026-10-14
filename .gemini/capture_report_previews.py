import json
import base64
import urllib.request
import websocket
import time
import os

with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/test_report_pdf_exact.py', 'r') as f:
    code = f.read()

# Let's inspect report_275mm.pdf by loading it in Chrome
ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

def b_cmd(method, params=None):
    b_ws.send(json.dumps({'id': 100, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(b_ws.recv())
        if resp.get('id') == 100:
            return resp

# Read sample html from test script output or load test_275mm.html
# Let's create an HTML file for screen preview
from test_report_pdf_exact import sample_html

preview_css = """
<style>
  @media screen {
    body {
      background: #e2e8f0;
      padding: 20px;
      margin: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .reportSheet {
      background: #fff;
      width: 210mm;
      height: 297mm;
      max-height: 297mm;
      box-sizing: border-box;
      margin: 0 0 30px 0;
      padding: 10mm 14mm 10mm 14mm;
      box-shadow: 0 4px 18px rgba(0,0,0,0.15);
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .sheetBody {
      flex: 0 0 auto;
    }
    .pageFooter {
      margin-top: auto;
      flex-shrink: 0;
    }
    .noPrintBar {
      display: none;
    }
  }
  @media print {
    html, body {
      margin: 0 !important;
      padding: 0 !important;
      background: #fff !important;
    }
    .reportSheet {
      width: 100% !important;
      height: 275mm !important;
      max-height: 275mm !important;
      min-height: 275mm !important;
      margin: 0 !important;
      padding: 0 !important;
      box-shadow: none !important;
      border-radius: 0 !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: space-between !important;
      box-sizing: border-box !important;
    }
    .sheetBody {
      flex: 0 0 auto !important;
    }
    .pageFooter {
      margin-top: auto !important;
      flex-shrink: 0 !important;
    }
    .page-2 {
      page-break-before: always !important;
      break-before: page !important;
      padding-top: 0 !important;
    }
    .noPrint, .noPrintBar {
      display: none !important;
    }
  }
</style>
"""

final_html = sample_html.replace('</head>', f'{preview_css}</head>')
preview_file = 'c:/Users/hario/Downloads/CardioVision-AI/.gemini/report_preview.html'
with open(preview_file, 'w', encoding='utf-8') as f:
    f.write(final_html)

new_t = b_cmd("Target.createTarget", {"url": f"file:///{preview_file}"})
target_id = new_t['result']['targetId']

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
target_tab = [t for t in tabs if t.get('id') == target_id][0]
t_ws = websocket.create_connection(target_tab['webSocketDebuggerUrl'], suppress_origin=True)

msg_id = 0
def t_cmd(method, params=None):
    global msg_id
    msg_id += 1
    t_ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(t_ws.recv())
        if resp.get('id') == msg_id:
            return resp

t_cmd("Page.enable")
t_cmd("Runtime.enable")
t_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1000,
    "height": 2600,
    "deviceScaleFactor": 1,
    "mobile": False
})
time.sleep(0.5)

# Screenshot page 1 and page 2
# Get box model of page-1
box1 = t_cmd("Runtime.evaluate", {
    "expression": """
    (() => {
        const p1 = document.querySelector('.page-1');
        const r = p1.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
    })()
    """,
    "returnByValue": True
})
r1 = box1['result']['result']['value']
print("Page 1 rect:", r1)

box2 = t_cmd("Runtime.evaluate", {
    "expression": """
    (() => {
        const p2 = document.querySelector('.page-2');
        const r = p2.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
    })()
    """,
    "returnByValue": True
})
r2 = box2['result']['result']['value']
print("Page 2 rect:", r2)

# Screenshot Page 1
ss1 = t_cmd("Page.captureScreenshot", {
    "clip": { "x": r1['x'], "y": r1['y'], "width": r1['width'], "height": r1['height'], "scale": 1 }
})
img1_data = base64.b64decode(ss1['result']['data'])
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/page1_preview.png', 'wb') as pf:
    pf.write(img1_data)
print("Saved page1_preview.png")

# Screenshot Page 2
ss2 = t_cmd("Page.captureScreenshot", {
    "clip": { "x": r2['x'], "y": r2['y'], "width": r2['width'], "height": r2['height'], "scale": 1 }
})
img2_data = base64.b64decode(ss2['result']['data'])
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/page2_preview.png', 'wb') as pf:
    pf.write(img2_data)
print("Saved page2_preview.png")

# Also let's check positions of footer relative to sheet bottom
footer_pos = t_cmd("Runtime.evaluate", {
    "expression": """
    (() => {
        const p2 = document.querySelector('.page-2');
        const f2 = p2.querySelector('.pageFooter');
        const rPage = p2.getBoundingClientRect();
        const rFoot = f2.getBoundingClientRect();
        return {
            pageHeight: rPage.height,
            footerBottomRelativeToPage: rFoot.bottom - rPage.top,
            gapBelowFooter: rPage.bottom - rFoot.bottom
        };
    })()
    """,
    "returnByValue": True
})
print("Footer 2 metric:", footer_pos['result']['result']['value'])

t_ws.close()
b_cmd("Target.closeTarget", {"targetId": target_id})
b_ws.close()
print("Done capturing previews!")
