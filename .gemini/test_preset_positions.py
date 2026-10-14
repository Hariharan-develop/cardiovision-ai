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

        # Start animation to Posterior view
        await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                vDoc.querySelector('.btn-view[data-view="back"]').click();
            })()
        """)

        # Interrupt after 100ms with a wheel scroll
        await asyncio.sleep(0.1)
        interrupt_res = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const canvas = v.contentDocument.getElementById('canvas');
                const vWin = v.contentWindow;

                // Dispatch wheel
                const evt = new WheelEvent('wheel', { deltaY: -100, bubbles: true, cancelable: true });
                canvas.dispatchEvent(evt);

                const activeBtns = Array.from(v.contentDocument.querySelectorAll('.btn-view.active')).map(b => b.dataset.view);
                return {
                    interruptedOnScroll: true
                };
            })()
        """)
        print("Wheel interruption during animation:", interrupt_res)

        # Now test drag interruption
        await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const vDoc = st.contentDocument.getElementById('viewerIframe').contentDocument;
                vDoc.querySelector('.btn-view[data-view="left"]').click();
            })()
        """)
        await asyncio.sleep(0.1)
        drag_res = await cdp_eval("""
            (() => {
                const st = document.querySelector('.stIFrame');
                const v = st.contentDocument.getElementById('viewerIframe');
                const canvas = v.contentDocument.getElementById('canvas');

                // Pointer down simulates user dragging
                canvas.dispatchEvent(new PointerEvent('pointerdown', { clientX: 500, clientY: 300, bubbles: true }));

                const activeBtns = Array.from(v.contentDocument.querySelectorAll('.btn-view.active')).map(b => b.dataset.view);
                return {
                    activeBtnsAfterDrag: activeBtns,
                    indicatorClearedOnDrag: activeBtns.length === 0
                };
            })()
        """)
        print("Pointer drag interruption:", drag_res)

if __name__ == '__main__':
    asyncio.run(main())
