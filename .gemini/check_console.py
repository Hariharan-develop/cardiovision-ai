import json, urllib.request, websocket, time

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

t_cmd('Console.enable')
t_cmd('Runtime.enable')

# Collect console messages for 5 seconds
start = time.time()
while time.time() - start < 6.0:
    msg = json.loads(t_ws.recv())
    if msg.get('method') == 'Runtime.consoleAPICalled':
        args = [a.get('value', a.get('description', '')) for a in msg.get('params', {}).get('args', [])]
        print('CONSOLE:', msg['params']['type'], *args)

t_ws.close()
b_cmd('Target.closeTarget', {'targetId': target_id})
b_ws.close()
