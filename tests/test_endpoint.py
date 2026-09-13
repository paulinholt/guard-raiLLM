from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import io
import shutil
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from test_helpers import ROOT, module

ep = module("endpoint_audit", ROOT / "skills/guard-raillm/scripts/endpoint_audit.py")
SECRET = "synthetic-fixture-content-that-must-never-appear-in-reports"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_HEAD(self):
        self.respond(False)

    def do_GET(self):
        self.respond(True)

    def respond(self, body):
        self.server.seen.append((self.command, self.path, self.headers.get("Authorization"), self.headers.get("Origin")))
        status = 200
        if self.path == "/redirect":
            status = 302
        elif self.path == "/limited":
            status = 429
        elif self.path == "/error":
            status = 500
        elif self.path.startswith("/guard-raillm-missing-"):
            status = 404
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        if self.path == "/redirect":
            self.send_header("Location", "http://169.254.169.254/" + SECRET)
        if self.path == "/cors":
            self.send_header("Access-Control-Allow-Origin", self.headers.get("Origin", "https://normal.invalid"))
            self.send_header("Access-Control-Allow-Credentials", "true")
        if self.path == "/fixed-cors":
            self.send_header("Access-Control-Allow-Origin", ep.ORIGINS[0])
            self.send_header("Access-Control-Allow-Credentials", "true")
        if self.path == "/wildcard":
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Credentials", "true")
        if self.path == "/cookie":
            self.send_header("Set-Cookie", "session=" + SECRET + "; Path=/")
        if self.path == "/hardened":
            for name in ("Strict-Transport-Security", "Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy"):
                self.send_header(name, "fixture")
        content = ("Traceback (most recent call last): " if self.path == "/error" else "") + SECRET
        content = content.encode() if self.path != "/large" else b"A" * (ep.MAX_BODY * 2)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if body:
            try:
                if self.path == "/slow":
                    for value in content:
                        self.wfile.write(bytes([value]))
                        self.wfile.flush()
                        time.sleep(0.1)
                else:
                    self.wfile.write(content)
            except OSError:
                pass


@contextmanager
def server(tls_context=None):
    app = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    app.daemon_threads = True
    app.seen = []
    if tls_context:
        app.socket = tls_context.wrap_socket(app.socket, server_side=True)
    worker = threading.Thread(target=app.serve_forever, daemon=True)
    worker.start()
    try:
        yield app, f"{'https' if tls_context else 'http'}://127.0.0.1:{app.server_port}"
    finally:
        app.shutdown()
        app.server_close()
        worker.join(timeout=2)


def client(url, **kwargs):
    return ep.Client(ep.parse_target(url), interval=0.25, allow_private=True, **kwargs)


