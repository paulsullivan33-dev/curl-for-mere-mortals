# Writing Criteria

Every guide in this repo is written to the same
standard. If you're adding or editing a guide —
human or AI — hold it to these.

1. **Plain words, real ideas.** Simple language,
   never dumbed-down concepts. Explain jargon on
   first use; collect terms in the glossary.
2. **No hype.** No marketing adjectives, no
   "revolutionary," no promises about what
   something will do for the reader.
3. **Honest about limits.** Say what the thing
   *can't* do. State uncertainty instead of
   smoothing it over. Validation notes include
   what remains unverified.
4. **No invented numbers.** Benchmarks, defaults,
   and specs are either measured or qualified with
   "depends on your setup." If it wasn't tested,
   say so.
5. **Checkable.** Commands are meant to be run,
   with "Check:" blocks showing what success looks
   like. Sources are linked, not asserted.
6. **Respect the reader's setup.** Call out
   Windows/Mac/Linux differences. Don't assume a
   GPU, a budget, or prior experience.
7. **Safety isn't skipped.** Real risks get
   stated plainly, not buried.
8. **Scoped.** Each guide says what it covers and
   points elsewhere for the rest. No guide
   pretends to be the whole subject.
9. **Structure over prose.** Tables, before/after
   examples, symptom → fix. Scannable beats essay.

## Verification notes for this guide

Standard 3 and 4 applied to this guide,
specifically. curl **8.5.0** (the Ubuntu
build, `libcurl/8.5.0` on OpenSSL 3.0.13) was
on the build machine, and every quoted output
is a capture from it. Working transcripts are
kept with the build (`curl-lab/transcripts/`).

**The lab.** A fixture server written for the
guide, shipped as `examples/echo_server.py`
(Python 3.12.3 standard library only,
`ThreadingHTTPServer` on loopback), run in
three copies: plain HTTP on 8901, TLS on
8902 (self-signed certificate from the
shipped `examples/lab-setup.sh`, OpenSSL
3.0.13; SANs `DNS:localhost`, `IP:127.0.0.1`),
and Python's `http.server` as a generic
static server on 8903. The fixture's
endpoints each exist to be exercised:
`/echo` reports the request it received as
JSON (headers, content type, parsed form
fields, multipart field/file breakdown),
`/status/NNN` answers any status,
`/redirect(-chain)` redirects once/twice,
`/protected` enforces basic auth
(`paul`/`specimen-pass`) or a bearer token
(`specimen-token`), `/set-cookie` + `/whoami`
run the cookie flow, `/file.bin` is 8192
deterministic bytes (`byte i = i mod 251`)
with genuine Range support and a published
SHA-256 (`25df2449…f809a7f`, stable across
runs by construction), `/flaky` fails 503
twice then recovers, `/slow` answers after
5 seconds. One deliberate fixture limit: the
multipart parser is a boundary split written
for teaching, and its reported file size
(77 for the shipped 78-byte `upload.txt`) is
its own count of the part's content — quoted
in chapter 4 as the server reported it.

**Verified by running, per chapter:**

- *Ch. 1:* `curl --version` (both lines,
  including the full `Protocols:` list), `curl
  --help | head -6`, and the first request
  against `/hello`.
- *Ch. 2:* `-i` and `-I` on `/hello`
  (identical headers, HEAD without body,
  `Content-Length: 27` against a countable
  body); `-i` on `/status/404` and
  `/protected` (the `WWW-Authenticate` header
  captured); the status loop 200/201/301/404/500
  via `-w '%{http_code}'`; the trap itself —
  `/status/404` delivered with exit **0**; the
  `-s` / `-sS` pair against the dead port
  9999 (empty silence vs the `(7)` message,
  exit 7 both ways); `-D`/`-o` splitting
  `/json` into header and body files, both
  `cat`ed back.
- *Ch. 3:* the full `-v` exchange on
  `/hello`, and `--trace-ascii` to a file,
  read back — byte offsets, per-chunk sizes,
  the body rendered `..` for its line ending.
- *Ch. 4:* against `/echo`'s JSON reports —
  `-d 'name=specimen&count=2'` parsed back
  into `form_fields`; `--data-urlencode`
  round-tripping "J R R Tolkien & Sons" and
  "Mesquite, TX" (wire form
  `J+R+R+Tolkien+%26+Sons`, `%2C` for the
  comma); `-d @payload.json` arriving labelled
  `application/x-www-form-urlencoded`, and
  the same body re-labelled
  `application/json` by `-H`; `-d @upload.txt`
  proving the newline strip (two lines run
  together in the reported body); `-F` with a
  file and a field, unpacked by the server
  into `files`/`form_fields`; `-X PUT`; and
  `-G --data-urlencode` placing `?q=hello+world`
  in the request line (read from `-v`).
- *Ch. 5:* `-u` right and wrong against
  `/protected` (200 body vs `401` body); the
  `Authorization: Basic` header captured in
  an `/echo` report and decoded back with
  `base64 -d` to `paul:specimen-pass`; bearer
  right (200) and wrong (`%{http_code}` 401);
  the process-list experiment, run three
  ways against the 5-second `/slow` — `-u`
  shows its password **blanked** in `ps`
  output (curl 8.5.0 rewriting its own argv,
  quoted as captured, with the text warning
  not to rely on it), `-H 'Authorization:
  Bearer …'` from an environment variable
  shows the token **in full**, `-K
  lab-curlrc` shows no secret; the `-K` file
  itself `cat`ed, `ls -l` showing `-rw-------`
  after `chmod 600`, and its `/protected`
  call succeeding.
