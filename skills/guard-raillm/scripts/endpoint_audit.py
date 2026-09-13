#!/usr/bin/env python3
"""Bounded HTTP endpoint assessment. Python stdlib; no crawling or exploits."""
import argparse
import http.client
import ipaddress
import json
import os
from pathlib import Path
import queue
import re
import socket
import ssl
import threading
import time
from urllib.parse import unquote, urlsplit
import uuid

VERSION = "0.2.0"
ORIGINS = ("https://audit-one.invalid", "https://audit-two.invalid")
MAX_BODY = 65536


class AuditError(Exception):
    """Error with a fixed, non-sensitive public message."""


def validate_budgets(max_requests, duration, interval, timeout):
    if not 1 <= max_requests <= 40 or not 1 <= duration <= 120 or not 0.25 <= interval <= 10 or not 0.1 <= timeout <= 10:
        raise AuditError("Invalid request, duration, interval or timeout budget.")


def parse_target(url):
    if not isinstance(url, str) or any(ord(c) < 33 or ord(c) > 126 for c in url):
        raise AuditError("Use an ASCII URL without whitespace or control characters.")
    try:
        parts = urlsplit(url)
        port = parts.port if parts.port is not None else (443 if parts.scheme == "https" else 80)
    except ValueError:
        raise AuditError("Invalid URL or port.") from None
    if (parts.scheme not in {"http", "https"} or not parts.hostname or parts.username is not None
            or parts.password is not None or parts.query or parts.fragment or "\\" in url or "%" in parts.netloc):
        raise AuditError("Use HTTP(S), without credentials, query strings, fragments or escaped hosts.")
    if not 1 <= port <= 65535:
        raise AuditError("Invalid port.")
    host = parts.hostname.lower()
    if not re.fullmatch(r"[a-z0-9.:-]+", host):
        raise AuditError("Invalid hostname; use punycode for international domain names.")
    path = validate_path(parts.path or "/")
    display_host = f"[{host}]" if ":" in host else host
    return {"scheme": parts.scheme, "host": host, "port": port, "path": path,
            "origin": f"{parts.scheme}://{display_host}:{port}"}


def validate_path(path):
    if (not isinstance(path, str) or not path.startswith("/") or path.startswith("//")
            or any(ord(c) < 33 or ord(c) > 126 for c in path) or any(c in path for c in "?#\\")):
        raise AuditError("Routes must be absolute paths without queries or fragments.")
    decoded = unquote(path)
    if (any(ord(c) < 32 or ord(c) == 127 for c in decoded) or "\\" in decoded
            or any(part in {".", ".."} for part in decoded.split("/"))):
        raise AuditError("Ambiguous or unsafe route path.")
    return path


def sensitive_path(path):
    parts = unquote(path).lower().split("/")
    return any(part == ".git" or part.startswith(".env") or part.endswith((".pem", ".key")) for part in parts)


