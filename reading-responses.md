# Reading What Came Back

A web reply has three parts: a **status
line** saying how it went, **headers** —
name-and-value lines carrying the metadata —
and the **body**, the content itself. Plain
`curl` shows you only the body. The skills in
this chapter are how you see the other two,
because when a request goes wrong, the body
is the last place the truth lives.

## Headers too: `-i`

```
$ curl -i http://127.0.0.1:8901/hello
HTTP/1.1 200 OK
Server: CurlLab/1.0
Date: Tue, 20 Oct 2026 00:48:07 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 27

Hello from the lab server.
```

`-i` (long form `--include`) prints the
headers ahead of the body, with a blank line
between them — the same blank line that
separates them on the wire. Read the capture
top down:

- `HTTP/1.1 200 OK` is the status line: the
  protocol, the **status code**, and a
  short phrase. The code is the machine's
  verdict; the phrase is a courtesy for
  humans and occasionally lies by vagueness.
- `Server:` names the software that answered
  (the lab's is `CurlLab/1.0`).
- `Date:` is the server's clock, in GMT.
- `Content-Type:` says what the body *is* —
  here plain text with UTF-8 characters.
  Believing this header is how programs
  decide whether they're holding JSON, HTML,
  or a picture of a cat.
- `Content-Length: 27` is the body's size in
  bytes. "Hello from the lab server." plus
  its end-of-line is exactly 27.

## Headers only: `-I`

```
$ curl -I http://127.0.0.1:8901/hello
HTTP/1.1 200 OK
Server: CurlLab/1.0
Date: Tue, 20 Oct 2026 00:48:07 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 27
```

`-I` sends a **HEAD** request: "describe the
thing, don't send it." The headers match
what a GET would return — including that
`Content-Length: 27` — but no body follows.
It's the cheap way to ask "does this exist,
how big is it, when did it change" before
committing to a download. Two cautions: some
servers answer HEAD lazily or not at all,
and a HEAD that disagrees with its GET is
the server's fault, not curl's — when the
two argue, believe the GET.

## Status codes, honestly

Codes come in families, by first digit:
**2xx** success, **3xx** redirection ("it's
over there"), **4xx** the request was wrong
(404 not found, 401 unauthorised, 403
forbidden), **5xx** the server failed. The
lab's `/status/NNN` endpoint answers with any
code you name, which makes the family
portraits easy to collect — these are real:

```
$ for code in 200 201 301 404 500
> do printf 'asked %-4s got ' $code
>   curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8901/status/$code
> done
asked 200  got 200
asked 201  got 201
asked 301  got 301
asked 404  got 404
asked 500  got 500
```

(asking 301 without following it simply
reports the redirect; chapter 6 follows.)

The codes you'll actually meet weekly: `200`
fine; `201` created something; `301`/`302`
moved; `400` your request was malformed;
`401` log in first; `403` logged in, still
no; `404` not here; `429` too fast; `500`
the server fell over; `503` the server is
down, busy, or pretending to be.

## The trap: an error is still a success

```
$ curl -s http://127.0.0.1:8901/status/404
You asked for status 404.
```

…and curl exits **0**. From curl's side of
the fence, everything worked: it connected,
asked, and faithfully delivered the reply.
The reply happened to *be* an error page.
This is the single most important thing to
understand about using curl in scripts: **an
HTTP error status is not a curl failure.**
Unless you ask, a script can "succeed" its
way through a 404, a 500, and an expired
login page, saving each one as if it were
data. Chapter 9 is about closing that hole
(`-f`, exit codes, deadlines); for now, the
habit to build is *looking*:

```
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8901/status/404
404
```

`-w` (write-out) prints values curl tracked
during the transfer — `%{http_code}` here —
and `-o /dev/null` throws the body away.
That pair turns curl into a question-asker:
*don't show me the thing, tell me how it
went.* Chapter 9 leans on `-w` properly.

## Silence, and when it hides too much

`-s` (`--silent`) suppresses the progress
meter and curl's own error messages. In
scripts you almost always want it — but the
capture below is the classic debugging
purgatory it creates. Same dead address,
twice:

```
$ curl -s http://127.0.0.1:9999/hello
$ echo $?
7
$ curl -sS http://127.0.0.1:9999/hello
curl: (7) Failed to connect to 127.0.0.1 port 9999 after 0 ms: Couldn't connect to server
```

Bare `-s` printed *nothing* and failed with
exit code 7 (couldn't connect): the silence
hides the reason along with the noise. The
fix is `-sS` — capital S for "show errors
anyway" — which is the combination scripts
should use: quiet on success, articulate on
failure. The number in parentheses, `(7)`,
is curl's own error code; chapter 9 collects
the ones that matter.

## Splitting the reply into files

`-D` dumps the headers to a file while `-o`
takes the body:

```
$ curl -s -D headers.txt -o body.txt http://127.0.0.1:8901/json
$ cat headers.txt
HTTP/1.1 200 OK
Server: CurlLab/1.0
Date: Tue, 20 Oct 2026 00:49:59 GMT
Content-Type: application/json
Content-Length: 101
$ cat body.txt
{
  "service": "curl-lab",
  "status": "ok",
  "specimens": 3,
  "nested": {
    "real": false
  }
}
```

That split is how you keep evidence: the
body for the program, the headers for the
human who gets asked why the program did
what it did.

Check: `curl -i` on the lab shows a `200 OK`
status line, a `Content-Length` matching the
body you can count, and a blank line before
the body; `-I` shows the same headers with
no body; and the `/status/404` request
*still* exits 0 — you've seen the trap with
your own eyes, which is the point.

Next: watching the exchange itself, request
included.
