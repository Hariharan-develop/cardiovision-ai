import asyncio, json, urllib.request, websockets

async def cdp_call(ws, method, params=None):
    msg_id = getattr(cdp_call, "counter", 1) + 1
    cdp_call.counter = msg_id
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        raw = await ws.recv()
        res = json.loads(raw)
        if res.get("id") == msg_id:
            return res

async def cdp_eval(ws, expr):
    res = await cdp_call(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    })
    if "result" in res and "result" in res["result"] and "value" in res["result"]["result"]:
        return res["result"]["result"]["value"]
    if "exceptionDetails" in res.get("result", {}):
        return {"error": res["result"]["exceptionDetails"]}
    return res

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    target = next((p for p in pages if "CardioVision" in p.get("title", "")), pages[0])
    ws_url = target["webSocketDebuggerUrl"]
    print("Connecting to:", target.get("title"))

    async with websockets.connect(ws_url) as ws:
        # Step 1: Switch to 3D Visualization tab
        print("\n--- Navigating to 3D Visualization ---")
        nav_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                if (!st) return { err: 'no stIFrame' };
                const stWin = st.contentWindow;
                if (typeof stWin.switchNav === 'function') {
                    stWin.switchNav('viewer3d');
                }
                return { switched: true };
            })()
        """)
        print("Nav switch:", nav_res)

        # Wait for meshes to complete loading
        print("\nWaiting for 106 meshes to load in viewerIframe...")
        for _ in range(30):
            status = await cdp_eval(ws, """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    if (!st) return 'no st';
                    const v = st.contentDocument.getElementById('viewerIframe');
                    if (!v) return 'no v';
                    const doc = v.contentDocument;
                    if (!doc) return 'no doc';
                    const el = doc.getElementById('loadStatus');
                    return el ? el.innerText : 'loading';
                })()
            """)
            if "Complete heart loaded" in str(status) or "106/106" in str(status):
                print("Mesh loading complete:", str(status).encode('ascii', 'replace').decode('ascii').strip())
                break
            await asyncio.sleep(1)

        # Test helper to get viewer context
        ctx_check = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                return {
                    hasCardio3D: !!vWin.CardioVision3D,
                    hasCamera: !!(vWin.CardioVision3D && vWin.CardioVision3D.camera),
                    hasControls: !!(vWin.CardioVision3D && vWin.CardioVision3D.controls)
                };
            })()
        """)
        print("Context check:", ctx_check)

        # -----------------------------------------------------------------
        # TEST 1 & 2: Continuous Zoom In (Up 10x) and Zoom Out (Down 10x)
        # -----------------------------------------------------------------
        print("\n--- TEST 1: Continuous Zoom In (Scroll upward 10 times) ---")
        zoom_in_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const canvas = v.contentDocument.getElementById('canvas');
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                const initialDist = cam.position.distanceTo(controls.target);
                const distances = [initialDist];

                for (let i = 0; i < 10; i++) {
                    const evt = new WheelEvent('wheel', {
                        deltaY: -100, // scroll up
                        deltaMode: 0,
                        clientX: 600,
                        clientY: 300,
                        bubbles: true,
                        cancelable: true
                    });
                    canvas.dispatchEvent(evt);
                    controls.update();
                    distances.push(cam.position.distanceTo(controls.target));
                }

                // Check strict monotonic decrease of camera distance (zoom in)
                const isMonotonic = distances.every((d, idx) => idx === 0 || d <= distances[idx - 1]);
                return {
                    initialDist,
                    finalDist: distances[distances.length - 1],
                    distances,
                    isMonotonicZoomIn: isMonotonic && (distances[distances.length - 1] < initialDist)
                };
            })()
        """)
        print(f"Zoom In Monotonic: {zoom_in_res.get('isMonotonicZoomIn')}")
        print(f"Start dist: {zoom_in_res.get('initialDist'):.2f} -> End dist: {zoom_in_res.get('finalDist'):.2f}")

        print("\n--- TEST 2: Continuous Zoom Out (Scroll downward 10 times) ---")
        zoom_out_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const canvas = v.contentDocument.getElementById('canvas');
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                const initialDist = cam.position.distanceTo(controls.target);
                const distances = [initialDist];

                for (let i = 0; i < 10; i++) {
                    const evt = new WheelEvent('wheel', {
                        deltaY: 100, // scroll down
                        deltaMode: 0,
                        clientX: 600,
                        clientY: 300,
                        bubbles: true,
                        cancelable: true
                    });
                    canvas.dispatchEvent(evt);
                    controls.update();
                    distances.push(cam.position.distanceTo(controls.target));
                }

                const isMonotonic = distances.every((d, idx) => idx === 0 || d >= distances[idx - 1]);
                return {
                    initialDist,
                    finalDist: distances[distances.length - 1],
                    distances,
                    isMonotonicZoomOut: isMonotonic && (distances[distances.length - 1] > initialDist)
                };
            })()
        """)
        print(f"Zoom Out Monotonic: {zoom_out_res.get('isMonotonicZoomOut')}")
        print(f"Start dist: {zoom_out_res.get('initialDist'):.2f} -> End dist: {zoom_out_res.get('finalDist'):.2f}")

        # -----------------------------------------------------------------
        # TEST 3: Alternate zoom in/out repeatedly (no freeze / resets)
        # -----------------------------------------------------------------
        print("\n--- TEST 3: Alternate Zoom In/Out Repeatedly ---")
        alternate_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const canvas = v.contentDocument.getElementById('canvas');
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                let success = true;
                const deltas = [-100, 100, -100, 100, -100, 100, -100, 100];
                for (let delta of deltas) {
                    const dBefore = cam.position.distanceTo(controls.target);
                    const evt = new WheelEvent('wheel', { deltaY: delta, bubbles: true, cancelable: true });
                    canvas.dispatchEvent(evt);
                    controls.update();
                    const dAfter = cam.position.distanceTo(controls.target);
                    if (delta < 0 && dAfter >= dBefore) success = false;
                    if (delta > 0 && dAfter <= dBefore) success = false;
                }
                return { alternatingSuccess: success, finalDist: cam.position.distanceTo(controls.target) };
            })()
        """)
        print("Alternating zoom success:", alternate_res.get("alternatingSuccess"))

        # -----------------------------------------------------------------
        # TEST 4: Rotate then zoom
        # -----------------------------------------------------------------
        print("\n--- TEST 4: Rotate Heart, Then Zoom ---")
        rotate_zoom_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const canvas = v.contentDocument.getElementById('canvas');
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                // Simulate pointer drag to rotate
                const downEvt = new PointerEvent('pointerdown', { clientX: 500, clientY: 300, bubbles: true });
                canvas.dispatchEvent(downEvt);
                const moveEvt = new PointerEvent('pointermove', { clientX: 580, clientY: 340, bubbles: true });
                window.dispatchEvent(moveEvt);
                const upEvt = new PointerEvent('pointerup', { clientX: 580, clientY: 340, bubbles: true });
                window.dispatchEvent(upEvt);

                // Now zoom in
                const dBefore = cam.position.distanceTo(controls.target);
                const evt = new WheelEvent('wheel', { deltaY: -120, bubbles: true, cancelable: true });
                canvas.dispatchEvent(evt);
                controls.update();
                const dAfter = cam.position.distanceTo(controls.target);

                return {
                    dragAndZoomWorked: dAfter < dBefore,
                    dBefore,
                    dAfter
                };
            })()
        """)
        print("Rotate then zoom worked:", rotate_zoom_res.get("dragAndZoomWorked"))

        # -----------------------------------------------------------------
        # TEST 5: Active Camera Indicator & Preset Views
        # -----------------------------------------------------------------
        print("\n--- TEST 5: Camera Presets & Active Button Indicators ---")
        presets = ['front', 'back', 'left', 'right', 'top', 'bottom']
        for p in presets:
            res_p = await cdp_eval(ws, f"""
                (() => {{
                    const st = document.querySelector('.stIFrame');
                    const v = st.contentDocument.getElementById('viewerIframe');
                    const vDoc = v.contentDocument;
                    const vWin = v.contentWindow;

                    // Click preset button
                    const btn = vDoc.querySelector(`.btn-view[data-view="{p}"]`);
                    if (btn) btn.click();

                    const activeBtns = Array.from(vDoc.querySelectorAll('.btn-view.active')).map(b => b.dataset.view);
                    return {{
                        preset: '{p}',
                        activeBtns,
                        isActiveCorrect: activeBtns.length === 1 && activeBtns[0] === '{p}',
                        camPos: {{
                            x: vWin.CardioVision3D.camera.position.x.toFixed(2),
                            y: vWin.CardioVision3D.camera.position.y.toFixed(2),
                            z: vWin.CardioVision3D.camera.position.z.toFixed(2)
                        }}
                    }};
                }})()
            """)
            print(f"Preset {p}: Active indicator correct = {res_p.get('isActiveCorrect')}, Pos = {res_p.get('camPos')}")

        # Test Reset Perspective button
        res_reset = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vDoc = v.contentDocument;
                const vWin = v.contentWindow;

                const resetBtn = vDoc.querySelector('#btnReset');
                if (resetBtn) resetBtn.click();

                const activeBtns = Array.from(vDoc.querySelectorAll('.btn-view.active')).map(b => b.dataset.view);
                return {
                    activeBtns,
                    isActiveFront: activeBtns.length === 1 && activeBtns[0] === 'front'
                };
            })()
        """)
        print("Reset Perspective restored Anterior indicator:", res_reset.get("isActiveFront"))

        # -----------------------------------------------------------------
        # TEST 6: Complete Heart vs Coronary Focus (Preserve Zoom)
        # -----------------------------------------------------------------
        print("\n--- TEST 6: Complete Heart <-> Coronary Focus (Preserve Zoom Level) ---")
        preset_zoom_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vDoc = v.contentDocument;
                const vWin = v.contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                // Zoom in first
                const evt = new WheelEvent('wheel', { deltaY: -200, bubbles: true, cancelable: true });
                vDoc.getElementById('canvas').dispatchEvent(evt);
                controls.update();

                const distBefore = cam.position.distanceTo(controls.target);

                // Switch to Coronary Focus
                vDoc.querySelector('#presetCoronary').click();
                const distCoronary = cam.position.distanceTo(controls.target);

                // Switch back to Complete Heart
                vDoc.querySelector('#presetComplete').click();
                const distComplete = cam.position.distanceTo(controls.target);

                return {
                    distBefore: distBefore.toFixed(3),
                    distCoronary: distCoronary.toFixed(3),
                    distComplete: distComplete.toFixed(3),
                    zoomPreserved: (distBefore.toFixed(3) === distCoronary.toFixed(3)) && (distCoronary.toFixed(3) === distComplete.toFixed(3))
                };
            })()
        """)
        print("Zoom preserved during preset toggle:", preset_zoom_res.get("zoomPreserved"), preset_zoom_res)

        # -----------------------------------------------------------------
        # TEST 7: Switch dashboard tabs and return
        # -----------------------------------------------------------------
        print("\n--- TEST 7: Switch Dashboard Tabs and Return ---")
        tab_switch_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const stWin = st.contentWindow;

                // Switch to results tab
                stWin.switchNav('results');
                // Switch back to viewer3d
                stWin.switchNav('viewer3d');

                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                const dBefore = cam.position.distanceTo(controls.target);
                const evt = new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true });
                v.contentDocument.getElementById('canvas').dispatchEvent(evt);
                controls.update();
                const dAfter = cam.position.distanceTo(controls.target);

                return {
                    controlsStillWorking: dAfter < dBefore,
                    dBefore,
                    dAfter
                };
            })()
        """)
        print("Controls working after tab switch:", tab_switch_res.get("controlsStillWorking"))

        # -----------------------------------------------------------------
        # TEST 8: Window Resize
        # -----------------------------------------------------------------
        print("\n--- TEST 8: Browser Window Resize Handling ---")
        resize_res = await cdp_eval(ws, """
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const vWin = v.contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const controls = vWin.CardioVision3D.controls;

                const dBefore = cam.position.distanceTo(controls.target);
                // Trigger resize event inside iframe
                vWin.dispatchEvent(new Event('resize'));

                const dAfter = cam.position.distanceTo(controls.target);
                return {
                    zoomUnchangedOnResize: dBefore.toFixed(3) === dAfter.toFixed(3),
                    dBefore: dBefore.toFixed(3),
                    dAfter: dAfter.toFixed(3)
                };
            })()
        """)
        print("Zoom unchanged on window resize:", resize_res.get("zoomUnchangedOnResize"))

        # -----------------------------------------------------------------
        # TEST 9: Artery Selection, Highlighting & Inspector Readability
        # -----------------------------------------------------------------
        print("\n--- TEST 9: Artery Selection & Inspector Readability ---")
        for vessel in ['lad', 'lcx', 'rca']:
            vessel_res = await cdp_eval(ws, f"""
                (() => {{
                    const st = document.querySelector('.stIFrame');
                    const v = st.contentDocument.getElementById('viewerIframe');
                    const vDoc = v.contentDocument;
                    const vWin = v.contentWindow;

                    // Focus vessel group via chip
                    vWin.focusVesselGroup('{vessel}');

                    const detail = vDoc.getElementById('detail');
                    const titleEl = detail.querySelector('strong');
                    const sublabel = detail.querySelector('.sublabel');
                    const filenameEl = detail.querySelector('.filename');
                    const predBox = detail.querySelector('.pred-box');
                    const predVal = detail.querySelector('.pred-val');

                    return {{
                        vessel: '{vessel}',
                        title: titleEl ? titleEl.innerText : '',
                        sublabel: sublabel ? sublabel.innerText : '',
                        filename: filenameEl ? filenameEl.innerText : '',
                        hasPredBox: !!predBox,
                        predVal: predVal ? predVal.innerText : ''
                    }};
                }})()
            """)
            print(f"Vessel {vessel.upper()}:")
            print(f"  Title: {vessel_res.get('title')}")
            print(f"  Sublabel: {vessel_res.get('sublabel')}")
            print(f"  Filename: {vessel_res.get('filename')}")
            print(f"  Prediction displayed: {vessel_res.get('predVal')}")

        print("\n==========================================")
        print("ALL VERIFICATION CHECKS COMPLETED!")
        print("==========================================")

if __name__ == "__main__":
    asyncio.run(main())
