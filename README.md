# ai-skills

Small repository of reusable AI assistant skills.

Each skill is stored as a Markdown document with YAML frontmatter and is intended to give an assistant a focused workflow, checklist, and output format for a specific engineering task.

## Repository Structure

```text
skills/
  <skill-name>/
    SKILL.md
```

At the moment, the repository contains these skills:

- `adversarial-review`: guidance for challenging specs, designs, implementations, workflows, and test plans with evidence-based failure-mode review and risk-focused verification.
- `archive-extraction-safety`: guidance for reviewing safe ZIP/TAR/archive extraction, including traversal, symlinks, hardlinks, absolute and Windows paths, Unicode normalization, decompression limits, nested archives, permissions, overwrite policy, containment, cleanup, and parser mismatch.
- `equivalence-class-audit`: guidance for turning one concrete defect, incident, review finding, test failure, or bug report into a locked-scope audit of equivalent defects across sibling fields, mirror use sites, bounds, contracts, paths, modes, tests, docs, and projections.
- `web-app-security-review`: guidance for defensive web application security review of code, PRs, designs, vulnerability reports, and fixes across access control, auth, browser, API, data-flow, supply-chain, cloud, and abuse-risk surfaces.
- `filesystem-path-safety`: guidance for auditing external-input filesystem path construction under trusted roots, including traversal, symlink, TOCTOU, containment, and mutation-safety checks.
- `ssrf-outbound-fetch-review`: guidance for reviewing, designing, implementing, and testing SSRF protections around outbound HTTP fetches, from egress policy contracts through transport and redirect behavior.
- `spock-voice`: guidance for adopting a Spock-inspired, precise, analytical, restrained, and lightly dry conversational register.
- `nestjs-code-review`: guidance for reviewing NestJS applications with severity-classified findings covering modules, DI, controllers, DTOs, guards, exception handling, persistence, testing, API design, performance, and microservices.
- `nestjs-development`: guidance for designing, scaffolding, implementing, refactoring, and testing NestJS features with idiomatic patterns, anti-patterns, and a structured build workflow.
- `review-cycle-gatekeeper`: guidance for enforcing review/fix cycle closure gates so findings are explicitly resolved, verified, owned, or waived before merge.
- `multi-lens-review`: guidance for structuring a multi-lens review (intent, design, implementation, security, adversarial, verification) and synthesizing the lens findings into a single integrated decision with required actions and residual risk.
- `test-gap-to-test-plan`: guidance for converting review findings and unverified behaviors into a prioritized, owned, layer-typed test plan that tracks the test evidence a downstream merge gate will require.

## Included Skills

### `adversarial-review`

This skill is aimed at specs, designs, implementations, workflows, migrations, operational procedures, and test plans that need deliberate failure-mode review before they are trusted.

It helps an assistant:

- identify the target, intended behavior, assumptions, and evidence basis before judging
- apply optional review lenses for reliability, maintainability, security/privacy, user workflow, and verification
- classify failure modes with concrete categories, severity, and evidence standards
- distinguish confirmed issues, likely risks, open questions, accepted tradeoffs, and test gaps
- convert top risks into adversarial tests, mitigations, or acceptance criteria
- return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts without inventing findings

### `archive-extraction-safety`

This skill is aimed at code and designs that extract untrusted or semi-trusted archives into a destination directory.

It helps an assistant:

- define the extraction contract, accepted formats, destination root, allowed entry types, overwrite policy, and resource limits
- review ZIP/TAR traversal, absolute paths, Windows drive/UNC paths, Unicode/path normalization, symlinks, hardlinks, special files, executable bits, permission/ownership restoration, parser mismatch, and destination containment
- check file count, decompressed size, compression ratio, nested archive depth, and partial extraction cleanup
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, tests, and residual risk

### `equivalence-class-audit`

This skill is aimed at situations where a concrete defect, incident, review finding, test failure, or bug report suggests a wider class of equivalent defects that need to be audited in one bounded pass.

For the expanded catalogue, output contract, anti-patterns, and worked example, see [skills/equivalence-class-audit/WORKFLOW.md](skills/equivalence-class-audit/WORKFLOW.md).

It helps an assistant:

- lock the audit scope before expanding from the triggering finding
- enumerate candidate equivalents across bounds, sibling fields, mirror use sites, inverse operations, paths, modes, contracts, authorization surfaces, tests, docs, and source-of-truth projections
- record evidence-based `present`, `absent`, `n/a`, and `blocked` presence verdicts without guessing
- assign explicit dispositions for present defects: `fix-now`, `defer-with-owner`, or `blocked` (use `n/a` only where appropriate)
- return one structured audit report with rows for every applicable axis or candidate, plus fix-now defects, deferred follow-ups, out-of-scope candidates, blocking questions, and test/doc implications

