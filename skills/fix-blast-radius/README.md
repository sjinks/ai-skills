# fix-blast-radius

> Use when: assessing what a proposed fix or patch could newly break before it is pushed, tracing fix impact through callers, shared state, and contracts, checking whether a fix regresses other resolved findings, or attaching a verification step to each impact risk of a fix.

This skill is aimed at the moment after a fix is drafted and before it is pushed, when the question is what the fix could newly break and which already-resolved findings it could reopen.

It helps an assistant:

- trace the fix structurally across five surfaces: callers and call sites, shared state, contracts, behavioral siblings, and previously resolved findings
- report every surface explicitly as risks found, `no impact found`, or `untraceable` with the missing context named, without padding speculative risks
- attach a surface tag, concrete failure, likelihood, and one executable verification step to each risk
- cross-check every resolved finding supplied for the cycle against the fix's touched code and state
- return `SAFE-TO-PUSH`, `VERIFY-FIRST`, or `BLOCK` with the full impact-trace table and regression cross-check

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
