import asyncio
import json
import base64
import os
import websockets
import urllib.request

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"
ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def test_and_capture():
    targets = json.loads(urllib.request.urlopen(CDP_HTTP_ENDPOINT).read().decode())
    target = next((t for t in targets if "CardioVision" in t.get("title", "") or "8501" in t.get("url", "")), None)
    if not target:
        print("Target not found!")
        return

    ws_url = target.get("webSocketDebuggerUrl")
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
            await asyncio.sleep(0.3)
            res = await call("Page.captureScreenshot", {"format": "png"})
            await call("Emulation.setFocusEmulationEnabled", {"enabled": True})
            data = res.get("result", {}).get("data", "")
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Captured screenshot: {out_file} ({len(data)} b64 bytes)")
            return out_file

        await call("Page.bringToFront")
        await call("Emulation.setFocusEmulationEnabled", {"enabled": True})

        # Reload page so that the updated components/heart_viewer.html is loaded
        print("Reloading Streamlit page...", flush=True)
        await call("Page.reload")
        await asyncio.sleep(4.0)

        # Wait for stIFrame to be mounted
        print("Waiting for stIFrame to mount...", flush=True)
        for i in range(20):
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
                print(f"stIFrame mounted successfully (attempt {i})", flush=True)
                break
            await asyncio.sleep(1.0)

        # Navigate to 3D Visualization tab
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

        # Wait for heart to load (106 meshes)
        print("Waiting for 106 meshes to load in viewerIframe...", flush=True)
        for i in range(30):
            res = await call("Runtime.evaluate", {
                "expression": """
                    (() => {
                        const stFrame = document.querySelector('.stIFrame');
                        if (!stFrame || !stFrame.contentDocument) return { ready: false, count: 0, reason: 'no stFrame' };
                        const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                        if (!vIframe || !vIframe.contentDocument) return { ready: false, count: 0, reason: 'no viewerIframe' };
                        const vWin = vIframe.contentWindow;
                        const statusEl = vIframe.contentDocument.querySelector('#loadStatus');
                        const txt = statusEl ? statusEl.textContent : '';
                        const loadedCount = vWin.root ? vWin.root.children.length : 0;
                        const ready = txt.includes('Complete heart loaded') || loadedCount >= 106;
                        return { ready, txt, count: loadedCount };
                    })()
                """,
                "returnByValue": True
            })
            val = res.get("result", {}).get("value", {})
            safe_txt = str(val.get("txt", "")).encode("ascii", "replace").decode("ascii")
            print(f"[{i}] Loaded: {val.get('count')} - Status: {safe_txt}", flush=True)
            if val.get("ready"):
                print(">>> 106 Meshes Loaded! <<<", flush=True)
                break
            await asyncio.sleep(1.0)

        await asyncio.sleep(1.5)

        # TEST A: Verify Heartbeat section is completely removed
        print("\n================== VERIFYING HEARTBEAT CONTROLS REMOVAL ==================", flush=True)
        eval_hb = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const toggleHb = vDoc.querySelector('#toggleHeartbeat');
                    const sliderBpm = vDoc.querySelector('#bpmSlider');
                    const pulseDot = vDoc.querySelector('#heartbeatPulseDot');
                    const allText = vDoc.body.textContent;
                    const hasHeartbeatText = allText.includes('Heartbeat Animation') || allText.includes('Heartbeat Motion');
                    
                    return {
                        hasToggle: !!toggleHb,
                        hasSlider: !!sliderBpm,
                        hasPulseDot: !!pulseDot,
                        hasHeartbeatText: hasHeartbeatText,
                        controlsAreClean: (!toggleHb && !sliderBpm && !pulseDot && !hasHeartbeatText)
                    };
                })()
            """,
            "returnByValue": True
        })
        hb_res = eval_hb.get("result", {}).get("value", {})
        print("Heartbeat removal verification:\n", json.dumps(hb_res, indent=2), flush=True)

        # TEST B: Inspect Left Coronary Stem
        print("\n================== VERIFYING LEFT CORONARY STEM INSPECTOR & NEUTRAL COLOR ==================", flush=True)
        eval_stem = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Ensure panel scroll is at top and perspective is reset
                    if (vDoc.querySelector('.panel')) vDoc.querySelector('.panel').scrollTop = 0;
                    if (vDoc.querySelector('#btnReset')) vDoc.querySelector('#btnReset').click();

                    // Check Left Coronary Stem material color before click
                    const stemMat = vWin.materials['left_coronary_stem'];
                    const stemColor = '#' + stemMat.color.getHexString();
                    const stemEmissive = '#' + stemMat.emissive.getHexString();

                    // Click CAD Overall chip to inspect Left Coronary Stem
                    vWin.focusVesselGroup('cad');

                    // Read detail card HTML and text
                    const detailEl = vDoc.querySelector('#detail');
                    const detailText = detailEl ? detailEl.textContent : '';

                    return {
                        stemColor: stemColor,
                        stemEmissive: stemEmissive,
                        isStemColorNeutral: stemColor === '#e6d6c2',
                        isStemEmissiveZero: stemEmissive === '#000000',
                        containsGlobalCad: detailText.includes('Global CAD Prediction'),
                        containsNotLocalized: detailText.includes('Not a Localized Left-Main Stenosis Prediction'),
                        containsNeutralRef: detailText.includes('Neutral Reference (#E6D6C2)')
                    };
                })()
            """,
            "returnByValue": True
        })
        stem_res = eval_stem.get("result", {}).get("value", {})
        print("Left Coronary Stem verification:\n", json.dumps(stem_res, indent=2), flush=True)

        await asyncio.sleep(1.0)
        await capture("verified_01_left_coronary_stem_inspector.png")

        # TEST C: Deselect and verify Left Coronary Stem remains neutral in Risk Overlay Mode
        print("\n================== VERIFYING RISK OVERLAY MODE WITH NEUTRAL STEM ==================", flush=True)
        eval_risk = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Deselect
                    vWin.CardioVision3D.clearSelectionHighlights();

                    // Activate Risk Overlay Mode
                    vDoc.querySelector('#modeRisk').click();

                    const stemMat = vWin.materials['left_coronary_stem'];
                    const stemColorInRisk = '#' + stemMat.color.getHexString();
                    const stemEmissiveInRisk = '#' + stemMat.emissive.getHexString();

                    const ladColorInRisk = '#' + vWin.materials['lad'].color.getHexString();
                    const lcxColorInRisk = '#' + vWin.materials['lcx'].color.getHexString();
                    const rcaColorInRisk = '#' + vWin.materials['rca'].color.getHexString();

                    return {
                        stemColorInRisk,
                        stemEmissiveInRisk,
                        isStemNeutralInRisk: stemColorInRisk === '#e6d6c2' && stemEmissiveInRisk === '#000000',
                        ladColorInRisk,
                        lcxColorInRisk,
                        rcaColorInRisk
                    };
                })()
            """,
            "returnByValue": True
        })
        risk_res = eval_risk.get("result", {}).get("value", {})
        print("Risk overlay verification with neutral stem:\n", json.dumps(risk_res, indent=2), flush=True)

        await asyncio.sleep(1.0)
        await capture("verified_02_risk_overlay_no_heartbeat.png")

        # TEST D: Switch to Anatomy Mode showing full left panel without heartbeat controls
        print("\n================== VERIFYING ANATOMY MODE NO HEARTBEAT ==================", flush=True)
        eval_anat = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vDoc.querySelector('#modeAnatomy').click();
                    vWin.CardioVision3D.clearSelectionHighlights();
                    vDoc.querySelector('.panel').scrollTop = 0;
                    return { ok: true };
                })()
            """,
            "returnByValue": True
        })
        await asyncio.sleep(1.0)
        await capture("verified_03_anatomy_mode_no_heartbeat.png")

        print("\n>>> ALL VERIFICATION CHECKS COMPLETE! <<<", flush=True)

if __name__ == "__main__":
    asyncio.run(test_and_capture())
