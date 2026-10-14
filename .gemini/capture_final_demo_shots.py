import asyncio
import json
import base64
import os
import websockets

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"
ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def capture_demo_shots():
    import urllib.request
    with urllib.request.urlopen(CDP_HTTP_ENDPOINT) as resp:
        targets = json.loads(resp.read().decode())
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
            if params:
                payload["params"] = params
            await ws.send(json.dumps(payload))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id:
                    return res

        async def screenshot(filename):
            await call("Emulation.setFocusEmulationEnabled", {"enabled": False})
            await asyncio.sleep(0.3)
            res = await call("Page.captureScreenshot", {"format": "png"})
            await call("Emulation.setFocusEmulationEnabled", {"enabled": True})
            data = res.get("result", {}).get("data", "")
            out_file = os.path.join(ARTIFACT_DIR, filename)
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Captured: {out_file} ({len(data)} b64 bytes)")
            return out_file

        await call("Page.bringToFront")

        # 1. Ensure we are on 3D Visualization tab in main dashboard
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const doc = stFrame ? stFrame.contentDocument : document;
                    const nav3D = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (nav3D) nav3D.click();

                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    if (vDoc.querySelector('.panel')) vDoc.querySelector('.panel').scrollTop = 0;
                    if (vDoc.querySelector('#presetComplete')) vDoc.querySelector('#presetComplete').click();
                    if (vDoc.querySelector('#btnReset')) vDoc.querySelector('#btnReset').click();
                })()
            """
        })
        await asyncio.sleep(1.2)

        # 2. Shot A: Anatomy Mode (default colors)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vDoc.querySelector('.panel').scrollTop = 0;
                    vDoc.querySelector('#presetComplete').click();
                    vDoc.querySelector('#modeAnatomy').click();
                    vWin.CardioVision3D.clearSelectionHighlights();
                    vDoc.querySelector('#btnReset').click();
                })()
            """
        })
        await asyncio.sleep(1.0)
        await screenshot("demo_01_anatomy_mode.png")

        # 3. Shot B: Risk Overlay Mode with illustrative probabilities (0.12, 0.54, 0.83)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vDoc.querySelector('.panel').scrollTop = 0;
                    vWin.CardioVision3D.updateProbabilities({
                        CAD: { risk: 91.7, label: 'CAD' },
                        LAD: { risk: 12.0, label: 'Normal' },
                        LCX: { risk: 54.0, label: 'Stenotic' },
                        RCA: { risk: 83.0, label: 'Stenotic' }
                    });
                    vDoc.querySelector('#modeRisk').click();
                    vWin.CardioVision3D.clearSelectionHighlights();
                    vDoc.querySelector('#btnReset').click();
                })()
            """
        })
        await asyncio.sleep(1.0)
        await screenshot("demo_02_illustrative_risk_mode.png")

        # 4. Shot C: Electric Purple Selection on LAD in Risk Overlay Mode
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');
                })()
            """
        })
        await asyncio.sleep(1.0)
        await screenshot("demo_03_purple_selection_active.png")

        # 5. Shot D: Deselect LAD - restores to LAD risk color (#47b365)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.CardioVision3D.clearSelectionHighlights();
                })()
            """
        })
        await asyncio.sleep(1.0)
        await screenshot("demo_04_restored_risk_color_after_deselect.png")

        # 6. Shot E: Coronary Focus with Real Model Predictions
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.CardioVision3D.updateProbabilities({
                        CAD: { risk: 91.7, label: 'CAD' },
                        LAD: { risk: 79.0, label: 'Stenotic' },
                        LCX: { risk: 65.0, label: 'Stenotic' },
                        RCA: { risk: 51.7, label: 'Stenotic' }
                    });
                    vDoc.querySelector('#presetCoronary').click();
                })()
            """
        })
        await asyncio.sleep(1.0)
        await screenshot("demo_05_coronary_focus_risk_mode.png")

        # Restore Complete Heart
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vDoc = stFrame.contentDocument.getElementById('viewerIframe').contentDocument;
                    vDoc.querySelector('#presetComplete').click();
                })()
            """
        })
        print("Demo screenshots capture completed successfully.")

if __name__ == "__main__":
    asyncio.run(capture_demo_shots())
