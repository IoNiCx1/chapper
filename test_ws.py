import asyncio
import websockets
import json

CONVERSATION_ID = "578a3514-765c-48f6-9552-1b0ff9944bc7"
TOKEN = "hU1X0RmUAcg7ChHuFOolCFUq1hFPhQjX2deW9PPnyfI"  # User 1's token

async def main():
    uri = f"ws://127.0.0.1:8000/ws/chat/{CONVERSATION_ID}/?token={TOKEN}"
    async with websockets.connect(uri) as websocket:
        print("Connected!")

        # Send a test message
        await websocket.send(json.dumps({"text": "Hello from the WebSocket test!"}))
        print("Sent message")

        # Wait for the broadcast to come back
        response = await websocket.recv()
        print("Received:", response)

asyncio.run(main())