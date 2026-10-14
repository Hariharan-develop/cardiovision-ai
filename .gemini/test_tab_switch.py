import asyncio
import json
import base64
import os
import websockets
import urllib.request

CDP_HTTP_ENDPOINT = "http://localhost:9222/json"
ARTIFACT_DIR = r"C:\Users\hario\.gemini\antigravity-ide\brain\8cd09337-1c91-438d-aacf-249a561d03c7"

async def test():
    targets = json.loads(urllib.request.urlopen(CDP_HTTP_ENDPOINT).read().decode())
    target = next((t for t in targets if "8501" in t.get("url", "")), None)
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=50 * 1024 * 1024) as ws:
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

        await call("Page.enable")
        await call("Runtime.enable")

        # Switch to 3D tab
        res = await call("Runtime.evaluate", {
            "expression": """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    if (st && st.contentWindow && st.contentWindow.switchNav) {
                        st.contentWindow.switchNav('viewer3d');
                        return 'switched via switchNav';
                    }
                    const doc = st ? st.contentDocument : document;
                    const nav3D = Array.from(doc.querySelectorAll('.navItem')).find(el => el.textContent && el.textContent.includes('3D Visualization'));
                    if (nav3D) {
                        nav3D.click();
                        return 'clicked nav3D';
                    }
                    return 'not found';
                })()
            """,
            "returnByValue": True
        })
        val = res.get("result", {}).get("result", {}).get("value")
        print("Switch result:", val, flush=True)

        await asyncio.sleep(1.0)

        # Capture screenshot
        r = await call("Page.captureScreenshot", {"format": "png"})
        data = r.get("result", {}).get("data", "")
        out_path = os.path.join(ARTIFACT_DIR, "test_3d_tab.png")
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(data))
        print("Captured test_3d_tab.png:", len(data), flush=True)

if __name__ == "__main__":
    asyncio.run(test())