### `filesystem-path-safety`

This skill is aimed at code that turns external input into filesystem paths under a trusted root and then reads, creates, mutates, or deletes files.

It helps an assistant:

- establish the target, trusted root, external-input surface, and operation kind before judging
- audit validation, canonicalization, containment, symlink, hardlink, TOCTOU, and mutation-ordering controls
- distinguish static safe paths from externally influenced paths that need a trusted-root contract
- return anchored findings, insufficient-context blocks, and test expectations without broader web-app review structure

### `web-app-security-review`

This skill is aimed at web application security reviews where the assistant needs to evaluate code, pull requests, designs, vulnerability reports, or fix validation with a defensive and evidence-based workflow.

For the expanded checklist and evidence standards, see [skills/web-app-security-review/WORKFLOW.md](skills/web-app-security-review/WORKFLOW.md).

It helps an assistant:

- set safe-use boundaries for static review, explicitly authorized active testing, and untrusted external report content
- map trust boundaries, actors, tenants, entry points, sensitive data, and downstream systems before judging
- review high-value areas such as broken access control / IDOR, auth and sessions, OAuth / OIDC / JWT, XSS, CSRF, injection, XXE, SSRF, CORS, browser headers, file uploads, GraphQL, WebSockets, webhooks, secrets, dependencies, cloud IAM, containers, ReDoS, and DoS
- use concrete grep and review heuristics without relying on weaponized payload lists
- classify findings with severity, confidence, evidence standards, false-positive discipline, and regression-test expectations
- route narrow outbound-fetch and filesystem path construction work to `ssrf-outbound-fetch-review` and `filesystem-path-safety` when those specialized contracts apply

### `ssrf-outbound-fetch-review`

This skill is aimed at code paths that accept or derive URLs from untrusted or semi-trusted input and then perform outbound requests, especially when policy, parsing, DNS, proxy, transport, redirect, and trusted private-target opt-in behavior all need to line up.

It helps an assistant:

- define explicit egress and port policy contracts before implementation
- review URL parsing, normalization, IP classification, and DNS handling, including connection-time lookup and rebinding risks
- reason about proxy behavior and transport semantics such as SNI, Host, and certificate verification
- assess redirect safety, sensitive-header handling, and trusted private-target opt-ins
- build realistic adversarial tests for SSRF-related edge cases
- return findings in a consistent, review-ready format

The skill covers both implementation concerns and review discipline, including boundaries, required input context, a definition of done, and a structured output contract.

### `spock-voice`

This skill is aimed at responses where the user explicitly asks for a Spock-inspired conversational register. It focuses on calm logic, scientific precision, disciplined curiosity, and understated dry humor while keeping the user's goal primary.

It helps an assistant:

- stay concise, analytical, and exact
- prefer evidence, probabilities, tradeoffs, and clearly stated assumptions
- use calm restraint rather than emotional flourish
- add light dry wit only when it improves warmth or clarity
- avoid impersonation, signature catchphrases, or style choices that override safety and accuracy
- apply the voice only to advisory commentary, leaving code, commit messages, PR text, and required structured output in a neutral register

### `nestjs-code-review`

This skill is aimed at NestJS pull requests, feature branches, security reviews, and architecture validations where a repeatable review contract is more useful than ad-hoc style comments.

It helps an assistant:

- restate the change as intent, scope, risk surfaces, severity rubric, and out-of-scope before judging
- walk a checklist covering module architecture and DI, controllers and the request lifecycle, DTOs and validation, guards and auth, exception handling, configuration and bootstrap, persistence, testing, API design, performance, and microservices
- flag NestJS-specific anti-patterns such as fat controllers, direct ORM access from controllers, `forwardRef` overuse, and modules exporting themselves
- return findings classified as Critical, Warning, or Suggestion, each with file/line evidence and a concrete fix
- stay stack-neutral on ORM and auth strategy while respecting existing project conventions

### `nestjs-development`

This skill is aimed at designing, scaffolding, implementing, refactoring, or debugging NestJS code that needs to be idiomatic, secure, testable, and consistent with the project's existing conventions.

It helps an assistant:

