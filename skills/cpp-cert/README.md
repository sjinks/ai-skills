# cpp-cert

> Use when: reviewing, designing, implementing, or debugging C/C++ for SEI CERT secure-coding violations detected by clang-tidy cert-* checks: unchecked standard-library return values, command injection via system()/popen(), raw memory operations on non-trivial types, pointer arithmetic on polymorphic objects, exception throw/copy safety, signal-handler async-safety, predictable or unseeded RNGs, deprecated unsafe C functions, and other undefined-behavior or security-sensitive constructs.

This skill encodes the clang-tidy `cert-*` catalog of the SEI CERT C/C++ Coding Standard: constructs that are undefined, unspecified, security-sensitive, or error-prone by the standard's criteria even when they compile cleanly. Each finding maps to a specific CERT rule ID and the canonical `cert-<id>` clang-tidy check.

It helps an assistant:

- audit declarations/namespaces, error handling and exceptions, memory and object operations, expressions and types, concurrency and signals, and security-sensitive API calls against the matching CERT rule
- cite the CERT rule ID and the canonical `cert-<id>` clang-tidy check name so each finding is reproducible and optionally automatable
- separate undefined-behavior and security violations (higher severity) from latent or hygiene issues, and require a documented, rule-specific exception for any suppression
- name CERT rules that need program analysis beyond clang-tidy's reach, and route out-of-scope performance, lifetime, or general-concurrency concerns instead of judging them here
- return `BLOCK`, `CONCERNS`, or `CLEAN` with per-finding CERT mappings, checklist status, test expectations, residual risk, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
