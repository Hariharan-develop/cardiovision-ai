import asyncio, json, urllib.request, websockets

async def check():
    pages = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json/list").read().decode())
    target = [p for p in pages if "8501" in p.get("url", "")][0]
    async with websockets.connect(target["webSocketDebuggerUrl"]) as ws:
        await ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """(() => {
                    const stFrame = document.querySelector('.stIFrame');
                    if (!stFrame) return { error: 'no stFrame' };
                    const vIframe = stFrame.contentDocument.getElementById('viewerIframe');
                    if (!vIframe) return { error: 'no viewerIframe' };
                    const vWin = vIframe.contentWindow;
                    const vent = vWin.root ? vWin.root.children.find(c => c.userData && c.userData.group === 'ventricles') : null;
                    const lad = vWin.root ? vWin.root.children.find(c => c.userData && c.userData.group === 'lad') : null;
                    const state = vWin.CardioVision3D ? vWin.CardioVision3D.getHeartbeatState() : null;
                    return {
                        state,
                        ventScale: vent ? [vent.scale.x, vent.scale.y, vent.scale.z] : null,
                        ladScale: lad ? [lad.scale.x, lad.scale.y, lad.scale.z] : null,
                        ventPos: vent ? [vent.position.x, vent.position.y, vent.position.z] : null,
                        ladPos: lad ? [lad.position.x, lad.position.y, lad.position.z] : null
                    };
                })()""",
                "returnByValue": True
            }
        }))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(check())
