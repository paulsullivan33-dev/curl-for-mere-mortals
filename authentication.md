# Authentication

The lab's `/protected` endpoint turns
strangers away — chapter 2 met its `401
Unauthorized`, complete with a
`WWW-Authenticate` header naming the scheme
it expects. This chapter presents credentials
two ways, then spends its real length on the
part most tutorials skip: **where the
credential ends up after you've typed it.**

The lab's credentials are specimens:
username `paul`, password `specimen-pass`,
or a bearer token `specimen-token`. Yours
will not be, which is exactly why the second
half of this chapter exists.

## Basic auth: `-u`

```
$ curl -s -u paul:specimen-pass http://127.0.0.1:8901/protected
You are in. The specimen word is 'plum'.
$ curl -s -u paul:wrong-password http://127.0.0.1:8901/protected
Authentication required.
```

`-u user:password` performs **HTTP basic
authentication**: curl encodes the pair and
sends it as an `Authorization` header on the
request. What that header actually contains
is worth seeing once, via `/echo`:

```
    "Authorization": "Basic cGF1bDpzcGVjaW1lbi1wYXNz",
$ echo cGF1bDpzcGVjaW1lbi1wYXNz | base64 -d
paul:specimen-pass
```

That is **Base64**: an encoding, reversible
by anyone who can read it — as you just did,
with no key and no effort. Basic auth is not
encryption and pretends not to be; it is safe
only because **HTTPS** (chapter 8) encrypts
the whole conversation, header included.
Over plain HTTP, a basic credential is a
postcard. Every API key and token in this
chapter's family rides in a header the same
way and deserves the same respect: the header
is visible to anything that can see the
traffic or the request itself.

## Bearer tokens: just a header

Many APIs skip usernames and issue a single
token, presented as `Authorization: Bearer
<token>`:

```
$ curl -s -H 'Authorization: Bearer specimen-token' http://127.0.0.1:8901/protected
You are in. The specimen word is 'plum'.
$ curl -s -o /dev/null -w '%{http_code}\n' -H 'Authorization: Bearer wrong-token' http://127.0.0.1:8901/protected
401
```

No new machinery: `-H` from chapter 4, with
the server's expected incantation in it.
Whoever holds the token is believed — there
is no password behind it — so a token is a
credential in full, not a username in part.

## Where credentials leak

Three places collect what you type, and the
captures below — all against the lab's
five-second `/slow` endpoint, which keeps
curl alive long enough to watch — show each.

**1. Your shell history.** Every command you
type is recorded (in `~/.bash_history` and
its equivalents) *before* curl runs. History
files outlive sessions, get backed up, and
get read by anything that reads your home
directory. A password on a command line is a
password in a file. This leak has no capture
to show because there is nothing to run:
it's the typing itself.

**2. The process list — with a surprise.**
While a command runs, other users on the
machine can read its arguments with `ps`.
The classic advice is that `-u` therefore
exposes your password mid-flight. On the
build machine, the truth is better and
narrower:

```
$ ps -eo args | grep "[c]url"
curl -s -u                    http://127.0.0.1:8901/slow -o /dev/null
curl -s -H Authorization: Bearer specimen-token http://127.0.0.1:8901/slow -o /dev/null
curl -s -K lab-curlrc http://127.0.0.1:8901/slow -o /dev/null
```

(Only the curl lines are shown; the full
listing also matched the sandbox's own shell
processes, whose paths contain "curl".)
Line one: modern curl **rewrites its own
argument list** to blank the `-u` password —
those spaces are deliberate, curl covering
its tracks after reading the value. Do not
build on this: it's a courtesy of recent
curl on systems that allow it, not a
guarantee, and it does nothing about history.
Line two is the real exposure: the token set
from an environment variable stayed **fully
visible**, because it's just a header, and
curl scrubs only what it knows is a password.
Environment variables keep secrets out of
your *history*; they do not keep them out of
*the process list* while the command runs,
and other tools (`/proc/<pid>/environ`, on
Linux, to the owner and root) can read the
variable itself.

**3. URLs and logs.** Credentials embedded in
a URL — `https://user:password@host/` — are
kept by everything that keeps URLs: browser
and proxy logs, server logs, the trace files
of chapter 3. curl accepts the form; prefer
`-u` or a header every time, and treat query
strings (chapter 4's `-G`) as publishable:
servers log them in full.

## The safer patterns

**A config file, kept private.** `-K` reads
options from a file, one per line:

```
$ cat lab-curlrc
user = "paul:specimen-pass"
$ ls -l lab-curlrc
-rw------- 1 root nogroup 28 Oct 20 00:48 lab-curlrc
$ curl -s -K lab-curlrc http://127.0.0.1:8901/protected
You are in. The specimen word is 'plum'.
```

The process list (line three above) shows
only `-K lab-curlrc`: no secret in the
arguments, none in history beyond the file's
name, and `chmod 600` — that `-rw-------` —
means only your account can read the file.
`-K` files can carry any options (`header`,
`cacert`, and the rest), which makes them
the natural home for per-service curl setups,
credentials included. Protect the file like
the credential it is: in a private directory,
never committed to a repository.

**Let curl ask.** `-u paul` with no password
makes curl prompt for it interactively;
nothing is typed into history or the process
list. Interactive only — a script has no
keyboard to answer with — but for by-hand
work it's the cleanest form.

**The older standard.** `~/.netrc` (read
with `--netrc`) stores per-machine logins in
a long-established format that other tools
(ftp clients, some APIs) also honour. It
shares the config file's rule: keep it
`chmod 600`, in your home directory, out of
repositories.

Check: `-u` and the bearer header both open
`/protected`, and both wrong values get the
`401`; the base64 in your own echo decodes
back to the specimen pair in one command;
and a `ps` taken while a slow `-K` request
runs shows the file's name and nothing else.
If you can see your real password in any of
those places, the pattern, not the password,
is what to change.

Next: fetching files properly — names,
resumes, and redirects.
