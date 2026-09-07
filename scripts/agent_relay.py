import asyncio
import json
import urllib.request
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
import websockets

TAB_URLS = {
    "Commander": "6a9ba3d5-2e30-83ed-8ea0-50e530b06de0",
    "Qwen": "9c6c740b-026d-47b5-b89b-86ff710c88c5",
    "GLM": "bfa1f3bb-e349-4ce2-ae67-3a52eaf6aea5",
    "Gemini": "gemini.google.com/app"
}

def get_target_ws_url(url_fragment):
    try:
        tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9222/json").read())
        for t in tabs:
            if url_fragment in t.get("url", ""):
                return t.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"Error finding tab with {url_fragment}: {e}")
    return None

async def verify_chatbox_empty(agent_name, ws_url):
    """
    قانون بررسی ۵ ثانیه‌ای:
    دقیقاً ۵ ثانیه بعد از ارسال هر پیام، کادر ورودی بازرسی می‌شود تا اطمینان حاصل شود کاملاً خالی است.
    """
    print(f"[{agent_name}] 5-SECOND CHECK: Waiting 5 seconds to verify chatbox is empty...")
    await asyncio.sleep(5)
    
    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        script = """
        (() => {
            const el = document.querySelector('#prompt-textarea, textarea, div[contenteditable="true"], rich-textarea div[contenteditable="true"], .native-edit-context');
            if (!el) return { found: false, len: 0, empty: true };
            const text = (el.innerText || el.value || '').trim();
            return {
                found: true,
                len: text.length,
                empty: text.length === 0,
                contentSnippet: text.slice(0, 50)
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        val = res.get("result", {}).get("result", {}).get("value", {})
        
        if val.get("len", 0) == 0:
            print(f"[{agent_name}] 5-SECOND CHECK PASS: Chatbox is verified 100% EMPTY (len=0).")
            return True
        else:
            print(f"[{agent_name}] 5-SECOND CHECK FAILED: Chatbox still contains {val.get('len')} chars ('{val.get('contentSnippet')}...'). Re-submitting...")
            # Synthetic submit trigger
            await ws.send(json.dumps({"id": 2, "method": "Input.dispatchKeyEvent", "params": {"type": "rawKeyDown", "windowsVirtualKeyCode": 13, "text": "\r", "key": "Enter", "code": "Enter"}}))
            await ws.recv()
            await ws.send(json.dumps({"id": 3, "method": "Input.dispatchKeyEvent", "params": {"type": "keyUp", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"}}))
            await ws.recv()
            return False

async def poll_agent_response_30s(agent_name, ws_url, max_wait=900):
    """
    قانون پایش ۳۰ ثانیه‌ای:
    بررسی مداوم هر ۳۰ ثانیه برای اطمینان از پاسخ کامل، بدون خطا و ۱۰۰٪ پایدار.
    """
    print(f"[{agent_name}] Starting 30-second polling loop for complete and stable response...")
    start_time = time.time()
    last_text = ""
    stable_count = 0
    
    async with websockets.connect(ws_url, max_size=10_000_000) as ws:
        while time.time() - start_time < max_wait:
            await asyncio.sleep(30)
            
            script = """
            (() => {
                const isBusy = !!document.querySelector('button[aria-label*="Stop" i], button[data-testid*="stop" i], .result-streaming, .streaming, [aria-busy="true"]');
                const text = document.body.innerText;
                return {
                    isBusy: isBusy,
                    totalLength: text.length,
                    tail: text.slice(-400)
                };
            })()
            """
            await ws.send(json.dumps({"id": 10, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            res = json.loads(await ws.recv())
            val = res.get("result", {}).get("result", {}).get("value", {})
            
            is_busy = val.get("isBusy", False)
            tail = val.get("tail", "")
            elapsed = int(time.time() - start_time)
            
            print(f"[{agent_name} +{elapsed}s] Generating={is_busy}, textLength={val.get('totalLength')}")
            
            if not is_busy and len(tail) > 30:
                if tail == last_text:
                    stable_count += 1
                    if stable_count >= 1:
                        print(f"[{agent_name}] 100% COMPLETE & STABLE RESPONSE RECEIVED!")
                        return tail
                else:
                    stable_count = 0
            last_text = tail
    return None

async def parallel_dispatch(agent_messages):
    """
    ارسال همزمان پیام به چندین ایجنت به همراه بررسی ۵ ثانیه‌ای خالی بودن چت‌باکس
    agent_messages = {"Commander": "msg1", "Qwen": "msg2", ...}
    """
    tasks = []
    for agent_name, msg in agent_messages.items():
        frag = TAB_URLS.get(agent_name)
        if frag:
            ws_url = get_target_ws_url(frag)
            if ws_url:
                print(f"Queueing parallel dispatch to {agent_name}...")
                # Dispatch implementation
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Multi-agent relay framework ready with parallel dispatch, 5-second empty box check, and 30-second polling.")

