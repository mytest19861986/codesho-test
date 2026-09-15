import asyncio
import json
import urllib.request
import websockets
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from capture_p7_gemini_screenshots import (
    cockpit_p7_html,
    confirm_modal_p7_html,
    revocation_modal_p7_html
)

async def snap_one(ws, page_html, out_path, is_mobile):
    msg_id = 1
    async def call(method, params=None):
        nonlocal msg_id
        curr = msg_id
        msg_id += 1
        await ws.send(json.dumps({'id': curr, 'method': method, 'params': params or {}}))
        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            if data.get('id') == curr:
                return data

    b64 = base64.b64encode(page_html.encode('utf-8')).decode('ascii')
    await call('Page.navigate', {'url': f'data:text/html;base64,{b64}'})
    await asyncio.sleep(1)

    if is_mobile:
        await call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
    else:
        await call('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
    await asyncio.sleep(1)

    res = await call('Page.captureScreenshot', {'format': 'png'})
    data = res.get('result', {}).get('data', '')
    with open(out_path, 'wb') as f:
        f.write(base64.b64decode(data))
    print(f"Captured {out_path} ({len(data)} chars base64)")
    await call('Emulation.clearDeviceMetricsOverride')

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target = tabs[0]
    orig_url = target.get('url')
    out_dir = 'temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini'

    async with websockets.connect(target['webSocketDebuggerUrl'], max_size=50_000_000) as ws:
        # 1. Desktop
        await snap_one(ws, cockpit_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_desktop_1440x900.png'), False)
        # 2. Mobile
        await snap_one(ws, cockpit_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_mobile_390x844.png'), True)
        # 3. Confirm Modal
        await snap_one(ws, confirm_modal_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_confirm_modal_1440x900.png'), False)
        # 4. Revocation Modal
        await snap_one(ws, revocation_modal_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_revocation_modal_1440x900.png'), False)
        
        # Restore orig url
        msg_id = 100
        await ws.send(json.dumps({'id': msg_id, 'method': 'Page.navigate', 'params': {'url': orig_url}}))

    print("\nAll 4 screenshots captured successfully in single websocket connection!")

if __name__ == '__main__':
    asyncio.run(main())
