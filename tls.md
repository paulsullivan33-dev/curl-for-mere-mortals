# TLS: The Padlock, and Removing It

The sibling volume *OpenSSL for Mere Mortals*
takes a handshake apart bolt by bolt; this
chapter stays in the curl driver's seat. When curl
fetches an `https://` address, the connection
is wrapped in **TLS**: the traffic is
encrypted, and — the part this chapter is
about — the server presents a **certificate**
and curl *verifies* it before trusting
anything. The lab's second server speaks
TLS on port 8902, using the self-signed
certificate from `examples/lab-setup.sh`:

```
$ openssl x509 -in lab-tls/cert.pem -noout -subject -ext subjectAltName
subject=CN = localhost
X509v3 Subject Alternative Name:
    DNS:localhost, IP Address:127.0.0.1
```

A specimen certificate: issued by itself, to
itself, covering the names `localhost` and
`127.0.0.1`, good for a year. Everything that
follows uses it.

## The default is refusal

```
$ curl -sS https://127.0.0.1:8902/hello
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. ...
[exit 60]
```

(Message trimmed after its second paragraph;
the full text is that explanatory.) Failure
**60**, and nothing was fetched. This is not
curl being difficult. Verification asks three
questions of the certificate: is it signed by
an authority I trust (a chain leading to the
**trust store** — the bundle of root
certificates your system or curl install
carries), is it in date, and does it name
*this* host? The lab certificate fails the
first question outright: it is signed by
itself, and no trust store on earth lists
it. A certificate can be honestly encrypted
and still fail here — verification is about
*identity*, not secrecy, and curl refuses
the connection rather than let you confuse
the two.

Real certificates pass all three checks
silently. From the one public capture in
this guide:

```
$ curl -s https://example.com -o /dev/null -w '%{http_code} %{ssl_verify_result} %{url_effective}\n'
200 0 https://example.com/
```

`%{ssl_verify_result}` is 0 when verification
succeeded — the normal, unremarkable state of
the public web: a chain to a trusted root,
in date, naming `example.com`.

## `-k`: the override, and its price

```
$ curl -sk https://127.0.0.1:8902/hello
Hello from the lab server.
```

`-k` (`--insecure` — the long name is the
honest one) skips verification **entirely**:
no chain, no name check, no dates. The
connection is still encrypted, but to
*whom* is now unexamined — the lab server, or
any machine in the middle presenting any
certificate at all. curl accepts all of them
without a murmur.

There are legitimate minutes for `-k`: a
first probe of a device whose certificate
you're about to fix, a lab (this one) before
the `--cacert` step below. As a habit, and
in any script that outlives the afternoon,
it converts HTTPS into expensive HTTP. The
most dangerous sentence in operations is
"we'll remove the -k later," written in a
script that then runs for six years.
Everything `-k` tolerates — expired,
wrong-name, self-signed, intercepted — is
something an attacker can also produce.

## `--cacert`: trust, extended deliberately

The correct way to accept the lab's
certificate is to name it as a trusted
authority:

```
$ curl -sS --cacert lab-tls/cert.pem https://127.0.0.1:8902/hello
Hello from the lab server.
$ curl -sS --cacert lab-tls/cert.pem https://localhost:8902/hello
Hello from the lab server.
```

Both names work — the certificate's subject
alternative names cover the IP address and
the hostname alike, which is why the setup
script put both in. Now verification runs in
full: the chain (short: the certificate
itself, presented as its own authority) is
trusted *because you said so, for this
command*, the name matches the address you
asked for, and `-v` confirms the verdict:

```
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519 / RSASSA-PSS
* Server certificate:
*  SSL certificate verify ok.
```

(Grep-trimmed from `--cacert`'s `-v`
against `localhost`: TLS 1.3, a modern
cipher, and the three words that matter.)
This is also the pattern for *real* private
infrastructure: a company's internal CA, a
home lab CA — `--cacert their-ca.pem`, and
curl trusts exactly that authority, no more.
Had the certificate named only `localhost`,
the `127.0.0.1` request would have failed 60
with "subject name does not match" — the
same three questions, a different one
answering no.

Where the everyday trust store lives depends
on the build: Linux distributions point curl
at the system bundle under `/etc/ssl`, while
the Windows and macOS builds generally lean
on the operating system's own store — which
is why a certificate your browser trusts is
occasionally one your script's curl does
not, and why `--cacert` exists.

Client certificates — proving *your* identity
with `--cert` and `--key` — are the mirror
image of this chapter: real, useful in
mutual-TLS setups, and named here rather
than taught; curl's own documentation covers
them once the server side makes sense.

Check: the plain request to 8902 fails with
exit 60; `-k` fetches the page, having
checked nothing; `--cacert` fetches it
having checked everything, against an
authority you chose. If you take one
sentence from the chapter: `-k` answers the
question "can I reach it?", `--cacert`
answers "can I *trust* it?" — ask the second
whenever the answer will matter tomorrow.

Next: time, failure, and exit codes — the
scripting chapter.
