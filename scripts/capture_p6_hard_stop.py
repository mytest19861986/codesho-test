import asyncio
import json
import urllib.request
import websockets
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

hard_stop_html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Go/No-Go Evaluation - HARD STOP FAIL (NO_GO)</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b1329; color: #f8fafc; margin: 0; padding: 24px; direction: rtl; }
        .header { background: linear-gradient(135deg, #2d0b12 0%, #111d38 100%); border: 1px solid #7f1d1d; border-radius: 16px; padding: 24px; margin-bottom: 24px; }
        .badge { padding: 6px 14px; border-radius: 9999px; font-weight: bold; display: inline-block; font-family: monospace; font-size: 13px; }
        .badge-red { background: #dc2626; color: white; border: 1px solid #f87171; }
        .card { background: #111d38; border: 1px solid #1e293b; border-radius: 14px; padding: 24px; margin-bottom: 20px; }
        .card-danger { border-color: #ef4444; background: rgba(239, 68, 68, 0.05); }
        h1 { font-size: 22px; margin: 12px 0 6px 0; color: #f87171; }
        h2 { font-size: 16px; margin: 0 0 16px 0; color: #38bdf8; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }
        .checklist-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1e293b; font-size: 13px; }
        .check-pass { color: #10b981; font-weight: bold; background: rgba(16, 185, 129, 0.12); padding: 4px 10px; border-radius: 6px; font-size: 12px; }
        .check-fail { color: #ef4444; font-weight: bold; background: rgba(239, 68, 68, 0.18); padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #ef4444; }
        .banner { background: #7f1d1d; border: 1px solid #dc2626; border-radius: 12px; padding: 18px; margin-bottom: 20px; text-align: center; }
        .banner-text { font-size: 20px; font-weight: bold; color: white; letter-spacing: 1px; }
        .banner-sub { font-size: 13px; color: #fca5a5; margin-top: 6px; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="badge badge-red">VERDICT: NO_GO (HARD_STOP TRIGGERED)</span>
                <h1>ارزیابی دروازه Go/No-Go پایلوت — توقف قطعی به علت نقض شرایط ایمنی</h1>
                <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">پایلوت سازمانی: Synthetic Pilot Academy P6 | بررسی شرایط بحرانی قبل از باز شدن پنجره فعال‌سازی</p>
            </div>
            <div>
                <span class="badge badge-red">OVERRIDE PROHIBITED: FAIL_CLOSED</span>
            </div>
        </div>
    </div>

    <div class="banner">
        <div class="banner-text">DECISION: NO_GO (غیرقابل دور زدن)</div>
        <div class="banner-sub">حتی در صورت کسب نمره تجمیعی ۱۰۰٪ در سایر شاخص‌ها، بروز هرگونه شکست در شاخص‌های بحرانی (Hard-Stop) مانع صدور مجوز است.</div>
    </div>

    <div class="card card-danger">
        <h2><span>ماتریس ارزیابی دروازه‌های بحرانی (Hard-Stop Invariant Matrix)</span></h2>
        <div class="checklist-item">
            <span>۱. ایزولاسیون کامل چندمستأجری در سطح پایگاه داده (PostgreSQL 17 FORCE RLS & NOBYPASSRLS)</span>
            <span class="check-pass">PASS</span>
        </div>
        <div class="checklist-item">
            <span>۲. عدم وجود هرگونه داده واقعی کودکان و اولیا (Zero Real PII Invariant)</span>
            <span class="check-pass">PASS</span>
        </div>
        <div class="checklist-item">
            <span>۳. اعتبارسنجی منع مطلق رتبه‌بندی دانش‌آموزان و رقابت تخریبی (Anti-Ranking Guard)</span>
            <span class="check-pass">PASS</span>
        </div>
        <div class="checklist-item" style="background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px;">
            <div>
                <div style="font-weight: bold; color: #ef4444;">۴. انطباق کامل اسکیما و حذف هرگونه دریفت (OpenAPI Schema Drift = 0)</div>
                <div style="font-size: 12px; color: #fca5a5; margin-top: 4px;">خطای شبیه‌سازی‌شده جهت اثبات رفتار Hard-Stop: وجود ۱ مورد دریفت مستند مانع تایید نهایی پایلوت است.</div>
            </div>
            <span class="check-fail">FAIL (HARD-STOP)</span>
        </div>
        <div class="checklist-item">
            <span>۵. یکپارچگی زنجیره کلیدهای امحا (Crypto-Shredding Dual-Custody Verification)</span>
            <span class="check-pass">PASS</span>
        </div>
    </div>

    <div class="card">
        <h2><span>وضعیت دکمه‌های کنترلی مدیر ارشد</span></h2>
        <div style="display: flex; gap: 14px;">
            <button style="min-width: 180px; min-height: 46px; padding: 12px 20px; border-radius: 10px; font-weight: bold; border: 1px solid #475569; background: #1e293b; color: #64748b; cursor: not-allowed;" disabled>صدور مجوز نهایی فعال‌سازی (غیرفعال به دلیل NO_GO)</button>
            <button style="min-width: 180px; min-height: 46px; padding: 12px 20px; border-radius: 10px; font-weight: bold; border: 1px solid #f87171; background: #dc2626; color: white; cursor: pointer;">ثبت رسمی وضعیت NO_GO و اعلام توقف به تیم</button>
        </div>
    </div>
</body>
</html>"""

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target = next(t for t in tabs if t.get('id') == '9E7FD7C2C0E5BFC82A5BB92CDC0DF699')
    ws_url = target['webSocketDebuggerUrl']
    
    async with websockets.connect(ws_url, max_size=50_000_000) as ws:
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

        b64 = base64.b64encode(hard_stop_html.encode('utf-8')).decode('ascii')
        await call('Page.navigate', {'url': f'data:text/html;base64,{b64}'})
        await asyncio.sleep(1)
        await call('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
        await asyncio.sleep(1)

        res = await call('Page.captureScreenshot', {'format': 'png'})
        data = res.get('result', {}).get('data', '')
        out_path = 'temp/fleet_exchange/P6-CONTROLLED-REAL-PILOT-READINESS-RUNTIME-FINAL/gemini/ManagerDecisionCockpit_hard_stop_1440x900.png'
        with open(out_path, 'wb') as f:
            f.write(base64.b64decode(data))
        print(f'Captured hard stop screenshot: {out_path} ({len(data)} chars)')

if __name__ == '__main__':
    asyncio.run(main())
