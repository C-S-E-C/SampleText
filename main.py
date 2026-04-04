import asyncio
from websockets.asyncio.server import serve
import websockets.exceptions
import json
import pairing
actions = []
async def handler(websocket):
    while True:
        try:
            msg = await websocket.recv()
            data = json.loads(msg)
            if not data['action'] in actions:
                await websocket.send(json.dumps({"error": "Invalid action"}))
            else:
                # ping
                if data['action'] == 'ping':
                    await websocket.send(json.dumps({"response": "pong"}))
                # start_pairing
                elif data['action'] == 'start_pairing':
                    await pairing.start_pairing(data, websocket)
        except websockets.exceptions.ConnectionClosedOK:
            break
        except Exception as e:
            print(f"Error receiving message: {e}")
            await websocket.close()
            break

async def main():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())