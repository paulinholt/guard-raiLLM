# Secrets and environment exposure

Start with paths and metadata, then use redacted scanning. Do not dump `.env`, process environments, keychains, credential stores or secret-bearing scanner JSON into the model context. Read only necessary configuration structure through a redacting local tool. A secret can leak even when its file is ignored by Git.

Inspect current tracked/untracked files, reachable Git history, build output, source maps, Docker layers/context, CI logs/artifacts, public directories, browser bundles, error pages, telemetry and documentation. Source review cannot establish whether a deployed server serves `/.env`; mark deployment exposure unverified unless an authorized bounded check is available. Do not request or persist the response body of a real secret file.

| Signal | Interpretation |
|---|---|
| `.env` exists locally | Normal configuration pattern; not itself a vulnerability |
| `.env` tracked | Exposure candidate; determine whether values are genuine and repository access, without printing them |
| `.env.example` | May still contain secrets; filename is not an exemption from scanning |
| `NEXT_PUBLIC_`, `VITE_`, client configuration | Values may enter browser builds; inspect what the build actually exports |
| Public Firebase/Supabase key | May be intentionally public; check key privilege, backend authorization and rules before classifying |
| Privileged private key/server token in browser | Treat the exposure path as urgent; provider validation is unnecessary |

Report file/line or commit/path, credential category, exposure surface and evidence confidence. Omit token prefixes/suffixes and secret-derived hashes when unnecessary. Distinguish suspected fixture values from real credentials. Protect report files with appropriate local permissions; ignored reports are not encrypted or access-controlled.

Containment sequence when exposure is credible: notify owner with redacted evidence; identify consumers and replacement plan; revoke/rotate through the owner-authorized process; check access logs and scope; remove the source of exposure and regenerate affected artifacts; address reachable history/caches with explicit approval; verify replacement and monitor misuse. Deleting a file or adding `.gitignore` does not revoke a credential. History rewrites can disrupt collaborators and cannot erase copies already obtained.

Prefer scoped short-lived credentials/workload identity and secret-manager injection where the architecture supports it. Keep dev/test/prod credentials separate. Verify redaction in logs, exception serializers, tracing and support exports. Do not upload the source or scanner evidence to a third-party service as an incidental audit step.

Sources: [OWASP secrets lifecycle](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [Gitleaks](https://github.com/gitleaks/gitleaks).
