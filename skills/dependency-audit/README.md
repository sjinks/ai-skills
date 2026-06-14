# dependency-audit

> Use when: auditing application or tooling dependencies for known vulnerabilities, license risk, maintenance health in audit/risk/release context, abandoned packages, unused-dependency removal risk, dependency bloat with policy/security/release impact, transitive risk, supply-chain integrity, lockfile evidence gaps, or scanner findings that need evidence-based triage.

This skill is aimed at dependency risk reviews where manifests, lockfiles, scanner reports, advisory records, license context, and deployment reachability need to be reconciled into a practical release or merge verdict.

It helps an assistant:

- start from existing manifests, lockfiles, CI files, scanner reports, and project evidence rather than running package scripts or networked scanners by default
- classify known vulnerabilities, license risk, maintenance health, abandoned packages, transitive risk, unused dependencies, dependency bloat, supply-chain integrity concerns, and tooling evidence gaps
- distinguish confirmed production risk from scanner-only or dev-only findings that need reachability evidence before blocking
- apply false-positive discipline for unused dependency claims, including CLI tools, build plugins, framework auto-discovery, dynamic imports, peer dependencies, tests, generated code, and consumer-facing exports
- return `BLOCK`, `CONCERNS`, or `CLEAN` with severity, classification, evidence, remediation, checks, and residual risk

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
