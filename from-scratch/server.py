import select
import socket


def get_listen_socket(host, port):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((host, port))
    listen_socket.listen(1)
    return listen_socket


def connection_handler_for_server(server, host, port):
    listen_socket = get_listen_socket(host, port)
    connection_handler = ConnectionHandler(
            listen_socket,
            server.connection_made)
    return connection_handler


class ConnectionHandler(object):
    """A handler that calls a server's connection_made method."""
    def __init__(self, socket, connection_made_callback):
        self.socket = socket
        self.connection_made_callback = connection_made_callback

    def readable(self):
        return True

    def writeable(self):
        return False

    def read(self):
        socket, addr = self.socket.accept()
        self.connection_made_callback(socket, addr)

    def write(self):
        raise RuntimeError("Unreachable")

    def fileno(self):
        return self.socket.fileno()


class Server(object):
    def __init__(self, handler_adder):
        self.clients = {}  # addr --> ClientHandler
        self.handler_adder = handler_adder

    def connection_made(self, socket, addr):
        print("Server: connection made by {}".format(addr))
        client = ClientHandler(
                socket,
                addr,
                self.client_data_received,
                self.client_connection_closed)
        self.clients[addr] = client
        self.handler_adder(client)

    def client_connection_closed(self, addr):
        self.clients.pop(addr)

    def client_data_received(self, data):
        for client in self.clients.values():
            client.buf += data


class ClientHandler(object):
    def __init__(self, socket, addr, data_received, connection_closed):
        self.socket = socket
        self.addr = addr
        self.data_received = data_received
        self.connection_closed = connection_closed
        self.buf = ''

    def readable(self):
        return True

    def writeable(self):
        return len(self.buf) > 0

    def read(self):
        data = self.socket.recv(1024)
        if len(data) == 0:
            self.connection_closed(self.addr)
        self.data_received(data)

    def write(self):
        self.socket.send(self.buf)
        self.buf = ''

    def fileno(self):
        return self.socket.fileno()


class Reactor(object):
    def __init__(self):
        self.fileno_map = {}  # fileno -> Handler

    def add_handler(self, handler):
        self.fileno_map[handler.fileno()] = handler

    def run(self):
        """Run the reactor (i.e. event loop).

        Args:
            handlers (list[Handler]):
        """
        while 1:
            readers = []
            writers = []
            for fileno, elem in self.fileno_map.items():
                if elem.readable():
                    readers.append(fileno)
                if elem.writeable():
                    writers.append(fileno)

            readers_ready, writers_ready, _ = select.select(
                    readers, writers, [])
            for reader in readers_ready:
                self.fileno_map[reader].read()
            for writer in writers_ready:
                self.fileno_map[writer].write()


def main():
    reactor = Reactor()
    server = Server(reactor.add_handler)
    connection_handler = connection_handler_for_server(
            server,
            'localhost',
            12344)
    reactor.add_handler(connection_handler)
    reactor.run()


if __name__ == "__main__":
    main()

