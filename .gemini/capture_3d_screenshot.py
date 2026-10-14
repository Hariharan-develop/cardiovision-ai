import asyncio, json, urllib.request, websockets, base64

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
        await asyncio.sleep(1)

        # Capture screenshot
        shot = await cdp_call('Page.captureScreenshot', {'format': 'png'})
        data = base64.b64decode(shot['data'])
        out_path = 'C:/Users/hario/.gemini/antigravity-ide/brain/8cd09337-1c91-438d-aacf-249a561d03c7/final_3d_viewer_verified.png'
        with open(out_path, 'wb') as f:
            f.write(data)
        print("Saved screenshot to:", out_path)

if __name__ == '__main__':
    asyncio.run(main())
