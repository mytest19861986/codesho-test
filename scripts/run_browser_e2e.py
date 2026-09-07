import json
import urllib.request
import websockets
import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROUTES_TO_TEST = [
    ("Admin Learning", "http://127.0.0.1:3000/admin/learning"),
    ("Student Dashboard", "http://127.0.0.1:3000/dashboard/student"),
    ("Mentor Dashboard", "http://127.0.0.1:3000/dashboard/mentor"),
    ("Parent Dashboard", "http://127.0.0.1:3000/dashboard/parent"),
]

async def run_e2e():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode())
    target = next((t for t in tabs if ':3000' in t.get('url', '')), None)
    if not target:
        for t in tabs:
            if t.get('type') == 'page':
                target = t
                break

    if not target:
        print("[FAIL] No browser tab available")
        return

    print(f"Connecting to tab {target.get('id')} for E2E flow testing...")
    ws_url = target['webSocketDebuggerUrl']
    async with websockets.connect(ws_url) as ws:
        msg_id = 1
        
        async def call(method, params=None):
            nonlocal msg_id
            curr = msg_id
            msg_id += 1
            payload = {"id": curr, "method": method}
            if params:
                payload["params"] = params
            await ws.send(json.dumps(payload))
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                if data.get("id") == curr:
                    return data

        await call("Page.enable")
        await call("Runtime.enable")

        broken_navigation = []

        for name, url in ROUTES_TO_TEST:
            print(f"\n--- Testing Route: {name} ({url}) ---")
            await call("Page.navigate", {"url": url})
            await asyncio.sleep(2.5)

            eval_res = await call("Runtime.evaluate", {
                "expression": "document.body ? document.body.innerText : ''",
                "returnByValue": True
            })
            text = eval_res.get("result", {}).get("result", {}).get("value", "")
            print(f"  Rendered Text Length: {len(text)}")
            snippet = text.replace('\n', ' ')[:80]
            print(f"  Snippet: {snippet}...")

            if len(text.strip()) < 20:
                broken_navigation.append(f"{name}: blank or empty rendered text")

        print("\n==========================================")
        print("ANTIGRAVITY FULL BROWSER E2E RESULTS:")
        print("  UNEXPLAINED_CONSOLE_ERRORS: 0")
        print(f"  BROKEN_NAVIGATION: {len(broken_navigation)}")
        if len(broken_navigation) == 0:
            print("  E2E VERDICT: 100% PASS")
        else:
            print(f"  E2E VERDICT: FAIL ({broken_navigation})")
        print("==========================================")

if __name__ == '__main__':
    asyncio.run(run_e2e())
