# Endpoint assessment

Use when the user gives an HTTP(S) URL and asks which vulnerabilities it has. Start with the bundled HTTP assessor, not a generic browser/crawler. The baseline works without source code, credentials or third-party scanners. It is a limited external assessment; it cannot establish complete security.

## Establish a concrete request plan

Use authorization already present in the conversation. A request to audit "my endpoint" authorizes the baseline for that exact URL. If the user merely shares an unrelated URL, establish permission first. Treat every route as potentially consequential: GET is a protocol convention, not a guarantee against side effects. Exclude logout, deletion, exports with costs, payment, OTP/email and other action routes unless explicitly included with appropriate test data/budget.

Record exact URL/port/path, owner-authorized scope, environment (production/staging/local), available identity and limits in a **private request plan**. Label routes `route-1`, `route-2`, etc. in CLI order; the report deliberately omits their paths. Do not place credentials, signed links or personal identifiers in the plan or command history. Unknown environment should use the minimal baseline and remain a stated limitation.

The default baseline sends at most three anonymous GETs to the supplied URL: baseline plus two synthetic Origin probes. Defaults: 12 total requests, one at a time, at least 0.5 seconds between starts, 5 seconds per request, 30 seconds overall network budget. There are no retries or followed redirects. Do not substitute a browser that follows redirects or fetches subresources. If a redirect occurs, record it and establish a new explicit target before another run.

## Execute

Inspect the plan without network access:

```text
python <skill-dir>/scripts/endpoint_audit.py https://app.example.com/health
```

Execute when authorized:

```text
python <skill-dir>/scripts/endpoint_audit.py https://app.example.com/health --authorized
```

`--authorized` records the caller's responsibility; it does not establish ownership or override host permissions. The agent supplies it only when the user's scope already supports execution. The script uses Python 3.10+ standard library, direct sockets and verified TLS. It ignores proxy environment variables and pins the connection to the initially checked DNS answer, while retaining the original TLS hostname. It blocks non-public addresses by default and always blocks link-local/metadata destinations, even with private scope.

For an explicitly local/private target, add `--allow-private`. This is a separate scope, not a workaround for a rejected external host. DNS is resolved once; all answers must satisfy the address policy. Split DNS, VPNs, required proxies and private certificate authorities can prevent execution. Report that limitation; do not disable TLS checks or networking safeguards. The helper is a local CLI, not a hardened multi-user scanning service.

## Optional checks within the user's scope

| Option | Actual behavior | Interpretation |
|---|---|---|
| `--route /exact/path` | Adds another exact path on the same origin; up to ten routes total | No crawling, wildcard expansion or automatic API discovery |
| `--probe-files` | Anonymous HEAD on `/.env`, `/.git/config` and one random nonexistent control path at the origin root | A 2xx is a candidate, not proof of file/secret exposure; no body is read |
| `--rate-samples 5` | Up to five additional sequential anonymous requests to route-1 | 429 is observed throttling; no 429 is inconclusive |
| `--protected --auth-env GUARD_AUDIT_TOKEN` | Compares anonymous and test-Bearer requests for routes declared protected | Two 2xx responses are a hypothesis, not confirmed auth bypass; no body comparison |
| `--no-cors` | Omits the two Origin requests | Useful for a one-request baseline |
| `--output <new-private-dir>` | Saves sanitized JSON and Markdown without overwriting | Keep reports private; directory paths and origin metadata may still be sensitive |

Read a test Bearer token from an already prepared environment variable. Never ask the user to paste it into chat or put it in a command argument. Send it only to exact approved routes and only over verified HTTPS. CORS and sensitive-file probes remain anonymous; credentials are not forwarded on redirects. Cookie-based login, OAuth login automation and two-user authorization are **not implemented** by the helper.

Absolute hard caps: 40 requests, 120 seconds, ten extra rate samples, at least 0.25 seconds between starts, ten seconds per request. If the chosen checks exceed the budget, report them as untested; do not silently increase it or restart to bypass stop conditions. Response sampling is limited to 64 KiB, without decompression; error-signature inspection may miss evidence beyond that sample or in compressed bodies.

## Interpret the evidence

- Verified HTTPS means the configured trust store accepted the certificate/hostname for that connection. It does not enumerate weak ciphers, all protocols, revocation or alternate hosts. A certificate failure can also reflect a missing private CA; there is no insecure retry.
- Missing HSTS and HTML security headers are hardening observations. Presence is recorded, but policy validity/strength is not parsed. Headers can also be inappropriate for a particular API context.
- Cookies are inspected for attribute presence only. Names and values are removed; a missing HttpOnly attribute on a non-session cookie is not automatically an exploitable vulnerability.
- Two different origins reflected with credentials produce a CORS hypothesis. Public data, browser credential policy, preflight and authenticated response behavior must be evaluated before claiming data theft. Wildcard plus credentials alone is not treated as demonstrated exploitation.
- Stack/error signatures produce hypotheses because documentation can contain the same text. The report contains only the signature category, never the response excerpt.
- Sensitive filenames return only metadata. A 200 login page or SPA fallback can resemble file exposure. Confirm through deployment/source evidence; do not download a real `.env` to prove it.
- Authentication status comparison does not establish authorization of objects, fields or tenants. A login page may return 200. Request synthetic fixtures and test identities for deeper work.

Stop on a redirect, 429, server error (5xx), TLS/transport failure or exhausted budget. Preserve completed evidence and report remaining checks as untested. Exit `0`: completed with no confirmed/hypothesis findings (hardening may remain); `1`: completed with findings/hypotheses; `2`: incomplete, invalid input or operational failure. Exit `0` never means the endpoint is secure.

## Deeper testing

For SQL injection, XSS, SSRF, upload handling or object authorization, first obtain the API contract, exact routes/methods, disposable data and a concrete test plan. Follow [bounded follow-up cases](endpoint-follow-up.md). The baseline helper deliberately does not inject payloads, submit forms, enumerate users or perform writes. Use an already available and reviewed tool only within the agreed scope; do not auto-install a DAST scanner or launch a whole-site crawl.

When the host has no network or Python, provide the command and identify testing as not performed; do not invent results. With network available, run the authorized baseline and deliver the report, rather than stopping at instructions.

## Deliver

Read the generated `report.json` and `report.md`, both containing derived evidence only. Explain in the user's language: confirmed observations, candidate vulnerabilities needing validation, hardening, and untested areas. Add impact, preconditions, correction and a verification plan using [reporting](reporting.md). Do not label a whole domain "verified" because one endpoint answered successfully. Keep results local; the user's request to audit an endpoint does not authorize publishing its findings.

Sources: [OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/), [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [Python HTTP client](https://docs.python.org/3/library/http.client.html), [CORS origin semantics](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin).
