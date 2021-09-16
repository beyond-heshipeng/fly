import asyncio

from aiomultiprocess import Worker


class Server:
    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop

    async def send_message(self, data: bytes):
        _, writer, = await asyncio.open_connection(self.host, self.port, loop=self.loop)
        writer.write(data)
        writer.close()

    @staticmethod
    async def handle_message(reader, writer):
        data = await reader.read(100)
        message = data.decode()
        print(message)

    async def start(self):
        server = await asyncio.start_server(Server.handle_message, self.host)
        async with server:
            await server.start_serving()
        # self.loop.create_task(await server.serve_forever())
        # server = await asyncio.start_server(Server.handle_message, self.host, self.port)
        # async with server:
        #     await server.serve_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    s = Server('127.0.0.1', '9999', loop)
    asyncio.run(s.start())
    asyncio.run(s.send_message(b"123"))
