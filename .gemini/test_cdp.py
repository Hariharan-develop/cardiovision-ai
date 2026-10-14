import asyncio, json, urllib.request, websockets

async def cdp_call(ws, method, params=None):
    msg_id = getattr(cdp_call, "counter", 1) + 1
    cdp_call.counter = msg_id
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        res = json.loads(await ws.recv())
        if res.get("id") == msg_id:
            return res

async def main():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    target = next((p for p in pages if "CardioVision" in p.get("title", "")), pages[0])
    ws_url = target["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url) as ws:
        # Clear wheel logs inside vIframe
        await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                    const vDoc = vIframe.contentDocument;
                    const vWin = vIframe.contentWindow;
                    vWin._wheelLogs = [];
                    return { cleared: true };
                })()
            """,
            "returnByValue": True
        })

        # Get iframe bounding rect in screen coordinates
        rect = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const stRect = stFrame.getBoundingClientRect();
                    const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                    const vRect = vIframe.getBoundingClientRect();
                    return {
                        x: stRect.left + vRect.left + (vRect.width / 2),
                        y: stRect.top + vRect.top + (vRect.height / 2),
                        vRect: { left: vRect.left, top: vRect.top, width: vRect.width, height: vRect.height }
                    };
                })()
            """,
            "returnByValue": True
        })
        coords = rect.get("result", {}).get("result", {}).get("value", {})
        print("Iframe rect raw:", rect)
        print("Iframe center coords in top window:", coords)

        # Dispatch 5 real mouseWheel events via CDP at coords x, y
        for i in range(5):
            await cdp_call(ws, "Input.dispatchMouseEvent", {
                "type": "mouseWheel",
                "x": int(coords["x"]),
                "y": int(coords["y"]),
                "deltaX": 0,
                "deltaY": -100
            })
            await asyncio.sleep(0.05)

        # Check wheel logs inside vIframe
        res = await cdp_call(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const stFrame = document.querySelector('.stIFrame');
                    const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                    const vWin = vIframe.contentWindow;
                    return {
                        receivedCount: vWin._wheelLogs ? vWin._wheelLogs.length : 0,
                        logs: vWin._wheelLogs
                    };
                })()
            """,
            "returnByValue": True
        })
        print("CDP mouseWheel result inside iframe:", json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
