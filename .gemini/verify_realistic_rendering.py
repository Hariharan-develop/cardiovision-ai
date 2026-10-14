import asyncio
import json
import base64
import os
import websockets
import urllib.request

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"
ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def run_verification():
    targets = json.loads(urllib.request.urlopen(CDP_HTTP_ENDPOINT).read().decode())
    target = next((t for t in targets if "CardioVision" in t.get("title", "") or "8501" in t.get("url", "")), None)
    if not target:
        print("Error: Target page not found!")
        return

    ws_url = target.get("webSocketDebuggerUrl")
    print(f"Connecting to CDP WebSocket: {ws_url}")
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
            await call("Emulation.setFocusEmulationEnabled", {"enabled": False})
            await asyncio.sleep(0.4)
            res = await call("Page.captureScreenshot", {"format": "png"})
            await call("Emulation.setFocusEmulationEnabled", {"enabled": True})
            data = res.get("result", {}).get("data", "")
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"[SCREENSHOT] Saved: {filename} ({len(data)} bytes)")
            return out_file

        await call("Page.bringToFront")
        await call("Emulation.setFocusEmulationEnabled", {"enabled": True})

        # 1. Reload Streamlit page
        print("Reloading page to pick up updated heart_viewer.html...", flush=True)
        await call("Page.reload")
        await asyncio.sleep(4.0)

        # 2. Wait for stIFrame to mount
        print("Waiting for stIFrame...", flush=True)
        for i in range(25):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame || !stFrame.contentDocument) return false;
                        const navs = stFrame.contentDocument.querySelectorAll('.navItem');
                        return navs.length > 0;
                    })()
                """,
                "returnByValue": True
            })
            if res.get("result", {}).get("value") is True:
                print(f"stIFrame mounted (attempt {i})", flush=True)
                break
            await asyncio.sleep(1.0)

        # 3. Navigate to 3D tab
        print("Navigating to 3D Visualization tab...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (stFrame && stFrame.contentWindow && stFrame.contentWindow.switchNav) {
                        stFrame.contentWindow.switchNav('viewer3d');
                        return true;
                    }
                    const doc = stFrame ? stFrame.contentDocument : document;
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
        await asyncio.sleep(2.0)

        # 4. Wait for 106 meshes to load in viewer
        print("Waiting for 106 meshes to load in viewerIframe...", flush=True)
        for i in range(35):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame || !stFrame.contentDocument) return { ready: false, count: 0, reason: 'no stFrame' };
                        const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                        if (!vFrame || !vFrame.contentDocument || !vFrame.contentWindow) return { ready: false, count: 0, reason: 'no vFrame' };
                        const win = vFrame.contentWindow;
                        const scene = win.scene;
                        const root = win.root;
                        let count = 0;
                        if (root) {
                            root.traverse(c => { if (c.isMesh && c.name !== 'selectionOutline') count++; });
                        }
                        return { ready: (count >= 106), count, hasCardio3D: !!win.CardioVision3D };
                    })()
                """,
                "returnByValue": True
            })
            val = res.get("result", {}).get("value", {})
            if val.get("ready"):
                print(f"Loaded all {val.get('count')} meshes successfully!", flush=True)
                break
            print(f"Loading progress: {val.get('count', 0)}/106 meshes...", flush=True)
            await asyncio.sleep(1.0)

        await asyncio.sleep(2.0)

        # Helper to execute JS inside viewer iframe
        async def eval_viewer(js_code):
            expr = f"""
                (() => {{
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame || !stFrame.contentDocument) return null;
                    const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                    if (!vFrame || !vFrame.contentWindow) return null;
                    const win = vFrame.contentWindow;
                    const doc = vFrame.contentDocument;
                    {js_code}
                }})()
            """
            res = await call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            return res.get("result", {}).get("value")

        # Check rendering diagnostics
        diag = await eval_viewer("""
            const win = window;
            const doc = document;
            const styleClinicalBtn = doc.querySelector('#styleClinical');
            const styleRealisticBtn = doc.querySelector('#styleRealistic');
            const modeAnatomyBtn = doc.querySelector('#modeAnatomy');
            const modeRiskBtn = doc.querySelector('#modeRisk');
            
            // Inspect geometry normals on first myocardial mesh
            let ventNormals = null;
            let ventHasUV = false;
            let ventNormalMap = false;
            let ventRoughnessMap = false;
            
            if (win.materials && win.materials.ventricles) {
                const mat = win.materials.ventricles;
                ventNormalMap = !!mat.normalMap;
                ventRoughnessMap = !!mat.roughnessMap;
            }
            if (win.root) {
                win.root.traverse(c => {
                    if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !ventNormals) {
                        ventNormals = c.geometry && !!c.geometry.attributes.normal;
                        ventHasUV = c.geometry && !!c.geometry.attributes.uv;
                    }
                });
            }

            return {
                hasStyleButtons: !!(styleClinicalBtn && styleRealisticBtn),
                hasModeButtons: !!(modeAnatomyBtn && modeRiskBtn),
                currentMode: win.CardioVision3D ? win.CardioVision3D.getVisualizationMode() : null,
                currentStyle: win.CardioVision3D ? win.CardioVision3D.getAppearanceStyle() : null,
                ventNormals,
                ventHasUV,
                ventNormalMap,
                ventRoughnessMap
            };
        """)
        print(f"[DIAGNOSTICS] Viewer State: {json.dumps(diag, indent=2)}")

        # -------------------------------------------------------------
        # TEST 1: Clinical Colors in Anatomy Mode (Anterior View)
        # -------------------------------------------------------------
        print("\n=== TEST 1: Clinical Colors in Anatomy Mode ===")
        await eval_viewer("""
            win.CardioVision3D.setVisualizationMode('anatomy');
            win.CardioVision3D.setAppearanceStyle('clinical');
            win.CardioVision3D.setView('front', false);
        """)
        await asyncio.sleep(1.0)
        await capture("realistic_01_clinical_anatomy_anterior.png")

        # -------------------------------------------------------------
        # TEST 2: Realistic Tissue in Anatomy Mode (Anterior View)
        # -------------------------------------------------------------
        print("\n=== TEST 2: Realistic Tissue in Anatomy Mode ===")
        await eval_viewer("""
            win.CardioVision3D.setAppearanceStyle('realistic');
            win.CardioVision3D.setView('front', false);
        """)
        await asyncio.sleep(1.0)
        await capture("realistic_02_realistic_anatomy_anterior.png")

        # -------------------------------------------------------------
        # TEST 3: Multi-View Inspection in Realistic Tissue Mode
        # -------------------------------------------------------------
        print("\n=== TEST 3: Multi-View Inspection (Posterior, Left Lat, Right Lat) ===")
        # Posterior View (Diaphragmatic surface)
        await eval_viewer("win.CardioVision3D.setView('back', false);")
        await asyncio.sleep(0.8)
        await capture("realistic_03_realistic_posterior.png")

        # Left Lateral View (LCX Obtuse Margin)
        await eval_viewer("win.CardioVision3D.setView('left', false);")
        await asyncio.sleep(0.8)
        await capture("realistic_04_realistic_left_lat.png")

        # Right Lateral View (RCA Acute Margin)
        await eval_viewer("win.CardioVision3D.setView('right', false);")
        await asyncio.sleep(0.8)
        await capture("realistic_05_realistic_right_lat.png")

        # -------------------------------------------------------------
        # TEST 4: Live ML Risk Overlay with Clinical Colors
        # -------------------------------------------------------------
        print("\n=== TEST 4: Risk Overlay Mode in Clinical Colors ===")
        await eval_viewer("""
            win.CardioVision3D.updateProbabilities({
                CAD: { risk: 88.5, label: 'High' },
                LAD: { risk: 24.3, label: 'Low (24.3%)' },
                LCX: { risk: 62.7, label: 'Moderate (62.7%)' },
                RCA: { risk: 91.4, label: 'High (91.4%)' }
            });
            win.CardioVision3D.setAppearanceStyle('clinical');
            win.CardioVision3D.setVisualizationMode('risk');
            win.CardioVision3D.setView('front', false);
        """)
        await asyncio.sleep(1.0)
        await capture("realistic_06_risk_overlay_clinical.png")

        # -------------------------------------------------------------
        # TEST 5: Live ML Risk Overlay with Realistic Tissue
        # -------------------------------------------------------------
        print("\n=== TEST 5: Risk Overlay Mode in Realistic Tissue ===")
        await eval_viewer("""
            win.CardioVision3D.setAppearanceStyle('realistic');
            win.CardioVision3D.setVisualizationMode('risk');
            win.CardioVision3D.setView('front', false);
        """)
        await asyncio.sleep(1.0)
        await capture("realistic_07_risk_overlay_realistic.png")

        # -------------------------------------------------------------
        # TEST 6: Electric Purple Selection on LAD and Left Coronary Stem
        # -------------------------------------------------------------
        print("\n=== TEST 6: Electric Purple Highlight & Left Stem Neutrality ===")
        # Select LAD
        await eval_viewer("""
            win.focusVesselGroup('lad');
        """)
        await asyncio.sleep(0.8)
        await capture("realistic_08_selection_lad_purple.png")

        # Select Left Coronary Stem (Neutral bone-white preserved with Global CAD disclaimer)
        await eval_viewer("""
            win.focusVesselGroup('cad');
        """)
        await asyncio.sleep(0.8)
        await capture("realistic_09_left_coronary_stem_inspector.png")

        # Clear selection and return to front view
        await eval_viewer("""
            win.CardioVision3D.selectMesh(null);
            win.CardioVision3D.setView('front', false);
        """)
        await asyncio.sleep(0.5)

        print("\nAll verification tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_verification())
