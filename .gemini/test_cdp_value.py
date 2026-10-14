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
                    const iframes = Array.from(document.querySelectorAll('iframe'));
                    const stFrame = document.querySelector('.stIFrame');
                    let subFrames = [];
                    if (stFrame && stFrame.contentDocument) {
                        subFrames = Array.from(stFrame.contentDocument.querySelectorAll('iframe')).map(f => f.id);
                    }
                    return {
                        url: location.href,
                        mainIframesCount: iframes.length,
                        stFrameFound: !!stFrame,
                        subFramesInSt: subFrames
                    };
                })()
            """,
            "returnByValue": True
        })
        val = res.get("result", {}).get("result", {}).get("value")
        print("DOM State:", json.dumps(val, indent=2))

if __name__ == "__main__":
    asyncio.run(check())
