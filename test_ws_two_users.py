import asyncio
import websockets
import json

CONVERSATION_ID = "578a3514-765c-48f6-9552-1b0ff9944bc7"
USER1_TOKEN = "hU1X0RmUAcg7ChHuFOolCFUq1hFPhQjX2deW9PPnyfI"
USER2_TOKEN = "oqI6Psg2C5VmQlFuXZTlyBkbk0ELMuhC3Ud-5y7xKbM"


async def listen(name, token):
    uri = f"ws://127.0.0.1:8000/ws/chat/{CONVERSATION_ID}/?token={token}"
    async with websockets.connect(uri) as ws:
        print(f"[{name}] connected")
        while True:
            msg = await ws.recv()
            print(f"[{name}] received: {msg}")


async def sender(token):
    uri = f"ws://127.0.0.1:8000/ws/chat/{CONVERSATION_ID}/?token={token}"
    async with websockets.connect(uri) as ws:
        await asyncio.sleep(2)  # give the listener time to connect first
        print("[User1] sending message...")
        await ws.send(json.dumps({"text": "Can you see this instantly?"}))
        await asyncio.sleep(2)  # stay open long enough to see the echo


async def main():
    # Run User 2 as a pure listener, and User 1 as the one who sends
    await asyncio.gather(
        listen("User2", USER2_TOKEN),
        sender(USER1_TOKEN),
    )


asyncio.run(main())