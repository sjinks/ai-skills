---
name: dependency-audit
description: "Use when: auditing application or tooling dependencies for known vulnerabilities, license risk, maintenance health in audit/risk/release context, abandoned packages, unused-dependency removal risk, dependency bloat with policy/security/release impact, transitive risk, supply-chain integrity, lockfile evidence gaps, or scanner findings that need evidence-based triage."
argument-hint: "Describe the package ecosystem, manifests and lockfiles, production/dev/runtime scope, distribution model, advisory or scanner evidence, CI/tests, and deployment/reachability context."
user-invocable: true
---

# Dependency Audit

Use this skill for evidence-based dependency review across application and tooling packages. The goal is to decide whether dependency risk is confirmed, likely, unresolved, accepted, or only a test/evidence gap without treating every scanner line as equally blocking.

## When to Use

- Reviewing dependency manifests, lockfiles, package manager changes, dependency update PRs, or release readiness.
- Triage of known vulnerabilities, CVEs, GHSA/advisory records, malicious-package reports, typosquat concerns, compromised maintainers, or suspicious release behavior.
- Auditing license risk, production versus development exposure, transitive packages, abandoned packages, unused dependencies, duplicate packages, heavy dependency additions, or dependency-health concerns when tied to audit, risk, release, removal, compliance, or policy context.
- Comparing scanner output against project reachability, package versions, lockfile resolution, runtime deployment, and tests.
- Reviewing package supply-chain controls such as lockfiles, checksums, provenance, registry source, signature/attestation evidence, and publish-script or install-script exposure.

## When Not to Use

- General package installation help, version selection, or package-manager troubleshooting with no audit question.
- Choosing a library based only on feature fit, API ergonomics, performance, or popularity.
- Ordinary package comparison, bundle-size tuning, performance advice, maintenance-cadence comparison, dependency-count discussion, or popularity ranking unless the user frames it as an audit, risk, release, removal, compliance, or policy decision.
- Routine code review where dependencies are not part of the risk surface.
- Legal advice about whether a license is acceptable for the user's organization. Flag risks for owner/legal review instead.
- Active scanning, dependency installation, package script execution, exploit reproduction, or network calls unless the user explicitly authorizes the exact tool, target, command, and environment.

## Boundaries/Safety

- Start from existing project files: manifests, lockfiles, workspace config, build config, import sites, CI files, deployment config, scanner reports, and advisory references already provided or present in the repository.
- Do not install dependencies, update lockfiles, execute package scripts, run `npm audit`, `pip-audit`, `cargo audit`, `go list -m`, `mvn`, `gradle`, `dotnet`, `bundle audit`, `composer audit`, container scanners, or any networked scanner without explicit user approval.
- Explicit approval for scanners or package-manager commands is necessary but not sufficient. Before running an approved command, inspect and state expected side effects: lifecycle script or plugin execution, lockfile/cache/file mutation, dependency installation, external network disclosure, and upload of private package names, registry URLs, SBOMs, source paths, or project metadata.
- Prefer provided reports and no-script, offline, frozen-lockfile, read-only, dry-run, local-cache, or non-mutating modes when they preserve the audit goal. Block and ask for clarified approval or safer controls when side effects, network disclosure, lifecycle/plugin execution, or mutation behavior is unavailable, ambiguous, or cannot be disabled.
- Treat active or networked scanner results as external evidence. Name the scanner/tool, data source, run time or report timestamp, command provenance when known, and whether the result is fresh for the audited lockfile.
- Do not run reporter-supplied commands, package postinstall scripts, proof-of-concept code, or untrusted links as part of audit triage.
- Do not claim a license is legally acceptable. Classify license uncertainty and route it for project owner or legal review.
- Keep findings tied to concrete dependencies, versions, paths, advisories, licenses, import/reachability evidence, or explicit missing evidence.

## Required Input Context

Collect the narrowest useful context before judging:

