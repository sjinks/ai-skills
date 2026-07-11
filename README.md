# ai-skills

Small repository of reusable AI assistant skills.

Each skill is stored as a Markdown document with YAML frontmatter and is intended to give an assistant a focused workflow, checklist, and output format for a specific engineering task.

## Repository Structure

```text
skills/
  <skill-name>/
    README.md   # overview and links for this skill
    SKILL.md    # the full skill definition
```

## Skills

The repository currently contains the following skills, grouped by area. Each links to its own README; the full definition lives in that skill's `SKILL.md`.

### Requirements & Specification

- [`acceptance-criteria-quality`](skills/acceptance-criteria-quality/README.md) — Writing, rewriting, and auditing acceptance criteria against a five-property contract — testable, observable, single, scoped, and implementation-neutral — plus a five-category coverage check, so each criterion can be objectively verified before work starts.
- [`requirements-ambiguity-audit`](skills/requirements-ambiguity-audit/README.md) — Auditing draft specs, requirements, and user stories for ambiguity across eight classes — vague quantifiers, undefined terms, missing actors, conflicting requirements, placeholders, unspecified paths, ambiguous references, and untestable wording — with quotes, plausible readings, and proposed rewrites.
- [`requirement-sharpening`](skills/requirement-sharpening/README.md) — Making requirements buildable and decidable rather than merely well-formed across six checks — measured threshold plus named method, no deferred behavior, implementation-decoupled wording, discriminating MUST/SHOULD/MAY ranking, a leaned-on-dependency completeness matrix, and a bidirectional traceability invariant — preserving every stable ID.
- [`scope-boundary-definition`](skills/scope-boundary-definition/README.md) — Making a work item's boundaries explicit before planning: in-scope, out-of-scope, non-goal, and deferred lists, a smallest valuable slice, surfaced boundary decisions, and scope-creep risks with pre-empting boundary statements.
- [`assumption-surfacing`](skills/assumption-surfacing/README.md) — Sweeping a spec, plan, design, or estimate for implicit assumptions across data, ordering, scale, auth-context, environment, compatibility, dependency-behavior, and people-process categories, classifying each as verify-before-build or accept-with-risk.
- [`spec-edge-case-enumeration`](skills/spec-edge-case-enumeration/README.md) — Sweeping a feature spec across eight edge-case dimensions — empty/boundary, error paths, permissions, concurrency, time, locale and text, limits, and lifecycle — and separating spec decisions from implementation details and deep-review flags.
- [`spec-deviation-handling`](skills/spec-deviation-handling/README.md) — The moment implementation discovers the spec is wrong, incomplete, ambiguous, or infeasible mid-build: six deviation classes, proceed/pause/escalate dispositions with conservative tie-breaks, interim behavior, and spec-fix requests instead of silent divergence.
- [`implementation-task-decomposition`](skills/implementation-task-decomposition/README.md) — Decomposing an approved spec or design into ordered, independently verifiable implementation steps — per-step scope, verification check, do-not-touch boundary, dependencies, and risk — with vague material routed to blocked-on questions.

### Architecture & Design

- [`architecture-decision-record`](skills/architecture-decision-record/README.md) — Writing, rewriting, and auditing architecture decision records against an eight-field contract — title, status, context, decision drivers, real options with costs, decision, positive and negative consequences, and revisit triggers — so decisions stay reconstructible.
- [`architecture-tradeoff-analysis`](skills/architecture-tradeoff-analysis/README.md) — Comparing candidate architectures against weighted quality attributes with a strong/adequate/weak/unknown score table, mandatory per-option costs, constraint-based elimination, evidence needs, and a recommendation or deciding question — never a decision made for the owner.
- [`interface-contract-design`](skills/interface-contract-design/README.md) — Designing or auditing a boundary's contract before implementation — per-operation inputs, outputs, distinguishable errors, idempotency, and side effects, plus boundary-level ordering, versioning posture, and single-owner invariants — with implementation leakage flagged and open choices routed to the owner.
- [`dependency-choice-review`](skills/dependency-choice-review/README.md) — Design-time build-vs-adopt decisions on libraries, frameworks, services, and platforms across six dimensions — maintenance health, API stability, fit, lock-in and exit, operational burden, license and policy — with exit paths, evidence needs, and reversal triggers.
- [`failure-mode-design`](skills/failure-mode-design/README.md) — Deciding failure behavior at design time: sweeping each component→dependency edge across slow, down, wrong, and partial failure shapes, assigning one degradation policy per edge with a concrete blast radius and observability signal, and settling idempotency under retry for every mutating flow.
- [`type-safe-design`](skills/type-safe-design/README.md) — Designing, reviewing, refactoring, and test-planning type-safe architecture where contracts, validation states, generics, reflection, factories, and compiler feedback affect correctness and change locality.
- [`data-migration-safety`](skills/data-migration-safety/README.md) — Planning or auditing schema and data migration implementations: expand-contract phases, idempotent batched backfills, concurrent-write accounting, per-phase rollback and verification, consumer switch mapping, and a labeled point-of-no-return.

