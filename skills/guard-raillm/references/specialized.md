# Specialized extensions and coverage limits

The primary baseline targets web apps, APIs and their infrastructure. Route additional stacks to current primary documentation and suitable tooling. Record exact specialization coverage; do not inherit a passing web review.

| Stack | Additional work |
|---|---|
| Mobile/desktop | OS credential storage, deep links/IPC, exported components, local data, certificate validation, update signing and platform permissions |
| C/C++/Rust unsafe/FFI | Memory ownership/lifetime, integer boundaries, parsers, concurrency and unsafe interfaces; isolated sanitizers/fuzzing with resource budgets |
| Cryptography/protocols | Standard constructions and maintained libraries, key/nonce lifecycle, randomness, verification and protocol context; specialist review for new designs |
| Smart contracts | Chain-specific authorization, value flow, reentrancy, oracle assumptions, upgrades and economic invariants; use isolated forks/testnets only when authorized |
| Embedded/OT/IoT | Device identity, signed update chain, debug interfaces, physical assumptions and safety constraints; no active testing on operational equipment by default |
| ML pipelines | Training data provenance, poisoning, artifact deserialization, model access and evaluation leakage |

Identify which evidence/tools/expertise are missing and define a follow-up validation scope. No single checklist covers all security domains.
