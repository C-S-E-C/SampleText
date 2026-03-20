import asyncio
import json
import websockets

class SimpleWSServer:
    def __init__(self):
        self.clients = {}  # {user_id: websocket}
        self.msg_queue = asyncio.Queue()  # 消息收件箱

    async def _producer_handler(self, websocket, path):
        """内部接收协程：只负责把收到的消息丢进队列"""
        user_id = None
        try:
            async for raw_message in websocket:
                data = json.loads(raw_message)
                
                # 预处理登录，方便后续识别来源
                if data.get("type") == "login":
                    user_id = data.get("user_id")
                    self.clients[user_id] = websocket
                    print(f"[系统] {user_id} 已连接")
                    continue
                
                # 将消息包装后存入队列，等待你的主逻辑 get
                if user_id:
                    await self.msg_queue.put({"from": user_id, "data": data})

        except Exception as e:
            print(f"[错误] 连接异常: {e}")
        finally:
            if user_id in self.clients:
                del self.clients[user_id]

    async def get_message(self):
        """这就是你要的：阻塞式获取下一条消息"""
        return await self.msg_queue.get()

    async def send_private(self, to_id, payload):
        """私发"""
        ws = self.clients.get(to_id)
        if ws and ws.open:
            await ws.send(json.dumps(payload))

    async def broadcast(self, payload):
        """广播"""
        if not self.clients: return
        msg = json.dumps(payload)
        await asyncio.gather(*[ws.send(msg) for ws in self.clients.values() if ws.open])

    async def main_logic(self):
        """你的业务逻辑编写处"""
        print("服务器逻辑已就绪...")
        while True:
            # 这里的代码会暂停，直到队列里有新消息
            packet = await self.get_message()
            
            sender = packet["from"]
            msg_content = packet["data"]
            
            print(f"收到来自 {sender} 的指令: {msg_content}")

            # --- 在这里编写你的业务逻辑 ---
            if msg_content.get("action") == "ping":
                await self.send_private(sender, {"msg": "pong"})
            
            elif msg_content.get("action") == "tell_everyone":
                await self.broadcast({"from": sender, "announcement": "hello!"})
            # ---------------------------

    def run(self, host="localhost", port=8765):
        """启动入口"""
        start_server = websockets.serve(self._producer_handler, host, port)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_until_complete(self.main_logic()) # 运行你的主逻辑循环

if __name__ == "__main__":
    server = SimpleWSServer()
    server.run()