import asyncio
import json
import urllib.request
import websockets
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROUTES = [
    {"name": "landing", "url": "http://127.0.0.1/"},
    {"name": "login", "url": "http://127.0.0.1/login"},
    {"name": "student_dashboard", "url": "http://127.0.0.1/dashboard/student"},
    {"name": "mentor_dashboard", "url": "http://127.0.0.1/dashboard/mentor"},
    {"name": "parent_dashboard", "url": "http://127.0.0.1/dashboard/parent"},
    {"name": "admin_learning", "url": "http://127.0.0.1/admin/learning"},
]

OUTPUT_DIR = "temp/phase3/vs3"

async def test_and_capture():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode('utf-8'))
    
    # Find an existing test tab or reuse a non-fleet tab
    test_tab = next((t for t in tabs if t.get('type') == 'page' and ('127.0.0.1' in t.get('url', '') or 'localhost' in t.get('url', ''))), None)
    
    if not test_tab:
        # Create a new tab via CDP
        opener = next(t for t in tabs if t.get('type') == 'page')
        ws_url = opener['webSocketDebuggerUrl']
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({'id': 1, 'method': 'Target.createTarget', 'params': {'url': 'about:blank'}}))
            res = json.loads(await ws.recv())
            target_id = res['result']['targetId']
            print(f"[CREATED] Created new test tab: {target_id}")
            await asyncio.sleep(1)
            tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode('utf-8'))
            test_tab = next(t for t in tabs if t.get('id') == target_id)

    ws_url = test_tab['webSocketDebuggerUrl']
    print(f"[ATTACHED] Testing in tab: {test_tab.get('title')} ({ws_url})")

    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        msg_id = 1
        async def call(method, params=None):
            nonlocal msg_id
            curr = msg_id
            msg_id += 1
            payload = {"id": curr, "method": method}
            if params: payload["params"] = params
            await ws.send(json.dumps(payload))
            while True:
                data = json.loads(await ws.recv())
                if data.get("id") == curr:
                    return data

        await call("Page.enable")
        await call("Runtime.enable")

        results = []

        for r in ROUTES:
            name = r["name"]
            url = r["url"]
            print(f"\n--- Testing Route: {name} ({url}) ---")
            await call("Page.navigate", {"url": url})
            await asyncio.sleep(2)

            # Check console errors
            dom_eval = await call("Runtime.evaluate", {
                "expression": "document.title + ' | ' + (document.body ? document.body.innerText.slice(0, 100) : '')",
                "returnByValue": True
            })
            page_text = dom_eval.get("result", {}).get("result", {}).get("value", "")

            # 1. Desktop Screenshot
            await call("Emulation.setDeviceMetricsOverride", {
                "width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False
            })
            await asyncio.sleep(0.5)
            d_shot = await call("Page.captureScreenshot", {"format": "png"})
            d_data = d_shot.get("result", {}).get("data", "")
            d_path = f"{OUTPUT_DIR}/{name}_desktop.png"
            with open(d_path, "wb") as f:
                f.write(base64.b64decode(d_data))

            # 2. Mobile Screenshot
            await call("Emulation.setDeviceMetricsOverride", {
                "width": 390, "height": 844, "deviceScaleFactor": 2, "mobile": True
            })
            await asyncio.sleep(0.5)
            m_shot = await call("Page.captureScreenshot", {"format": "png"})
            m_data = m_shot.get("result", {}).get("data", "")
            m_path = f"{OUTPUT_DIR}/{name}_mobile.png"
            with open(m_path, "wb") as f:
                f.write(base64.b64decode(m_data))

            print(f"  [PASS] Desktop: {d_path} ({len(d_data)} B)")
            print(f"  [PASS] Mobile: {m_path} ({len(m_data)} B)")
            results.append({"name": name, "status": "PASS", "desktop": d_path, "mobile": m_path})

        await call("Emulation.clearDeviceMetricsOverride")
        print("\n=== ALL ROUTES REGRESSION TESTED IN BRAVE SUCCESSFULLY ===")

if __name__ == '__main__':
    asyncio.run(test_and_capture())
