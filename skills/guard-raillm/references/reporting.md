# Evidence and reporting contract

Use [the template](../assets/report-template.md) in the user's language. Save to an agreed private location; default to a new file under `.guard-raillm/`, avoid overwriting earlier audits, and exclude the directory from commits without changing existing ignore rules unnecessarily.

Each finding includes: stable ID, title, category, severity, confidence, status (`confirmed`, `hypothesis`, `hardening`, `fixed`, `accepted-risk`), affected asset/location/revision, evidence, preconditions, concrete impact, existing controls considered, remediation, negative and positive verification, and residual risk. Only the owner can accept risk; record decision/date, never infer acceptance from silence. `fixed` requires verification evidence and a distinction between local code and deployed state.

| Severity | Contextual interpretation |
|---|---|
| Critical | Credible broad privileged compromise or severe sensitive data exposure with low practical barriers |
| High | Material account/tenant boundary failure, privileged secret exposure or major integrity loss |
| Medium | Constrained compromise or resource/business abuse with meaningful prerequisites |
| Low | Limited demonstrated impact or defense-in-depth weakness |
| Informational | Observation; no demonstrated exploitable impact |

Confidence is independent: `high` for traced/reproduced evidence; `medium` for strong code/configuration evidence with a deployment dependency; `low` for unresolved hypotheses. Do not assign a CVSS score unless its version and complete vector are defensible. Missing tests alone do not increase vulnerability severity. Deduplicate a shared root cause but preserve all affected paths.

Coverage ledger: domain, applicability, status, files/endpoints checked, tests/tool commands, limitations. List failures and skips alongside successes. "No confirmed findings within this scope" is valid; "the system is secure" is not. Separate observed facts from architectural recommendations. Include the smallest sanitized evidence sufficient for the owner to reproduce locally.

Remediation order follows practical risk and dependencies: contain active exposure, restore authorization boundaries, bound abuse/cost, then improve hardening and operational detection. Do not publish a report, open issues containing vulnerabilities or send notifications without authorization.