### Code Review & Quality

- [`adversarial-review`](skills/adversarial-review/README.md) — Challenging specs, designs, implementations, workflows, and test plans with evidence-based failure-mode review and risk-focused verification.
- [`multi-lens-review`](skills/multi-lens-review/README.md) — Structuring a multi-lens review (intent, design, implementation, security, adversarial, verification) and synthesizing the lens findings into a single integrated decision with required actions and residual risk.
- [`single-pass-review-completeness`](skills/single-pass-review-completeness/README.md) — Making one review round complete by construction: enumerate eight review dimensions up front, sweep the whole diff per dimension, and declare covered, skipped, and gapped coverage explicitly.
- [`review-finding-quality`](skills/review-finding-quality/README.md) — Writing, rewriting, and auditing review findings against a five-field contract — severity, anchor, problem, fix direction, and an objective `Resolved when` acceptance condition — so each finding closes in one round.
- [`review-cycle-gatekeeper`](skills/review-cycle-gatekeeper/README.md) — Enforcing review/fix cycle closure gates so findings are explicitly resolved, verified, owned, or waived before merge.
- [`review-disagreement-resolution`](skills/review-disagreement-resolution/README.md) — Resolving stalled reviewer-author disputes by classifying each part as fact, standard, or preference, anchoring it to a verifiable source, and applying a decision rule that ends review-thread ping-pong.
- [`pr-scope-slicer`](skills/pr-scope-slicer/README.md) — Deciding whether a change set is too large or mixed to review in one pass and planning ordered, independently reviewable slices along mechanical/semantic, refactor/behavior, dependency, subsystem, and risk axes.
- [`pre-review-self-audit`](skills/pre-review-self-audit/README.md) — Author-side pre-review self-checks covering diff hygiene, scope, tests, contracts, commit atomicity, description accuracy, discovered project checks, reviewer anticipation, and repeated-pattern consistency, so the predictable first review round disappears.
- [`commit-message-quality`](skills/commit-message-quality/README.md) — Drafting, rewriting, validating, or auditing one git commit message against a subject/body/footer contract — conventional-by-default subject grammar, a why-focused body, clean trailers, and no leaked secrets — returning a verdict, the detected mode, and per-part checks.
- [`pr-description-quality`](skills/pr-description-quality/README.md) — Drafting, rewriting, validating, or auditing one pull request's title and body against a contract — a PR-level title, a what/why body with honest testing notes, linked issues, and explicit risks — honoring the repo's PR template when present, returning a verdict, the detected structure, and per-part checks.
- [`commit-hygiene`](skills/commit-hygiene/README.md) — Cleaning up a branch's commit history before review or merge — squashing fixup/WIP commits, dropping dead or accidental commits, splitting mixed commits, and reordering for bisectability — returning a recommend-only rebase plan, per-commit actions, and shared-branch/backup cautions, never running git itself.
- [`fix-batching-and-root-cause`](skills/fix-batching-and-root-cause/README.md) — Planning a fix batch over review findings by clustering findings with an evidenced shared cause, choosing root-cause versus justified symptom-level fix depth, and ordering fixes so the next review round is the last one.
- [`fix-blast-radius`](skills/fix-blast-radius/README.md) — Assessing what a drafted fix could newly break before it is pushed, tracing impact across callers, shared state, contracts, behavioral siblings, and previously resolved findings, with one verification step per risk.
- [`equivalence-class-audit`](skills/equivalence-class-audit/README.md) — Turning one concrete defect, incident, review finding, test failure, or bug report into a locked-scope audit of equivalent defects across sibling fields, mirror use sites, bounds, contracts, paths, modes, tests, docs, and projections.
- [`test-gap-to-test-plan`](skills/test-gap-to-test-plan/README.md) — Converting review findings and unverified behaviors into a prioritized, owned, layer-typed test plan that tracks the test evidence a downstream merge gate will require.
- [`test-quality-review`](skills/test-quality-review/README.md) — Auditing an individual test (not a test plan) for quality: whether it can fail for one behavioral reason, targets observable behavior over incidental detail, is deterministic and isolated, and covers the negative/boundary paths it claims, returning a per-test `solid`/`weak`/`cannot-fail` verdict.

