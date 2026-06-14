# review-cycle-gatekeeper

> Use when: enforcing review-fix cycle quality gates, verifying review findings are closed, checking merge readiness, validating fix evidence after a review round, deciding go/no-go on merge, auditing unresolved or reopened review threads, confirming regressions introduced by fixes are tracked, and producing a final pre-merge gate decision.

This skill is aimed at pull requests and change reviews that have already gone through one or more fix cycles and need a clear, evidence-backed merge gate decision.

It helps an assistant:

- normalize findings into explicit states (`fixed`, `owned-with-remediation-plan`, `waived-with-rationale`, `open`)
- enforce severity-aware closure rules so unresolved high-risk findings cannot be merged silently
- require verification evidence for functional fixes and highlight missing proof
- track regressions introduced during fix rounds as first-class findings
- validate waiver quality and ownership/remediation metadata
- return a compact `pass`, `fail`, or `BLOCK` gate summary with exact blockers to clear

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
