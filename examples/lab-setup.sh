#!/bin/sh
# Build the TLS half of the curl lab: a self-signed certificate
# for localhost, in ./lab-tls next to this script.
#
# The certificate is a specimen. Its key protects nothing, the
# name is localhost, and the whole directory is disposable.
# echo_server.py --tls refuses to start without it.
set -eu
cd "$(dirname "$0")"

if [ -f lab-tls/cert.pem ]; then
    echo "lab-tls/cert.pem already exists; delete lab-tls/ to rebuild."
    exit 0
fi

mkdir -p lab-tls
openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout lab-tls/key.pem -out lab-tls/cert.pem \
    -days 365 -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null

echo "Lab certificate created:"
openssl x509 -in lab-tls/cert.pem -noout -subject -dates
echo
echo "Start the lab servers (two terminals, or background them):"
echo "  python3 echo_server.py          # http://127.0.0.1:8901"
echo "  python3 echo_server.py --tls    # https://127.0.0.1:8902"
