# Optional tools and honest execution

The skill works as a manual review without external scanners. The bundled inventory uses Python 3.10+ standard library and outputs only paths/metadata. Exit `0` means inventory completed; `2` means invalid input, errors or truncation. Neither means secure/insecure. It excludes dependency directories and `.git`, skips links/reparse points and never reads file contents. Run on a stable local checkout; filesystem races are not a sandbox boundary.

Select available tools to answer a specific question:

| Tool | Useful evidence | Limits / data handling |
|---|---|---|
| Gitleaks | Working tree and Git-history secret candidates | Use full redaction; verify report fields locally before ingesting; reachable history only |
| Semgrep / CodeQL | Language-aware patterns/data flow | Rules, language support and build requirements affect coverage; inspect build execution |
| Trivy | Dependencies, images and IaC configuration | Vulnerability databases may need network; secret reports can contain sensitive content |
| OSV-Scanner / ecosystem audit | Resolved dependency advisories | May transmit dependency metadata; identify network behavior before execution |
| ZAP | Authorized local/staging HTTP behavior | Crawling and even baseline jobs generate traffic; forms may mutate state |
| Database/provider emulators | Policy and cross-user integration tests | Emulator behavior does not establish production configuration |

Do not install or invoke every tool by default. Check installed version and `--help` before selecting flags; pin reviewed versions/rules for reproducible automation. No `curl | sh`, unreviewed `npx` downloads, automatic fix flags, or upload of private code as a hidden prerequisite.

Example commands for a reviewed Gitleaks installation (confirm against its version):

```text
gitleaks dir <project-dir> --redact=100 --report-format json --report-path <private-report-path>
gitleaks git <project-dir> --redact=100 --report-format json --report-path <private-history-report-path>
```

Reports must stay outside public artifacts; the tool may include sensitive paths or metadata even with values redacted. Distinguish findings exit codes from operational errors using that version's documentation. Record scanner version, rule set, database timestamp, scanned revision, exclusions, build/network use and failures. Never convert any nonzero status into an empty passing result.

Primary documentation: [Gitleaks](https://github.com/gitleaks/gitleaks), [Semgrep](https://semgrep.dev/docs/), [CodeQL](https://codeql.github.com/docs/), [Trivy](https://trivy.dev/), [OSV-Scanner](https://github.com/google/osv-scanner), [ZAP](https://www.zaproxy.org/docs/).
