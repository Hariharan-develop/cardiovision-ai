import json
import urllib.request
import websocket
import time

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
t = [x for x in tabs if '8501' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], suppress_origin=True)

# Check url and iframes
req = {'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': """
(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    return {
        url: window.location.href,
        iframeCount: iframes.length,
        iframeSrcs: iframes.map(f => f.src || 'inline-srcdoc')
    };
})()
""", 'returnByValue': True}}

ws.send(json.dumps(req))
res = json.loads(ws.recv())
print(res.get('result', {}).get('result', {}).get('value'))
ws.close()
