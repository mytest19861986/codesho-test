import websocket
import json
import urllib.request
import base64
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = r'G:\project\codesho\codesho\codesho\docs\evidence\post_wave3_visual_review'
os.makedirs(OUT_DIR, exist_ok=True)

def capture_suite():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    parent_tab = next(t for t in tabs if 'parent' in t.get('url', '') or '3001' in t.get('url', ''))
    print("Connecting to tab:", parent_tab['url'])
    
    ws = websocket.create_connection(parent_tab['webSocketDebuggerUrl'], suppress_origin=True)
    msg_id = 0
    def cdp(method, params=None):
        nonlocal msg_id
        msg_id += 1
        ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
        while True:
            resp = json.loads(ws.recv())
            if resp.get('id') == msg_id:
                return resp

    print("1. Capturing parent_desktop_1440x900...")
    cdp('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
    cdp('Page.navigate', {'url': 'http://172.19.144.16:3001/parent'})
    time.sleep(3.0)
    shot1 = cdp('Page.captureScreenshot', {'format': 'png'})
    with open(os.path.join(OUT_DIR, 'parent_desktop_1440x900.png'), 'wb') as f:
        f.write(base64.b64decode(shot1['result']['data']))
    print('Captured parent_desktop_1440x900.png')

    print("2. Capturing parent_above_fold_close...")
    shot2 = cdp('Page.captureScreenshot', {'format': 'png', 'clip': {'x': 250, 'y': 70, 'width': 1150, 'height': 380, 'scale': 1}})
    with open(os.path.join(OUT_DIR, 'parent_above_fold_close.png'), 'wb') as f:
        f.write(base64.b64decode(shot2['result']['data']))
    print('Captured parent_above_fold_close.png')

    print("3. Capturing parent_kpi_strip_close...")
    shot3 = cdp('Page.captureScreenshot', {'format': 'png', 'clip': {'x': 250, 'y': 380, 'width': 1150, 'height': 150, 'scale': 1}})
    with open(os.path.join(OUT_DIR, 'parent_kpi_strip_close.png'), 'wb') as f:
        f.write(base64.b64decode(shot3['result']['data']))
    print('Captured parent_kpi_strip_close.png')

    print("4. Capturing parent_notification_popover_close...")
    click_bell_js = "(() => { const b = document.querySelector('button[aria-label=\"اعلان‌های نظارتی\"]'); if (b) b.click(); })()"
    cdp('Runtime.evaluate', {'expression': click_bell_js})
    time.sleep(1.0)
    shot4 = cdp('Page.captureScreenshot', {'format': 'png', 'clip': {'x': 850, 'y': 10, 'width': 550, 'height': 450, 'scale': 1}})
    with open(os.path.join(OUT_DIR, 'parent_notification_popover_close.png'), 'wb') as f:
        f.write(base64.b64decode(shot4['result']['data']))
    print('Captured parent_notification_popover_close.png')

    print("5. Capturing parent_mobile_390x844...")
    cdp('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 2, 'mobile': True})
    cdp('Page.navigate', {'url': 'http://172.19.144.16:3001/parent'})
    time.sleep(3.0)
    shot5 = cdp('Page.captureScreenshot', {'format': 'png'})
    with open(os.path.join(OUT_DIR, 'parent_mobile_390x844.png'), 'wb') as f:
        f.write(base64.b64decode(shot5['result']['data']))
    print('Captured parent_mobile_390x844.png')
    ws.close()
    print("All 5 captures complete successfully!")

if __name__ == '__main__':
    capture_suite()
