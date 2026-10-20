# Sending Data

So far every request has been a GET: "show
me." Sending is the other half of the web —
forms, API calls, uploads — and in curl it
all flows from one option. The lab's `/echo`
endpoint exists for this chapter: it answers
with a JSON report of exactly what arrived,
so every claim below is checkable against
the server's own account.

## `-d` makes a POST

```
$ curl -s -d 'name=specimen&count=2' http://127.0.0.1:8901/echo
{
  "method": "POST",
  "path": "/echo",
  "content_type": "application/x-www-form-urlencoded",
  "headers": {
    "Host": "127.0.0.1:8901",
    "User-Agent": "curl/8.5.0",
    "Accept": "*/*",
    "Content-Length": "21",
    "Content-Type": "application/x-www-form-urlencoded"
  },
  "body": "name=specimen&count=2",
  "form_fields": {
    "name": "specimen",
    "count": "2"
  }
}
```

Adding `-d` (long form `--data`) does three
things at once: it switches the method to
**POST**, it puts your string in the request
body, and it labels the body with the
`Content-Type` of an HTML form,
`application/x-www-form-urlencoded` — the
encoding browsers use when a form's fields
are joined as `name=value&name=value`. The
server parsed those two fields back out and
reported them under `form_fields`. (All the
echo captures in this chapter except this
first one are trimmed to the lines that
change; the header block repeats.)

Multiple `-d` flags join with `&`, and the
variations matter:

| Option | Difference that bites |
|--------|-----------------------|
| `-d` / `--data` | sends the string as-is; `@file` reads a file |
| `--data-urlencode` | percent-encodes its value first |
| `--data-raw` | like `-d`, but a leading `@` stays literal |
| `--data-binary` | `@file` contents sent untouched |

## Let curl do the encoding

That form encoding has rules: spaces, `&`,
and `,` inside a *value* must be escaped, or
the server reads your data as structure.
Hand-escaping is error-prone; `--data-urlencode`
does it:

```
$ curl -s --data-urlencode 'name=J R R Tolkien & Sons' --data-urlencode 'city=Mesquite, TX' http://127.0.0.1:8901/echo
  "body": "name=J+R+R+Tolkien+%26+Sons&city=Mesquite%2C+TX",
  "form_fields": {
    "name": "J R R Tolkien & Sons",
    "city": "Mesquite, TX"
  }
```

The wire body shows the escapes (`+` for
spaces, `%26` for the `&` that is *data*, not
a separator, `%2C` for the comma), and the
server's parsed fields show the values back
intact. If you send values with `-d`
unencoded, the `&` in "Tolkien & Sons"
becomes a field boundary and your data
arrives in pieces — silently, because the
request is perfectly legal; it's just not
the request you meant.

## JSON: the body and the label are separate jobs

APIs usually want JSON. `-d` will happily
carry it — from a file with `@`:

```
$ curl -s -d @payload.json http://127.0.0.1:8901/echo
  "content_type": "application/x-www-form-urlencoded",
  "body": "{\"count\":2,\"name\":\"specimen\",\"tags\":[\"lab\",\"example\"]}",
```

The JSON arrived byte-perfect — but labelled
as a *form*. Many APIs reject that outright;
lenient ones parse the body and never tell
you the label was wrong. `-d` sets the form
label by default no matter what you feed it,
so declaring JSON is a second, explicit job:

```
$ curl -s -d @payload.json -H 'Content-Type: application/json' http://127.0.0.1:8901/echo
  "content_type": "application/json",
  "body": "{\"count\":2,\"name\":\"specimen\",\"tags\":[\"lab\",\"example\"]}"
```

`-H` adds (or replaces) a header. Rule of
thumb worth taping to the monitor: **curl
moves bytes faithfully and labels them
conservatively; if the bytes are JSON, say
so.** The same pattern sends data typed
inline: `-d '{"name":"specimen"}'` with the
same `-H` — mind your shell's quoting, single
quotes outside, double quotes inside.

## The `@file` newline trap

`-d @file` reads the file but **strips
carriage returns and newlines** — a courtesy
designed for one-line data files, and a trap
for everything else. The lab's two-line
`upload.txt`, sent that way:

```
  "body": "A specimen file for upload practice.It contains nothing but these two lines.",
```

One line, the line break gone, the sentences
run together. When the bytes must be exact,
use `--data-binary @file` instead.

## Real uploads: `-F`

File uploads in forms are a different
encoding, `multipart/form-data`, where each
field is its own section and files travel as
attachments. `-F` builds it:

```
$ curl -s -F 'note=@upload.txt' -F 'kind=specimen' http://127.0.0.1:8901/echo
  "content_type": "multipart/form-data; boundary=------------------------2PC2Rn2tkyUbw9h0yaTONE",
  "form_fields": {
    "kind": "specimen"
  },
  "files": {
    "note": {
      "filename": "upload.txt",
      "size": 77
    }
  }
```

Two `-F` options: `note=@upload.txt` (the
`@` again meaning "from this file", now with
its name attached) and a plain field,
`kind=specimen`. curl invented the boundary
string in the `Content-Type`, packed both
parts, and the server unpacked them: field
under `form_fields`, file under `files` with
its filename. This is the shape photo
uploads, document submissions, and most
"attach a file" forms on the web still use.

## Other methods, and data going up a GET

Occasionally an API wants another method —
PUT, DELETE, PATCH. `-X` names it:

```
$ curl -s -X PUT -d 'replaced=true' http://127.0.0.1:8901/echo
  "method": "PUT",
```

`-X` changes the word and nothing else; the
`-d` still makes the body and (by itself)
would have implied POST. Prefer letting `-d`,
`-F`, and `-I` imply their methods, and keep
`-X` for the methods nothing implies.

And when data belongs in the *address*
instead — a query string — `-G` moves `-d`
family data up there, encoded:

```
$ curl -G --data-urlencode 'q=hello world' http://127.0.0.1:8901/json -o /dev/null -v
> GET /json?q=hello+world HTTP/1.1
```

Only the request line is shown (the rest of
`-v` is chapter 3's subject; the JSON body
went to `/dev/null`). The request went out
as a GET with `?q=hello+world` attached.
Note that the full URL now contains your
data — which servers log, a point chapter 5
returns to.

Check: against `/echo`, your POST reports
`method` POST and your fields parsed back;
`--data-urlencode` round-trips a value with
spaces and an `&` intact; your JSON reports
`application/json` once you've added the
header; and `-F` reports your file under
`files` with its name. If any field arrives
split or re-labelled, the echo has just
shown you the exact moment it happened.

Next: proving who you are — and where the
proof can leak.