- *Ch. 6:* `-O` on `/file.bin` (8192 bytes on
  disk, final meter state); `-o` with a
  custom name (8192, size-confirmed); `-O`
  against `python3 -m http.server` for
  `upload.txt`, contents `cat`ed; `-i` on
  `/redirect` (302 + `Location`); `-L`
  following it; `-L` on `/redirect-chain`
  with `-w` reporting `200 2 …/hello`; the
  resume — a 3000-byte partial (cut with
  `head -c`) completed via `-C -`, curl
  printing "** Resuming transfer from byte
  position 3000", fetching exactly 5192 more
  bytes, final size 8192 and SHA-256 matching
  the server-published hash; the same `-C -`
  against the range-blind `http.server`
  refusing with exit **33** ("doesn't seem to
  support byte ranges") and the 30-byte
  partial left byte-identical; `-f -o` on a
  404 leaving **no file** and exit 22.
- *Ch. 7:* the whole cookie arc —
  `/whoami` before any cookie, `-c jar.txt`
  on `/set-cookie`, the jar file `cat`ed
  (Netscape format, session cookie, expiry
  0), `-b jar.txt` greeted by name at
  `/whoami`, and the inline `-b 'name=value'`
  form producing the identical greeting.
- *Ch. 8:* the lab certificate read with
  `openssl x509` (subject + SANs); the plain
  HTTPS request failing **60** with curl's
  full "failed to verify the legitimacy"
  text; `-k` succeeding; `--cacert`
  succeeding for both `127.0.0.1` and
  `localhost`; `-v` under `--cacert`
  capturing `SSL certificate verify ok.` and
  the TLSv1.3 cipher line; and, against the
  public internet, `example.com` reporting
  `%{ssl_verify_result}` **0** with its `-sI`
  headers and body captured (see the public
  capture note below).
- *Ch. 9:* `--max-time 2` against `/slow` —
  exit **28**, message verbatim ("Operation
  timed out after 2002 milliseconds");
  `-f` exit **22** on `/status/503`; the
  `--retry` pair — `/flaky` succeeding after
  its failures with `--retry 5 --retry-delay 1`
  (sequence: a prior bare `-f` call consumed
  failure one and exited 22; the retry call
  met failure two, paused, succeeded), and
  `--retry 2` against the unrecoverable
  `/status/503` exiting 22 after its retries;
  malformed URL `curl http://` exiting **3**
  ("No host part in the URL"); exit 7
  (chapter 2) and exit 60 (chapter 8) complete
  the table's captured codes.
- *Ch. 10:* `examples/health.sh` (the shipped
  file is the captured script plus a comment
  header) run against the healthy endpoint,
  `/status/503`, and a dead port — UP/0,
  DOWN/1, DOWN/1; the `curl | jq -r .status`
  pipe answering `ok` (jq 1.7, the sibling
  guide's tool); the checksum recipe end to
  end — fresh download, `sha256sum -c`
  answering `file.bin: OK` — and its negative:
  a 3000-byte truncation answering `FAILED`
  with exit 1.

**Capture hygiene (declared trims):**
progress meters are shown in their final
state only (they redraw in place; the
intermediate frames carry no information);
`-v` and trace captures drop the build
sandbox's proxy-environment notice (a line
naming the sandbox's own proxy variables and
internal addresses — on the build network
curl reached the internet *through* a proxy,
which also put a `HTTP/1.1 200 Connection
Established` line ahead of `example.com`'s
own headers in its `-sI` transcript —
readers on a direct connection won't see
that line, and no chapter quotes it); one repeated response
header block in chapter 3 is elided with
`...`. Dates, speeds, and timings in the
captures are the capture runs' own and will
differ on a reader's machine; where the
capture harness itself left a mark — two
no-output commands recorded the *pipeline's*
exit 1 where curl exited 0 — no chapter
quotes those markers, and every exit code a
chapter does quote was captured from curl
directly.

**Documented-only (not run), and why:**

- *Exit code 6 (couldn't resolve).* The build
  sandbox's DNS is intercepted and answers
  for every name, real or invented — attempts
  on `nonexistent.invalid` (proxy bypassed,
  so the resolver path itself was what
  answered) ended in connection resets (56),
  never in a genuine resolution failure. The code is described from curl's
  documentation and flagged in the chapter's
  table.
- *A connect-phase timeout.* Every
  unroutable address the sandbox offered was
  refused or reset immediately by its network
  fabric (exits 7 and 56); nothing blackholed
  a connection long enough for
  `--connect-timeout` to fire. The *total*
  deadline (exit 28) is captured for real;
  the connect deadline is taught as its
  partner with the reason stated in chapter
  9.
- *Installation* on a reader's machine
  (package managers, the Windows/macOS
  bundled builds) is described, not performed
  — the build machine already had curl 8.5.0.
  Platform differences named in the chapters
  (trust-store locations, `-k` reach) are
  general knowledge, phrased as such.
- *Named, not taught:* client certificates
  (`--cert`/`--key`), `--netrc`, `--retry-all-errors`,
  `--fail-with-body` (named beside `-f`; the
  `-f` behaviour itself is captured), the
  login-flow block in chapter 7 (a pattern
  built from the captured `-b`/`-c` calls,
  labelled as a pattern in place), and the
  non-HTTP protocols in curl's banner.

**One public capture:** chapter 8's
`example.com` verification line (and its
`-sI`/body captures kept with the
transcripts) went over the real internet
from the build machine, through its proxy.
It is labelled in the text; the guide does
not depend on it, and every other capture is
loopback.

Specimen discipline, for the record: the only
credentials in the guide are the lab's
invented ones; the only certificate is the
lab's self-signed specimen, generated for
the page; the only "personal" data is a
fictional form value in Mesquite, TX. The
lab's servers were stopped when the build
finished, and nothing in the guide requires
them to be anyone else's.
