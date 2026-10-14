import json
import urllib.request
import websocket

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
t = [x for x in tabs if '8501' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], suppress_origin=True)

expr = """
(() => {
    const iframe = document.querySelector('iframe');
    if (!iframe) return { error: 'no iframe' };
    const win = iframe.contentWindow;
    const doc = iframe.contentDocument;
    if (!win || !doc) return { error: 'no win or doc' };
    const fn = win.exportClinicalReport ? win.exportClinicalReport.toString() : null;
    return {
        hasExportFn: !!fn,
        hasResearchPrototype: fn ? fn.includes('Research Prototype Record') : false,
        hasConfidential: fn ? fn.includes('Confidential Prototype Record') : false,
        hasSheetBody: fn ? fn.includes('sheetBody') : false,
        hasHeight274: fn ? fn.includes('height: 274mm') : false,
        title: doc.title,
        bodyLen: doc.body ? doc.body.innerHTML.length : 0
    };
})()
"""

req = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True}}
ws.send(json.dumps(req))
res = json.loads(ws.recv())
print(res.get('result', {}).get('result', {}).get('value'))
ws.close()
