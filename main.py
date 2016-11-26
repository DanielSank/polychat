import argparse
import asyncio


REMOTE_SERVER_PORT = 12345
LOCAL_PORT = 1234


class Daemon:
    """Accepts connections from user and makes connections to server"""

    def __init__(self, loop):
        self.loop = loop

    async def start_local_server(self, port):
        self.local_connection = await self.loop.create_server(
            lambda: LocalConnection(self.handle_data_from_client),
            'localhost',
            port)

    async def connect_to_remote_server(self, host, port):
        transport, connection = await self.loop.create_connection(
            lambda: RemoteConnection(),
            host,
            port)
        self.remote_transport = transport
        self.remote_connection = connection

    def handle_data_from_client(self, data):
        self.remote_transport.write(data)


class LocalConnection(asyncio.Protocol):
    """Connection to local client"""

    def __init__(self, handle_data_from_client):
        self.handle_data_from_client = handle_data_from_client

    def connection_made(self, transport):
        print("client connected")

    def data_received(self, data):
        """Handle data from local client by passing it to the server"""
        self.handle_data_from_client(data)


class RemoteConnection(asyncio.Protocol):
    """Connection to remote server"""

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        print(data.decode('utf-8'))


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
        self.server.connections.add(self)
        print("New connection from {}".format(ip))

    def data_received(self, data):
        text = data.decode('utf-8')
        print("Received {} from {}".format(text, self.ip))
        data = "{}: {}".format(self.ip, text).encode('utf-8')
        self.server.data_received(data)


async def main_daemon(loop, host, port, done):
    daemon = Daemon(loop)
    await daemon.start_local_server(port)
    print("daemon started local server")
    await daemon.connect_to_remote_server('localhost', REMOTE_SERVER_PORT)
    print("daemon connected to remote server")
    await done.wait()
    print("connection should be closed here")


async def main_server(loop, host, port, done):
    server = Server()
    s = await loop.create_server(
            lambda: ServerConnection(server),
            'localhost',
            REMOTE_SERVER_PORT)
    print("Server started")
    await done.wait()
    for c in server.connections:
        c.close()
        await c.wait_closed()
    print("Server closed")


def main(host, port, as_server):
    if as_server:
        main = main_server
    else:
        main = main_daemon

    loop = asyncio.get_event_loop()
    done = asyncio.Event()

    future = loop.create_task(main(
        loop,
        host,
        port,
        done))
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
                        help="Sets host address")
    parser.add_argument('--port',
                        '-p',
                        default=LOCAL_PORT,
                        help="Sets connection port")
    server_group = parser.add_mutually_exclusive_group(required=True)
    server_group.add_argument('--server',
                              '-s',
                              dest='as_server',
                              action='store_true',
                              help="Run in server mode")
    server_group.add_argument('--client',
                              '-c',
                              dest='as_server',
                              action='store_false',
                              help="Run in client mode")
    parser.set_defaults(as_server=False)
    args = parser.parse_args()
    host, port, as_server = args.host, args.port, args.as_server

    main(host, port, as_server)
