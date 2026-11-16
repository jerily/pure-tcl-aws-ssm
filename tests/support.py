"""Local HTTP assertions with independent AWS Signature V4 verification."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, quote, urlsplit


def verify_signature(request, body):
    auth = request.headers.get("Authorization", "")
    match = re.fullmatch(r"AWS4-HMAC-SHA256 Credential=([^,]+), SignedHeaders=([^,]+), Signature=([0-9a-f]{64})", auth)
    assert match, "missing or malformed SigV4 authentication"
    credential, names, signature = match.groups()
    access, date, region, service, terminal = credential.split("/")
    assert access == "test" and terminal == "aws4_request"
    url = urlsplit(request.path)
    query = "&".join(sorted(quote(k, safe="-_.~") + "=" + quote(v, safe="-_.~") for k, v in parse_qsl(url.query, keep_blank_values=True)))
    headers = "".join(name + ":" + " ".join(request.headers[name].split()) + "\n" for name in names.split(";"))
    payload = request.headers.get("x-amz-content-sha256", hashlib.sha256(body).hexdigest())
    assert payload == hashlib.sha256(body).hexdigest(), "payload digest mismatch"
    path = url.path if service == "s3" else quote(url.path, safe="/-_.~")
    canonical = "\n".join([request.command, path, query, headers, names, payload])
    scope = "/".join([date, region, service, terminal])
    to_sign = "\n".join(["AWS4-HMAC-SHA256", request.headers["x-amz-date"], scope, hashlib.sha256(canonical.encode()).hexdigest()])
    key = b"AWS4test"
    for value in [date, region, service, terminal]:
        key = hmac.new(key, value.encode(), hashlib.sha256).digest()
    expected = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
    assert hmac.compare_digest(expected, signature), "signature mismatch"
    return service


class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, value, headers=None):
        if isinstance(value, (dict, list)):
            body = json.dumps(value, ensure_ascii=False).encode()
            content_type = "application/x-amz-json-1.1"
        else:
            body = value.encode() if isinstance(value, str) else value
            content_type = "application/octet-stream"
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Type", content_type)
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def handle_request(self):
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.route(body)
        except Exception as error:
            self.server.failures.append(repr(error))
            self.reply(400, {"__type": "FixtureFailure", "message": str(error)})

    do_GET = do_POST = do_PUT = do_DELETE = do_HEAD = handle_request


def run(handler, script="http.test"):
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        server.failures = []
        server.calls = {}
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            env = dict(os.environ, AWS_EC2_METADATA_DISABLED="true", NO_PROXY="127.0.0.1,localhost")
            result = subprocess.run([sys.argv[1], str(Path(__file__).with_name(script)), f"http://127.0.0.1:{server.server_port}"], env=env, timeout=90)
            assert result.returncode == 0, "Tcl assertions failed"
            assert not server.failures, server.failures
        finally:
            server.shutdown()
            worker.join()