### Debugging & Refactoring

- [`hypothesis-driven-debugging`](skills/hypothesis-driven-debugging/README.md) — Disciplined failure investigation: reproduce first, falsifiable mechanism hypotheses, one-variable discriminating experiments with recorded verdicts, a root-cause-versus-symptom call, and a regression check before any fix counts as done.
- [`refactoring-safety`](skills/refactoring-safety/README.md) — Behavior-preserving refactors: characterization coverage before touching code, one named transformation per step with a green check after each, separated mechanical and hand edits, and a stop-and-reclassify tripwire when behavior shifts.
- [`flaky-test-diagnosis`](skills/flaky-test-diagnosis/README.md) — Turning a non-deterministic test deterministic by root-causing why it fails: reproduce with repeat/shuffle/parallel/sanitizer runs, classify against a symptom→cause→fix table, separate a test bug from a real code race/leak, and fix at the source rather than by sleep/retry/disable.
- [`perf-measurement`](skills/perf-measurement/README.md) — Making C++ server/hot-path performance work empirical: choosing a noise-resistant metric for the change size, counting allocations directly, isolating layer cost with control servers, profiling and bucketing under load, and changing one thing then re-measuring — recording negative results and avoiding known no-op "fixes".

### Security Review

- [`web-app-security-review`](skills/web-app-security-review/README.md) — Defensive web application security review of code, PRs, designs, vulnerability reports, and fixes across access control, auth, browser, API, data-flow, supply-chain, cloud, and abuse-risk surfaces.
- [`ssrf-outbound-fetch-review`](skills/ssrf-outbound-fetch-review/README.md) — Reviewing, designing, implementing, and testing SSRF protections around outbound HTTP fetches, from egress policy contracts through transport and redirect behavior.
- [`filesystem-path-safety`](skills/filesystem-path-safety/README.md) — Auditing external-input filesystem path construction under trusted roots, including traversal, symlink, TOCTOU, containment, and mutation-safety checks.
- [`archive-extraction-safety`](skills/archive-extraction-safety/README.md) — Reviewing safe ZIP/TAR/archive extraction, including traversal, symlinks, hardlinks, absolute and Windows paths, Unicode normalization, decompression limits, nested archives, permissions, overwrite policy, containment, cleanup, and parser mismatch.
- [`auth-claim-contract-review`](skills/auth-claim-contract-review/README.md) — Reviewing auth/security claim contracts across JWT, OIDC, SAML, token, and session flows, including optional claims, missing-vs-invalid semantics, issuer-validator-consumer drift, authorization mapping, propagation, serialization, revocation, freshness, fallback defaults, and confused-deputy risks.
- [`unicode-text-security-review`](skills/unicode-text-security-review/README.md) — Reviewing security-sensitive Unicode text handling, including strict UTF-8 decoding, overlong and surrogate rejection, NFC/NFKC normalization order, canonical and compatibility equivalence, byte-vs-character validation drift, identifier spoofing, confusables, storage/index drift, length/truncation units, decode-layer ordering, and display injection.
- [`dependency-audit`](skills/dependency-audit/README.md) — Auditing application and tooling dependencies for known vulnerabilities, license risk, maintenance health, abandoned packages, unused dependencies, dependency bloat, transitive risk, and supply-chain integrity.

### C++

