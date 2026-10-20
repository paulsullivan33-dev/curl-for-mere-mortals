# Watching the Conversation

`-i` shows you the reply. `-v` shows you the
*conversation*: your request going out, the
reply coming back, and curl's own running
commentary on connecting, authenticating,
and closing. When something fails and the
body won't say why, this is where the why
lives. It is the single most useful debugging
option curl has.

```
$ curl -v http://127.0.0.1:8901/hello
*   Trying 127.0.0.1:8901...
* Connected to 127.0.0.1 (127.0.0.1) port 8901
> GET /hello HTTP/1.1
> Host: 127.0.0.1:8901
> User-Agent: curl/8.5.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: CurlLab/1.0
< Date: Tue, 20 Oct 2026 00:48:07 GMT
< Content-Type: text/plain; charset=utf-8
< Content-Length: 27
<
{ [27 bytes data]
* Connection #0 to host 127.0.0.1 left intact
Hello from the lab server.
```

(Capture trimmed: the progress meter and a
line reporting proxy environment variables
are left out. On a machine whose shell sets
`http_proxy` and friends, `-v` names them in
its first lines — worth knowing before you
conclude a site is "down" when your proxy
is.)

## Reading the directions

Every line carries a one-character compass:

| Mark | Means |
|------|-------|
| `*` | curl talking about itself: connecting, TLS, closing |
| `>` | sent by you: your request line and headers |
| `<` | received: the server's status line and headers |
| `{` / `}` | data (body bytes) going out / coming in |

The story in the capture, in order: curl
tries the address and connects (the `*`
lines); sends a request — `GET /hello
HTTP/1.1`, asking for the `/hello` page by
the HTTP method **GET** — with three headers
of its own devising: `Host` (which site on
that machine; required, and the server may
answer differently per name), `User-Agent`
(curl introducing itself, honestly, as
`curl/8.5.0`), and `Accept: */*` ("I'll take
anything"). A lone `>` line ends your half:
the blank line that says *headers over*.

Then the reply (`<` lines — chapter 2's
headers, seen arriving), a `{ [27 bytes
data]` note standing in for the body itself,
and the body printed last, after curl notes
it left the connection open for reuse.

Things `-v` settles at a glance on a bad
day: whether you connected to the address
you *meant* (the `Trying` line), whether the
server saw the path and headers you think
you sent (the `>` lines), whether it
redirected you somewhere unexpected (a `3xx`
in the `<` lines), and whose name is on the
certificate when TLS is involved (chapter 8
reads those `*` lines).

## Keeping it: `--trace-ascii`

`-v` scrolls past. `--trace-ascii` writes
the same conversation to a file, in
numbered, timestamp-free plain text, with
each chunk's offset and size recorded:

```
$ curl -s --trace-ascii trace.txt http://127.0.0.1:8901/hello
Hello from the lab server.
$ cat trace.txt
== Info:   Trying 127.0.0.1:8901...
== Info: Connected to 127.0.0.1 (127.0.0.1) port 8901
=> Send header, 82 bytes (0x52)
0000: GET /hello HTTP/1.1
0015: Host: 127.0.0.1:8901
002b: User-Agent: curl/8.5.0
0043: Accept: */*
0050:
<= Recv header, 17 bytes (0x11)
0000: HTTP/1.1 200 OK
...
<= Recv data, 27 bytes (0x1b)
0000: Hello from the lab server..
== Info: Connection #0 to host 127.0.0.1 left intact
```

(One sandbox proxy-notice line trimmed from
the head; the response headers, identical to
the `-i` capture in chapter 2, are elided
with `...`.) The offsets on the left —
`0000`, `0015`, `002b` — are byte positions,
in hexadecimal. They matter when a server
is picky about exactly what arrived: the
trace proves the bytes, not your intentions.
Note the body's final characters rendered as
`..` — non-printing bytes (the line ending)
shown as dots, which is what makes the ASCII
trace safe to keep in a log or paste into a
bug report.

`--trace` (without `-ascii`) adds a hex
dump beside the text — the tool for binary
protocols and for proving a byte is really
a zero. `--trace-time` prefixes timestamps
when the question is *when*, not *what*.

## Which watcher when

| Situation | Reach for |
|-----------|-----------|
| "What did it send back?" | `-i` |
| "Why did that fail?" | `-v` |
| "I need to show someone / keep it" | `--trace-ascii` |
| "Something binary is wrong" | `--trace` |
| "Just the facts, for a script" | `-sS` + `-w` (ch. 9) |

One caution that applies to every watcher:
**traces contain secrets.** Headers include
your `Authorization` header, cookies include
session values. A trace is a specimen only
when the credentials are; before pasting a
real one anywhere, read it the way chapter 5
teaches you to read anything bearing tokens.

Check: `curl -v` on the lab shows your three
default request headers between the `>` marks
and the reply between the `<` marks; a trace
file written by `--trace-ascii` records the
same exchange with byte offsets; and neither
changes what the server received — watching
is free.

Next: putting something in the request —
data, forms, and files.
