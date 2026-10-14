import asyncio, json, urllib.request, websockets, base64, os

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    p = [x for x in pages if "8501" in x.get("url", "")][0]
    ws_url = p["webSocketDebuggerUrl"]
    print("Connecting to:", p["title"], "at", ws_url, flush=True)

    msg_id = 0
    async with websockets.connect(ws_url, max_size=30_000_000) as ws:
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == cid:
                    return msg.get("result", {})

        async def capture(name):
            await asyncio.sleep(0.8)
            res = await call("Page.captureScreenshot", {"format": "png"})
            data = res.get("data")
            filepath = os.path.join(ARTIFACT_DIR, name)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(data))
            print(f"Captured: {filepath}", flush=True)
            return filepath

        # Ensure we are on 3D view
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const doc = stFrame ? stFrame.contentDocument : document;
                    const navItem = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (navItem) navItem.click();
                })()
            """
        })
        await asyncio.sleep(1)

        # 1. LAD Selection (Front view)
        print("Selecting LAD...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lad');
                })()
            """
        })
        await capture("cardiovision_lad_electric_purple.png")

        # 2. LCX Selection (Left lateral view)
        print("Selecting LCX...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('lcx');
                })()
            """
        })
        await capture("cardiovision_lcx_electric_purple.png")

        # 3. RCA Selection (Right lateral view)
        print("Selecting RCA...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.focusVesselGroup('rca');
                })()
            """
        })
        await capture("cardiovision_rca_electric_purple.png")

        # 4. Myocardial Selection (Anterior view, click Left Ventricle Wall)
        print("Selecting Myocardium...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.setView('front');
                    let lvMesh = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'ventricles' && c.userData.label && c.userData.label.includes('Left ventricle') && !lvMesh) {
                            lvMesh = c;
                        }
                    });
                    if (!lvMesh) {
                        vWin.root.traverse(c => {
                            if (c.isMesh && c.userData && c.userData.group === 'ventricles' && !lvMesh) {
                                lvMesh = c;
                            }
                        });
                    }
                    if (lvMesh) vWin.selectMesh(lvMesh);
                })()
            """
        })
        await capture("cardiovision_myocardium_electric_purple.png")

        # 5. Clean Deselection (Reset)
        print("Deselecting (null)...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vWin = stFrame.contentDocument.getElementById('viewerIframe').contentWindow;
                    vWin.selectMesh(null);
                })()
            """
        })
        await capture("cardiovision_deselection_reset.png")
        print("All high-res screenshots successfully generated!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
