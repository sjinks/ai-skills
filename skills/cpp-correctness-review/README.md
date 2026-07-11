# cpp-correctness-review

> Use when: reviewing, debugging, or designing bounded C or C++ operation correctness, including wrong conditions, invalid state transitions, off-by-one errors, signed/unsigned mistakes, truncation, size calculations, iterator misuse in single-threaded flows, partial operation handling, stale cached state, overload mistakes, boundary cases, or tests that contradict implementation.

This skill reviews whether one bounded C or C++ operation does the right thing for the visible contract and concrete inputs. It focuses on functional behavior: expected result or state versus reachable actual result or state.

It helps an assistant:

- establish the target operation, expected contract, and concrete inputs or states under review
- trace normal, boundary, partial, and failure paths without inventing unspecified behavior
- catch off-by-one errors, invalid state transitions, signed/unsigned mistakes, narrowing and size-calculation bugs, single-threaded iterator misuse, stale derived state, overload mistakes, and test/implementation contradictions
- separate correctness findings from lifetime, concurrency, security, performance, sanitizer, and broad-design concerns
- return `BLOCK`, `CONCERNS`, or `CLEAN` with contract, inputs/states reviewed, severity-classified findings, checklist status, regression-test expectations, residual risk, and a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.