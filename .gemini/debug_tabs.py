import asyncio
import json
import websockets
import urllib.request

async def test():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    target = next((t for t in targets if "CardioVision" in t.get("title", "") or "8501" in t.get("url", "")), None)
    if not target:
        print("No target!")
        return
    async with websockets.connect(target.get("webSocketDebuggerUrl"), max_size=50*1024*1024) as ws:
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
        
        # Enable runtime & page
        await call("Page.enable")
        await call("Runtime.enable")

        # Check frames
        tree = await call("Page.getFrameTree")
        print("Frame tree:", json.dumps(tree, indent=2)[:500])

        # Evaluate on main document
        r = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({
                        id: f.id,
                        src: f.src ? f.src.slice(0, 50) : '',
                        hasSrcdoc: !!f.srcdoc,
                        hasContentDoc: !!f.contentDocument
                    }));
                    return { iframes, title: document.title, url: window.location.href };
                })()
            """,
            "returnByValue": True
        })
        print("Main doc eval:", json.dumps(r.get("result", {}).get("value", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(test())