- Package ecosystem and package manager, including workspace/monorepo layout and build graph boundaries when dependency exposure differs by package.
- Manifests and lockfiles, such as `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `yarn.lock`, `bun.lock`, `bun.lockb`, `deno.lock`, `pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock`, `Cargo.toml`, `Cargo.lock`, `go.mod`, `go.sum`, `pom.xml`, `build.gradle`, `packages.lock.json`, `Gemfile.lock`, or `composer.lock`.
- Production, development, test, optional, peer, build-time, runtime, plugin, and CLI classification for each dependency under review.
- Distribution model for license analysis: internal service, SaaS, shipped binary, client-side bundle, library/SDK, container image, on-prem package, marketplace extension, or redistributed source.
- Advisory/source provenance: CVE/GHSA/OSV/vendor advisory IDs, scanner output, security bulletin, maintainer statement, registry metadata, or local policy rule.
- Current tests, CI gates, dependency update automation, and whether dependency checks are already enforced.
- Deployment and reachability context for vulnerabilities: execution path, exposed service, enabled feature, attack preconditions, package version, patched version, transitive parent, and whether the vulnerable code is bundled or reachable.
- Lockfile, checksum, registry, provenance, signature, attestation, vendored-source, generated-artifact, or SBOM evidence available for integrity checks.

## Evidence Sources

Use ecosystem-neutral evidence, favoring files already in the repository or supplied by the user:

- JavaScript/TypeScript/npm/pnpm/yarn/Bun/Deno: `package.json`, `package-lock.json`, `npm-shrinkwrap.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `yarn.lock`, `bun.lock`, `bun.lockb`, `deno.json`, `deno.lock`, workspace files, `turbo.json`, `nx.json`, package-manager audit reports, `npm ls` or package-manager tree output when explicitly provided.
- Python/pip/uv/poetry: `pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`, `Pipfile.lock`, `uv.lock`, `poetry.lock`, pip-audit/safety reports, wheel metadata when provided.
- Rust/cargo: `Cargo.toml`, `Cargo.lock`, cargo-audit or RustSec reports, crate features, target-specific dependencies.
- Go modules: `go.mod`, `go.sum`, module graph output, govulncheck output, replaced modules, vendored modules.
- Java/Maven/Gradle: `pom.xml`, Maven lock or effective dependency output, `build.gradle`, `gradle.lockfile`, dependency-check reports, plugin dependencies.
- .NET/NuGet: `*.csproj`, `Directory.Packages.props`, `packages.lock.json`, NuGet audit output, central package management files.
- Ruby/Bundler: `Gemfile`, `Gemfile.lock`, bundler-audit reports, platform-specific gems.
- PHP/Composer: `composer.json`, `composer.lock`, composer audit output, plugin configuration.
- Container/OS packages when explicitly in scope: Dockerfiles, image lock/SBOM files, package manager manifests, base image digest, distro advisory output, and scanner report provenance.
- SBOM and provenance artifacts when available: CycloneDX, SPDX, SLSA or in-toto attestations, build provenance, signature verification output, checksum manifests, vendored dependency directories, generated artifacts, and package metadata snapshots.

## Dependency Risk Taxonomy

Classify each relevant item with one or more of these categories:

- `known-vulnerability`: Advisory-backed vulnerability affecting an installed or requested version.
- `license-risk`: License missing, unknown, incompatible with the stated distribution model, or requiring owner/legal review.
- `maintenance-health`: Stale releases, low maintainer activity, unresolved critical issues, unsupported runtime, or weak security response.
- `abandoned-package`: Package is archived, deprecated, unmaintained, transferred without clear continuity, or replaced by an official successor.
- `transitive-risk`: Risk arrives through a parent dependency, plugin, toolchain, optional peer, or generated bundle rather than direct code.
- `unused-dependency`: Dependency appears unused after checking static imports and known dynamic/plugin/test/export patterns.
- `dependency-bloat`: New or existing dependency adds large footprint, duplicate functionality, deep graph, heavy bundle/runtime cost, or broad attack surface for little value.
- `supply-chain-integrity`: Suspicious publisher/registry change, ownership transfer, compromised package, missing lockfile/checksum, mutable version range, new or changed lifecycle script, provenance gap, dependency-confusion exposure, typosquat, source/artifact mismatch, registry source drift, or unexpected artifact contents.
- `tooling-evidence-gap`: Audit cannot be trusted because scanner provenance, timestamp, lockfile coverage, package classification, SBOM/provenance coverage, deployment artifact identity, or reachability evidence is missing.

## Severity And Verdicts

Use severity `CRITICAL | HIGH | MEDIUM | LOW` for each finding.

- `CRITICAL`: Confirmed compromise, malicious package, active exploitation of a reachable production dependency, credential-exposure install path, or a vulnerability with severe impact and direct reachability.
- `HIGH`: Confirmed vulnerable production/runtime dependency with meaningful attacker reachability; unacceptable or unknown license for a shipped/distributed artifact without owner-accepted tradeoff; missing lockfile or integrity evidence that makes a requested meaningful audit unreliable; suspicious package provenance that could affect builds or runtime. Missing evidence blocks the audit decision, not because it proves a vulnerability.
- `MEDIUM`: Plausible but not fully proven risk, vulnerable dev/build dependency with limited exposure, stale/abandoned package in an important path, transitive risk requiring parent upgrade, license uncertainty in a lower-risk distribution model, or unused/bloat concern with security or operational impact.
- `LOW`: Hygiene issue, minor maintenance concern, duplicate/dead dependency with limited impact, documentation gap, or scanner item with weak reachability and low consequence.

