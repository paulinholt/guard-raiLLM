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

Modes: `quick`, `full`, `diff`, `fix`, `verify`. The core instructions are in English and request responses in the user's language.

The bundled filename inventory is offline and does not read file contents. It is not a vulnerability scanner. External scanners are optional. The workflow does not grant permission for production probing, spend, infrastructure changes or disclosure.

Compatibility is based on the open skill format and platform documentation; v0.1.0 does not claim end-to-end testing across every host/model or measured vulnerability recall. It is not runtime protection or a security certification.

[Research in Portuguese](research.md) · [Evaluation scenarios](../evals/README.md) · [Contributing](../CONTRIBUTING.md) · [MIT license](../LICENSE).
