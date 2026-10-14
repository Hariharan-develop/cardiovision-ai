import urllib.request, json, websocket, base64

with open("test_output/extraction_tests/test1_text_medical.pdf", "rb") as f:
    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

with urllib.request.urlopen("http://127.0.0.1:9222/json") as res:
    tabs = json.loads(res.read().decode())
t = next(t for t in tabs if "8502" in t.get("url", ""))
ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)

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

def eval_js(expr):
    res = send_cmd("Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    })
    return res

script = f"""
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
        
        // Listen for extraction result
        uploadPatientReportFile(file);
        
        let attempts = 0;
        const interval = setInterval(() => {{
            attempts++;
            const rev = document.getElementById('extractionReviewContainer');
            if (rev && rev.style.display !== 'none') {{
                clearInterval(interval);
                resolve({{
                    success: true,
                    rows: document.querySelectorAll('.reviewTableRow').length,
                    filename: document.getElementById('extractDocFilename') ? document.getElementById('extractDocFilename').textContent : ''
                }});
            }} else if (attempts > 30) {{
                clearInterval(interval);
                const errBox = document.getElementById('uploadErrorBox');
                const errMsg = document.getElementById('uploadErrorMsg');
                resolve({{
                    success: false,
                    error: errBox ? errMsg.textContent : 'Timeout',
                    display: rev ? rev.style.display : 'no rev container'
                }});
            }}
        }}, 200);
    }} catch(e) {{
        reject(e.toString());
    }}
}})
"""

res = eval_js(script)
print("Result:", json.dumps(res, indent=2))
ws.close()
