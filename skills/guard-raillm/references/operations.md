# Business integrity, privacy and resilience

Review high-value state transitions rather than only endpoint input validation.

- Payments/orders/credits: server-side pricing and entitlements, transactional balances, idempotency bound to caller and request, replay and concurrency handling. Mock payment providers; do not create real charges.
- Webhooks: verify signature over the provider-defined raw payload, timestamp tolerance, replay protection, destination/account binding, event ordering and retry behavior. A valid signature alone does not make an event applicable to any tenant.
- Invitations/recovery/admin: expiry, single-use tokens, privilege changes, stale memberships, support impersonation and auditability. Email changes and account recovery must not bypass stronger authentication unexpectedly.
- Personal data: inventory purpose, collection, visibility, retention, deletion, exports, analytics, logs and third-party transfer. Identify jurisdiction/organizational policy needs; technical checks do not establish legal compliance.
- Logging/response: useful events for denied authorization, credential changes, budget exhaustion and privileged operations, without raw secrets or unnecessary personal data. Check alert ownership, actionable thresholds and tamper resistance.
- Recovery: verify restore evidence, backup access, recovery objectives and handling of deleted data on restore. An existing backup file is not proof of recoverability.
- Availability: timeouts, bounded retries with jitter, circuit breakers where appropriate, queue limits, cancellation and dependency failure behavior. Test mocked failure rather than causing an outage.

For concurrency defects, use a small deterministic local test proving a violated invariant, such as two accepted redemptions of one voucher. Report commercial impact conditionally when monetary scale is unknown.

Reference baseline: [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/), [API business-flow abuse](https://owasp.org/API-Security/editions/2023/en/0x11-t10/).