License distribution matrix:

- Shipped, redistributed, client-bundled, library/SDK, on-prem, marketplace, appliance, container/image distribution, or redistributed source artifacts with unknown or locally unacceptable license terms are `HIGH` and `Verdict: BLOCK` unless the project owner or legal/compliance record explicitly accepts the tradeoff for that distribution.
- Internal service or SaaS-only dependencies that are not redistributed default to `Verdict: CONCERNS` for unknown or questionable licenses unless local policy, contract terms, customer commitments, copyleft/source-disclosure obligations, export packaging, or legal/compliance guidance makes the issue blocking.
- Do not give legal conclusions about compatibility, obligations, or acceptability. State the distribution evidence, policy uncertainty, severity basis, and owner/legal question needed for a decision.

Verdicts:

- `Verdict: BLOCK` when there is a CRITICAL finding; a HIGH confirmed production/runtime vulnerability; unacceptable or unknown license for the distribution model without owner-accepted tradeoff; missing lockfile/evidence that prevents a meaningful audit the user requested; compromised, malicious, typosquat, or suspicious package evidence; or an unresolved tooling gap that invalidates the decision.
- `Verdict: CONCERNS` when risks remain but are not currently merge/release blocking: likely risks, open questions with bounded impact, dev-only scanner findings without proven reachability, maintenance-health concerns, dependency-bloat, unused dependencies, or accepted tradeoffs that need tracking.
- `Verdict: CLEAN` only when the relevant dependencies, requested scope, lockfile/provenance, in-scope license context, and in-scope reachability evidence are sufficient and no material findings remain.

Avoid overblocking scanner-only results. Do not return `BLOCK` for a scanner finding unless version, dependency path, vulnerable condition, and production/runtime reachability or policy impact are supported by evidence. If any of those are missing, classify the item as `Likely risk`, `Open question`, or `Test gap` with the evidence needed to upgrade or downgrade it.

## Evidence Standard

Classify each finding as exactly one of:

- `Confirmed issue`: Evidence shows the dependency/version/path/policy is affected.
- `Likely risk`: Evidence is strong but one required link is not fully proven.
- `Open question`: A decision depends on missing owner, license, reachability, deployment, or scanner provenance context.
- `Accepted tradeoff`: Owner/context accepts the risk; record scope, rationale, expiry/revisit trigger, and compensating controls when known.
- `Test gap`: Behavior, reachability, exploitability, or dependency use needs a test or CI check before the verdict can be considered durable.

Use `tooling-evidence-gap` when scanner, lockfile, SBOM, provenance, deployment artifact, or dependency classification evidence is absent or untrustworthy. Use `Test gap` when the dependency evidence is known but behavior, reachability, exploitability, or use still needs validation.

Each finding should name: dependency, version or range, direct/transitive path when known, category, severity, classification, evidence, impact, recommended action, and owner/question if unresolved. For artifact-level gaps such as a missing lockfile, stale scanner screenshot, absent SBOM, registry-source drift, or unknown deployment artifact, name the artifact, control, or evidence source instead of forcing the finding into a dependency name.

Each finding must include a parseable `Category: <one or more taxonomy labels>` line. Multiple categories are allowed only when the evidence independently supports each label; list the primary category first.

## Procedure

