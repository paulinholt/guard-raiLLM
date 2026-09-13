# Application, identity and API controls

Build an endpoint × principal × operation matrix. Include background jobs, internal/admin routes, older API versions, GraphQL resolvers and WebSocket subscriptions. Browser route guards and hidden buttons do not authorize server operations.

| Domain | Investigate | Verification |
|---|---|---|
| Authentication | Signup, login, MFA, recovery, session fixation, enumeration, OAuth/OIDC redirect/state/nonce/PKCE as applicable | Invalid/expired credentials and reused recovery tokens fail; legitimate flows remain usable |
| Tokens/sessions | Signature algorithm allowlist, issuer/audience/expiry, revocation, refresh rotation and cookie scope | Wrong audience, logout/revocation and stolen old refresh token cannot authorize actions |
| Authorization | Object, property and function access; field allowlists; membership transitions | Cross-user/tenant access, role escalation and mass assignment are denied server-side |
| Injection | SQL/NoSQL, OS commands, templates, LDAP, XML entities, unsafe deserialization, prototype pollution | Trace actual controlled input to sink and inspect context-specific defenses |
| XSS | HTML/JS/URL contexts, unsafe markdown, template escapes, stored content and DOM sinks | Untrusted data remains inert in the actual rendering context |
| CSRF/CORS | Ambient cookies, state-changing requests, origin checks, credentials and preflight behavior | Attacker-origin mutation fails; legitimate configured origin succeeds; CORS is not authentication |
| SSRF | URL import, webhooks, image fetch, redirects, DNS resolution and egress | Local mock transport rejects disallowed schemes/destinations at every hop; never probe metadata services live |
| Upload/path | Canonical paths, archive traversal, symlinks, content type, decompression, names, storage ownership | Fixture cannot escape destination, become executable, or read another user's object |
| Browser/transport | Production TLS termination, HSTS rollout, cookie flags, CSP, framing, cache and referrer policies | Inspect deployed layer if authorized; source-level missing headers alone is not proof |
| Protocols | GraphQL depth/cost/batching, WebSocket origin/auth renewal/message bounds, request smuggling across proxies | Use bounded local fixtures; record proxy configuration uncertainty |

Test an authorized request alongside each rejection to avoid fixes that simply disable the feature. UUIDs reduce guessability but never replace authorization. Do not call a defensive encoding function sufficient without verifying its output context. HSTS and restrictive CSP require deployment/domain knowledge and staged validation, especially third-party integrations.

Sources: [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/), [API Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/), [SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).
