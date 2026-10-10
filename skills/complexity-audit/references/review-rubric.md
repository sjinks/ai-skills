When to read: during candidate investigation, for complexity patterns and counterevidence; the core defines mandatory evidence gates, severity, and report outcomes.

# Complexity review rubric

Use these as **investigation prompts**, not automatic violations.

| Pattern | Look for | Counterevidence that may justify it |
| --- | --- | --- |
| Speculative abstraction | interface, base class, strategy, factory without distinct behavior or consumers | plugin/API boundary, dependency inversion, alternative implementations, test seam |
| Redundant indirection | pass-through wrappers, chains of trivial helpers, layers adding no policy | authorization, metrics, resource ownership, meaningful naming or API stability |
| Premature generalization | type parameters, registries, extensibility scaffolding for one concrete case | concrete near-term needs, existing protocol or domain variation |
| Configuration proliferation | flags and options with one valid deployment/value | operational variation, backward compatibility, environment-specific behavior |
| Unnecessary defensive code | fallback branches for locally proven invariants, repeated validations | external input, malformed state, race conditions, filesystem/network failures |
| Duplicate responsibilities | multiple layers performing the same validation/transformation | enforcement at separate trust boundaries or useful defense in depth |
| Scope creep | new modules, unrelated cleanup, new dependencies, incidental behavior changes | necessary migration or explicitly requested work |
| Hard-to-follow control flow | deeply nested orchestration, needless async/event indirection, obscure generic helpers | complex domain semantics, resource/synchronization needs |
| Misapplied DRY | abstraction replacing small clear duplication with indirection | actual recurring change that must remain consistent |

## Investigation guidance

For each pattern, inspect its actual callers and requirement or boundary role before judging necessity. Use the core's four evidence gates; this table is not sufficient evidence for a finding. Public interfaces, migrations, concurrency, authentication, and untrusted input require the relevant consumer or failure-path evidence before proposing simplifications.