- [`boost-asio`](skills/boost-asio/README.md) — Designing, implementing, reviewing, debugging, and testing Boost.Asio async I/O, executors, strands, timers, sockets, cancellation, backpressure, TLS streams, and coroutine flows.
- [`boost-beast`](skills/boost-beast/README.md) — Boost.Beast HTTP/WebSocket parser, serializer, body, stream, TLS, protocol-adapter, limits, strictness, lifecycle, and testing work.
- [`cmake-build-review`](skills/cmake-build-review/README.md) — Reviewing target-based CMake builds, including PUBLIC/PRIVATE/INTERFACE propagation, find_package vs FetchContent policy, install/export and package config correctness, generator expressions, multi-config behavior, and sanitizer/LTO/warning configuration.
- [`cpp-api-abi-review`](skills/cpp-api-abi-review/README.md) — Reviewing C++ library public headers and binary interfaces, including ABI stability classification, ODR risk from inlined code, noexcept contracts, extern "C" boundaries, symbol visibility, and versioning/migration mechanisms.
- [`cpp-cert`](skills/cpp-cert/README.md) — Reviewing C/C++ for SEI CERT secure-coding violations via the clang-tidy `cert-*` catalog, including std-namespace modification, unchecked return values, exception and throw/catch safety, raw memory ops on non-trivial types, polymorphic pointer arithmetic, signal-handler safety, predictable RNGs, and command injection.
- [`cpp-concurrency-review`](skills/cpp-concurrency-review/README.md) — Reviewing C++ multithreaded code using standard primitives, including data races, lock ordering and deadlock, condition-variable protocols, atomic memory ordering, thread lifecycle, cross-thread observer/callback dispatch, and shutdown semantics.
- [`cpp-const-correctness`](skills/cpp-const-correctness/README.md) — Resolving clang-tidy `misc-const-correctness` findings on never-mutated local variables (value, reference, and pointer locals), with correct qualifier placement, scope exclusions (parameters, members, globals), and return-move conflict handling.
- [`cpp-correctness-review`](skills/cpp-correctness-review/README.md) — Reviewing bounded C/C++ operation correctness: wrong conditions, invalid state transitions, off-by-one behavior, signed/unsigned mistakes, truncation, size calculations, single-threaded iterator misuse, partial operation handling, stale derived state, overload mistakes, boundary cases, and test/implementation contradictions.
- [`cpp-coroutines`](skills/cpp-coroutines/README.md) — C++20 coroutine types, promises, awaiters, handles, generators, frame lifetime, scheduler bridges, cancellation, symmetric transfer, allocation behavior, and tests.
- [`cpp-data-structure-selection`](skills/cpp-data-structure-selection/README.md) — Choosing or replacing the C++ container behind a lookup, membership test, dedup, ordering, or accumulation so work scales with input size: naming the asymptotic shape, matching structure to the dominant operation, respecting the small-N crossover, preserving ordering/stability/duplicate/reference guarantees, and gating hot-path swaps on measurement.
- [`cpp-error-handling-design`](skills/cpp-error-handling-design/README.md) — C++ error policy and exception safety, including exceptions vs `std::expected` vs error codes, basic/strong/nothrow guarantees, commit-rollback, `noexcept` and move interactions, destructor rules, and error propagation across module, ABI, thread, and coroutine boundaries.
- [`cpp-object-lifetime`](skills/cpp-object-lifetime/README.md) — Reviewing C++ object lifetime and ownership, including dangling pointers/references/views, iterator and reference invalidation, lambda capture lifetime, use-after-move, smart-pointer boundaries, and async handoff safety.
- [`cpp-openssl`](skills/cpp-openssl/README.md) — Designing, implementing, reviewing, and debugging C/C++ that calls the OpenSSL (or LibreSSL/BoringSSL) library API directly: fail-closed `SSL_CTX` policy, peer and hostname verification, object lifetime/refcounts, `SSL_get_error` IO and error-queue handling, `EVP` AEAD/KDF/RAND crypto, secret zeroization, and 1.1.1-vs-3.x portability. Not the `openssl(1)` CLI.
- [`cpp-performance`](skills/cpp-performance/README.md) — Reviewing C++ runtime cost via the clang-tidy `performance-*` catalog, including unnecessary copies, expensive value parameters, range-for copies, misused `std::move`, missing `noexcept` on move/swap, missing `reserve`, and inefficient container/string/algorithm operations.
- [`cpp-sanitizer-triage`](skills/cpp-sanitizer-triage/README.md) — Triaging ASan/TSan/UBSan/MSan/LSan reports, including report anatomy, root cause vs symptom separation, true-positive vs tool-limitation vs configuration-artifact classification, suppression-file discipline, and sanitizer build/runtime configuration.
- [`cpp-server-hardening-review`](skills/cpp-server-hardening-review/README.md) — Reviewing C++ network servers for safe-by-default behavior under untrusted load: first-request and idle timeouts, connection caps with accept-shed backpressure, guaranteed once-only per-connection teardown (including TLS handshake failure), the install-after-teardown leak class, bounded per-id caches, fail-closed TLS/verification defaults, and read-time bound enforcement.
- [`cpp-struct-layout`](skills/cpp-struct-layout/README.md) — Reviewing C/C++ class/struct/union member layout to remove padding waste by reordering members from largest to smallest alignment, computing before/after `sizeof`, and withholding reorders for ABI/wire-format/C-interop frozen layouts.

### NestJS

