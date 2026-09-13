# Databases, tenant boundaries and storage

Map application identities to database identities. Inspect schema migrations, grants, runtime connection role, policy definitions, query filters, views, functions, caches, exports and object storage. A tenant ID supplied by the client must not establish membership.

| Area | Review and negative test |
|---|---|
| Object/tenant authorization | User A cannot read/update/delete user B's object, list its metadata, export it, or obtain signed URLs; repeat across tenants and anonymous access |
| PostgreSQL RLS | Verify enabled policies, table grants, `USING` versus `WITH CHECK`, command/role coverage and runtime role; test INSERT and ownership changes, not only SELECT |
| Privileged paths | Owners, superusers and roles with BYPASSRLS can bypass policies; inspect service credentials and SECURITY DEFINER functions, search path and execution grants |
| Supabase | Check exposed schemas, view execution semantics, RPC/functions, storage policies and edge functions; distinguish public publishable/anon keys from privileged service/secret keys |
| Firebase | Review Firestore/Realtime Database/Storage rules and queries; test denied cross-user operations in the emulator; server/Admin SDK bypasses rules and requires its own authorization |
| SQL/NoSQL injection | Follow dynamic predicates, raw ORM calls, sort/column names and operator objects; bind values and allowlist identifiers/operators |
| Connections | Restricted network access, authenticated clients, verified transport, least-privilege app and migration roles, timeouts and bounded pools |
| Concurrency | Transactions, isolation, uniqueness constraints, idempotency and retry policy preserve ownership, balances and inventory under simultaneous operations |
| Storage | Private object policy, upload authorization, path ownership, signed URL expiry and safe content serving; check backups, public buckets and CDN caches |
| Lifecycle | Restore tests, backup permissions/encryption, retention/deletion propagation, replicas, exports and audit trail |

RLS is one implementation of isolation, not mandatory for every database architecture. Absence of RLS alone is a design observation until the real access model is understood. Conversely, enabled RLS does not prove effective isolation. Never use production service credentials to demonstrate cross-tenant access; request an isolated fixture or document the untested path.

Minimal fixture: anonymous, user A, user B, tenant A administrator, tenant B administrator and a separate backend principal; populate synthetic records. Assert allowed and denied SELECT/INSERT/UPDATE/DELETE, membership changes and signed downloads. Use application and database interfaces separately where both are exposed. Keep migrations as reviewable patches; applying them is a separate deployment action.

Sources: [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Firebase rule patterns](https://firebase.google.com/docs/rules/basics), [OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).
