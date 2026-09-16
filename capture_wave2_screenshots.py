import asyncio
import json
import base64
import os
import urllib.request
import websockets

OUT_DIR = r"G:\project\codesho\codesho\docs\coordination\screenshots_wave2_after"
os.makedirs(OUT_DIR, exist_ok=True)

ROUTES = [
    ("STUDENT_DASHBOARD", "http://127.0.0.1/student"),
    ("STUDENT_LEARNING", "http://127.0.0.1/student/learning"),
    ("STUDENT_COACHING", "http://127.0.0.1/student/coaching"),
    ("STUDENT_GROWTH", "http://127.0.0.1/student/growth"),
    ("STUDENT_PORTFOLIO", "http://127.0.0.1/student/portfolio"),
]

VIEWPORTS = [
    ("DESKTOP_1440x900", 1440, 900, False),
    ("MOBILE_390x844", 390, 844, True),
]

async def capture_all():
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read().decode("utf-8"))
    tab = [t for t in tabs if t.get("id") == "14086648467E155409DF6CB851271E82"][0]

    async with websockets.connect(tab["webSocketDebuggerUrl"], max_size=50*1024*1024) as ws:
        msg_id = 100
        async def run_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == msg_id:
                    return msg

        for r_name, r_url in ROUTES:
            for vp_name, w, h, is_mobile in VIEWPORTS:
                await run_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": w,
                    "height": h,
                    "deviceScaleFactor": 1,
                    "mobile": is_mobile
                })
                
                await run_cmd("Page.navigate", {"url": r_url})
                await asyncio.sleep(2.5)
                
                res = await run_cmd("Page.captureScreenshot", {"format": "png"})
                data = res.get("result", {}).get("data")
                if data:
                    filename = f"{r_name}_{vp_name}.png"
                    filepath = os.path.join(OUT_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(data))
                    print(f"Captured: {filename} ({os.path.getsize(filepath)} bytes)")
                else:
                    print(f"Error capturing: {r_name} {vp_name}, result: {res}")

        print("Done capturing all 10 screenshots.")

if __name__ == "__main__":
    asyncio.run(capture_all())
