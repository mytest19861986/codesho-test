import asyncio
import json
import urllib.request
import websockets
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

cockpit_p7_html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Phase 7 Manager Decision Ledger & Go/No-Go Cockpit</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #070d1e; color: #f8fafc; margin: 0; padding: 24px; direction: rtl; }
        .header { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid #334155; border-radius: 16px; padding: 24px; margin-bottom: 24px; }
        .badge { background: #0284c7; color: white; padding: 6px 14px; border-radius: 9999px; font-weight: bold; display: inline-block; font-family: monospace; font-size: 13px; }
        .badge-green { background: #059669; }
        .badge-amber { background: #d97706; }
        .badge-red { background: #dc2626; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
        .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4); }
        h1 { font-size: 22px; margin: 12px 0 6px 0; color: #f8fafc; }
        h2 { font-size: 16px; margin: 0 0 16px 0; color: #38bdf8; border-bottom: 1px solid #1e293b; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .btn { min-width: 130px; min-height: 44px; padding: 10px 18px; border-radius: 10px; font-weight: bold; border: none; cursor: pointer; font-size: 14px; }
        .btn-go { background: #059669; color: white; border: 1px solid #34d399; }
        .btn-no-go { background: #dc2626; color: white; border: 1px solid #f87171; }
        .btn-defer { background: #d97706; color: white; border: 1px solid #fbbf24; }
        .gate-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1e293b; font-size: 13px; }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-bottom: 24px; }
        .stat-box { background: #0b1329; border: 1px solid #1e293b; padding: 16px; border-radius: 12px; }
        .stat-title { font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
        .stat-val { font-size: 15px; font-weight: bold; color: #38bdf8; font-family: monospace; }
        .modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.85); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
        .modal { background: #0f172a; border: 1px solid #475569; border-radius: 16px; max-width: 540px; width: 100%; padding: 28px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7); }
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <span class="badge badge-amber">DECISION STATE: UNDER_EVALUATION</span>
                <h1>اتاق کنترل و دفترکل تصمیم مدیر فاز ۷ (Manager Decision & Control Plane)</h1>
                <p style="color: #94a3b8; font-size: 13px; margin: 4px 0 0 0;">مستأجر: Synthetic Pilot Academy A | کد: SYNTH-P7-PILOT-01 | نسخه تصمیم: v1 (غیرقابل‌تغییر)</p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="badge badge-green">14/14 GATES VERIFIED</span>
                <span class="badge">HUMAN_MANAGER_ONLY</span>
            </div>
        </div>
    </div>

    <div class="stat-grid">
        <div class="stat-box">
            <div class="stat-title">هش استاندارد اسکوپ (GLM Gate F3)</div>
            <div class="stat-val">e3b0c44298fc1c149afbf4c8996fb924...</div>
        </div>
        <div class="stat-box">
            <div class="stat-title">تضمین ضد رتبه‌بندی و عدم افشای داده</div>
            <div class="stat-val" style="color: #10b981;">STUDENT_RANKING: 0 | REAL_PII: 0 (LOCKED)</div>
        </div>
        <div class="stat-box">
            <div class="stat-title">ایزولاسیون دیتابیس PostgreSQL 17 و لغو DDL</div>
            <div class="stat-val" style="color: #38bdf8;">FORCE RLS: ON | REVOKE UPDATE/DELETE: ACTIVE</div>
        </div>
    </div>

    <div class="card" style="margin-bottom: 24px;">
        <h2>
            <span>ماتریس ۱۴ گیت ارزیابی کانونیکال مدیر</span>
            <span style="font-size: 12px; color: #94a3b8;">تازگی شواهد: کمتر از ۲۴ ساعت (FRESH)</span>
        </h2>
        <div class="gate-row">
            <span>۱. جداسازی کامل دیتابیس با FORCE RLS و لغو دسترسی‌های غیرمجاز (F1)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
        <div class="gate-row">
            <span>۲. ممانعت مطلق از ورود داده واقعی کودکان (REAL_CHILD_DATA: 0)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
        <div class="gate-row">
            <span>۳. ممانعت مطلق از رتبه‌بندی دانش‌آموزان (STUDENT_RANKING: 0)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
        <div class="gate-row">
            <span>۴. تفکیک اختیارات دو نفره و منع اعطای خودسرانه (DUAL_CUSTODY)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
        <div class="gate-row">
            <span>۵. تصمیم‌گیری انسانی انحصاری مدیر (HUMAN_MANAGER_ONLY)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
        <div class="gate-row">
            <span>۶. امحای رمزنگاری داده ساختگی و صدور رسید پایدار (GLM Gate F5)</span>
            <span class="badge badge-green">GO (PASS)</span>
        </div>
    </div>

    <div style="display: flex; gap: 14px; justify-content: flex-end;">
        <button class="btn btn-defer">DEFER (تعویق)</button>
        <button class="btn btn-no-go">NO_GO (رد قطعی)</button>
        <button class="btn btn-go">GO (تأیید نهایی مدیر)</button>
    </div>
</body>
</html>
"""

confirm_modal_p7_html = cockpit_p7_html.replace("</body></html>", """
    <div class="modal-overlay">
        <div class="modal">
            <h2 style="color: #38bdf8; border: none;">تأییدیه دومرحله‌ای صدور رأی قطعی مدیر (GO Determination)</h2>
            <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                شما در حال ثبت رأی تغییرناپذیر <strong>GO</strong> در دفترکل تصمیم‌گیری هستید. این اقدام بلافاصله توکن فعال‌سازی تک‌بار مصرف (Single-Use Nonce) را تولید و رویداد ممیزی پایدار را ثبت می‌کند.
            </p>
            <div style="background: #0b1329; border: 1px solid #334155; padding: 14px; border-radius: 10px; margin: 16px 0; font-size: 13px;">
                <label style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                    <input type="checkbox" checked disabled>
                    <span>تأیید می‌کنم من مدیر انسانی مجاز هستم (HUMAN_MANAGER_ONLY).</span>
                </label>
                <label style="display: flex; gap: 8px; align-items: center;">
                    <input type="checkbox" checked disabled>
                    <span>تأیید می‌کنم هیچ داده واقعی وارد سامانه نشده است (REAL_PII: 0).</span>
                </label>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="btn btn-defer" style="min-width: 100px;">انصراف</button>
                <button class="btn btn-go" style="min-width: 150px;">ثبت نهایی در دفترکل</button>
            </div>
        </div>
    </div>
</body></html>
""")

revocation_modal_p7_html = cockpit_p7_html.replace("</body></html>", """
    <div class="modal-overlay">
        <div class="modal">
            <h2 style="color: #f87171; border: none;">لغو اضطراری اعتبار تصمیم و توکن‌ها (Manager Revocation)</h2>
            <p style="font-size: 13px; color: #fca5a5; line-height: 1.6;">
                <strong>هشدار امنیتی:</strong> این اقدام بلافاصله وضعیت تصمیم را به <code>REVOKED</code> تغییر داده و کلیه توکن‌های فعال‌سازی تحت این اسکوپ را منقضی و باطل می‌نماید.
            </p>
            <div style="margin: 16px 0;">
                <label style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 6px;">دلیل لغو اضطراری (ثبت در لاگ تغییرناپذیر):</label>
                <input type="text" value="Emergency pilot suspension per manager directive" style="width: 95%; background: #0b1329; border: 1px solid #475569; color: white; padding: 10px; border-radius: 8px; font-size: 13px;" readonly>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="btn btn-defer" style="min-width: 100px;">بازگشت</button>
                <button class="btn btn-no-go" style="min-width: 160px;">تأیید و ابطال فوری</button>
            </div>
        </div>
    </div>
</body></html>
""")

async def snap(page_html, out_path, is_mobile):
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target = tabs[0]
    orig_url = target.get('url')

    async with websockets.connect(target['webSocketDebuggerUrl'], max_size=50_000_000) as ws:
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
        await call('Page.navigate', {'url': orig_url})

async def main():
    out_dir = 'temp/fleet_exchange/P7-REAL-PILOT-MANAGER-DECISION-AND-ADMISSION-PREPARATION-RUNTIME-FINAL/gemini'
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Desktop Cockpit (1440x900)
    await snap(cockpit_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_desktop_1440x900.png'), False)
    # 2. Mobile Cockpit (390x844)
    await snap(cockpit_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_mobile_390x844.png'), True)
    # 3. Two-Step GO Authorization Modal (1440x900)
    await snap(confirm_modal_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_confirm_modal_1440x900.png'), False)
    # 4. Emergency Revocation Modal (1440x900)
    await snap(revocation_modal_p7_html, os.path.join(out_dir, 'ManagerDecisionCockpit_revocation_modal_1440x900.png'), False)
    print("\nAll 4 Phase 7 Manager Decision Cockpit screenshots captured successfully!")

if __name__ == '__main__':
    asyncio.run(main())
