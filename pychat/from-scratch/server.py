"""
A very simple, dumb chat server.

To use me, run me from the command line
    python server.py
Then, in a separate terminal window, telnet into me,
    telnet localhost 12344
You can now send me messages from telnet. In order to see chat between two
clients, start another telnet session in another window. You can now chat with
yourself :-)

To understand how this module works, start with Reactor and work your way
through the rest of the classes from there.
"""


import select
import socket


def get_listen_socket(host, port):
    """Get a socket that listens for incoming connections.

    Args:
        host (str): Hostname, i.e. 'localhost'.
        port (int): Port on which to listen for incoming connections.

    Returns (socket): A socket listening for connections on the given host and
        port.
    """
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind((host, port))
    listen_socket.listen(1)
    return listen_socket


def connection_handler_for_server(server, host, port):
    """Get a connection handler for a server.

    Args:
        server:
        host (str):
        port (int): See get_listen_socket.

    Returns (ConnectionHandler): A ConnectionHandler for the given server.
    """
    listen_socket = get_listen_socket(host, port)
    connection_handler = ConnectionHandler(
            listen_socket,
            server.connection_made)
    return connection_handler


class Handler(object):
    """A handler for the Reactor.

    See the Reactor class for an explanation of what Handlers do.
    """
    def register_as_reader(self):
        """Return True if I should sign up for reading, False otherwise."""

    def register_as_writer(self):
        """Return True if I should sign up for writing, False otherwise."""

    def read(self):
        """Called by reactor when I can read without blocking."""

    def write(self):
        """Called by reactor when I can write without blocking."""

    def fileno(self):
        """Return my file descriptor.

        Usually, return the fileno of a socket I represent.
        """


class ConnectionHandler(Handler):
    """A handler representing a listening socket.

    For a socket, "listening" means that the socket is awaiting incoming
    connections. When a remote peer tries to establish a connection with a
    listening socket, the socket becomes kkk

    I participate in the reactor event loop. If the select call completes
    returning me. then that means that a client is trying to connect to me, and
    so I accept the incoming connection and pass the resulting socket to a
    callback (connection_made argument in my __init__)). Usually, this callback
    is the connection_made method on a server for which I'm listening for
    incoming connections.

    Attributes;
        socket (socket): The socket this handler uses to listen for incoming
            connections.
        connection_made (function): When a new connection comes in, we call this
            function with the new socket and address as arguments. Typically,
            this function is the connection_made method of a server.
    """
    def __init__(self, socket, connection_made):
        self.socket = socket
        self.connection_made = connection_made

    def register_as_reader(self):
        """I always register as reader because I always wait for connections."""
        return True

    def register_as_writer(self):
        return False

    def read(self):
        """Called by Reactor when I'm ready for I/O.

        The OS detects that a listening socket is ready for I/O when a remote
        peer attempts to establish a connection. When this happens, if I am
        registered as a reader in a call to select, the call returns with my
        file descriptor as an available reader. This is my cue to accept the
        incoming connection. When a connection is accepted, a _new_ socket is
        opened and used for communication with the remote peer. I pass this
        socket into my connection_made function so that whoever's on the other
        end of that function can do somethin with the new socket.
        """
        socket, addr = self.socket.accept()
        self.connection_made(socket, addr)

    def write(self):
        raise RuntimeError("Unreachable")

    def fileno(self):
        return self.socket.fileno()


class Server(object):
    """A chat server.

    Attributes:
        clients (dict): Maps addresses (str) to clients (ClientHandler).
        add_handler (function): Function I call to add a new handler to the
            reactor. Usually, I call this function when I want to add a new
            ClientHandler.
        """
    def __init__(self, add_handler):
        self.clients = {}  # addr --> ClientHandler
        self.add_handler = add_handler

    def connection_made(self, socket, addr):
        """Handle a new connection.

        This method is usually called by a ConnectionHandler.

        Args:
            socket (socket): Socket associated with the new connection.
            add (str): Address of remote peer who made the new connection.

        Nothing is returned. Instead, we make a handler to represent the new
        connection and add it to the reactor.
        """
        print("Server: connection made by {}".format(addr))
        client = ClientHandler(
                socket,
                addr,
                self.client_data_received,
                self.client_connection_closed)
        self.clients[addr] = client
        self.add_handler(client)

    def client_connection_closed(self, addr):
        self.clients.pop(addr)

    def client_data_received(self, data):
        """Handle data incoming from a client.

        Args:
            data (str): The incoming data, e.g. a chat message.

        We simply add the data to each client's output buffer so that it will
        be written out over their sockets.
        """
        for client in self.clients.values():
            client.buf += data


class ClientHandler(object):
    """A handler representing a single client.

    Attributes:
        socket (socket): The socket through which we communicate with the
            client.
        addr (string): The client's address.
        data_received (function): Function to call when we receive data from the
            client.
        connection_closed (function): Function to call when the connection to
            the client is closed.
        buf (str): Data buffer containing bytes to be sent to the client.
    """
    def __init__(self, socket, addr, data_received, connection_closed):
        self.socket = socket
        self.addr = addr
        self.data_received = data_received
        self.connection_closed = connection_closed
        self.buf = ''

    def register_as_reader(self):
        return True

    def register_as_writer(self):
        return len(self.buf) > 0

    def read(self):
        data = self.socket.recv(1024)
        if len(data) == 0:
            # If a socket comes back as ready for reading for a select call, but
            # there's no data to be read, this means the socket is closed by the
            # remote peer.
            self.connection_closed(self.addr)
        self.data_received(data)

    def write(self):
        num_bytes_sent = self.socket.send(self.buf)
        self.buf = self.buf[num_bytes_sent:]

    def fileno(self):
        return self.socket.fileno()


class Reactor(object):
    """An event loop.

    The Reactor (so called because it reacts to network activity), is an event
    loop which notifies handlers when they have data ready to be read. Each
    handler must have the interface described by the Handler class above.

    The magic bit of the Reactor is the system call 'select'. Select takes two
    arguments, a list of readers and a list of writers. The call returns when
    at least one of the readers or writers can read or write without blocking.
    See the documentation for select for details.
    """
    def __init__(self):
        self.fileno_map = {}  # fileno -> Handler

    def add_handler(self, handler):
        self.fileno_map[handler.fileno()] = handler

    def run(self):
        """Run the reactor (i.e. event loop).

        Each time around the loop, we find out which of our handlers wants to
        register as a reader or writer. When then pass the readers and writers
        to select, and block until one or more of them is ready for I/O. Then,
        we call their read() or write() methods as appropriate.
        """
        while 1:
            readers = []
            writers = []
            for fileno, elem in self.fileno_map.items():
                if elem.register_as_reader():
                    readers.append(fileno)
                if elem.register_as_writer():
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

