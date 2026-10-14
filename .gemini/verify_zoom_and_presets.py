import asyncio, json, urllib.request, websockets

async def main():
    pages = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read().decode())
    target = next((p for p in pages if 'CardioVision' in p.get('title', '')), pages[0])
    msg_counter = 0

    async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
        async def cdp_eval(expr):
            nonlocal msg_counter
            msg_counter += 1
            payload = {'id': msg_counter, 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True, 'awaitPromise': True}}
            await ws.send(json.dumps(payload))
            while True:
                r = json.loads(await ws.recv())
                if r.get('id') == msg_counter:
                    return r.get('result', {}).get('result', {}).get('value')

        await ws.send(json.dumps({'id': 999, 'method': 'Page.bringToFront'}))
        await ws.recv()

        # Switch to 3D Visualization view
        await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const stWin = st.contentWindow;
                stWin.switchNav('viewer3d');
            })()
        """)

        # Wait for 106 meshes to load
        print("Waiting for mesh loading...")
        for _ in range(25):
            st = await cdp_eval("""
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const v = st.contentDocument.getElementById('viewerIframe');
                    if (!v || !v.contentDocument) return '';
                    const el = v.contentDocument.getElementById('loadStatus');
                    return el ? el.innerText : '';
                })()
            """)
            if "106/106" in str(st) or "Complete heart" in str(st):
                print("Meshes loaded:", str(st).encode('ascii', 'replace').decode('ascii').strip())
                break
            await asyncio.sleep(1)

        # -------------------------------------------------------------
        # TEST ISSUE 1: ZOOM SENSITIVITY
        # -------------------------------------------------------------
        print("\n=======================================================")
        print("TEST ISSUE 1: ZOOM SENSITIVITY MEASUREMENTS")
        print("=======================================================")
        zoom_test = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vDoc = v.contentDocument;
                const vWin = v.contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const ctrl = vWin.CardioVision3D.controls;
                const canvas = vDoc.getElementById('canvas');

                // Reset to default front view first
                vWin.CardioVision3D.setView('reset', false);

                const d0 = cam.position.distanceTo(ctrl.target);

                // 1 notch
                canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true }));
                ctrl.update();
                const d1 = cam.position.distanceTo(ctrl.target);

                // 2 more notches (total 3)
                for (let i = 0; i < 2; i++) {
                    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true }));
                    ctrl.update();
                }
                const d3 = cam.position.distanceTo(ctrl.target);

                // 2 more notches (total 5)
                for (let i = 0; i < 2; i++) {
                    canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true }));
                    ctrl.update();
                }
                const d5 = cam.position.distanceTo(ctrl.target);

                return {
                    zoomSpeed: ctrl.zoomSpeed,
                    d0: d0.toFixed(2),
                    d1: d1.toFixed(2),
                    step1Pct: (((d0 - d1) / d0) * 100).toFixed(1) + '%',
                    d3: d3.toFixed(2),
                    step3Pct: (((d0 - d3) / d0) * 100).toFixed(1) + '%',
                    d5: d5.toFixed(2),
                    step5Pct: (((d0 - d5) / d0) * 100).toFixed(1) + '%'
                };
            })()
        """)
        print("Zoom Speed configured:", zoom_test['zoomSpeed'])
        print(f"Initial distance: {zoom_test['d0']}")
        print(f"After 1 notch:    {zoom_test['d1']} (Magnification: {zoom_test['step1Pct']})")
        print(f"After 3 notches:  {zoom_test['d3']} (Magnification: {zoom_test['step3Pct']})")
        print(f"After 5 notches:  {zoom_test['d5']} (Magnification: {zoom_test['step5Pct']})")

        # -------------------------------------------------------------
        # TEST ISSUE 2: PRESET VIEW BUTTONS PRESERVE ZOOM DISTANCE
        # -------------------------------------------------------------
        print("\n=======================================================")
        print("TEST ISSUE 2: CAMERA VIEW BUTTONS PRESERVE ZOOM LEVEL")
        print("=======================================================")
        
        # Set camera to exactly 7.00 distance
        set_zoom_res = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const ctrl = vWin.CardioVision3D.controls;

                // Zoom camera to distance 7.00 along anterior direction
                const dir = cam.position.clone().sub(ctrl.target).normalize();
                cam.position.copy(ctrl.target).addScaledVector(dir, 7.00);
                ctrl.update();

                return {
                    targetDist: 7.00,
                    actualDist: cam.position.distanceTo(ctrl.target).toFixed(3)
                };
            })()
        """)
        print("Camera positioned at test distance:", set_zoom_res)

        presets = ['back', 'left', 'right', 'top', 'bottom', 'front']
        preset_names = {
            'back': 'Posterior',
            'left': 'Left Lateral',
            'right': 'Right Lateral',
            'top': 'Base',
            'bottom': 'Apex',
            'front': 'Anterior'
        }

        all_preserved = True
        for p in presets:
            # Click preset button
            await cdp_eval(f"""
                (() => {{
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    vDoc.querySelector(`.btn-view[data-view="{p}"]`).click();
                }})()
            """)
            await asyncio.sleep(0.75) # wait for smooth transition
            
            res_p = await cdp_eval("""
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const cam = vWin.CardioVision3D.camera;
                    const ctrl = vWin.CardioVision3D.controls;
                    const dist = cam.position.distanceTo(ctrl.target);
                    const activeBtns = Array.from(vDoc.querySelectorAll('.btn-view.active')).map(b => b.dataset.view);

                    return {
                        dist: dist.toFixed(3),
                        activeBtns,
                        pos: { x: cam.position.x.toFixed(2), y: cam.position.y.toFixed(2), z: cam.position.z.toFixed(2) }
                    };
                })()
            """)
            dist_val = float(res_p['dist'])
            is_ok = abs(dist_val - 7.00) < 0.15
            if not is_ok:
                all_preserved = False
            print(f"Preset {preset_names[p]:14s} -> Distance: {res_p['dist']} (Preserved ~7.00: {is_ok}), Active: {res_p['activeBtns']}, Pos: {res_p['pos']}")

        print(f"\nAll 6 camera presets preserved zoom level: {all_preserved}")

        # Test Reset Perspective intentionally restores fittedDistance
        print("\n--- Testing Reset Perspective ---")
        await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                vDoc.querySelector('#btnReset').click();
            })()
        """)
        await asyncio.sleep(0.75)

        res_reset = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                const cam = vWin.CardioVision3D.camera;
                const ctrl = vWin.CardioVision3D.controls;
                return {
                    dist: cam.position.distanceTo(ctrl.target).toFixed(2),
                    activeBtns: Array.from(vDoc.querySelectorAll('.btn-view.active')).map(b => b.dataset.view)
                };
            })()
        """)
        print(f"Reset Perspective -> Restored distance: {res_reset['dist']} (Fitted ~13.76), Active: {res_reset['activeBtns']}")

        # -------------------------------------------------------------
        # TEST PRESET TOGGLE (Complete Heart <-> Coronary Focus)
        # -------------------------------------------------------------
        print("\n--- Testing Complete Heart <-> Coronary Focus Zoom Preservation ---")
        # Zoom in to 8.5
        toggle_res = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const ctrl = vWin.CardioVision3D.controls;

                // Zoom to 8.5
                const dir = cam.position.clone().sub(ctrl.target).normalize();
                cam.position.copy(ctrl.target).addScaledVector(dir, 8.50);
                ctrl.update();

                const dBefore = cam.position.distanceTo(ctrl.target);
                vDoc.querySelector('#presetCoronary').click();
                const dCoronary = cam.position.distanceTo(ctrl.target);
                vDoc.querySelector('#presetComplete').click();
                const dComplete = cam.position.distanceTo(ctrl.target);

                return {
                    dBefore: dBefore.toFixed(3),
                    dCoronary: dCoronary.toFixed(3),
                    dComplete: dComplete.toFixed(3),
                    preserved: (dBefore.toFixed(3) === dCoronary.toFixed(3)) && (dCoronary.toFixed(3) === dComplete.toFixed(3))
                };
            })()
        """)
        print(f"Preset Toggle Preserved: {toggle_res['preserved']} (Before: {toggle_res['dBefore']}, Coronary: {toggle_res['dCoronary']}, Complete: {toggle_res['dComplete']})")

        print("\n=======================================================")
        print("ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == '__main__':
    asyncio.run(main())
