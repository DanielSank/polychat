# python-chat
Chat client/server with python 3's asyncio

## How to run

### Server

```
$ python server.py --host=xxx --port=xxx
```

### Client

```
$ python daemon.py --server-host=xxx --server-port=xxx local-port=<local port>
```

Then, in another shell,

```
$ telnet localhost <local port>
```

Type your chat messages into the telnet session.
Incoming chat will show up in the daemon.

