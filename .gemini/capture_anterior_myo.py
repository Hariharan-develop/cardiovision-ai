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
                msg = json.loads(await ws.recv())
                if msg.get("id") == cid:
                    return msg.get("result", {})

        js = """
        (() => {
            const st = document.querySelector('.stIFrame');
            const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
            const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
            vDoc.querySelector('[data-view="front"]').click();
            
            let targetMesh = null;
            vWin.root.traverse(c => {
                if (c.isMesh && c.userData && c.userData.group === 'ventricles' && c.userData.label && c.userData.label.includes('Free wall') && !targetMesh) {
                    targetMesh = c;
                }
            });
            if (targetMesh) vWin.selectMesh(targetMesh);
            return {
                label: targetMesh ? targetMesh.userData.label : null,
                outlines: vWin.getActiveOutlineMeshes().length
            };
        })()
        """
        res_eval = await call("Runtime.evaluate", {"expression": js, "returnByValue": True})
        print("Eval:", res_eval.get("result", {}).get("value"))
        await asyncio.sleep(1.2)

        shot = await call("Page.captureScreenshot", {"format": "png"})
        filepath = os.path.join(ARTIFACT_DIR, "cardiovision_myocardium_anterior.png")
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved:", filepath)

if __name__ == "__main__":
    asyncio.run(main())
