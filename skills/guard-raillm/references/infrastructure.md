# Infrastructure and software supply chain

Separate source intent from observed deployment state. Inventory manifests/lockfiles, registries, Docker/IaC, CI workflows, public ingress, IAM, storage, DNS and observability. Record exact installed/resolved versions where available.

- Dependencies: use current vendor advisories and lockfile resolution, including transitive/runtime versus dev/build exposure. Check install scripts, dependency confusion, typosquatting, abandoned components and artifact integrity. No automatic force-upgrades; inspect breaking changes and retest.
- CI: least privilege per job, pinned action commits, restricted token scope, untrusted PR handling, script interpolation, caches/artifact trust and OIDC subject/audience conditions. Do not combine privileged `pull_request_target` with execution of an untrusted checkout. Agent-reviewed PR text is also an injection surface.
- Build: avoid secret arguments/layers, inspect multi-stage copies and `.dockerignore`, pin meaningful versions/digests with an update process, verify provenance where used. Do not execute unknown build hooks just to inventory packages.
- Runtime: non-root where feasible, minimized capabilities, read-only filesystems where compatible, resource limits, no unnecessary host mounts/Docker socket, restricted service accounts and network egress. In Kubernetes inspect RBAC, service exposure, workload identity and network policy effectiveness.
- Cloud/network: public database/admin endpoints, overly broad IAM, bucket policies, security groups, TLS termination, origin bypass and dangling DNS. Read-only configuration access does not authorize changes.
- Observability: debug mode, verbose errors, sensitive metrics labels and unauthenticated consoles; audit access and retention. Reports and source maps can expose internals even without credentials.

Validate with selected scanner output and configuration evidence. A scanner database that failed to update or an IaC directory that was skipped stays an explicit coverage gap. File presence is discovery, not proof of secure/insecure deployment.

Sources: [GitHub secure workflow use](https://docs.github.com/en/actions/reference/security/secure-use), [Trivy](https://github.com/aquasecurity/trivy).
