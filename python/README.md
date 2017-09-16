# Chat!

## python
Chat client/server with python 3's asyncio

### Server

In a shell, run the server:

```
$ python server.py --host=xxx --port=yyy
```

### Client

Once the server is running somewhere, in a shell, run the daemon:

```
$ python daemon.py --server-host=xxx --server-port=yyy local-port=<local port>
```

Then, in another shell, telnet into the daemon:

```
$ telnet localhost <local port>
```

Type your chat messages into the telnet session.
Incoming chat will show up in the daemon.
