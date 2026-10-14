import asyncio
import json
import urllib.request
import websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    target = next((t for t in targets if "8501" in t.get("url", "")), None)
    async with websockets.connect(target["webSocketDebuggerUrl"]) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            p = {"id": msg_id, "method": method}
            if params: p["params"] = params
            await ws.send(json.dumps(p))
            while True:
                r = json.loads(await ws.recv())
                if r.get("id") == msg_id: return r

        res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame || !stFrame.contentDocument) return { error: 'no stFrame' };
                    const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                    if (!vFrame) return { error: 'no vFrame' };
                    const vDoc = vFrame.contentDocument;
                    const vWin = vFrame.contentWindow;
                    if (!vDoc || !vWin) return { error: 'no vDoc/vWin' };
                    
                    return {
                        title: vDoc.title,
                        status: vDoc.querySelector('#loadStatus') ? vDoc.querySelector('#loadStatus').textContent : 'no status el',
                        hasThree: !!vWin.THREE,
                        hasCardio3D: !!vWin.CardioVision3D,
                        loadedCount: vWin.loaded ? vWin.loaded.length : 'no loaded',
                        entriesCount: vWin.entries ? vWin.entries.length : 'no entries',
                        styleClinicalBtn: !!vDoc.querySelector('#styleClinical'),
                        styleRealisticBtn: !!vDoc.querySelector('#styleRealistic'),
                        modeAnatomyBtn: !!vDoc.querySelector('#modeAnatomy'),
                        modeRiskBtn: !!vDoc.querySelector('#modeRisk')
                    };
                })()
            """,
            "returnByValue": True
        })
        val = res.get("result", {}).get("result", {}).get("value")
        print("Viewer Iframe State:", json.dumps(val, indent=2))

if __name__ == "__main__":
    asyncio.run(check())
