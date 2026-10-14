import asyncio, json, urllib.request, websockets, base64, os

ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    p = [x for x in pages if "8501" in x.get("url", "")][0]
    
    msg_id = 0
    async with websockets.connect(p["webSocketDebuggerUrl"], max_size=30_000_000) as ws:
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            cid = msg_id
            await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                if msg.get("id") == cid:
                    return msg.get("result", {})

        async def capture(name):
            await asyncio.sleep(0.8)
            shot = await call("Page.captureScreenshot", {"format": "png"})
            filepath = os.path.join(ARTIFACT_DIR, name)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print("Successfully saved:", filepath, flush=True)

        await call("Page.bringToFront")

        # Switch to 3D tab
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const doc = st ? st.contentDocument : document;
                    const nav = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent.includes('3D Visualization'));
                    if (nav) nav.click();
                })()
            """
        })
        await asyncio.sleep(1)

        # 1. Hide Atria and Ventricles, Select Exposed Papillary Muscle
        print("Capturing exposed internal structure...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    // Uncheck Ventricles and Atria
                    const ventCheck = vDoc.querySelector('[data-group="ventricles"]');
                    const atriaCheck = vDoc.querySelector('[data-group="atria"]');
                    if (ventCheck) { ventCheck.checked = false; ventCheck.dispatchEvent(new Event('change')); }
                    if (atriaCheck) { atriaCheck.checked = false; atriaCheck.dispatchEvent(new Event('change')); }

                    // Select exposed papillary muscle
                    let pap = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'internal_myocardium' && !pap) pap = c;
                    });
                    if (pap) vWin.selectMesh(pap);
                })()
            """
        })
        await capture("bugfix_exposed_internal_structure.png")

        # 2. Enable ONLY Conduction System, Select SA Node
        print("Capturing conduction only...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    vDoc.querySelectorAll('[data-group]').forEach(cb => {
                        cb.checked = (cb.dataset.group === 'conduction_system');
                        cb.dispatchEvent(new Event('change'));
                    });

                    let sa = null;
                    vWin.root.traverse(c => {
                        if (c.isMesh && c.userData && c.userData.group === 'conduction_system' && !sa) sa = c;
                    });
                    if (sa) vWin.selectMesh(sa);
                })()
            """
        })
        await capture("bugfix_conduction_only_selected.png")

        # 3. Coronary Focus Mode (Click-Through Ghosted Myocardium)
        print("Capturing Coronary Focus click-through...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;

                    vDoc.querySelector('#presetCoronary').click();
                    vWin.focusVesselGroup('lad');
                })()
            """
        })
        await capture("bugfix_coronary_focus_ghosted.png")

        # 4. Re-enable Complete Heart Mode
        print("Capturing Complete Heart restored...", flush=True)
        await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                    vDoc.querySelector('#presetComplete').click();
                })()
            """
        })
        await capture("bugfix_complete_heart_restored.png")

        print("All bugfix verification screenshots complete!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