class EndpointTests(unittest.TestCase):
    def test_plan_never_resolves_or_connects(self):
        with patch.object(ep.socket, "getaddrinfo", side_effect=AssertionError("network")):
            with patch.object(sys, "argv", ["endpoint", "https://example.invalid/private"]):
                self.assertEqual(ep.main(), 0)

    def test_sensitive_plan_matches_actual_method(self):
        with patch.object(sys, "argv", ["endpoint", "https://example.invalid/.env"]), patch.object(sys, "stdout", new_callable=io.StringIO) as out:
            self.assertEqual(ep.main(), 0)
            plan = json.loads(out.getvalue())
            self.assertEqual(plan["methods"], ["HEAD"])
            self.assertEqual(plan["planned_requests"], 1)

    def test_tls_checks_cannot_be_disabled(self):
        context = ssl._create_unverified_context()
        with patch.object(ep, "resolve", return_value=(socket.AF_INET, ("127.0.0.1", 443))):
            with self.assertRaises(ep.AuditError):
                ep.Client(ep.parse_target("https://fixture.invalid"), context=context)

    def test_invalid_budgets_do_not_resolve(self):
        with patch.object(ep, "resolve", side_effect=AssertionError("network")):
            for kwargs in ({"max_requests": 41}, {"duration": float("inf")}, {"interval": 0}, {"timeout": float("nan")}):
                with self.assertRaises(ep.AuditError):
                    ep.Client(ep.parse_target("https://fixture.invalid"), **kwargs)

    def test_reject_ambiguous_urls(self):
        for url in ("file:///etc/passwd", "https://user:pass@example.com", "https://example.com/?token=x",
                    "https://example.com/#x", "https://example.com/../secret", "https://example.com/%0d%0a",
                    "https://example.com\\evil", "https://example.com:0/", "https://[::1%25x]/"):
            with self.subTest(url=url), self.assertRaises(ep.AuditError):
                ep.parse_target(url)

    def test_public_scope_blocks_localhost(self):
        with self.assertRaises(ep.AuditError):
            ep.resolve("127.0.0.1", 80, False, 1)

    def test_metadata_blocked_even_in_private_scope(self):
        answers = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 80))]
        with patch.object(ep.socket, "getaddrinfo", return_value=answers), self.assertRaises(ep.AuditError):
            ep.resolve("metadata.invalid", 80, True, 1)

    def test_mixed_dns_answers_rejected(self):
        answers = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 80)) for ip in ("8.8.8.8", "127.0.0.1")]
        with patch.object(ep.socket, "getaddrinfo", return_value=answers), self.assertRaises(ep.AuditError):
            ep.resolve("mixed.invalid", 80, False, 1)

    def test_dns_pin_prevents_second_resolution(self):
        with server() as (app, url):
            transport = client(url)
            with patch.object(ep.socket, "getaddrinfo", side_effect=AssertionError("second lookup")):
                response = transport.request("/hardened")
            self.assertEqual(response["status"], 200)
            self.assertEqual(len(app.seen), 1)

    def test_reflection_requires_two_matching_origins(self):
        with server() as (_, url):
            for path, expected in (("/cors", True), ("/fixed-cors", False), ("/wildcard", False)):
                report = ep.audit(client(url), [path])
                candidates = [f for f in report["findings"] if f["code"] == "credentialed-origin-reflection"]
                self.assertEqual(bool(candidates), expected)
                if candidates:
                    self.assertEqual(candidates[0]["status"], "hypothesis")

    def test_redirect_never_followed(self):
        with server() as (app, url):
            report = ep.audit(client(url), ["/redirect"], files=True, rate_samples=3)
            self.assertEqual(len(app.seen), 1)
            self.assertEqual(report["stop_reason"], "redirect-not-followed")
            self.assertNotIn(SECRET, json.dumps(report))

    def test_remaining_routes_are_recorded_after_stop(self):
        with server() as (_, url):
            report = ep.audit(client(url), ["/redirect", "/hardened"])
            coverage = {item["check"]: item["status"] for item in report["coverage"]}
            self.assertEqual(coverage["route-2:baseline"], "not-tested")
            self.assertEqual(coverage["route-2:cors"], "not-tested")

    def test_stop_on_429_and_500(self):
        with server() as (app, url):
            for path, reason in (("/limited", "rate-limited"), ("/error", "server-error")):
                before = len(app.seen)
                report = ep.audit(client(url), [path], rate_samples=10)
                self.assertEqual(len(app.seen) - before, 1)
                self.assertEqual(report["stop_reason"], reason)
                self.assertNotIn(SECRET, json.dumps(report))

    def test_sensitive_paths_only_head(self):
        with server() as (app, url):
            report = ep.audit(client(url), ["/hardened"], cors=False, files=True)
            seen = [(method, path) for method, path, _, _ in app.seen]
            self.assertIn(("HEAD", "/.env"), seen)
            self.assertIn(("HEAD", "/.git/config"), seen)
            self.assertNotIn(("GET", "/.env"), seen)
            self.assertTrue(all(f["status"] == "hypothesis" for f in report["findings"] if f["code"] == "sensitive-path-candidate"))

    def test_explicit_sensitive_endpoint_never_gets_body(self):
        with server() as (app, url):
            ep.audit(client(url), ["/.env", "/.git/config"])
            self.assertEqual([method for method, _, _, _ in app.seen], ["HEAD", "HEAD"])

    def test_request_budget_and_no_absence_claim(self):
        with server() as (app, url):
            report = ep.audit(client(url, max_requests=2), ["/hardened"], cors=False, rate_samples=10)
            self.assertEqual(len(app.seen), 2)
            self.assertEqual(report["stop_reason"], "request-budget")
            self.assertEqual(next(c for c in report["coverage"] if c["check"] == "rate-limit")["status"], "inconclusive")

    def test_bounded_body_and_redacted_reports(self):
        with server() as (_, url), tempfile.TemporaryDirectory() as tmp:
            report = ep.audit(client(url), ["/cookie", "/large"], cors=False)
            self.assertEqual(report["requests"][1]["bytes_sampled"], ep.MAX_BODY)
            ep.save_report(report, Path(tmp) / "result")
            for name in ("report.json", "report.md"):
                self.assertNotIn(SECRET, (Path(tmp) / "result" / name).read_text())
            with self.assertRaises(FileExistsError):
                ep.save_report(report, Path(tmp) / "result")

    def test_slow_response_deadline(self):
        with server() as (_, url):
            start = time.monotonic()
            report = ep.audit(client(url, duration=1, timeout=1), ["/slow"], cors=False)
            self.assertLess(time.monotonic() - start, 2.5)
            self.assertFalse(report["complete"])

    def test_no_plaintext_credentials(self):
        with server() as (app, url):
            with self.assertRaises(ep.AuditError):
                client(url, token=SECRET)
            self.assertEqual(app.seen, [])

    def test_tls_failure_has_no_insecure_retry(self):
        with patch.object(ep, "resolve", return_value=(socket.AF_INET, ("127.0.0.1", 443))):
            transport = ep.Client(ep.parse_target("https://fixture.invalid"))
        with patch.object(ep.PinnedConnection, "request", side_effect=ssl.SSLCertVerificationError("private detail")) as call:
            report = ep.audit(transport, ["/"])
            self.assertEqual(call.call_count, 1)
            self.assertEqual(report["stop_reason"], "tls-certificate-verification-failed")
            self.assertNotIn("private detail", json.dumps(report))

    def test_real_tls_and_credential_isolation(self):
        openssl = shutil.which("openssl")
        if not openssl and Path("C:/Program Files/Git/usr/bin/openssl.exe").exists():
            openssl = "C:/Program Files/Git/usr/bin/openssl.exe"
        if not openssl:
            self.skipTest("OpenSSL CLI needed only to generate an ephemeral local TLS fixture")
        with tempfile.TemporaryDirectory() as tmp:
            cert, key = Path(tmp) / "cert.pem", Path(tmp) / "key.pem"
            subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                            "-subj", "/CN=127.0.0.1", "-addext", "subjectAltName=IP:127.0.0.1",
                            "-keyout", str(key), "-out", str(cert)], check=True, capture_output=True, timeout=20)
            tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            tls.load_cert_chain(cert, key)
            trust = ssl.create_default_context(cafile=str(cert))
            with server(tls) as (app, url):
                report = ep.audit(client(url, token=SECRET, context=trust), ["/hardened"], protected=True)
                self.assertTrue(report["complete"])
                self.assertEqual([auth for _, _, auth, _ in app.seen], [None, "Bearer " + SECRET, None, None])
                self.assertNotIn(SECRET, json.dumps(report))
                before = len(app.seen)
                rejected = ep.audit(client(url), ["/hardened"])
                self.assertEqual(rejected["stop_reason"], "tls-certificate-verification-failed")
                self.assertEqual(len(app.seen), before)

    def test_cli_executes_local_assessment(self):
        with server() as (_, url), tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "audit"
            run = subprocess.run([sys.executable, str(ROOT / "skills/guard-raillm/scripts/endpoint_audit.py"),
                                  url + "/hardened", "--authorized", "--allow-private", "--no-cors", "--output", str(output)],
                                 text=True, capture_output=True, timeout=10)
            self.assertEqual(run.returncode, 1)  # confirmed plaintext transport observation
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["requests_sent"], 1)
            self.assertTrue(report["complete"])
            self.assertNotIn(SECRET, run.stdout + run.stderr)
