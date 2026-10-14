import json, urllib.request, websocket, re

with open(r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\viewer.html', 'r', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'"filename":\s*"([^"]+)"', text)

ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

b_id = 0
def b_cmd(method, params=None):
    global b_id
    b_id += 1
    b_ws.send(json.dumps({'id': b_id, 'method': method, 'params': params or {}}))
    while True:
        r = json.loads(b_ws.recv())
        if r.get('id') == b_id: return r

res = b_cmd('Target.createTarget', {'url': 'http://localhost:8000/viewer.html'})
target_id = res['result']['targetId']

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
tab = [t for t in tabs if t.get('id') == target_id][0]
t_ws = websocket.create_connection(tab['webSocketDebuggerUrl'], suppress_origin=True)

test_script = f"""
(async () => {{
    const list = {json.dumps(entries)};
    const results = [];
    for (const f of list) {{
        const url = './models/' + encodeURIComponent(f);
        try {{
            const r = await fetch(url);
            if (!r.ok) results.push({{ file: f, status: r.status, text: r.statusText }});
        }} catch(e) {{
            results.push({{ file: f, error: e.toString() }});
        }}
    }}
    return results;
}})()
"""

t_ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': test_script, 'returnByValue': True, 'awaitPromise': True}}))
while True:
    r = json.loads(t_ws.recv())
    if r.get('id') == 1:
        bad = r['result']['result']['value']
        print(f'Browser fetch failures: {len(bad)}')
        for b in bad:
            print(' ', b)
        break

t_ws.close()
b_cmd('Target.closeTarget', {'targetId': target_id})
b_ws.close()
