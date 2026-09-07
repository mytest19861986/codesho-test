import sys
import json
import urllib.request
import websockets
import asyncio

sys.stdout.reconfigure(encoding='utf-8')

async def inspect_agent(url_snippet, name):
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read().decode())
    target = next((t for t in tabs if url_snippet in t.get('url', '')), None)
    if not target:
        print(f"[{name}] Tab not found")
        return
    
    ws_url = target['webSocketDebuggerUrl']
    async with websockets.connect(ws_url) as ws:
        js = """
        (() => {
            const msgs = document.querySelectorAll('.message, [data-message-author-role="assistant"], .model-response-text, .response-content, message-content, article, div.chat-message');
            const last = msgs[msgs.length - 1];
            return last ? last.innerText : 'EMPTY';
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        text = res.get("result", {}).get("result", {}).get("value", "")
        print(f"==================== {name} LAST MESSAGE (Length: {len(text)}) ====================")
        print(text[-800:] if len(text) > 800 else text)
        print("=================================================================================\n")

async def main():
    await inspect_agent('9c6c740b-026d-47b5-b89b-86ff710c88c5', 'QWEN')
    await inspect_agent('bfa1f3bb-e349-4ce2-ae67-3a52eaf6aea5', 'GLM')

if __name__ == '__main__':
    asyncio.run(main())
