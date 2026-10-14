import asyncio, json, urllib.request, websockets

async def main():
    pages = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read().decode())
    target = next((p for p in pages if 'CardioVision' in p.get('title', '')), pages[0])
    msg_counter = 0

    async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
        async def cdp_eval(expr):
            nonlocal msg_counter
            msg_counter += 1
            payload = {'id': msg_counter, 'method': 'Runtime.evaluate', 'params': {'expression': expr, 'returnByValue': True, 'awaitPromise': True}}
            await ws.send(json.dumps(payload))
            while True:
                r = json.loads(await ws.recv())
                if r.get('id') == msg_counter:
                    return r.get('result', {}).get('result', {}).get('value')

        await ws.send(json.dumps({'id': 999, 'method': 'Page.bringToFront'}))
        await ws.recv()

        res = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                const cam = vWin.CardioVision3D.camera;
                const ctrl = vWin.CardioVision3D.controls;
                
                let stepEvents = [];
                vWin._stepEvents = stepEvents;
                
                // Let's inspect animateCameraTo implementation in vWin
                // Let's test calling animateCameraTo with tracking
                const THREE = cam.constructor;
                
                const startPos = cam.position.clone();
                const endPos = new startPos.constructor(0, 8.5, 0.24);
                
                let animId = null;
                const startTime = performance.now();
                function myStep(now) {
                    stepEvents.push({ now, elapsed: now - startTime });
                    if (now - startTime < 300) {
                        animId = vWin.requestAnimationFrame(myStep);
                    }
                }
                animId = vWin.requestAnimationFrame(myStep);
                
                return { started: true };
            })()
        """)
        print("Test RAF start:", res)

        await asyncio.sleep(0.5)

        res2 = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                return { stepCount: vWin._stepEvents ? vWin._stepEvents.length : 0, first: vWin._stepEvents[0], last: vWin._stepEvents[vWin._stepEvents.length - 1] };
            })()
        """)
        print("Test RAF result:", res2)

if __name__ == '__main__':
    asyncio.run(main())
