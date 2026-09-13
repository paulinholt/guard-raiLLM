# guard-raiLLM

A portable application security audit skill by [Paulo Leal Taveira](https://github.com/paulinholt).

Review rate limits, authorization, database isolation, secret exposure, APIs, infrastructure, supply chain, AI integrations and operational controls. Findings require evidence, impact, remediation and verification. Hypotheses and untested areas remain explicit.

## Install

```sh
git clone https://github.com/paulinholt/guard-raiLLM.git
cd guard-raiLLM
python scripts/install.py --dest ~/.agents/skills
```

Use `~/.claude/skills` for Claude Code or the configured Kimi Code skills directory (currently `~/.kimi-code/skills` by default). The installer uses Python 3.10+, performs a local copy and refuses to overwrite existing installations. See the [platform guide and official sources](installation.md).

Invoke `$guard-raillm` in Codex, `/guard-raillm` in Claude Code or `/skill:guard-raillm` in Kimi Code. Example:

```text
Use guard-raillm in full mode to audit this project.
Prioritize rate limits, cross-tenant authorization and exposed secrets.
Report evidence, proposed fixes and verification gaps. Respond in English.
```

Modes: `endpoint`, `quick`, `full`, `diff`, `fix`, `verify`. The core instructions are in English and request responses in the user's language.

## Audit an endpoint

```sh
python skills/guard-raillm/scripts/endpoint_audit.py https://your-app.example/health --authorized
```

Only assess targets you are authorized to test. Without `--authorized`, this prints an offline plan. The v0.2.0 helper performs bounded HTTP checks for TLS trust, header presence, cookie attributes, CORS behavior and error signatures. Optional scoped checks cover sensitive filenames with HEAD, test-Bearer authentication comparison and rate-limit sampling. It writes sanitized JSON/Markdown reports, follows no redirects and never sends credentials over HTTP.

This is an external baseline, not a full DAST scanner. Injection, two-user object authorization, database policies and internal secrets require follow-up evidence. A 200 on a sensitive path is a hypothesis; missing 429 responses do not prove missing rate limits. See [the full workflow](../skills/guard-raillm/references/endpoint.md).

The bundled filename inventory is offline and does not read file contents. It is not a vulnerability scanner. External scanners are optional. The workflow does not grant permission for production probing, spend, infrastructure changes or disclosure.

Compatibility is based on the open skill format and platform documentation; v0.2.0 includes local HTTP/HTTPS integration tests but does not claim end-to-end testing across every host/model or measured vulnerability recall. It is not runtime protection or a security certification.

[Research in Portuguese](research.md) · [Evaluation scenarios](../evals/README.md) · [Contributing](../CONTRIBUTING.md) · [MIT license](../LICENSE).
