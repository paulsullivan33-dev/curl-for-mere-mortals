# Timeouts, Retries, and Exit Codes

Everything before this chapter assumed the
other end answers. Real networks contain
servers that hang, hosts that vanish, and
services that fail one request in five. This
chapter is the defensive half of curl: making
failure **prompt**, **visible**, and — where
it's likely temporary — **retried**, so that
a script's "it worked" starts to mean
something.

## Failure as an exit code: `-f`

Chapter 2's trap, closed. Without `-f`, an
HTTP error status is a successful transfer
of an error page, exit 0. With `-f`
(`--fail`), curl treats any 4xx or 5xx as
what it is:

```
$ curl -sf http://127.0.0.1:8901/status/503
[exit 22]
```

Silent about the body (`-f` sends none of it
to stdout; chapter 6 watched it refuse to
save a 404 page), articulate in the exit
code: **22, HTTP error**. If you need the
error *body* too — APIs often explain
themselves in it — `--fail-with-body` keeps
the body and still exits 22. As a rule: `-f`
on every scripted curl, unless the script's
whole job is examining failures.

## Deadlines: `--max-time` and `--connect-timeout`

An un-deadlined curl waits as long as the
other end takes — forever, if forever is
what's on offer. The lab's `/slow` endpoint
answers after 5 seconds:

```
$ curl -sS --max-time 2 http://127.0.0.1:8901/slow
curl: (28) Operation timed out after 2002 milliseconds with 0 bytes received
[exit 28]
```

`--max-time 2` gives the *entire transfer*
two seconds; at the deadline curl walks away
with exit **28**. Its partner,
`--connect-timeout`, bounds only the
connecting phase — the useful pair being a
short connect deadline (a host that won't
even shake hands is dead, don't wait) inside
a longer total one (a big file on a slow
link is alive, give it room). A connect
timeout also lands on 28; producing one for
a capture needs a host that silently ignores
connection attempts, which the build lab's
loopback network doesn't contain — every
address there answers or refuses instantly —
so that half is stated rather than shown,
and `criteria.md` keeps the note. On real
networks (a firewalled address, a route to
nowhere) it is the timeout that fires first,
and the discipline transfers unchanged:

```
curl -fsS --connect-timeout 5 --max-time 30 URL
```

is the shape worth memorizing: fail on HTTP
errors, connect within 5 seconds or not at
all, whole thing done in 30 or it's a 28.

## Retries: riding out the flaky

Some failures are weather, not climate. The
lab's `/flaky` endpoint answers `503` to its
first two requests, then recovers. `-f` on
its own simply reports the storm:

```
$ curl -sf http://127.0.0.1:8901/flaky
[exit 22]
```

`--retry` waits and asks again:

```
$ curl -s --retry 5 --retry-delay 1 -f http://127.0.0.1:8901/flaky
Third time lucky: the flaky endpoint is up.
[exit 0]
```

Behind that quiet capture: the first request
met the endpoint's second 503 (the bare `-f`
call above had eaten the first), `--retry-delay`
paused a second, and the next request found
the endpoint recovered — body delivered,
exit 0. curl retries what looks temporary —
timeouts, dropped connections, and the
408/429/5xx statuses — up to the count you
give, then reports the *final* failure
honestly:

```
$ curl -s --retry 2 --retry-delay 1 -f http://127.0.0.1:8901/status/503
[exit 22]
```

`/status/503` never recovers, so after the
first try and two retries the exit is the
same 22 as an unretried call — retries spend
time to buy success, never to hide failure.
`--retry-max-time` caps the total spent
retrying, for scripts with their own
deadlines to keep. And a boundary worth
respecting: retrying a **POST** re-sends the
data — safe for the idempotent requests APIs
design for it, a duplicate order if they
didn't. Retry GETs freely; retry writes only
when the API says they're safe to repeat.

## The exit codes worth knowing

curl has dozens; these seven cover nearly
every bad day, and all but one were captured
in this guide:

| Exit | Meaning | Where seen |
|------|---------|------------|
| 0 | the transfer worked (whatever the *status* said, without `-f`) | everywhere |
| 3 | the URL itself is malformed | `curl http://` → "URL rejected: No host part in the URL" |
| 6 | the name couldn't be resolved | not capturable in the build lab — its DNS answers for every name; the code is DNS's way of saying "no such host" |
| 7 | couldn't connect — refused, or nothing there | ch. 2, the dead port 9999 |
| 22 | HTTP error status, with `-f` | this chapter |
| 28 | a deadline passed — connect or total | this chapter |
| 60 | the certificate failed verification | ch. 8 |

The parenthesised number in curl's own error
messages — `curl: (28) ...` — is this code,
so logs quote it for free. `man curl` lists
the rest under EXIT CODES for the day a 47
(too many redirects) or a 35 (TLS connect
error) shows up unexplained — chapter 6's
33, the resume refusal, is already a friend.

## Scripting defensively, assembled

Put the chapter together and a scripted curl
call grows a standard shape:

```
curl -fsS --connect-timeout 5 --max-time 30 --retry 3 URL
```

`-f` so errors fail, `-sS` so success is
silent and failure speaks, deadlines so
nothing hangs, retries for the weather. Two
shell habits complete it:

- **Test the exit, don't grep the output.**
  `if curl -f ...; then` is a question with a
  reliable answer; searching a body for
  "error" is a guess wearing a costume.
- **Pipelines hide the left side's code.**
  `curl ... | jq ...` reports jq's exit, not
  curl's, unless the shell's `pipefail` is
  set — the sibling guide to jq captured the
  difference line by line. A pipeline that
  must not fail silently sets it, or checks
  `%{http_code}` itself (chapter 2's `-w`).

Check: `--max-time 2` against `/slow` exits
28 with the deadline named in the message;
`--retry` brings `/flaky` home with exit 0
and leaves `/status/503` at 22; and a
`-fsS` call shows nothing at all on success.
The defences are each one option long; the
expensive failures are the ones that didn't
have them.

Next: recipes — the whole guide, applied.
