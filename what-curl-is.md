# What curl Is

**curl** is a command-line tool for moving
data to and from a URL. You give it an
address; it speaks the protocol — HTTP,
HTTPS, FTP, and a few dozen others — performs
the transfer, and hands you whatever came
back. It has been doing this, free and open
source, since the late 1990s, which is why it
is already installed nearly everywhere: Linux
and macOS ship it, Windows 10 and 11 ship it,
and half the software on your machine quietly
contains its library half, **libcurl**.

This guide is about the command line, and
about HTTP in particular, because that is
where curl earns its keep day to day: asking
an API what it thinks, fetching a file
without opening a browser, and — the skill
the later chapters build — *watching* a web
exchange closely enough to see exactly where
it went wrong.

## What curl is not

- **Not a browser.** It does not render
  pages, run JavaScript, or follow the links
  on a page. It fetches the one URL you named
  and stops. When a site "works in the
  browser" but curl gets a login page or a
  script, that difference is usually the
  answer.
- **Not a crawler or a mirroring tool.** It
  will not wander a site for you; tools like
  `wget --mirror` exist for that. curl does
  one transfer per URL, precisely, and (with
  the right options, chapter 6) resumably.
- **Not silent about its work.** Uniquely
  among everyday tools, curl will show you
  the entire conversation — every header both
  ways, every byte accounted for — if you ask
  with `-v`. Chapters 2 and 3 are built on
  that willingness.

## Have you got it?

```
$ curl --version | head -2
curl 8.5.0 (x86_64-pc-linux-gnu) libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.3 brotli/1.1.0 zstd/1.5.5 libidn2/2.3.7 libpsl/0.21.2 (+libidn2/2.3.7) libssh/0.10.6/openssl/zlib nghttp2/1.59.0 librtmp/2.3 OpenLDAP/2.6.10
Release-Date: 2023-12-06, security patched: 8.5.0-2ubuntu10.15
```

That capture — like every capture in this
guide — is from the machine the guide was
built on: curl **8.5.0** on Linux. The long
first line is curl introducing its parts:
the library version, the TLS library
(OpenSSL here; Windows uses its own,
macOS uses Apple's), and the supporting
libraries. The second output line begins:

```
Protocols: dict file ftp ftps gopher gophers http https imap ...
```

(on the build machine; the list continues for
another line). If `curl --version` answers at
all, you have curl; the version matters
mostly when an option from a newer release is
missing on an older one. On the off chance it
doesn't answer: install it from your package
manager (`curl` is the package name almost
everywhere) and come back.

`curl --help` opens with the common options:

```
$ curl --help | head -6
Usage: curl [options...] <url>
 -d, --data <data>          HTTP POST data
 -f, --fail                 Fail fast with no output on HTTP errors
 -h, --help <category>      Get help for commands
 -i, --include              Include protocol response headers in the output
 -o, --output <file>        Write to file instead of stdout
```

The full list runs to hundreds of options;
nobody memorizes it, and this guide doesn't
try. `curl --help all` shows everything,
grouped, and `man curl` is famously thorough.
The chapters teach the few dozen options that
cover everyday work.

## The lab

Most of this guide happens in a small world
built for it: a tiny inspection server,
`examples/echo_server.py`, that answers with
*what it received* — your headers, your form
fields, your cookies, your credentials — so
you can watch your requests land. Start it in
its own terminal:

```
$ cd examples
$ python3 echo_server.py
lab server on http://127.0.0.1:8901
```

`127.0.0.1` is **loopback**: your own machine,
talking to itself. Nothing leaves the
computer, and the credentials are specimens
(`paul` / `specimen-pass`, a bearer token of
`specimen-token`) invented for the lab and
worth nothing. A second copy of the server
speaks TLS on port 8902 once
`examples/lab-setup.sh` has made its
self-signed certificate; that arrives in
chapter 8. One chapter also makes a single
labelled trip to a public site,
`example.com`, the internet's designated
example.

## Your first request

```
$ curl http://127.0.0.1:8901/hello
Hello from the lab server.
```

That is the whole trick, and everything else
in this guide is refinement. curl resolved
the address, connected, sent a request,
received a reply, and printed the **body** —
the actual content — to your terminal. The
noisy lines that normally accompany a
transfer (a progress meter; trimmed from the
captures in this guide, and covered properly
in chapter 6) went to the error stream, not
into the output, which is why curl pipes so
well: what lands on standard output is the
data, only the data.

Check: `curl --version` answers with a
version line; the lab server prints its
address line and stays running; and
`curl http://127.0.0.1:8901/hello` prints the
one-line hello. If the last of those fails
with "Couldn't connect", the server isn't
running — it owns the terminal you started
it in, and closing that terminal stops it.

Next: learning to read everything the server
sent back, not just the body.
