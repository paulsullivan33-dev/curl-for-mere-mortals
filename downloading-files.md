# Downloading Files

Fetching a page to the screen is chapter 1.
Fetching a *file* — something that should
land on disk, whole, under the right name,
surviving interruption — has its own handful
of options. All of them are on display here
against the lab and against a plain static
file server, so the two flavours of "a file
on the web" both appear.

## Saving: `-O` and `-o`

```
$ curl -O http://127.0.0.1:8901/file.bin
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  8192  100  8192    0     0  3134k      0 --:--:-- --:--:-- --:--:-- 4000k
$ ls -l file.bin
-rw-rw---- 1 root nogroup 8192 Oct 20 00:49 file.bin
```

`-O` (capital; `--remote-name`) saves the
reply under the file name from the URL —
`file.bin` here — in the current directory.
The **progress meter** above it is curl's
running report, printed to the error stream:
total size, bytes received, percentage,
speed, and time estimates. It redraws itself
in place on a terminal (the captures show
only its final state); `-#` turns it into a
progress bar if you prefer. When curl's
output is piped or logged instead of
watched, the meter is noise — that's what
chapter 2's `-s` is for.

`-o name` (`--output`) is the same save with
*your* name instead: `curl -s -o custom.bin
...` fetched the same endpoint silently into
`custom.bin` (8192 bytes, verified with
`ls`). Two habits ride along: the name in
the URL is the server's suggestion, not a
promise — `-O` takes it on trust, so know
your source — and curl will happily
**overwrite** an existing file of the same
name, either way, without asking.

The static-server flavour is the same
command against any ordinary web space —
here, Python's built-in file server sharing
the lab's `examples/` directory on port
8903:

```
$ curl -O http://127.0.0.1:8903/upload.txt
100    78  100    78 ...
$ cat upload.txt
A specimen file for upload practice.
It contains nothing but these two lines.
```

(One meter, trimmed to its final line; the
server is `python3 -m http.server`, the
quickest way to hand a directory to curl —
or to anything else — on your own network.)

## Redirects: `-L`

Chapter 2 collected a `301` and left it
hanging. Servers move things: http to https,
old path to new, short link to long. Without
instructions, curl reports the move and
stops:

```
$ curl -s -i http://127.0.0.1:8901/redirect
HTTP/1.1 302 Found
...
Location: /hello

Redirecting to /hello.
```

`-L` (`--location`) tells curl to *follow*:
re-ask at the `Location` address, up to 50
times by default, and deliver the final
destination's reply:

```
$ curl -s -L http://127.0.0.1:8901/redirect
Hello from the lab server.
$ curl -s -L -o /dev/null -w '%{http_code} %{num_redirects} %{url_effective}\n' http://127.0.0.1:8901/redirect-chain
200 2 http://127.0.0.1.8901/hello
```

The chain endpoint redirects twice, and the
`-w` variables from chapter 2 read the whole
journey back: final code 200, 2 redirects
taken, effective URL the `/hello` it landed
on. Downloads from real sites very often
need `-L` — release pages, mirrors, and
sign-in gates all redirect — and the mirror
image is also true: a script that follows
redirects *without looking* can be led
anywhere the first server (or whoever
compromised it) points. `--max-redirs` caps
the count when that matters.

## Resuming: `-C -`

The download died at byte 3000 of 8192 —
power, wifi, patience. Start over? curl can
ask the server for just the rest, *if* the
server supports range requests:

```
$ ls -l partial.bin
-rw-rw---- 1 root nogroup 3000 ... partial.bin
$ curl -C - -o partial.bin http://127.0.0.1:8901/file.bin
** Resuming transfer from byte position 3000
100  5192  100  5192 ...
$ ls -l partial.bin
-rw-rw---- 1 root nogroup 8192 ... partial.bin
```

(The partial file here was cut from a
complete download with `head -c 3000`, to
stage the interruption; meter trimmed as
before.) `-C -` means "continue, you work
out where from" — curl looks at the existing
file's size and requests the remainder,
appending it. 3000 + 5192 = 8192: the size
is right. Is the *content* right? Size alone
can't prove that; chapter 10's recipe checks
the hash. And the server that can't do
ranges at all gets caught before it can hurt
you — against the range-blind `http.server`
of the earlier capture, the same command
refuses:

```
$ curl -C - -O http://127.0.0.1:8903/upload.txt
** Resuming transfer from byte position 30
curl: (33) HTTP server doesn't seem to support byte ranges. Cannot resume.
```

Exit **33**, and the 30-byte partial was
left exactly as it was. curl asked for a
partial answer, noticed it got a whole one,
and declined to glue the two together —
still, checking for `Accept-Ranges: bytes`
in the headers (chapter 2) before a long
resume remains the cheap way to know.

## Failing like you mean it

One option from chapter 9 belongs here
early, because downloads are where it bites
first. By default, if the URL *errors* —
404, 500 — curl saves the error page as your
file, exits 0, and says nothing. `-f`
(`--fail`) refuses the trade:

```
$ curl -f -o none.bin http://127.0.0.1:8901/status/404
curl: (22) The requested URL returned error: 404
[exit 22]
$ ls -l none.bin
ls: cannot access 'none.bin': No such file or directory
```

No file, a clear message, an exit code a
script can see. In interactive use it's a
preference; in anything automated it's the
difference between a pipeline and a
prank — chapter 9 gives `-f` its full
context of deadlines and retries.

Check: `-O` leaves a file whose size matches
the `Content-Length` (or the meter's total);
an `-L` download of `/redirect-chain` ends
at `/hello` with 2 redirects counted; a
resumed file ends exactly the full size; and
a `-f` download of a 404 leaves *nothing*
behind but an exit code. All four are
thirty-second experiments against the lab,
which is what it's for.

Next: cookies — how a server remembers you
between requests.
