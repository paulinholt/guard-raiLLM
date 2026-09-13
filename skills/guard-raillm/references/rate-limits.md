# Rate limits and resource abuse

Inventory login, password reset, OTP, registration, search, exports, uploads, GraphQL, WebSocket messages, email/SMS, payment and LLM routes. Record who pays for each operation and which resource it consumes. Include origin endpoints that bypass a gateway.

| Control | Evidence to inspect | Bounded verification |
|---|---|---|
| Identity | Keys combine authenticated account/tenant/API credential with appropriate network controls | Two synthetic users cannot share or evade account budgets by changing headers |
| Proxy trust | Explicit trusted proxy chain; client cannot choose canonical IP via arbitrary forwarding headers | Spoofed headers do not reset the counter in a local proxy fixture |
| Distribution | Shared atomic counter or equivalent across replicas; TTL and clock semantics | Two local instances obey the same budget, including simultaneous requests |
| Window and burst | Documented sustained rate, burst allowance and weighted operation costs | With reduced fixture limits, exactly the intended requests succeed at the boundary |
| Failure behavior | Limiter-store outage has a deliberate per-route policy | Sensitive paid operations remain bounded; public availability follows documented degradation |
| Limits beyond HTTP | Body/decompressed size, pagination, complexity, query timeout, queue size, concurrency | Small fixtures cross each configured bound without generating actual exhaustion |
| Retry behavior | Consistent rejection status, useful retry timing, bounded client backoff | Rejected calls do not trigger retry storms or duplicate paid operations |
| Budget | Per-user/tenant and global spend caps enforced before dispatch | Mock provider rejects work when reservations exhaust the budget |

Do not prescribe one requests/minute value for every application. Determine expected traffic, shared NAT impact, abuse economics and service limits. IP-only login throttling is incomplete; account-only lockout can enable denial of service. Test separate principals, recovery paths and failed attempts without disclosing account existence.

Check counter atomicity, check-then-increment races, expiry reset, eviction, unbounded key cardinality, IPv6 representations, normalization, per-process memory stores in serverless deployments, cache bypass and alternate route versions. For distributed deployments, state explicitly if testing was single-process only.

For paid work, reserve budget atomically before enqueue/dispatch and reconcile completion, failure, timeout and cancellation. Token limits alone do not bound tool loops or parallel calls. Never run a flood to prove a missing limit: inspect code or lower the limit in an isolated test. Live testing needs authorized targets, identity, maximum requests/concurrency/cost, duration and stop conditions.

Sources: [OWASP API risks, resource consumption and business flows](https://owasp.org/API-Security/editions/2023/en/0x11-t10/), [OWASP DoS guidance](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html).
