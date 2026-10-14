import json, urllib.request, websocket, time

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

t_id = 0
def t_cmd(method, params=None):
    global t_id
    t_id += 1
    t_ws.send(json.dumps({'id': t_id, 'method': method, 'params': params or {}}))
    while True:
        r = json.loads(t_ws.recv())
        if r.get('id') == t_id: return r

t_cmd('Runtime.enable')

# Wait for loading to finish
time.sleep(3.0)

# Check which filenames are NOT in loaded
check_js = """
(() => {
    // Check entries against loaded
    const loadedFilenames = new Set(loaded.map(o => o.userData.filename));
    const failed = entries.filter(e => !loadedFilenames.has(e.filename));
    return failed;
})()
"""
res = t_cmd('Runtime.evaluate', {'expression': check_js, 'returnByValue': True})
failed_entries = res['result']['result']['value']
print(f'Failed entries ({len(failed_entries)}):')
for f in failed_entries:
    print(' ', f['id'], ':', f['filename'])

# Also let's test fetching one of the failed files directly via fetch() inside the browser!
if failed_entries:
    fetch_test_js = f"""
    (async () => {{
        const url = './models/' + encodeURIComponent({json.dumps(failed_entries[0]['filename'])});
        try {{
            const resp = await fetch(url);
            return {{ status: resp.status, statusText: resp.statusText }};
        }} catch(e) {{
            return {{ error: e.toString() }};
        }}
    }})()
    """
    fetch_res = t_cmd('Runtime.evaluate', {'expression': fetch_test_js, 'returnByValue': True, 'awaitPromise': True})
    print('Fetch test in browser:', fetch_res['result']['result']['value'])

t_ws.close()
b_cmd('Target.closeTarget', {'targetId': target_id})
b_ws.close()
