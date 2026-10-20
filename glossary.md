# Glossary

**API** — a programmatic front door to a
service: URLs that return data (often JSON)
instead of pages. Most curl work after
chapter 1 is API work.

**Base64** — an encoding that carries
arbitrary bytes as printable text. It is a
*representation*, not protection: anyone can
decode it, as chapter 5 does to a basic-auth
header.

**Basic authentication** — the oldest HTTP
login scheme: username and password joined
with a colon, Base64-encoded into an
`Authorization` header. Safe only inside
HTTPS.

**Bearer token** — a credential presented as
`Authorization: Bearer <token>`. Whoever
bears it is believed; there is nothing
behind it. Handle like a password.

**Body** — the content of a request or
reply, after the blank line that ends the
headers. What plain `curl` prints.

**Certificate** — a signed document binding
a public key to a name, presented by TLS
servers. Chapter 8 verifies them;
*OpenSSL for Mere Mortals* dissects them.

**Checksum** — a hash of a file's bytes,
published beside the file so a downloader
can prove the copy is whole. Chapter 10
checks one with `sha256sum -c`.

**Content-Type** — the header declaring what
a body *is*: `text/plain`,
`application/json`,
`application/x-www-form-urlencoded`,
`multipart/form-data`. The label and the
bytes are separate facts (chapter 4).

**Cookie** — a name-and-value pair a server
asks your client to remember and present on
later requests. The mechanism behind
staying logged in.

**Cookie jar** — curl's cookie file, in
Netscape format. `-c` writes it, `-b` reads
and sends from it. A file of live session
credentials; treat it as one.

**Exit code** — the number a command leaves
behind for the shell: 0 for success, a
specific failure number otherwise. curl's
are listed in chapter 9; `$?` reads the
last one.

**Form encoding** — `application/x-www-form-urlencoded`,
the browser-form format: fields as
`name=value&...`, with special characters
percent-encoded. `-d`'s default label;
`--data-urlencode` applies the escapes.

**Header** — a `Name: value` metadata line
in a request or reply. `Host`,
`Content-Length`, `Authorization`, and
`Set-Cookie` carry most of this guide.

**HEAD** — the HTTP method that asks for a
reply's headers without its body. Sent by
`-I`.

**HTTP method** — the verb of a request:
GET (show me), POST (take this), PUT,
DELETE, PATCH. `-d` implies POST; `-X` names
one outright.

**Loopback** — `127.0.0.1`, a machine's
address for itself. The lab lives there:
real HTTP, no network, nothing leaves the
computer.

**Multipart** — `multipart/form-data`, the
encoding that sends form fields and files
as separate sections divided by a boundary
string. Built by `-F`; how web uploads
travel.

**Progress meter** — curl's running report
of a transfer (totals, speed, time), drawn
on the error stream so it never pollutes
piped output. Silenced by `-s`, barred by `-#`.

**Proxy** — a middleman that carries
requests on your behalf, named in `-v`'s
first lines when your environment sets one.
`--noproxy` lists exceptions.

**Query string** — the `?name=value&...`
tail of a URL, carrying data inside the
address itself. Assembled by `-G`; logged
by servers in full.

**Range request** — asking a server for part
of a file ("bytes 3000 onward"), answered
with status 206. The mechanism `-C -`
resumes with; advertised as
`Accept-Ranges: bytes`.

**Redirect** — a 3xx reply whose
`Location` header names a new address.
curl reports it and stops; `-L` follows.

**Status code** — the server's three-digit
verdict: 2xx success, 3xx redirect, 4xx the
request's fault, 5xx the server's. Not the
same as curl's exit code — chapter 2's trap
is confusing the two.

**Trace** — the byte-exact record of an
exchange written by `--trace-ascii` /
`--trace`: offsets, chunks, and all.
Evidence, kept in a file.

**Trust store** — the bundle of root
certificates a system or program believes
by default. `--cacert` adds one authority
for a single command.

**URL** — the address curl is given: scheme,
host, port, path, query. One transfer per
URL, exactly as written.

**User-Agent** — the header in which a
client introduces itself. curl says
`curl/8.5.0`, honestly; `-A` changes it.

**Verbose (`-v`)** — curl narrating the
whole exchange: `*` its own actions, `>`
what you sent, `<` what came back.

**Write-out (`-w`)** — printing curl's own
measurements of a finished transfer —
`%{http_code}`, `%{time_total}`,
`%{num_redirects}`, and dozens more.
How scripts ask questions.
