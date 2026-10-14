import asyncio
import json
import urllib.request
import websockets

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"

async def check_console():
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

        # Evaluate what's inside the iframe
        res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame || !stFrame.contentDocument) return { error: 'no stFrame' };
                    const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                    if (!vFrame) return { error: 'no vFrame' };
                    const vDoc = vFrame.contentDocument;
                    const vWin = vFrame.contentWindow;
                    if (!vDoc) return { error: 'no vDoc' };
                    return {
                        title: vDoc.title,
                        statusText: vDoc.querySelector('#loadStatus') ? vDoc.querySelector('#loadStatus').textContent : 'no loadStatus',
                        bodyLen: vDoc.body ? vDoc.body.innerHTML.length : 0,
                        hasThree: !!vWin.THREE,
                        hasCardio3D: !!vWin.CardioVision3D,
                        loadedCount: vWin.loaded ? vWin.loaded.length : 'no loaded array',
                        failures: vWin.failures !== undefined ? vWin.failures : 'no failures',
                        baseUrl: vWin.MODEL_BASE_URL || 'no MODEL_BASE_URL'
                    };
                })()
            """,
            "returnByValue": True
        })
        print("IFrame state:", json.dumps(res.get("result", {}).get("value"), indent=2))

if __name__ == "__main__":
    asyncio.run(check_console())
