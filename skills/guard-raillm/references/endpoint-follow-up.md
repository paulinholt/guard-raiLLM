# Bounded follow-up after an endpoint baseline

These are agent-guided procedures, not automated capabilities of `endpoint_audit.py`. Select only the case implicated by evidence. Use current framework/vendor documentation for exact semantics. Record requests and expected invariants before execution; redact data locally before passing evidence to the model.

| Suspected issue | Required context | Smallest useful verification |
|---|---|---|
| Object authorization | Two synthetic users in different tenants, one disposable object owned by A, approved read route | A can read its object; B and anonymous cannot. Verify a synthetic marker, not status alone. Do not enumerate IDs or read real customer data |
| CORS disclosure | Approved origin policy, a test session, synthetic authenticated response | Verify browser access from a disallowed origin, including cookie/preflight behavior. Use a local test page and disposable session, never a real user's browser credentials |
| Reflected/stored XSS | Rendered input field and disposable record; permission for writes if needed | First trace a unique inert marker through encoding/context. An unescaped marker is a lead, not proof of script execution; use an isolated browser fixture for execution tests |
| Injection | Exact parameter schema and disposable staging data | Compare valid/invalid typed input and source/query construction. For active scanner payloads, require a reviewed narrow plan; no time-delay, data-extraction or out-of-band payloads in the baseline |
| SSRF | URL-fetching feature, egress policy and an owner-controlled receiver | Use a benign marker against that receiver only; never cloud metadata, local admin services or arbitrary third parties. A callback proves fetching, not necessarily unauthorized access |
| Upload/path traversal | Disposable storage and an approved upload route | Verify filename canonicalization and storage boundary with harmless fixture content; inspect storage locally rather than overwriting existing files |
| Rate enforcement | Documented rate/window/identity and staging controls | Lower the limit in staging and verify the boundary with a few requests. Test distributed enforcement separately; never increase production traffic until it fails |
| HTTP authentication | Endpoint contract and test identities | Confirm response meaning, redirects and cache behavior. Check rejected expired tokens locally; do not brute-force credentials or recovery flows |
| Debug/admin exposure | Intended exposure policy and deployment configuration | A page title or 200 alone is not admin access. Inspect access control with a disposable identity; do not try default passwords |

Read-only operations can still trigger billing or business actions. Do not infer permission for writes, callbacks, credential guessing or production exploitation from a generic URL audit. Reuse authorization that is explicit, but keep the requested method/route/data boundaries.

If a hypothesis cannot be validated safely with available evidence, keep it as a hypothesis with a precise next step. The value of the report is supported conclusions, not a larger vulnerability count.
