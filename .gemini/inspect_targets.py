import asyncio
import json
import urllib.request
import websockets

async def test():
    for tid in ['A0E4F62E0F10FE3A8B7E7BECCEB1F2F7', 'F328731CF280374AE9B5F7A473EC1D04', 'ED0E406F3A3F1A0ECAAA44D0F96FEFE7']:
        ws_url = f'ws://localhost:9222/devtools/page/{tid}'
        try:
            async with websockets.connect(ws_url) as ws:
                await ws.send(json.dumps({
                    'id': 1,
                    'method': 'Runtime.evaluate',
                    'params': {
                        'expression': '({ url: location.href, iframes: document.querySelectorAll("iframe").length, title: document.title })',
                        'returnByValue': True
                    }
                }))
                res = json.loads(await ws.recv())
                print(tid, res.get('result', {}).get('value'))
        except Exception as e:
            print(tid, 'Error:', e)

if __name__ == "__main__":
    asyncio.run(test())