def resolve(host, port, allow_private, timeout):
    """Resolve once with a bounded caller wait; connect only to these checked IPs."""
    result = queue.Queue(maxsize=1)

    def lookup():
        try:
            result.put(socket.getaddrinfo(host, port, type=socket.SOCK_STREAM))
        except OSError:
            result.put(None)

    threading.Thread(target=lookup, daemon=True).start()
    try:
        addresses = result.get(timeout=timeout)
    except queue.Empty:
        raise AuditError("DNS resolution timed out.") from None
    if not addresses:
        raise AuditError("DNS resolution failed.")
    checked = []
    for family, _, _, _, address in addresses:
        ip = ipaddress.ip_address(address[0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            raise AuditError("Link-local, metadata, reserved or multicast destinations are blocked.")
        if not ip.is_global and not (allow_private and (ip.is_private or ip.is_loopback)):
            raise AuditError("Non-public destination requires explicit private-network scope.")
        checked.append((family, address))
    return checked[0]


class PinnedConnection(http.client.HTTPConnection):
    def __init__(self, target, address, timeout, context):
        super().__init__(target["host"], target["port"], timeout=timeout)
        self.target = target
        self.address = address
        self.context = context

    def connect(self):
        family, address = self.address
        self.sock = socket.socket(family, socket.SOCK_STREAM)
        self.audit_socket = self.sock
        self.sock.settimeout(self.timeout)
        try:
            self.sock.connect(address)
            if self.target["scheme"] == "https":
                self.sock = self.context.wrap_socket(self.sock, server_hostname=self.target["host"])
                self.audit_socket = self.sock
        except BaseException:
            self.close()
            raise


def stop_socket(connection):
    sock = getattr(connection, "audit_socket", None)
    if sock:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()


def summarize_response(response, body, requested_origin=None):
    """Only allowlisted derived evidence survives. No raw header/body values."""
    headers = {}
    for key, value in response.getheaders():
        headers.setdefault(key.lower(), []).append(value)
    one = lambda name: headers.get(name, [""])[0]
    html = "text/html" in one("content-type").lower()
    cookies = []
    for value in headers.get("set-cookie", []):
        attrs = {part.strip().split("=", 1)[0].lower() for part in value.split(";")[1:]}
        cookies.append({"secure": "secure" in attrs, "httponly": "httponly" in attrs,
                        "samesite": "samesite" in attrs})
    text = body.decode("utf-8", errors="replace")
    signatures = []
    for label, pattern in (
        ("python-traceback", r"Traceback \(most recent call last\):"),
        ("java-stack-trace", r"\bat [\w.$]+\([^\n()]+\.java:\d+\)"),
        ("sql-error-detail", r"SQLSTATE\[[A-Z0-9]{5}\]"),
    ):
        if re.search(pattern, text):
            signatures.append(label)
    cors_origin = one("access-control-allow-origin")
    cors = "wildcard" if cors_origin == "*" else "probe" if cors_origin in ORIGINS else "other-or-absent"
    return {"status": response.status, "html": html, "bytes_sampled": len(body),
            "body_limit_reached": len(body) == MAX_BODY,
            "content_encoded": one("content-encoding").lower() not in {"", "identity"},
            "headers": {name: name in headers for name in (
                "strict-transport-security", "content-security-policy", "x-frame-options",
                "x-content-type-options", "referrer-policy")},
            "cors": cors, "cors_matches_sent_origin": bool(requested_origin and cors_origin == requested_origin),
            "cors_credentials": one("access-control-allow-credentials").strip() == "true",
            "cors_duplicate": len(headers.get("access-control-allow-origin", [])) > 1,
            "cookies": cookies, "error_signatures": signatures,
            "redirect": 300 <= response.status < 400,
            "retry_after_present": "retry-after" in headers}


class Client:
    def __init__(self, target, max_requests=12, duration=30, interval=0.5, timeout=5,
                 allow_private=False, token=None, context=None):
        validate_budgets(max_requests, duration, interval, timeout)
        self.target = target
        self.deadline = time.monotonic() + duration
        self.address = resolve(target["host"], target["port"], allow_private, min(timeout, duration))
        if token and target["scheme"] != "https":
            raise AuditError("Authentication requires HTTPS, including private targets.")
        self.token = token
        self.context = context or ssl.create_default_context()
        if not self.context.check_hostname or self.context.verify_mode != ssl.CERT_REQUIRED:
            raise AuditError("TLS hostname and certificate verification must remain enabled.")
        self.max_requests = max_requests
        self.interval = interval
        self.timeout = timeout
        self.count = 0
        self.last_start = None
        self.stop_reason = None

    def request(self, path, method="GET", origin=None, authenticated=False):
        if self.stop_reason:
            return None
        validate_path(path)
        if sensitive_path(path) and (method != "HEAD" or authenticated):
            raise AuditError("Sensitive-file paths permit anonymous HEAD metadata only.")
        if method not in {"GET", "HEAD", "OPTIONS"}:
            raise AuditError("Only GET, HEAD and OPTIONS are supported.")
        if self.count >= self.max_requests:
            self.stop_reason = "request-budget"
            return None
        wait = 0 if self.last_start is None else max(0, self.interval - (time.monotonic() - self.last_start))
        if time.monotonic() + wait >= self.deadline:
            self.stop_reason = "time-budget"
            return None
        time.sleep(wait)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            self.stop_reason = "time-budget"
            return None
        self.last_start = time.monotonic()
        self.count += 1
        conn = PinnedConnection(self.target, self.address, min(self.timeout, remaining), self.context)
        timer = threading.Timer(min(self.timeout, remaining), stop_socket, args=(conn,))
        timer.daemon = True
        timer.start()
        try:
            headers = {"User-Agent": f"guard-raillm/{VERSION}", "Accept-Encoding": "identity", "Connection": "close"}
            if origin:
                headers["Origin"] = origin
            if authenticated and self.token:
                headers["Authorization"] = "Bearer " + self.token
            conn.request(method, path, headers=headers)
            response = conn.getresponse()
            body = b"" if method == "HEAD" else response.read(MAX_BODY)
            if time.monotonic() >= min(self.last_start + self.timeout, self.deadline):
                self.stop_reason = "time-budget" if time.monotonic() >= self.deadline else "transport-error"
                return None
            result = summarize_response(response, body, origin)
            result["tls_verified"] = self.target["scheme"] == "https"
            if response.status == 429:
                self.stop_reason = "rate-limited"
            elif response.status >= 500:
                self.stop_reason = "server-error"
            elif result["redirect"]:
                self.stop_reason = "redirect-not-followed"
            return result
        except ssl.SSLCertVerificationError:
            self.stop_reason = "tls-certificate-verification-failed"
        except (OSError, http.client.HTTPException, ValueError):
            self.stop_reason = "transport-error"
        finally:
            timer.cancel()
            conn.close()
        return None


def finding(report, code, route, severity, status, evidence, remediation):
    report["findings"].append({"id": f"EP-{len(report['findings']) + 1:03}", "code": code,
                               "route": route, "severity": severity, "status": status,
                               "confidence": "medium" if status == "hypothesis" else "high",
                               "evidence": evidence, "remediation": remediation})


def assess_baseline(report, label, response, https):
    if not response or not 200 <= response["status"] < 300:
        return
    if https and not response["headers"]["strict-transport-security"]:
        finding(report, "hsts-absent", label, "low", "hardening", "HTTPS response omits HSTS.",
                "Evaluate domain coverage and staged HSTS rollout before enabling it.")
    if response["html"]:
        for key in ("content-security-policy", "x-content-type-options", "referrer-policy"):
            if not response["headers"][key]:
                finding(report, "header-absent-" + key, label, "low", "hardening",
                        "HTML response omits " + key + ".", "Configure and test the policy for this application's behavior.")
    for index, cookie in enumerate(response["cookies"], 1):
        missing = [name for name, present in cookie.items() if not present]
        if missing:
            finding(report, "cookie-attributes", label, "informational", "hypothesis",
                    f"Cookie #{index} lacks attributes: {', '.join(missing)}. Cookie identity/value omitted.",
                    "Identify whether it carries authentication; select attributes compatible with intended flows.")
    if response["error_signatures"]:
        finding(report, "error-details", label, "low", "hypothesis",
                "Response matched error signatures: " + ", ".join(response["error_signatures"]) + ".",
                "Verify it is a real error, not example text; return generic errors and keep diagnostics private.")


def audit(client, routes, cors=True, files=False, rate_samples=0, protected=False):
    if protected and not client.token:
        raise AuditError("Authenticated comparison requires a test token.")
    report = {"version": VERSION, "kind": "endpoint-assessment", "origin": client.target["origin"],
              "findings": [], "requests": [], "coverage": [], "stop_reason": None,
              "limitations": ["No crawling, brute force, injection payloads, TLS cipher enumeration or writes.",
                              "Response bodies and raw headers are never persisted; paths are labeled in CLI order.",
                              "Missing headers are hardening observations, not proof of exploitation.",
                              "Database/RLS, internal secrets and cross-tenant access need additional evidence.",
                              "Rate sampling cannot prove absence of rate limits or distributed enforcement.",
                              "GET/HEAD may still cause effects in a poorly designed application."]}
    if client.target["scheme"] == "http":
        finding(report, "plaintext-http", "origin", "low", "confirmed",
                "The configured assessment URL uses plaintext HTTP; HTTPS availability was not tested.",
                "Use HTTPS for production data and verify the intended HTTP-to-HTTPS policy.")

    def request(path, label, purpose, method="GET", origin=None, authenticated=False):
        response = client.request(path, method, origin, authenticated)
        if response is not None:
            report["requests"].append({"route": label, "purpose": purpose, "method": method, **response})
        return response

    for index, path in enumerate(routes, 1):
        label = f"route-{index}"
        sensitive = sensitive_path(path)
        base = request(path, label, "baseline", "HEAD" if sensitive else "GET")
        report["coverage"].append({"check": label + ":baseline", "status": "observed" if base else "not-tested"})
        if sensitive:
            if base and 200 <= base["status"] < 300:
                finding(report, "sensitive-path-candidate", label, "informational", "hypothesis",
                        "Explicit sensitive-file path returned 2xx to HEAD; no body or credential was sent/read.",
                        "Verify routing and deployed files locally; status alone cannot prove secret exposure.")
            continue
        assess_baseline(report, label, base, client.target["scheme"] == "https")
        if base and base["error_signatures"] and not 200 <= base["status"] < 300:
            finding(report, "error-details", label, "low", "hypothesis", "Error response contains a stack/error signature.",
                    "Verify genuine diagnostic exposure; return generic client errors.")
        if protected and base:
            auth = request(path, label, "authenticated-comparison", authenticated=True)
            if auth and 200 <= base["status"] < 300 and 200 <= auth["status"] < 300:
                finding(report, "protected-route-accepts-anonymous", label, "medium", "hypothesis",
                        "Route declared protected returned 2xx both anonymously and with the supplied test identity. Bodies were not compared.",
                        "Verify whether anonymous output exposes protected data; a login page or public response can also be 2xx.")
            report["coverage"].append({"check": label + ":authentication", "status": "observed" if auth else "not-tested"})
        if cors:
            probes = [request(path, label, "cors-probe", origin=origin) for origin in ORIGINS]
            if all(p and 200 <= p["status"] < 300 and p["cors_matches_sent_origin"] and p["cors_credentials"]
                   and not p["cors_duplicate"] for p in probes):
                finding(report, "credentialed-origin-reflection", label, "medium", "hypothesis",
                        "Two unrelated probe origins were allowed with credentials on successful responses; requests were anonymous.",
                        "Verify browser-readable sensitive data and cookie context; allow only intended origins.")
            report["coverage"].append({"check": label + ":cors", "status": "observed" if all(probes) else "not-tested"})
        if client.stop_reason:
            break
    if files:
        control = request("/guard-raillm-missing-" + uuid.uuid4().hex, "control", "missing-path-control", "HEAD")
        for label, path in (("env-file", "/.env"), ("git-config", "/.git/config")):
            response = request(path, label, "sensitive-file-metadata", "HEAD")
            if response and 200 <= response["status"] < 300:
                evidence = "Sensitive filename returned 2xx to HEAD; content was never read."
                if control and 200 <= control["status"] < 300:
                    evidence += " A nonexistent control path also returned 2xx, consistent with a fallback route."
                finding(report, "sensitive-path-candidate", label, "informational", "hypothesis", evidence,
                        "Inspect server routing/deployment locally; do not fetch or publish a real secret file.")
            report["coverage"].append({"check": label, "status": "observed" if response else "not-tested"})
    samples = []
    for _ in range(0 if sensitive_path(routes[0]) else rate_samples):
        response = request(routes[0], "route-1", "rate-sample")
        if response:
            samples.append(response["status"])
        if client.stop_reason:
            break
    report["coverage"].append({"check": "rate-limit", "status": "429-observed" if client.stop_reason == "rate-limited" else "inconclusive" if samples else "not-tested",
                               "samples_completed": len(samples)})
    report["coverage"].extend({"check": item, "status": "not-tested"} for item in
                              ("injection", "cross-tenant-authorization", "database-policies", "internal-secrets", "tls-ciphers"))
    recorded = {item["check"] for item in report["coverage"]}
    for index, path in enumerate(routes, 1):
        checks = [f"route-{index}:baseline"]
        if cors and not sensitive_path(path):
            checks.append(f"route-{index}:cors")
        if protected and not sensitive_path(path):
            checks.append(f"route-{index}:authentication")
        report["coverage"].extend({"check": check, "status": "not-tested"} for check in checks if check not in recorded)
    report["stop_reason"] = client.stop_reason
    report["requests_sent"] = client.count
    report["complete"] = client.stop_reason is None
    if client.stop_reason == "tls-certificate-verification-failed":
        finding(report, "tls-verification-failure", "origin", "medium", "hypothesis",
                "Certificate verification failed against the local trust store; no insecure retry was made.",
                "Check certificate validity, hostname, chain and whether this environment needs a private CA.")
    return report


def markdown(report):
    lines = ["# Endpoint assessment", "", f"Tool version: {VERSION}", "",
             f"Requests sent: {report['requests_sent']}. Stop reason: {report['stop_reason'] or 'completed'}.", "",
             "Routes use input-order labels. Consult the private request plan for exact paths.", "", "## Findings", ""]
    for item in report["findings"]:
        lines.extend([f"### {item['id']} — {item['code']}", "",
                      f"{item['route']} | {item['severity']} | {item['status']} | confidence: {item['confidence']}", "",
                      item["evidence"], "", "Remediation: " + item["remediation"], ""])
    if not report["findings"]:
        lines.extend(["No findings recorded within completed checks. This does not establish security.", ""])
    lines.extend(["## Coverage", ""])
    lines.extend(f"- {item['check']}: {item['status']}" for item in report["coverage"])
    lines.extend(["", "## Limitations", ""])
    lines.extend("- " + item for item in report["limitations"])
    return "\n".join(lines) + "\n"


def save_report(report, directory):
    directory = Path(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    for name, text in (("report.json", json.dumps(report, indent=2, ensure_ascii=True) + "\n"),
                       ("report.md", markdown(report))):
        fd = os.open(directory / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Explicit authorized HTTP(S) endpoint, without query or credentials")
    parser.add_argument("--authorized", action="store_true", help="Execute within authorization already granted by the owner")
    parser.add_argument("--route", action="append", default=[], help="Additional exact GET path on this origin")
    parser.add_argument("--no-cors", action="store_true")
    parser.add_argument("--probe-files", action="store_true", help="Also authorize HEAD on /.env, /.git/config and a missing path")
    parser.add_argument("--rate-samples", type=int, choices=range(0, 11), default=0)
    parser.add_argument("--protected", action="store_true", help="Routes are expected to require authentication")
    parser.add_argument("--auth-env", help="Name of environment variable holding a test Bearer token")
    parser.add_argument("--allow-private", action="store_true", help="Explicit local/private target authorization")
    parser.add_argument("--max-requests", type=int, default=12)
    parser.add_argument("--duration", type=float, default=30)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--output", type=Path, help="New private report directory; never overwritten")
    args = parser.parse_args()
    try:
        target = parse_target(args.url)
        validate_budgets(args.max_requests, args.duration, args.interval, args.timeout)
        routes = list(dict.fromkeys([target["path"], *(validate_path(p) for p in args.route)]))
        if len(routes) > 10:
            raise AuditError("At most ten exact routes are supported.")
        if args.protected and not args.auth_env:
            raise AuditError("Protected-route comparison needs --auth-env with a test identity.")
        if args.auth_env and not args.protected:
            raise AuditError("Use --protected to opt in to sending a test credential.")
        if (args.protected or args.rate_samples) and any(sensitive_path(p) for p in routes):
            raise AuditError("Sensitive-file routes cannot be used for credential or rate-limit tests.")
        sensitive_routes = sum(sensitive_path(p) for p in routes)
        normal_routes = len(routes) - sensitive_routes
        methods = (["GET"] if normal_routes else []) + (["HEAD"] if sensitive_routes or args.probe_files else [])
        plan = {"mode": "plan", "origin": target["origin"], "route_count": len(routes),
                "planned_requests": normal_routes * (1 + (0 if args.no_cors else 2) + int(args.protected))
                                    + sensitive_routes + (3 if args.probe_files else 0) + args.rate_samples,
                "max_requests": args.max_requests, "duration_seconds": args.duration,
                "methods": methods,
                "redirects": "never-followed", "sensitive_file_bodies": "never-read"}
        if not args.authorized:
            print(json.dumps(plan, indent=2))
            return 0
        output = args.output or Path(".guard-raillm") / ("endpoint-" + uuid.uuid4().hex)
        if output.exists() or output.is_symlink():
            raise AuditError("Output directory already exists; choose a new private directory.")
        token = None
        if args.auth_env:
            token = os.environ.get(args.auth_env)
            if not token or len(token) > 8192 or any(ord(c) < 33 or ord(c) > 126 for c in token):
                raise AuditError("Test token is missing or invalid; value not displayed.")
        client = Client(target, args.max_requests, args.duration, args.interval, args.timeout, args.allow_private, token)
        report = audit(client, routes, not args.no_cors, args.probe_files, args.rate_samples, args.protected)
        report["plan"] = {**plan, "mode": "executed"}
        save_report(report, output)
        print(markdown(report))
        print("Saved report.json and report.md in the selected private output directory.")
        return 2 if not report["complete"] else 1 if any(f["status"] in {"confirmed", "hypothesis"} for f in report["findings"]) else 0
    except AuditError as exc:
        print("Assessment not completed: " + str(exc))
        return 2
    except OSError:
        print("Assessment not completed: local I/O error. Existing reports are never overwritten.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
