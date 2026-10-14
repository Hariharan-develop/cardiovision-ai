import asyncio
import json
import urllib.request
import websockets

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"

async def check_iframe_errors():
    targets = json.loads(urllib.request.urlopen(CDP_HTTP_ENDPOINT).read().decode())
    target = next((t for t in targets if "CardioVision" in t.get("title", "") or "8501" in t.get("url", "")), None)
    if not target:
        print("Target not found!")
        return

    ws_url = target.get("webSocketDebuggerUrl")
    async with websockets.connect(ws_url) as ws:
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

        # Enable Log and Runtime to catch console errors
        await call("Log.enable")
        await call("Runtime.enable")

        res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame) return 'No stFrame';
                    const doc = stFrame.contentDocument;
                    if (!doc) return 'No doc inside stFrame';
                    const vFrame = doc.querySelector('#viewerIframe');
                    if (!vFrame) return 'No vFrame inside stFrame doc';
                    const vDoc = vFrame.contentDocument;
                    if (!vDoc) return 'No vDoc inside vFrame';
                    
                    const loadStatus = vDoc.querySelector('#loadStatus');
                    const scripts = Array.from(vDoc.querySelectorAll('script')).map(s => s.type || 'text/javascript');
                    const errs = vFrame.contentWindow.__caughtErrors || [];
                    
                    return {
                        vDocReady: vDoc.readyState,
                        loadStatusText: loadStatus ? loadStatus.innerHTML : 'No loadStatus el',
                        scripts: scripts,
                        vDocTitle: vDoc.title,
                        vWinThree: !!vFrame.contentWindow.THREE,
                        vWinBufferGeometryUtils: !!(vFrame.contentWindow.BufferGeometryUtils || (vFrame.contentWindow.THREE && vFrame.contentWindow.THREE.BufferGeometryUtils)),
                        errs: errs
                    };
                })()
            """,
            "returnByValue": True
        })
        print("Inspection result:", json.dumps(res.get("result", {}).get("value"), indent=2))

if __name__ == "__main__":
    asyncio.run(check_iframe_errors())