- [`nestjs-code-review`](skills/nestjs-code-review/README.md) — Reviewing NestJS applications with severity-classified findings covering modules, DI, controllers, DTOs, guards, exception handling, persistence, test changes, API design, performance, and microservices.
- [`nestjs-development`](skills/nestjs-development/README.md) — Designing, scaffolding, implementing, and refactoring NestJS features (including the test setup that ships with a feature) with idiomatic patterns, anti-patterns, and a structured build workflow; dedicated test design lives in `nestjs-testing`.
- [`nestjs-testing`](skills/nestjs-testing/README.md) — Designing test strategy and writing tests for NestJS: unit/integration/e2e layering, `@nestjs/testing` modules, provider and guard overrides, repository mocks, Supertest e2e, async and error paths, and coverage gaps.
- [`nestjs-version-upgrade`](skills/nestjs-version-upgrade/README.md) — Planning and executing NestJS version upgrades and major migrations: ordered reversible steps, breaking-change triage, peer and adapter sequencing, and per-step verification.

### Authoring & Verification

- [`agent-skill-audit`](skills/agent-skill-audit/README.md) — Holistic readiness audit of agent instructions, Agent Skills, custom-agent prompts, and instruction packages across discovery/delegation, instruction architecture, operational completeness, model/runtime portability, and maintainability/evaluability, with readiness ratings and a final verdict.
- [`instruction-quality-audit`](skills/instruction-quality-audit/README.md) — High-confidence diagnostic audit of AI instruction artifacts and packages for contradictions, precedence gaps, ambiguity, authority and side-effect conflicts, closure and failure-handling gaps, harmful duplication or cognitive burden, output-contract defects, and trusted custom diagnostics.
- [`cross-model-instruction-authoring`](skills/cross-model-instruction-authoring/README.md) — Creating, revising, and adapting Agent Skills, custom agent prompts, subagent instructions, and related instruction packages so they keep a model-neutral core, use runtime-specific adapters only where needed, and stay usable across smaller and frontier models without overconstraining implementation strategy.
- [`source-to-skill`](skills/source-to-skill/README.md) — Converting books, articles, documentation, notes, transcripts, and other source material into reusable agent skills with extraction, rights, provenance, and validation gates. Inspired by [book-to-skill](https://github.com/virgiliojr94/book-to-skill/blob/master/SKILL.md).
- [`factcheck`](skills/factcheck/README.md) — Verifying factual claims, citations, drafts, source support, evidence quality, verdicts, confidence, correction proposals, and uncertainty in report-only-first mode.
- [`doc-source-reconciliation`](skills/doc-source-reconciliation/README.md) — Verifying that a doc claiming to reflect the current implementation actually matches it across six fact classes — file names and extensions, target/example names, dependency lists, public type/option/enumerator names, volatile counts, and behavioral defaults — marking each match/stale/unverifiable with file evidence and stabilizing literals that would rot again.
- [`artifact-consolidation`](skills/artifact-consolidation/README.md) — Merging several same-kind planning artifacts (specs, architectures, or test plans) into one without losing or renumbering any stable ID: per-source concern namespaces, collision resolution by prefixing, a single deduplicated open-questions ledger, and superseded sources marked for removal only with explicit approval.
- [`handoff-note`](skills/handoff-note/README.md) — Creating portable handoff documents for another agent or person to continue active work with little or no prior context, preserving current state, completed work, failed attempts not to repeat, next steps, constraints, validation evidence, and open questions; not for general onboarding, status reports, changelogs, or PR summaries unless active continuation is required.

### Platform & Tooling

- [`gh-cli`](skills/gh-cli/README.md) — Running GitHub CLI (`gh`) commands correctly: `gh api` `-f` vs `-F` field flags, posting/editing PR/issue comments and review-thread replies, multi-line/special-character bodies via stdin or `--body-file`, pagination, and jq filtering, avoiding silent wrong-output from quoting or stdin mistakes.
- [`shell-portability`](skills/shell-portability/README.md) — Writing, reviewing, or fixing shell scripts that must run across multiple shells and OSes (POSIX sh vs bash/ksh/zsh, dash/busybox, GNU vs BSD/macOS coreutils), catching bashisms, non-portable utility flags, shebang mismatches, and locale/word-splitting hazards with portable replacements.
- [`vip-dev-env`](skills/vip-dev-env/README.md) — WordPress VIP Local Development Environment (LDE) workflows using `vip dev-env`, including creating and updating local environments, loading app code, inspecting services and logs, slug-first and message-driven troubleshooting of startup and HTTP 500 failures, Docker triage and escalation, and the local-repo-vs-container code boundary.

### Conversational Style

- [`spock-voice`](skills/spock-voice/README.md) — Adopting a Spock-inspired, precise, analytical, restrained, and lightly dry conversational register.

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
