import asyncio
import json
import base64
import os
import websockets
import urllib.request

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"
ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def capture_all():
    targets = json.loads(urllib.request.urlopen(CDP_HTTP_ENDPOINT).read().decode())
    target = next((t for t in targets if "8501" in t.get("url", "")), None)
    if not target:
        print("Error: Target page not found!")
        return

    ws_url = target.get("webSocketDebuggerUrl")
    print(f"Connecting to CDP WebSocket: {ws_url}", flush=True)
    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method}
            if params: payload["params"] = params
            await ws.send(json.dumps(payload))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id: return res

        async def capture(filename):
            res = await call("Page.captureScreenshot", {"format": "png"})
            data = res.get("result", {}).get("data", "")
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"[SCREENSHOT] Saved: {filename} ({len(data)} bytes)", flush=True)
            return out_file

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Page.bringToFront")

        # Reload Streamlit page to pick up updated heart_viewer.html
        print("Reloading Streamlit page...", flush=True)
        await call("Page.reload")
        await asyncio.sleep(4.0)

        # Navigate to 3D tab
        print("Switching to 3D tab...", flush=True)
        for i in range(20):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const st = document.querySelector('.stIFrame');
                        if (st && st.contentWindow && st.contentWindow.switchNav) {
                            st.contentWindow.switchNav('viewer3d');
                            return true;
                        }
                        const doc = st ? st.contentDocument : document;
                        const nav3D = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                        if (nav3D) {
                            nav3D.click();
                            return true;
                        }
                        return false;
                    })()
                """,
                "returnByValue": True
            })
            if res.get("result", {}).get("result", {}).get("value") is True:
                print("Switched to 3D tab successfully!", flush=True)
                break
            await asyncio.sleep(1.0)

        # Helper to execute code inside viewer iframe
        async def eval_viewer(js_code):
            expr = f"""
                (() => {{
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame || !stFrame.contentDocument) return null;
                    const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                    if (!vFrame || !vFrame.contentWindow || !vFrame.contentDocument) return null;
                    const win = vFrame.contentWindow;
                    const doc = vFrame.contentDocument;
                    {js_code}
                }})()
            """
            res = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            return res.get("result", {}).get("result", {}).get("value")

        # Wait until 3D viewer is loaded (106 meshes)
        print("Waiting for 106 meshes to load in viewer...", flush=True)
        for i in range(35):
            res = await eval_viewer("""
                let count = 0;
                if (win.root) {
                    win.root.traverse(c => { if (c.isMesh && c.name !== 'selectionOutline') count++; });
                }
                const status = doc.querySelector('#loadStatus') ? doc.querySelector('#loadStatus').textContent : '';
                return { count, ready: (count >= 106), status };
            """)
            if res and res.get("ready"):
                print(f"All {res.get('count')} meshes confirmed loaded!", flush=True)
                break
            await asyncio.sleep(1.0)

        await asyncio.sleep(2.0)

        # -------------------------------------------------------------
        # TEST 1: Clinical Colors in Anatomy Mode (Anterior View)
        # -------------------------------------------------------------
        print("\n=== TEST 1: Clinical Colors in Anatomy Mode ===", flush=True)
        await eval_viewer("""
            win.CardioVision3D.setVisualizationMode('anatomy');
            win.CardioVision3D.setAppearanceStyle('clinical');
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_01_clinical_anatomy_anterior.png")

        # -------------------------------------------------------------
        # TEST 2: Realistic Tissue in Anatomy Mode (Anterior View)
        # -------------------------------------------------------------
        print("\n=== TEST 2: Realistic Tissue in Anatomy Mode ===", flush=True)
        await eval_viewer("""
            win.CardioVision3D.setAppearanceStyle('realistic');
            win.CardioVision3D.setVisualizationMode('anatomy');
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_02_realistic_anatomy_anterior.png")

        # -------------------------------------------------------------
        # TEST 3: Multi-View Inspection in Realistic Tissue Mode
        # -------------------------------------------------------------
        print("\n=== TEST 3: Multi-View Inspection in Realistic Tissue Mode ===", flush=True)
        # Posterior View (Diaphragmatic surface)
        await eval_viewer("win.CardioVision3D.setView('back', false); return true;")
        await asyncio.sleep(1.0)
        await capture("verified_03_realistic_posterior.png")

        # Left Lateral View (LV obtuse margin / LCX)
        await eval_viewer("win.CardioVision3D.setView('left', false); return true;")
        await asyncio.sleep(1.0)
        await capture("verified_04_realistic_left_lat.png")

        # Right Lateral View (RV / RCA)
        await eval_viewer("win.CardioVision3D.setView('right', false); return true;")
        await asyncio.sleep(1.0)
        await capture("verified_05_realistic_right_lat.png")

        # -------------------------------------------------------------
        # TEST 4: Live ML Risk Overlay with Clinical Colors
        # -------------------------------------------------------------
        print("\n=== TEST 4: Risk Overlay Mode in Clinical Colors ===", flush=True)
        await eval_viewer("""
            win.CardioVision3D.updateProbabilities({
                CAD: { risk: 91.7, label: 'High' },
                LAD: { risk: 22.4, label: 'Low (22.4%)' },
                LCX: { risk: 58.6, label: 'Moderate (58.6%)' },
                RCA: { risk: 88.2, label: 'High (88.2%)' }
            });
            win.CardioVision3D.setAppearanceStyle('clinical');
            win.CardioVision3D.setVisualizationMode('risk');
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_06_risk_overlay_clinical.png")

        # -------------------------------------------------------------
        # TEST 5: Live ML Risk Overlay with Realistic Tissue
        # -------------------------------------------------------------
        print("\n=== TEST 5: Risk Overlay Mode in Realistic Tissue ===", flush=True)
        await eval_viewer("""
            win.CardioVision3D.setAppearanceStyle('realistic');
            win.CardioVision3D.setVisualizationMode('risk');
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_07_risk_overlay_realistic.png")

        # -------------------------------------------------------------
        # TEST 6: Electric Purple Selection on LAD Arterial System
        # -------------------------------------------------------------
        print("\n=== TEST 6: Electric Purple Highlight on LAD ===", flush=True)
        await eval_viewer("""
            win.focusVesselGroup('lad');
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_08_selection_lad_purple.png")

        # -------------------------------------------------------------
        # TEST 7: Left Coronary Stem Inspector (Neutral bone-white & Global CAD disclaimer)
        # -------------------------------------------------------------
        print("\n=== TEST 7: Left Coronary Stem Inspector Neutrality ===", flush=True)
        await eval_viewer("""
            win.focusVesselGroup('cad');
            return true;
        """)
        await asyncio.sleep(1.0)
        await capture("verified_09_left_coronary_stem_inspector.png")

        # Restore neutral anterior view in realistic style
        await eval_viewer("""
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
            return true;
        """)
        await asyncio.sleep(0.5)

        print("\n[SUCCESS] All 9 verified screenshots captured successfully!", flush=True)

if __name__ == "__main__":
    asyncio.run(capture_all())
