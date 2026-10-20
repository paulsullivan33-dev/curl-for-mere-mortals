# curl for Mere Mortals

**curl** is the command line's way of
talking to the web: one tool, already
installed almost everywhere, that fetches a
URL, posts a form, uploads a file, or calls
an API — and, uniquely among everyday tools,
will show you the *entire conversation* if
you ask. That second talent is why it is the
first instrument reached for when a web
request goes wrong.

This guide teaches curl the way it is
actually used: reading replies whole
(headers, status, body), sending data in its
three encodings, presenting credentials
without spraying them across the machine,
downloading files so they survive
interruption, and scripting with deadlines,
retries, and exit codes that tell the truth.

Almost everything happens in a small lab
built for the purpose: `examples/echo_server.py`,
a tiny inspection server that answers with
what it received — your headers, your form
fields, your files, your cookies — so every
claim in these chapters can be checked
against the server's own report, on
`127.0.0.1`, without anything leaving your
machine. A second copy speaks TLS with a
specimen certificate, so the padlock
chapters run for real too. The credentials
are specimens (`paul` / `specimen-pass`,
`specimen-token`), invented for the lab and
worth nothing.

A note on how this guide was verified.
curl 8.5.0 was on the build machine, and
every command quoted was run against the lab
above and captured: the parsed forms, the
base64 credential decoded back, the process
list showing a token in plain sight, the
resumed download, the cookie jar, exit codes
3, 7, 22, 28, and 60. Two things the lab
could not produce honestly — a DNS failure
(its resolver answers for every name) and a
pure connect timeout (its network refuses
instantly; nothing blackholes) — are stated
in place and ledgered in `criteria.md`. One
labelled capture comes from a public site,
`example.com`.

## What this guide covers

- [**What curl is**](what-curl-is.md) — the
  transfer tool and what it is not; checking
  your install; the lab; your first request
- [**Reading what came back**](reading-responses.md) —
  `-i` and `-I`, the parts of a reply, status
  codes, the error-that-exits-0 trap, `-s`
  versus `-sS`, splitting headers from body
- [**Watching the conversation**](watching-the-conversation.md) —
  `-v` line by line, `--trace-ascii` for the
  record, and which watcher for which trouble
- [**Sending data**](sending-data.md) — `-d`
  and POST, `--data-urlencode`, JSON and its
  Content-Type, the `@file` newline trap,
  `-F` uploads, methods and `-G`
- [**Authentication**](authentication.md) —
  basic auth and bearer tokens, base64 told
  honestly, and where credentials leak:
  history, the process list, logs — with the
  `-K` config-file pattern as the fix
- [**Downloading files**](downloading-files.md) —
  `-O`/`-o`, the progress meter, `-L`
  redirects, resuming with `-C -`, and `-f`
  before it bites
- [**Cookies**](cookies.md) — the jar:
  receiving with `-c`, sending with `-b`, and
  the session pattern behind every login
- [**TLS**](tls.md) — verification and what
  it asks, exit 60, `-k` and its price, and
  `--cacert` as trust extended deliberately
- [**Timeouts, retries, and exit codes**](timeouts-retries-and-exit-codes.md) —
  `--max-time`, `--connect-timeout`, `--retry`,
  the seven codes worth knowing, and the
  defensive script shape
- [**Recipes**](recipes.md) — a health check,
  a question for a local API, a download
  proven whole with its checksum, and the
  failure checklist
- [**Glossary**](glossary.md) — the terms,
  collected in one place

## What it doesn't cover

The other protocols curl speaks (FTP,
SFTP, SMTP, LDAP and friends appear in the
version banner and stay there); libcurl,
the programming library — the C API and its
bindings in other languages; building curl
from source; and HTTP itself as a subject —
this guide reads replies and sends requests,
but the protocol's full grammar (caching,
content negotiation, HTTP/2 and /3 framing)
belongs to its own shelf. Where a flag has a
newer or safer sibling, the chapter says so
in place.

## How to use this guide

Read chapter 1, start the lab, and keep a
terminal open from chapter 2 on: the echo
server rewards typing along, because every
reply it gives is about *your* request. Run
`examples/lab-setup.sh` before chapter 8.
Keep the lab afterward — its `/status`,
`/flaky`, and `/slow` endpoints are a
standing rehearsal for the day a real
service misbehaves in the same three ways.
