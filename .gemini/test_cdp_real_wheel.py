import asyncio, json, urllib.request, websockets

async def main():
    pages = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json/list').read().decode())
    target = next((p for p in pages if 'CardioVision' in p.get('title', '')), pages[0])
    msg_counter = 0

    async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
        async def cdp_call(method, params=None):
            nonlocal msg_counter
            msg_counter += 1
            payload = {'id': msg_counter, 'method': method, 'params': params or {}}
            await ws.send(json.dumps(payload))
            while True:
                r = json.loads(await ws.recv())
                if r.get('id') == msg_counter:
                    return r.get('result', {})

        await cdp_call('Page.bringToFront')

        # Get canvas center in screen coordinates
        rect_info = (await cdp_call('Runtime.evaluate', {
            'expression': """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const stRect = st.getBoundingClientRect();
                    const v = st.contentDocument.getElementById('viewerIframe');
                    const vRect = v.getBoundingClientRect();
                    return {
                        x: Math.round(stRect.left + vRect.left + (vRect.width / 2)),
                        y: Math.round(stRect.top + vRect.top + (vRect.height / 2))
                    };
                })()
            """,
            'returnByValue': True
        })).get('result', {}).get('value', {})
        print("Canvas center screen coordinates:", rect_info)

        # Get initial camera distance
        d_init = (await cdp_call('Runtime.evaluate', {
            'expression': """
                (() => {
                    const st = document.querySelector('.stIFrame');
                    const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                    const cam = vWin.CardioVision3D.camera;
                    const ctrl = vWin.CardioVision3D.controls;
                    return cam.position.distanceTo(ctrl.target);
                })()
            """,
            'returnByValue': True
        })).get('result', {}).get('value', 0)
        print(f"Initial distance before CDP wheel: {d_init:.2f}")

        # Dispatch 10 wheel up events (deltaY: -100) via CDP Input.dispatchMouseEvent
        zoom_in_distances = [d_init]
        for i in range(10):
            await cdp_call('Input.dispatchMouseEvent', {
                'type': 'mouseWheel',
                'x': rect_info['x'],
                'y': rect_info['y'],
                'deltaX': 0,
                'deltaY': -100
            })
            await asyncio.sleep(0.05)
            d_curr = (await cdp_call('Runtime.evaluate', {
                'expression': """
                    (() => {
                        const st = document.querySelector('.stIFrame');
                        const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                        const cam = vWin.CardioVision3D.camera;
                        const ctrl = vWin.CardioVision3D.controls;
                        return cam.position.distanceTo(ctrl.target);
                    })()
                """,
                'returnByValue': True
            })).get('result', {}).get('value', 0)
            zoom_in_distances.append(d_curr)

        print(f"Distances during 10x CDP wheel-up: {[round(d, 2) for d in zoom_in_distances]}")
        is_zoom_in_working = zoom_in_distances[-1] < zoom_in_distances[0]
        print(f"CDP real wheel zoom-in successful: {is_zoom_in_working}")

        # Dispatch 10 wheel down events (deltaY: +100) via CDP
        zoom_out_distances = [zoom_in_distances[-1]]
        for i in range(10):
            await cdp_call('Input.dispatchMouseEvent', {
                'type': 'mouseWheel',
                'x': rect_info['x'],
                'y': rect_info['y'],
                'deltaX': 0,
                'deltaY': 100
            })
            await asyncio.sleep(0.05)
            d_curr = (await cdp_call('Runtime.evaluate', {
                'expression': """
                    (() => {
                        const st = document.querySelector('.stIFrame');
                        const vWin = st.contentDocument.getElementById('viewerIframe').contentWindow;
                        const cam = vWin.CardioVision3D.camera;
                        const ctrl = vWin.CardioVision3D.controls;
                        return cam.position.distanceTo(ctrl.target);
                    })()
                """,
                'returnByValue': True
            })).get('result', {}).get('value', 0)
            zoom_out_distances.append(d_curr)

        print(f"Distances during 10x CDP wheel-down: {[round(d, 2) for d in zoom_out_distances]}")
        is_zoom_out_working = zoom_out_distances[-1] > zoom_out_distances[0]
        print(f"CDP real wheel zoom-out successful: {is_zoom_out_working}")

if __name__ == '__main__':
    asyncio.run(main())
