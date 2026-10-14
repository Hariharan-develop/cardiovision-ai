import json, urllib.request, websocket, base64, time, sys
sys.stdout.reconfigure(encoding='utf-8')

ver_res = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/version').read().decode())
b_ws = websocket.create_connection(ver_res['webSocketDebuggerUrl'], suppress_origin=True)

msg_id = 0
def b_cmd(method, params=None):
    global msg_id
    msg_id += 1
    b_ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
    while True:
        r = json.loads(b_ws.recv())
        if r.get('id') == msg_id: return r

res = b_cmd('Target.createTarget', {'url': 'http://localhost:8000/viewer.html'})
target_id = res['result']['targetId']

tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
tab = [t for t in tabs if t.get('id') == target_id][0]
t_ws = websocket.create_connection(tab['webSocketDebuggerUrl'], suppress_origin=True)

t_id = 0
def t_cmd(method, params=None):
    global t_id
    t_id += 1
    t_ws.send(json.dumps({'id': t_id, 'method': method, 'params': params or {}}))
    while True:
        r = json.loads(t_ws.recv())
        if r.get('id') == t_id: return r

t_cmd('Page.enable')
t_cmd('Runtime.enable')

# Wait for meshes to load: poll until status text says '39/39'
for i in range(20):
    time.sleep(1.0)
    status_res = t_cmd('Runtime.evaluate', {'expression': "document.querySelector('#status')?.textContent || ''", 'returnByValue': True})
    txt = status_res['result']['result']['value']
    print(f'Loading status [{i+1}s]: {txt}')
    if '39/39' in txt:
        break

time.sleep(1.0)
ss = t_cmd('Page.captureScreenshot')
img_bytes = base64.b64decode(ss['result']['data'])
with open('c:/Users/hario/Downloads/CardioVision-AI/.gemini/current_viewer_initial.png', 'wb') as f:
    f.write(img_bytes)

print('Saved current_viewer_initial.png')
t_ws.close()
b_cmd('Target.closeTarget', {'targetId': target_id})
b_ws.close()
