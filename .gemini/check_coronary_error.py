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
                    const vFrame = stFrame.contentDocument.querySelector('#viewerIframe');
                    const vWin = vFrame.contentWindow;
                    try {
                        vWin.applyCoronaryMode('anatomy');
                        return { ok: true, mode: vWin.getCurrentVisualizationMode() };
                    } catch (e) {
                        return { ok: false, error: e.message, stack: e.stack };
                    }
                })()
            """,
            "returnByValue": True
        })
        val = res.get("result", {}).get("result", {}).get("value")
        print("applyCoronaryMode call result:", json.dumps(val, indent=2))

if __name__ == "__main__":
    asyncio.run(check())