- restate intent and acceptance criteria, then walk a feature-module-first build workflow
- apply architecture principles such as thin controllers, fat services, explicit DI, validation at the edge, typed errors, and configuration over code
- use idiomatic patterns for modules, controllers, services, DTOs, custom decorators, global pipes/filters/interceptors at bootstrap, config validation, and unit tests with `@nestjs/testing`
- avoid common anti-patterns such as `new`-ing `@Injectable()` services, `any` on DTOs, hardcoded secrets, and `synchronize: true` in production
- prefer additive, reversible changes and call out breaking changes explicitly

### `review-cycle-gatekeeper`

This skill is aimed at pull requests and change reviews that have already gone through one or more fix cycles and need a clear, evidence-backed merge gate decision.

It helps an assistant:

- normalize findings into explicit states (`fixed`, `owned-with-remediation-plan`, `waived-with-rationale`, `open`)
- enforce severity-aware closure rules so unresolved high-risk findings cannot be merged silently
- require verification evidence for functional fixes and highlight missing proof
- track regressions introduced during fix rounds as first-class findings
- validate waiver quality and ownership/remediation metadata
- return a compact `pass`, `fail`, or `BLOCK` gate summary with exact blockers to clear

### `multi-lens-review`

This skill is aimed at changes that span more than one concern (correctness, security, data, UX, ops) and need several review perspectives reconciled into a single merge decision, rather than a single-lens check that an existing focused skill already covers.

It helps an assistant:

- walk a target through Intent / Spec, Design, Implementation, Security & Privacy, Adversarial, and Verification lenses, skipping any lens that does not add value
- delegate to focused skills such as `adversarial-review`, `ssrf-outbound-fetch-review`, or `nestjs-code-review` when a lens falls squarely in their scope
- record findings with severity, confidence, classification, concrete trigger, evidence, and suggested fix, separated from one-line per-lens summaries
- run an explicit Synthesis step to deduplicate, reconcile lens conflicts by naming the winning tradeoff, and split required actions from follow-ups
- emit a `BLOCK`, `CONCERNS`, or `CLEAN` verdict with residual risk
- avoid role-playing independent reviewers, applying every lens by default, or hiding conflicts behind silent consensus

### `test-gap-to-test-plan`

This skill is aimed at the step that comes after a review skill has produced findings: turning those findings into a concrete, prioritized, owned test plan that a merge gate can verify. It consumes upstream review output rather than re-judging it, and stays stack-neutral so it can sit behind `adversarial-review`, `multi-lens-review`, or an external review.

It helps an assistant:

- consume findings with severity from any of three declared vocabularies — the 4-level `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` scheme from `adversarial-review`, the 3-level `High` / `Medium` / `Low` scheme from `review-cycle-gatekeeper`, or the `Critical` / `Warning` / `Suggestion` rubric — and map them to `must-have` / `should-have` / `nice-to-have` priority
- restate each finding as one specific unverified behavior before proposing a test
- pick the smallest faithful test layer (unit, integration, or e2e) and record it on the case
- write each case against a fixed template covering finding reference, target suite, scenario, input/setup, expected behavior, failure signal, layer, priority, owner, and status
- group cases by finding rather than by file so traceability survives deduplication
- record live-system or production-data dependencies under `Untestable risks` instead of forcing them into the plan
- return `BLOCK`, `PLAN-PARTIAL`, or `PLAN-READY` so the result feeds directly into `review-cycle-gatekeeper` Gate Rule 4 once the plan's `must-have` cases are `landed`, and plans the test coverage that `adversarial-review` `Adversarial tests` / `verification-gap` findings call for rather than closing them on the strength of a proposed plan
- refuse to fabricate findings, severities, or owners; emit `BLOCK` when required input context is missing

## Skill Format

Each skill file follows the same high-level pattern:

1. YAML frontmatter for metadata such as name, description, and invocation hints.
2. A task-focused body describing when to use the skill.
3. Concrete procedures, checklists, and expected outputs.

The current skills use frontmatter fields such as:

- `name`
- `description`
- `argument-hint`
- `user-invocable`

## How To Use

Use this repository as:

- a source of reusable skill definitions
- a reference for writing additional task-specific AI skills
- a place to keep security and review workflows in a consistent format

When adding a new skill, prefer:

- one directory per skill under `skills/`
- a single `SKILL.md` entry point
- a narrow, well-defined trigger condition
- concrete checklists and output expectations instead of generic advice

## Next Additions

Natural follow-ups for this repository would be more narrowly scoped engineering skills in adjacent areas, for example request validation, egress deployment policy, language-specific secure coding workflows, or review-specific secure coding workflows.
