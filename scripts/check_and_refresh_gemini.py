import json
import urllib.request
import websockets
import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target = None
    for t in tabs:
        url = t.get('url', '')
        if 'gemini.google.com/app/3af5581dd212054b' in url:
            target = t
            break
            
    if not target:
        for t in tabs:
            if 'gemini.google.com' in t.get('url', ''):
                target = t
                break

    if not target:
        print("[ERROR] Gemini tab not found!")
        return

    print(f"Connecting to Gemini tab: {target.get('title')} ({target.get('id')})")
    async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
        # Check last message
        eval_script = """
        (() => {
            const msgs = document.querySelectorAll('.model-response-text, .response-content, message-content, [data-test-id="model-response"]');
            const last = msgs[msgs.length - 1];
            return {
                count: msgs.length,
                text: last ? last.innerText : ''
            };
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': eval_script, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        val = res.get('result', {}).get('result', {}).get('value', {})
        text = val.get('text', '')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"Total responses: {val.get('count')}")
        print(f"Total non-empty lines: {len(lines)}")
        print("Last message text:\n" + text[:300])

        if len(lines) <= 2 or len(text.strip()) < 80:
            print("\n[DETECTED SHORT/ONE-LINE RESPONSE] Triggering page reload and re-prompting...")
            # Reload page
            await ws.send(json.dumps({'id': 2, 'method': 'Page.reload'}))
            await ws.recv()
            print("Page reloaded. Waiting 8s for UI hydration...")
            await asyncio.sleep(8)
            print("Gemini tab ready for re-prompting.")
        else:
            print("\nResponse has sufficient lines/substance.")

if __name__ == '__main__':
    asyncio.run(main())
