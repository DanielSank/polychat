import argparse
import asyncio

import util


C = util.get_config()


class Server:
    def __init__(self):
        self.connections = set()

    def data_received(self, data):
        for c in self.connections:
            c.transport.write(data)


class ServerConnection(asyncio.Protocol):
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):
        ip = transport.get_extra_info('peername')
        self.ip = ip
        self.transport = transport
        self.server.connections.add(self)
        print("New connection from {}".format(ip))

    def data_received(self, data):
        text = data.decode('utf-8')
        print("Received {} from {}".format(text, self.ip))
        data = "{}: {}".format(self.ip, text).encode('utf-8')
        self.server.data_received(data)


async def server_main(loop, host, port, done):
    server = Server()
    s = await loop.create_server(
            lambda: ServerConnection(server),
            host,
            port)
    print("Server started")
    await done.wait()
    s.close()
    await s.wait_closed()
    print("Server closed")


def main(host, port):
    loop = asyncio.get_event_loop()
    done = asyncio.Event()

    future = loop.create_task(server_main(
        loop,
        host,
        port,
        done))
    print(f"Serving at {host}:{port}")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    done.set()
    loop.run_until_complete(future)
    loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test asyncio server')
    parser.add_argument('--host',
                        '-ho',
                        default='localhost',
                        help="Server hostname")
    parser.add_argument('--port',
                        '-p',
                        default=C["SERVER_PORT"],
                        help="Server port")
    args = parser.parse_args()
    host, port = args.host, args.port

    main(host, port)
