import argparse
import asyncio

import util


C = util.get_config()


class Daemon:
    """Accepts connections from user and makes connections to server"""

    def __init__(self, loop):
        self.loop = loop

    async def start_local_listener(self, port):
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


async def main_daemon(loop, server_host, server_port, local_port, done):
    daemon = Daemon(loop)
    await daemon.start_local_listener(local_port)
    print("daemon started local listener")
    await daemon.connect_to_remote_server(server_host, server_port)
    print("daemon connected to remote server")
    await done.wait()
    print("connection should be closed here")


def main(server_host, server_port, local_port):
    loop = asyncio.get_event_loop()
    done = asyncio.Event()

    future = loop.create_task(main_daemon(
        loop,
        server_host,
        server_port,
        local_port,
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
    parser.add_argument('--server-host',
                        '-sho',
                        default='localhost',
                        help="Server hostname")
    parser.add_argument('--server-port',
                        '-sp',
                        default=C["SERVER_PORT"],
                        help="Server port")
    parser.add_argument('--local-port',
                        '-lp',
                        default=C["LOCAL_PORT"],
                        help="Local port")
    args = parser.parse_args()
    s_host, s_port, l_port = args.server_host, args.server_port, args.local_port

    main(s_host, s_port, l_port)
