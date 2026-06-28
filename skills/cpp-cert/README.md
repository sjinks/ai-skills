# cpp-cert

> Use when: reviewing, designing, implementing, or debugging C/C++ for SEI CERT Coding Standard violations - modifying std namespaces, reserved identifiers, paired new/delete, unchecked standard-library return values, unchecked string-to-number conversions, setjmp/longjmp, exceptions thrown before main or from exception copy constructors, throw-by-value/catch-by-reference, float loop counters, signed-char-to-int conversions, padding/representation comparison, raw memory calls on non-trivial types, over-aligned operator new, self-assignment, pointer arithmetic on polymorphic objects, copying FILE/mutex objects, system()/popen(), deprecated unsafe C functions, std::rand and unseeded RNGs, signal-handler safety, and unsafe thread cancellation or termination.

This skill encodes the clang-tidy `cert-*` catalog of the SEI CERT C/C++ Coding Standard: constructs that are undefined, unspecified, security-sensitive, or error-prone by the standard's criteria even when they compile cleanly. Each finding maps to a specific CERT rule ID and the canonical `cert-<id>` clang-tidy check.

It helps an assistant:

- audit declarations/namespaces, error handling and exceptions, memory and object operations, expressions and types, concurrency and signals, and security-sensitive API calls against the matching CERT rule
- cite the CERT rule ID and the canonical `cert-<id>` clang-tidy check name so each finding is reproducible and optionally automatable
- separate undefined-behavior and security violations (higher severity) from latent or hygiene issues, and require a documented, rule-specific exception for any suppression
- name CERT rules that need program analysis beyond clang-tidy's reach, and route out-of-scope performance, lifetime, or general-concurrency concerns instead of judging them here
- return `BLOCK`, `CONCERNS`, or `CLEAN` with per-finding CERT mappings, checklist status, test expectations, residual risk, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
