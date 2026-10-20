# Recipes

Ten chapters of parts. This one assembles
three jobs the way they actually occur —
checking a service is up, asking a local API
a question, and downloading a file you can
prove is whole — plus the checklist for when
any of them goes wrong. Every output below
is from the lab; the shapes transfer as-is.

## Recipe 1: health-check a service

The question is binary — is it up? — so the
tool should answer binarily. `examples/health.sh`:

```sh
#!/bin/sh
# health.sh URL — prints UP or DOWN, exits 0 or 1
if curl -fsS --max-time 5 "$1" -o /dev/null 2>/dev/null; then
    echo "UP   $1"
else
    echo "DOWN $1"
    exit 1
fi
```

Every flag is a chapter: `-f` (an error page
is not "up", ch. 9), `-sS` (quiet success,
spoken failure — then discarded here so the
script's output stays clean), `--max-time 5`
(a hung service must not hang the checker),
`-o /dev/null` (the body is not the
question). Run against three states of the
world:

```
$ ./health.sh http://127.0.0.1:8901/json
UP   http://127.0.0.1:8901/json
[exit 0]
$ ./health.sh http://127.0.0.1:8901/status/503
DOWN http://127.0.0.1:8901/status/503
[exit 1]
$ ./health.sh http://127.0.0.1:9999/json
DOWN http://127.0.0.1:9999/json
[exit 1]
```

A healthy endpoint, a sick one, and an
absent one all sort correctly — note the 503
and the dead port give the same *answer*
with different causes underneath (a 22 and a
7, if you remove the `2>/dev/null` and look).
Wire the script into cron, a monitoring
tool, or another script's `if`, and the exit
code does the talking. What it does not do:
tell you the service is *correct*, only that
it answers like it means it. Point it at an
endpoint that exercises the real work if
"up" needs to mean "working".

## Recipe 2: ask a local API a question

Half the APIs you'll ever curl live on your
own machines: a router's status page, a
media server's JSON, a local AI model's
`/api/tags`-style endpoint. The pattern is
fetch, then extract one field — and the
extraction is where the sibling guide's
tool takes the baton:

```
$ curl -s http://127.0.0.1:8901/json | jq -r .status
ok
```

`jq -r .status` pulls the field and prints
it bare (the `-r` is "raw": no quotes), so a
shell variable can hold it:
`state=$(curl -s ... | jq -r .status)`.
Chapter 9's caution rides along: a pipeline
reports its *last* command's exit, so in
anything that must not guess, either set
`pipefail` or ask curl for the status
itself — `curl -s -o /dev/null -w
'%{http_code}'`, chapter 2 — before trusting
the field. Against a real service, add
chapter 5's header (`-H 'Authorization:
Bearer ...'`, from a `-K` file) and the call
is production-shaped; the lab version needs
none of it, which is what makes it a lab.

## Recipe 3: download, then prove it

Chapter 6 ended on a promise: size is not
proof. Publishers of real files often ship a
**checksum** — a hash of the file's bytes —
beside the download. The lab does the same
(`/file.bin.sha256` publishes the expected
SHA-256), and the verification is three
lines:

```
$ curl -sO http://127.0.0.1:8901/file.bin
$ echo "$(curl -s http://127.0.0.1:8901/file.bin.sha256)  file.bin" | sha256sum -c -
file.bin: OK
```

`sha256sum -c` recomputes the hash of what's
on disk and compares it to the line it was
fed — hash, two spaces, filename — answering
`OK` or `FAILED` per file, with an exit code
to match. Combined with chapter 6's `-C -`
resume and `-L` following, the full download
ritual for anything that matters is:
fetch with `-fL`, resume with `-C -` if it
interrupts, verify with the hash before you
use it. Where a publisher gives the hash on
the same page as the file, this proves
*integrity* (the file arrived whole) rather
than *authenticity* (the file is theirs) —
chapter 8's distinction, wearing overalls.
Signatures are the authenticity tool, and
they belong to the OpenSSL sibling's trade.

## When it breaks: the working order

Failed request, unknown cause. In order:

1. **Look at the exit code** (`echo $?`).
   7, 22, 28, 60 each indict a different
   suspect (ch. 9's table).
2. **Re-run with `-v`** and read the `*`
   lines: did it connect where you meant?
   What name is on the certificate? (ch. 3, 8)
3. **Read the `>` lines**: is the request
   you *sent* the request you *meant* —
   path, headers, method? Half of all API
   misery is visible here.
4. **Read the `<` lines and the body**:
   status, `Content-Type`, and the server's
   own error text. Servers are often righter
   than they first appear.
5. **Feed it to `/echo`** (or read a
   `--trace-ascii` file): if the lab server
   sees a perfect request, the difference is
   in the real server's expectations;
   compare its documentation against the
   `>` lines one header at a time.

Check: the health script sorts the lab's
three states correctly; the `jq` pipe
answers `ok`; and `sha256sum -c` says `OK`
for a file fetched fresh — and would say
`FAILED` for the truncated partial from
chapter 6, which is the entire point of
keeping it in the ritual.

That's the guide. The glossary collects the
terms; `examples/commands.txt` is the whole
thing on one page for the wall.
