#!/usr/bin/env python3
"""A tiny inspection server for "curl for Mere Mortals".

Run it, then point curl at it:

    python3 echo_server.py            # http://127.0.0.1:8901
    python3 echo_server.py --tls      # https://127.0.0.1:8902
                                      # (needs lab-tls/, see lab-setup.sh)

It answers with what it received, so you can watch curl's requests
land: headers, bodies, form fields, files, cookies, credentials.
Everything it knows is specimen data invented for the lab.

Endpoints:
    /               greeting and the endpoint list
    /hello          a plain-text hello
    /json           a small JSON document
    /status/NNN     that HTTP status code, with a one-line body
    /redirect       302 to /hello
    /redirect-chain 302 to /redirect (two hops to /hello)
    /protected      401 unless Basic paul:specimen-pass
                    or a Bearer header of specimen-token
    /set-cookie     sets a session cookie
    /whoami         reports the Cookie header it received, if any
    /echo           (POST/PUT) a JSON report of what arrived
    /file.bin       8192 deterministic bytes; honours Range
    /file.bin.sha256  the SHA-256 of those bytes, as text
    /flaky          503 twice, then 200 (for --retry)
    /slow           answers after 5 seconds (for timeouts)
"""

import hashlib
import json
import ssl
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

FILE_BYTES = bytes(i % 251 for i in range(8192))
FILE_SHA256 = hashlib.sha256(FILE_BYTES).hexdigest()
_flaky_hits = {"count": 0}

GREETING = """curl lab server. Try:
  /hello            plain text
  /json             a JSON document
  /status/404       any status code you name
  /redirect         a 302 to /hello
  /protected        needs the lab credentials
  /set-cookie       then visit /whoami
  /echo             POST something at it
  /file.bin         8192 bytes, resumable
"""


def parse_multipart(body, content_type):
    """Split a multipart/form-data body into (fields, files).

    Deliberately simple: parts are separated by the boundary string.
    Fields come back as {name: value}; files as
    {name: {"filename": ..., "size": ...}}.
    """
    boundary = content_type.split("boundary=", 1)[1].strip()
    delimiter = ("--" + boundary).encode()
    fields, files = {}, {}
    for part in body.split(delimiter):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        head, _, content = part.partition(b"\r\n\r\n")
        disposition = ""
        for line in head.decode("utf-8", "replace").split("\r\n"):
            if line.lower().startswith("content-disposition:"):
                disposition = line
        name = None
        filename = None
        for piece in disposition.split(";"):
            piece = piece.strip()
            if piece.startswith("name="):
                name = piece[5:].strip('"')
            elif piece.startswith("filename="):
                filename = piece[9:].strip('"')
        if name is None:
            continue
        if filename:
            files[name] = {"filename": filename, "size": len(content)}
        else:
            fields[name] = content.decode("utf-8", "replace")
    return fields, files


class LabHandler(BaseHTTPRequestHandler):
    server_version = "CurlLab/1.0"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    # Silence the default stderr request log would drown the lab;
    # keep it, actually: watching it is half the lesson. It stays.

    def _send(self, code, body, content_type="text/plain; charset=utf-8",
              extra_headers=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _authorized(self):
        auth = self.headers.get("Authorization", "")
        if auth == "Bearer specimen-token":
            return True
        if auth.startswith("Basic "):
            import base64
            try:
                decoded = base64.b64decode(auth[6:]).decode()
            except Exception:
                return False
            return decoded == "paul:specimen-pass"
        return False

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, GREETING)
        elif path == "/hello":
            self._send(200, "Hello from the lab server.\n")
        elif path == "/json":
            doc = {"service": "curl-lab", "status": "ok",
                   "specimens": 3, "nested": {"real": False}}
            self._send(200, json.dumps(doc, indent=2) + "\n",
                       "application/json")
        elif path.startswith("/status/"):
            try:
                code = int(path.split("/")[2])
            except (ValueError, IndexError):
                code = 400
            if code in (204, 304):
                self._send(code, "")
            else:
                self._send(code, f"You asked for status {code}.\n")
        elif path == "/redirect":
            self._send(302, "Redirecting to /hello.\n",
                       extra_headers={"Location": "/hello"})
        elif path == "/redirect-chain":
            self._send(302, "Redirecting to /redirect.\n",
                       extra_headers={"Location": "/redirect"})
        elif path == "/protected":
            if self._authorized():
                self._send(200, "You are in. The specimen word is 'plum'.\n")
            else:
                self._send(401, "Authentication required.\n",
                           extra_headers={
                               "WWW-Authenticate":
                                   'Basic realm="curl-lab"'})
        elif path == "/set-cookie":
            self._send(200, "Cookie set. Now visit /whoami.\n",
                       extra_headers={
                           "Set-Cookie":
                               "session=specimen-abc123; Path=/"})
        elif path == "/whoami":
            cookie = self.headers.get("Cookie")
            if cookie:
                self._send(200, f"Cookie received: {cookie}\n")
            else:
                self._send(200, "No cookie sent.\n")
        elif path == "/file.bin":
            self._serve_file()
        elif path == "/file.bin.sha256":
            self._send(200, FILE_SHA256 + "\n")
        elif path == "/flaky":
            _flaky_hits["count"] += 1
            if _flaky_hits["count"] <= 2:
                self._send(503, "Not yet. Try again.\n")
            else:
                self._send(200, "Third time lucky: the flaky "
                                "endpoint is up.\n")
        elif path == "/slow":
            time.sleep(5)
            self._send(200, "That took 5 seconds.\n")
        else:
            self._send(404, "No such endpoint in the lab.\n")

    def _serve_file(self):
        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes="):
            spec = range_header[6:].split(",", 1)[0]
            start_s, _, end_s = spec.partition("-")
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else len(FILE_BYTES) - 1
            end = min(end, len(FILE_BYTES) - 1)
            chunk = FILE_BYTES[start:end + 1]
            self.send_response(206)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range",
                             f"bytes {start}-{end}/{len(FILE_BYTES)}")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(chunk)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(FILE_BYTES)))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(FILE_BYTES)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        self._echo()

    def do_PUT(self):
        self._echo()

    def _echo(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        content_type = self.headers.get("Content-Type", "")
        report = {
            "method": self.command,
            "path": self.path,
            "content_type": content_type or None,
            "headers": {k: v for k, v in self.headers.items()},
            "body": body.decode("utf-8", "replace"),
        }
        if content_type.startswith("application/x-www-form-urlencoded"):
            parsed = parse_qs(body.decode("utf-8", "replace"))
            report["form_fields"] = {k: v[0] if len(v) == 1 else v
                                     for k, v in parsed.items()}
        elif content_type.startswith("multipart/form-data"):
            fields, files = parse_multipart(body, content_type)
            report["form_fields"] = fields
            report["files"] = files
            report["body"] = f"<{len(body)} bytes of multipart data>"
        self._send(200, json.dumps(report, indent=2) + "\n",
                   "application/json")


def main():
    tls = "--tls" in sys.argv
    if tls:
        port = 8902
        server = ThreadingHTTPServer(("127.0.0.1", port), LabHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain("lab-tls/cert.pem", "lab-tls/key.pem")
        server.socket = context.wrap_socket(server.socket,
                                            server_side=True)
        print(f"lab server (TLS) on https://127.0.0.1:{port}")
    else:
        port = 8901
        server = ThreadingHTTPServer(("127.0.0.1", port), LabHandler)
        print(f"lab server on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