1. Define `Target` and `Scope`: ecosystem, manifests/lockfiles, dependency set, production/dev/runtime boundary, distribution model, and whether container/OS packages are in scope.
2. Inventory evidence: manifests, lockfiles, advisory/scanner reports with provenance/timestamp, CI checks, import/build/deploy context, SBOM/provenance artifacts, and gaps.
3. Decide evidence sufficiency: if missing lockfile, scanner provenance, deployment artifact identity, package classification, or reachability evidence prevents the requested decision, create an artifact-level finding and return the smallest evidence needed to proceed.
4. Resolve dependency path: direct versus transitive, parent package, version range versus lockfile version, optional/peer/test/build/runtime classification, and bundled/runtime presence.
5. Triage known vulnerabilities: match advisory affected ranges to installed versions, then check vulnerable feature use, exposure, deployment, mitigations, fixed versions, and tests.
6. Triage license risk: map declared/resolved licenses to the in-scope distribution model and local policy; flag unknown or unacceptable licenses for owner/legal review.
7. Review maintenance health and abandoned packages: deprecation/archive status, release age, issue/security response, runtime support, known successor, and replacement cost.
8. Review transitive risk and dependency bloat: parent paths, duplicate packages, large graph additions, broad platform/native/runtime hooks, and whether a smaller existing dependency or standard library path fits.
9. Review unused dependency claims with false-positive discipline before recommending removal.
10. Review supply-chain integrity: lockfile presence, checksum/digest coverage, registry source, mutable ranges, lifecycle scripts, provenance/attestations when available, typosquat/dependency-confusion signals, package-transfer or publisher-change signals, source/artifact mismatch, and suspicious version jumps.
11. Produce severity, classification, verdict, remediation, tests/checks, and residual risk. Name fixed versions, parent-upgrade paths for transitives, lockfile-diff verification, CI/policy gates, rollback considerations for risky churn, and accepted-risk expiry or revisit triggers where relevant.

## False-Positive Discipline For Unused Dependency Checks

Do not call a dependency unused until these patterns are checked or marked out of scope:

- CLI binaries referenced by scripts, CI, Dockerfiles, Makefiles, task runners, release tooling, or developer docs.
- Build plugins, linters, formatters, transpilers, bundlers, framework adapters, code generators, migrations, and test runners.
- Framework auto-discovery, dependency injection, plugin naming conventions, entry points, reflection, annotations, service loaders, or config-driven loading.
- Dynamic imports, lazy imports, optional imports, platform-specific imports, feature flags, or environment-specific code.
- Optional peer dependencies and plugin host contracts.
- Type-only packages, stubs, annotations, source generators, and compile-time packages.
- Test fixtures, generated code, vendored code, examples, docs builds, or benchmark-only paths when those are intentionally in scope.
- Consumer-facing package exports where the project is a library/SDK and the dependency is part of the public API or peer contract.

## Output Format

Return this structure:

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <ecosystem, package set, manifests/lockfiles, distribution/deployment scope>
Scope: <production/dev/runtime boundary, included/excluded package classes, scanner/advisory sources>
Evidence reviewed:
- <file/report/source, provenance, timestamp/freshness when relevant>
Evidence sufficiency:
- <sufficient for requested scope, or artifact-level blockers and smallest evidence needed>
Findings:
- [SEVERITY] <dependency>@<version/range> or <artifact/control/evidence source> - <classification>
  Category: <primary taxonomy label>[, <secondary taxonomy label when evidence supports it>]
  Evidence: <manifest/lockfile/advisory/import/deploy/license/provenance evidence>
  Impact: <reachable effect or policy concern>
  Action: <upgrade/remove/replace/accept with owner/add check/investigate>
  Owner/question: <owner, legal/project decision, or unresolved question when applicable>
Open questions:
- <missing context that changes severity or verdict>
Checks and tests:
- <CI/scanner/test/removal validation/update verification, lockfile diff, fixed-version check, parent-upgrade verification, or recurrence-prevention gate needed>
Residual risk:
- <what remains after recommended action>
```

Findings must use severity `CRITICAL | HIGH | MEDIUM | LOW`, classification `Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap`, and taxonomy categories from this skill. Use artifact-level findings for missing or untrustworthy audit evidence instead of inventing a dependency/version. Keep `Target` and `Scope` narrow enough that `CLEAN` does not imply unaudited ecosystems, package classes, license questions, or deployment artifacts.

## Anti-Patterns

- Treating a scanner report as proof without matching installed version, dependency path, affected range, and reachability or policy impact.
- Ignoring lockfiles and auditing only version ranges from manifests.
- Blocking every devDependency vulnerability even when it is build-only, not shipped, and has no proven attacker path.
- Calling a package unused based only on grep without checking CLI scripts, plugin loading, generated code, tests, peer contracts, or library exports.
- Providing legal conclusions about license compatibility instead of flagging owner/legal review needs.
- Running networked scanners, package installs, or package scripts without explicit approval.
- Hiding missing provenance, stale scanner timestamps, missing lockfiles, or deployment uncertainty behind a confident verdict.
- Recommending broad dependency churn without tying it to specific evidence, fixed versions, tests, or rollback considerations.
- Forcing lockfile, SBOM, scanner-provenance, deployment-artifact, or registry-source gaps into a fake `dependency@version` finding instead of naming the missing artifact or control.
