import json, urllib.request, websocket, base64, time, os

print("=== Validating Complete CardioVision AI 3D Heart Model ===")

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

# Create test tab for http://localhost:8000/viewer.html
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

# Set high-resolution viewport (1920x1080)
t_cmd('Emulation.setDeviceMetricsOverride', {
    'width': 1600, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False
})

print("Waiting for all meshes to load...")
final_status = ""
for i in range(30):
    time.sleep(1.0)
    status_res = t_cmd('Runtime.evaluate', {
        'expression': "document.querySelector('#status')?.textContent || ''",
        'returnByValue': True
    })
    txt = status_res['result']['result']['value']
    print(f"[{i+1}s] {txt}")
    final_status = txt
    if "Complete heart loaded" in txt or ("65/65" in txt and "0 failed" in txt):
        break

time.sleep(1.0)

# Check count of loaded meshes in Three.js
stats_res = t_cmd('Runtime.evaluate', {
    'expression': """
    (() => {
        return {
            totalEntries: entries.length,
            loadedCount: loaded.length,
            failures: failures,
            statusText: document.querySelector('#status')?.textContent || ''
        };
    })()
    """,
    'returnByValue': True
})
stats = stats_res['result']['result']['value']
print("\nLoading statistics:", stats)
assert stats['loadedCount'] == 65, f"Expected 65 meshes, got {stats['loadedCount']}"
assert stats['failures'] == 0, f"Expected 0 failures, got {stats['failures']}"

# Directory for screenshots
ss_dir = r'c:\Users\hario\Downloads\CardioVision-AI\.gemini\heart_views'
os.makedirs(ss_dir, exist_ok=True)

views = ['front', 'back', 'left', 'right', 'top', 'bottom']
for v in views:
    t_cmd('Runtime.evaluate', {'expression': f"setView('{v}')"})
    time.sleep(0.6)
    ss = t_cmd('Page.captureScreenshot')
    img_data = base64.b64decode(ss['result']['data'])
    path = os.path.join(ss_dir, f'view_{v}.png')
    with open(path, 'wb') as f: f.write(img_data)
    print(f"Saved view: {path}")

# Test Coronary Focus Preset
print("\nTesting Coronary Focus Preset...")
t_cmd('Runtime.evaluate', {'expression': "applyPreset('coronary'); setView('front');"})
time.sleep(0.7)
ss_coronary = t_cmd('Page.captureScreenshot')
path_coronary = os.path.join(ss_dir, 'preset_coronary_focus.png')
with open(path_coronary, 'wb') as f: f.write(base64.b64decode(ss_coronary['result']['data']))
print(f"Saved coronary focus preset view: {path_coronary}")

# Test Complete Heart Preset
print("\nTesting Complete Heart Preset...")
t_cmd('Runtime.evaluate', {'expression': "applyPreset('complete'); setView('front');"})
time.sleep(0.7)
ss_complete = os.path.join(ss_dir, 'preset_complete_heart.png')
with open(ss_complete, 'wb') as f: f.write(base64.b64decode(t_cmd('Page.captureScreenshot')['result']['data']))
print(f"Saved complete heart preset view: {ss_complete}")

# Test Artery Click Selection
print("\nTesting Artery Click Identification...")
select_res = t_cmd('Runtime.evaluate', {
    'expression': """
    (() => {
        // Find LAD trunk mesh
        const ladMesh = loaded.find(o => o.userData.id === 'MM420');
        if (ladMesh) {
            let meshChild = null;
            ladMesh.traverse(c => { if (c.isMesh) meshChild = c; });
            selectMesh(meshChild || ladMesh);
        }
        return {
            selectedHtml: document.querySelector('#detail')?.innerHTML || '',
            selectedText: document.querySelector('#detail')?.innerText || ''
        };
    })()
    """,
    'returnByValue': True
})
sel = select_res['result']['result']['value']
print("Selected text in inspector:", sel['selectedText'].replace('\n', ' -- '))
assert 'LAD' in sel['selectedText'], "LAD not identified in detail inspector card!"

time.sleep(0.5)
ss_selected = os.path.join(ss_dir, 'artery_selected_inspection.png')
with open(ss_selected, 'wb') as f: f.write(base64.b64decode(t_cmd('Page.captureScreenshot')['result']['data']))
print(f"Saved selection inspection view: {ss_selected}")

t_ws.close()
b_cmd('Target.closeTarget', {'targetId': target_id})
b_ws.close()

print("\n=== ALL 3D HEART MODEL VALIDATIONS COMPLETED SUCCESSFULLY ===")
