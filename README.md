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

- `agent-skill-audit`: guidance for auditing agent instructions, skill files, `SKILL.md` artifacts, prompt-packaged workflows, and AI assistant instruction artifacts for consistency, cohesion, coherence, completeness, and weaker-model suitability.
- `adversarial-review`: guidance for challenging specs, designs, implementations, workflows, and test plans with evidence-based failure-mode review and risk-focused verification.
- `acceptance-criteria-quality`: guidance for writing, rewriting, and auditing acceptance criteria against a five-property contract — testable, observable, single, scoped, and implementation-neutral — plus a five-category coverage check, so each criterion can be objectively verified before work starts.
- `architecture-decision-record`: guidance for writing, rewriting, and auditing architecture decision records against an eight-field contract — title, status, context, decision drivers, real options with costs, decision, positive and negative consequences, and revisit triggers — so decisions stay reconstructible.
- `architecture-tradeoff-analysis`: guidance for comparing candidate architectures against weighted quality attributes with a strong/adequate/weak/unknown score table, mandatory per-option costs, constraint-based elimination, evidence needs, and a recommendation or deciding question — never a decision made for the owner.
- `archive-extraction-safety`: guidance for reviewing safe ZIP/TAR/archive extraction, including traversal, symlinks, hardlinks, absolute and Windows paths, Unicode normalization, decompression limits, nested archives, permissions, overwrite policy, containment, cleanup, and parser mismatch.
- `assumption-surfacing`: guidance for sweeping a spec, plan, design, or estimate for implicit assumptions across data, ordering, scale, auth-context, environment, compatibility, dependency-behavior, and people-process categories, classifying each as verify-before-build or accept-with-risk.
- `auth-claim-contract-review`: guidance for reviewing auth/security claim contracts across JWT, OIDC, SAML, token, and session flows, including optional claims, missing-vs-invalid semantics, issuer-validator-consumer drift, authorization mapping, propagation, serialization, revocation, freshness, fallback defaults, and confused-deputy risks.
- `boost-asio`: guidance for designing, implementing, reviewing, debugging, and testing Boost.Asio async I/O, executors, strands, timers, sockets, cancellation, backpressure, TLS streams, and coroutine flows.
- `boost-beast`: guidance for Boost.Beast HTTP/WebSocket parser, serializer, body, stream, TLS, protocol-adapter, limits, strictness, lifecycle, and testing work.
- `cmake-build-review`: guidance for reviewing target-based CMake builds, including PUBLIC/PRIVATE/INTERFACE propagation, find_package vs FetchContent policy, install/export and package config correctness, generator expressions, multi-config behavior, and sanitizer/LTO/warning configuration.
- `cpp-api-abi-review`: guidance for reviewing C++ library public headers and binary interfaces, including ABI stability classification, ODR risk from inlined code, noexcept contracts, extern "C" boundaries, symbol visibility, and versioning/migration mechanisms.
- `cpp-concurrency-review`: guidance for reviewing C++ multithreaded code using standard primitives, including data races, lock ordering and deadlock, condition-variable protocols, atomic memory ordering, thread lifecycle, and shutdown semantics.
- `cpp-coroutines`: guidance for C++20 coroutine types, promises, awaiters, handles, generators, frame lifetime, scheduler bridges, cancellation, symmetric transfer, allocation behavior, and tests.
- `cpp-error-handling-design`: guidance for C++ error policy and exception safety, including exceptions vs `std::expected` vs error codes, basic/strong/nothrow guarantees, commit-rollback, `noexcept` and move interactions, destructor rules, and error propagation across module, ABI, thread, and coroutine boundaries.
- `cpp-object-lifetime`: guidance for reviewing C++ object lifetime and ownership, including dangling pointers/references/views, iterator and reference invalidation, lambda capture lifetime, use-after-move, smart-pointer boundaries, and async handoff safety.
- `cpp-sanitizer-triage`: guidance for triaging ASan/TSan/UBSan/MSan/LSan reports, including report anatomy, root cause vs symptom separation, true-positive vs tool-limitation vs configuration-artifact classification, suppression-file discipline, and sanitizer build/runtime configuration.
- `dependency-audit`: guidance for auditing application and tooling dependencies for known vulnerabilities, license risk, maintenance health, abandoned packages, unused dependencies, dependency bloat, transitive risk, and supply-chain integrity.
- `dependency-choice-review`: guidance for design-time build-vs-adopt decisions on libraries, frameworks, services, and platforms across six dimensions — maintenance health, API stability, fit, lock-in and exit, operational burden, license and policy — with exit paths, evidence needs, and reversal triggers.
- `equivalence-class-audit`: guidance for turning one concrete defect, incident, review finding, test failure, or bug report into a locked-scope audit of equivalent defects across sibling fields, mirror use sites, bounds, contracts, paths, modes, tests, docs, and projections.
- `factcheck`: guidance for verifying factual claims, citations, drafts, source support, evidence quality, verdicts, confidence, correction proposals, and uncertainty in report-only-first mode.
- `failure-mode-design`: guidance for deciding failure behavior at design time: sweeping each component→dependency edge across slow, down, wrong, and partial failure shapes, assigning one degradation policy per edge with a concrete blast radius and observability signal, and settling idempotency under retry for every mutating flow.
- `fix-batching-and-root-cause`: guidance for planning a fix batch over review findings by clustering findings with an evidenced shared cause, choosing root-cause versus justified symptom-level fix depth, and ordering fixes so the next review round is the last one.
- `fix-blast-radius`: guidance for assessing what a drafted fix could newly break before it is pushed, tracing impact across callers, shared state, contracts, behavioral siblings, and previously resolved findings, with one verification step per risk.
- `instruction-quality-audit`: guidance for auditing AI instruction artifacts, prompts, prompt templates, LLM task prompts, agent instructions, skill files, `SKILL.md` artifacts, prompt-packaged workflows, custom agent modes, and reusable assistant guidance for contradictions, ambiguity, persona issues, cognitive load, duplication, semantic coverage gaps, missing error handling, and custom diagnostics.
- `interface-contract-design`: guidance for designing or auditing a boundary's contract before implementation — per-operation inputs, outputs, distinguishable errors, idempotency, and side effects, plus boundary-level ordering, versioning posture, and single-owner invariants — with implementation leakage flagged and open choices routed to the owner.
- `web-app-security-review`: guidance for defensive web application security review of code, PRs, designs, vulnerability reports, and fixes across access control, auth, browser, API, data-flow, supply-chain, cloud, and abuse-risk surfaces.
- `filesystem-path-safety`: guidance for auditing external-input filesystem path construction under trusted roots, including traversal, symlink, TOCTOU, containment, and mutation-safety checks.
- `ssrf-outbound-fetch-review`: guidance for reviewing, designing, implementing, and testing SSRF protections around outbound HTTP fetches, from egress policy contracts through transport and redirect behavior.
- `spock-voice`: guidance for adopting a Spock-inspired, precise, analytical, restrained, and lightly dry conversational register.
- `nestjs-code-review`: guidance for reviewing NestJS applications with severity-classified findings covering modules, DI, controllers, DTOs, guards, exception handling, persistence, testing, API design, performance, and microservices.
- `nestjs-development`: guidance for designing, scaffolding, implementing, refactoring, and testing NestJS features with idiomatic patterns, anti-patterns, and a structured build workflow.
- `pr-scope-slicer`: guidance for deciding whether a change set is too large or mixed to review in one pass and planning ordered, independently reviewable slices along mechanical/semantic, refactor/behavior, dependency, subsystem, and risk axes.
- `pre-review-self-audit`: guidance for author-side pre-review self-checks covering diff hygiene, scope, tests, contracts, commit atomicity, description accuracy, discovered project checks, and reviewer anticipation, so the predictable first review round disappears.
- `requirements-ambiguity-audit`: guidance for auditing draft specs, requirements, and user stories for ambiguity across eight classes — vague quantifiers, undefined terms, missing actors, conflicting requirements, placeholders, unspecified paths, ambiguous references, and untestable wording — with quotes, plausible readings, and proposed rewrites.
- `review-cycle-gatekeeper`: guidance for enforcing review/fix cycle closure gates so findings are explicitly resolved, verified, owned, or waived before merge.
- `review-disagreement-resolution`: guidance for resolving stalled reviewer-author disputes by classifying each part as fact, standard, or preference, anchoring it to a verifiable source, and applying a decision rule that ends review-thread ping-pong.
- `review-finding-quality`: guidance for writing, rewriting, and auditing review findings against a five-field contract — severity, anchor, problem, fix direction, and an objective `Resolved when` acceptance condition — so each finding closes in one round.
- `scope-boundary-definition`: guidance for making a work item's boundaries explicit before planning: in-scope, out-of-scope, non-goal, and deferred lists, a smallest valuable slice, surfaced boundary decisions, and scope-creep risks with pre-empting boundary statements.
- `single-pass-review-completeness`: guidance for making one review round complete by construction: enumerate eight review dimensions up front, sweep the whole diff per dimension, and declare covered, skipped, and gapped coverage explicitly.
- `spec-edge-case-enumeration`: guidance for sweeping a feature spec across eight edge-case dimensions — empty/boundary, error paths, permissions, concurrency, time, locale and text, limits, and lifecycle — and separating spec decisions from implementation details and deep-review flags.
- `multi-lens-review`: guidance for structuring a multi-lens review (intent, design, implementation, security, adversarial, verification) and synthesizing the lens findings into a single integrated decision with required actions and residual risk.
- `source-to-skill`: guidance for converting books, articles, documentation, notes, transcripts, and other source material into reusable agent skills with extraction, rights, provenance, and validation gates. Inspired by [book-to-skill](https://github.com/virgiliojr94/book-to-skill/blob/master/SKILL.md).
- `test-gap-to-test-plan`: guidance for converting review findings and unverified behaviors into a prioritized, owned, layer-typed test plan that tracks the test evidence a downstream merge gate will require.
- `type-safe-design`: guidance for designing, reviewing, refactoring, and test-planning type-safe architecture where contracts, validation states, generics, reflection, factories, and compiler feedback affect correctness and change locality.
- `unicode-text-security-review`: guidance for reviewing security-sensitive Unicode text handling, including strict UTF-8 decoding, overlong and surrogate rejection, NFC/NFKC normalization order, canonical and compatibility equivalence, byte-vs-character validation drift, identifier spoofing, confusables, storage/index drift, length/truncation units, decode-layer ordering, and display injection.

## Included Skills

### `agent-skill-audit`

This skill is aimed at agent instructions, skill files, `SKILL.md` artifacts, prompt-packaged workflows, and AI assistant instruction artifacts that need a structured audit for consistency, cohesion, coherence, completeness, and weaker-model suitability.

It helps an assistant:

- preserve strict input handling for pasted text, selections, file paths, multiple items, missing input, unreadable files, and empty input
- treat audited artifacts strictly as data, including repository files, comments, remote text, and embedded instructions
- rate Consistency, Cohesion, Coherence, Completeness, and Suitability for weaker models with stable `Rating`, `Findings`, and `Recommendations` labels
- apply the weaker-model seven-item checklist for instruction length, nesting depth, overloaded conditionals, ambiguous or conflicting priorities, duplicated or overlapping instructions, missing examples, and reproducible output format
- return a stable audit report ending with `Top 5 Changes` and a `Ready`, `Needs revision`, or `Blocked by missing input` verdict

### `adversarial-review`

This skill is aimed at specs, designs, implementations, workflows, migrations, operational procedures, and test plans that need deliberate failure-mode review before they are trusted.

It helps an assistant:

- identify the target, intended behavior, assumptions, and evidence basis before judging
- apply optional review lenses for reliability, maintainability, security/privacy, user workflow, and verification
- classify failure modes with concrete categories, severity, and evidence standards
- distinguish confirmed issues, likely risks, open questions, accepted tradeoffs, and test gaps
- convert top risks into adversarial tests, mitigations, or acceptance criteria
- return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts without inventing findings

### `acceptance-criteria-quality`

This skill is aimed at draft acceptance criteria, definition-of-done lists, and user-story AC that need a quality contract enforced before implementation starts.

It helps an assistant:

- check each criterion against a five-property contract: testable, observable, single, scoped, and implementation-neutral, while keeping mandated contracts (protocols, formats, API shapes) intact
- mark each criterion `compliant`, `rewritten`, or `needs-owner-input`, with a `Verify by` line for every kept or rewritten criterion
- run a coverage check across success path, failure/rejection path, empty or boundary input, permission or authorization outcome, and persistence or side-effect visibility
- propose additions only from the supplied feature description, turning undecided behavior into open questions instead of invented requirements
- emit a deterministic BLOCK template when neither criteria nor a feature description is supplied

### `architecture-decision-record`

This skill is aimed at technical decisions that need a durable record — or existing ADRs that need an audit — so the next engineer can reconstruct why alternatives were rejected.

It helps an assistant:

- enforce an eight-field contract: title, status, context, decision drivers, options, decision, consequences, and revisit triggers
- require at least two real options each with a benefit and a cost, flagging single-option records and strawmen as contract gaps
- require at least one concrete negative consequence and concrete revisit triggers
- mark inferred content `(inferred)` and route unmade choices to `### Open decisions` instead of deciding for the owner
- audit existing ADRs by restructuring them into the contract and listing every gap
- emit a deterministic BLOCK template when no decision context is supplied

### `architecture-tradeoff-analysis`

This skill is aimed at choices between candidate architectures, designs, or technical approaches that need a structured comparison before the decision is made.

It helps an assistant:

- score each option per attribute as `strong`, `adequate`, `weak`, or `unknown`, with rationale for non-adequate cells
- require every option to carry at least one `weak` or `unknown` cell and a concrete makes-worse line
- treat constraints as pass/fail eliminations rather than scores, and keep eliminated options visible in the table
- use supplied weights verbatim, mark missing weights `unstated`, and report a deciding question instead of forcing a winner
- map every `unknown` cell to the cheapest evidence that would settle it
- end with a recommendation or deciding question — the decision stays with the owner

### `archive-extraction-safety`

This skill is aimed at code and designs that extract untrusted or semi-trusted archives into a destination directory.

It helps an assistant:

- define the extraction contract, accepted formats, destination root, allowed entry types, overwrite policy, and resource limits
- review ZIP/TAR traversal, absolute paths, Windows drive/UNC paths, Unicode/path normalization, symlinks, hardlinks, special files, executable bits, permission/ownership restoration, parser mismatch, and destination containment
- check file count, decompressed size, compression ratio, nested archive depth, and partial extraction cleanup
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, tests, and residual risk

### `assumption-surfacing`

This skill is aimed at specs, plans, designs, and estimates about to be committed to, whose implicit assumptions need to become an explicit verification worklist before building starts.

It helps an assistant:

- sweep eight assumption categories: data, ordering, scale, auth-context, environment, compatibility, dependency-behavior, and people-process
- state each assumption as a falsifiable claim anchored to the plan text that depends on it
- classify each assumption as `verify-before-build` (with a verification step) or `accept-with-risk` (with the risk if wrong and the earliest signal that would reveal it)
- apply the tie-break that structural damage — schema, contract, security, data loss — forces `verify-before-build` regardless of likelihood
- produce the worklist without performing the verifications or inventing owners
- emit a deterministic BLOCK template when no plan or spec text is supplied

### `auth-claim-contract-review`

This skill is aimed at auth and security claim contracts where issuer, validator, consumer, missing-vs-invalid, propagation, or restoration behavior affects authorization or session safety.

It helps an assistant:

- map claim source, validators, consumers, and intended missing-vs-invalid semantics before judging
- review optional claims, JWT/OIDC/SAML/session/token claims, role/scope/permission/tenant/org/account mappings, origin markers, fallback defaults, and confused-deputy risks
- check serialization, cache/session restoration, token refresh, revocation, freshness, lifetime, and propagation boundaries for contract drift
- keep sensitive-data boundaries explicit by using redacted or synthetic examples instead of raw tokens, auth headers, secrets, credentials, private keys, customer PII, or private raw data
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, assumptions, unverified areas, and residual risk

### `boost-asio`

This skill is aimed at Boost.Asio networking and concurrency work where executor affinity, operation lifetime, cancellation, timeout behavior, backpressure, and deterministic shutdown matter.

It helps an assistant:

- distinguish Asio execution, transport, and cancellation concerns from Beast protocol policy and generic C++ coroutine mechanics
- design or review accept loops, socket sessions, timers, write queues, TLS streams, `co_spawn` flows, strands, thread pools, and shutdown models
- identify common async bugs such as raw `this` captures, stack-buffer lifetime, overlapping stream operations, unobserved detached coroutine failures, timeout races, and unbounded queues
- route to focused references for patterns, debugging, testing, observability, Beast/TLS integration, and migration work

### `boost-beast`

This skill is aimed at Boost.Beast HTTP and WebSocket work where parser/serializer policy, resource limits, stream ownership, EOF behavior, protocol upgrades, and security-sensitive framing need explicit handling.

It helps an assistant:

- separate Beast protocol boundaries from lower-level Asio executor concerns and generic HTTP/API design
- design or review HTTP parsers, serializers, body types, WebSocket sessions, TLS stream behavior, parser adapters, and protocol-facing tests
- enforce body/header limits, strictness gates, parser differential handling, close/drain/keep-alive policy, and request-smuggling-resistant framing decisions
- use role-specific, debugging, hardening, testing, and observability references without overloading the main skill file

### `cmake-build-review`

This skill is aimed at CMake build configuration where target structure, usage-requirement propagation, dependency sourcing, and install/export correctness determine whether builders and consumers get a working, maintainable build.

It helps an assistant:

- derive PUBLIC/PRIVATE/INTERFACE visibility from the header surface and catch over-linking and propagation leaks
- replace directory-scoped commands and global flag mutation with target-based equivalents
- consume dependencies as imported targets under an explicit find_package/FetchContent policy with version constraints
- review install/export setups: export sets, config and version files, BUILD_INTERFACE/INSTALL_INTERFACE include paths
- keep configuration logic multi-config-safe with generator expressions and make sanitizers/LTO/warnings opt-in, per-target, compile-and-link consistent
- return `BLOCK`, `CONCERNS`, or `CLEAN` with project shape, findings, checklist status, verification expectations, and an insufficient-context template

### `cpp-api-abi-review`

This skill is aimed at C++ library boundaries that other code compiles or links against, where the question is which changes break source compatibility, binary compatibility, or behavioral contracts, and how breaks are versioned.

It helps an assistant:

- identify the public/installed surface, the stated compatibility promise, and its toolchain assumptions before classifying any change
- classify changes as API-breaking, ABI-breaking, both, or neither, using accurate layout/vtable/signature rules and the safe-addition cases
- treat inline functions, templates, constexpr variables, and default arguments as compiled-into-consumers, with ODR and mixed-version analysis
- review boundary contracts: noexcept as a one-way promise, exceptions stopped at extern "C", export-macro and visibility discipline
- require a loud break mechanism (soname/major bump, inline-namespace version, symbol versioning) for every break, plus ABI-diff or link-test verification
- return `BLOCK`, `CONCERNS`, or `CLEAN` with the promise, findings, checklist status, verification expectations, and an insufficient-context template

### `cpp-concurrency-review`

This skill is aimed at C++ code that shares mutable state across threads with standard primitives, where the question is whether every access is provably ordered and shutdown is deterministic.

It helps an assistant:

- inventory shared mutable state and assign each item a named synchronization regime, then verify every access follows it
- check lock discipline: global acquisition order or `std::scoped_lock`, bounded hold times, and no calls into unknown code under locks
- verify condition-variable protocols (predicate loops under the right mutex, notify-after-change, shutdown wakes all waiters)
- review atomic protocols: acquire/release pairing, when `relaxed` is acceptable, double-checked initialization, ABA and `compare_exchange_weak` loops
- enforce thread lifecycle rules: join-on-all-paths or justified detach, explicit shutdown order, destruction races prevented by join or `weak_ptr`
- return `BLOCK`, `CONCERNS`, or `CLEAN` with shared-state inventory, findings, checklist status, test expectations, and an insufficient-context template

### `cpp-coroutines`

This skill is aimed at standalone C++20 coroutine mechanics where coroutine frame ownership, promise behavior, awaiter lifetime, scheduler interaction, exception propagation, cancellation, and allocation behavior determine correctness.

It helps an assistant:

- distinguish language-level coroutine design from Boost.Asio `awaitable` I/O flow and Beast protocol work
- design or review `task`, `generator`, custom awaiters, callback adapters, `promise_type`, `final_suspend`, continuation chaining, symmetric transfer, and custom frame allocation
- identify lifetime bugs such as dangling frames, dangling awaiters, double resume, missed resume, swallowed exceptions, detached work, and scheduler surprises
- plan deterministic tests for suspension, resumption, cancellation, early destruction, exception paths, scheduler hops, and frame-lifetime invariants

### `cpp-error-handling-design`

This skill is aimed at C++ code and APIs that must choose, implement, or review an error-reporting strategy and deliver stated exception-safety guarantees across boundaries.

It helps an assistant:

- establish an explicit error policy per layer: which channel (exceptions, `std::expected`, `std::error_code`) reports which failure class, with translation rules at boundaries
- separate recoverable failures from programming-bug contract violations and from unrepresentable states
- verify basic/strong/nothrow guarantees, requiring commit-rollback for strong claims and RAII ownership on throwing paths
- place `noexcept` deliberately on moves, swap, and destructors, including the container fallback consequences of throwing moves
- stop exceptions at `extern "C"`, thread, callback, and destructor boundaries, and carry errors across async hops with `std::exception_ptr` or `std::expected`
- enforce consumption: `[[nodiscard]]` error channels, no silent catch-and-swallow, every failure class has a consumer
- return `BLOCK`, `CONCERNS`, or `CLEAN` with the policy, findings, checklist status, failure-path test expectations, and an insufficient-context template
### `cpp-object-lifetime`

This skill is aimed at C++ code where a pointer, reference, view, iterator, or callback borrows storage owned by another object and the outlives-relationship is not enforced by construction.

It helps an assistant:

- map owners and borrowers, then check every borrow interval against moves, reallocation, container mutation, scope exit, and destruction order
- catch escaping `string_view`/`span`, references returned to locals, references held across `push_back`/`erase`, and iterator invalidation per container rules
- review lambda captures, stored callbacks, and async handoff so `this` and references cannot be used after their owners are destroyed
- enforce move-semantics discipline (moved-from objects limited to destruction, assignment, precondition-free operations, and specified post-move states) and smart-pointer ownership boundaries with `weak_ptr` cycle breaks
- return `BLOCK`, `CONCERNS`, or `CLEAN` with owners/borrowers, findings, checklist status, test expectations, and an insufficient-context template

### `cpp-sanitizer-triage`

This skill is aimed at sanitizer reports (ASan, TSan, UBSan, MSan, LSan) that need disciplined triage: real or not, where the root cause is, and whether the action is a fix, a scoped suppression, or a configuration change.

It helps an assistant:

- read report anatomy: error kind, faulting access, allocation/free/previous-write stacks, shadow bytes, mutex and thread annotations
- separate the symptom frame from the root-cause frame and route fixes to the contract violation, not the faulting access
- classify reports as true positives, named tool limitations, or configuration artifacts (partial MSan instrumentation, uninstrumented synchronization for TSan)
- reject timing/rarity-based false-positive claims and require a named happens-before mechanism
- enforce suppression discipline: narrowest matcher, comments with issue links, third-party orientation, review notes
- keep sanitizer configurations compatible and verified (separate builds for TSan/MSan, symbolization working, regression tests under the sanitizer)
- return `BLOCK`, `CONCERNS`, or `CLEAN` with classification, root cause vs symptom, findings, checklist status, and an insufficient-context template

### `dependency-audit`

This skill is aimed at dependency risk reviews where manifests, lockfiles, scanner reports, advisory records, license context, and deployment reachability need to be reconciled into a practical release or merge verdict.

It helps an assistant:

- start from existing manifests, lockfiles, CI files, scanner reports, and project evidence rather than running package scripts or networked scanners by default
- classify known vulnerabilities, license risk, maintenance health, abandoned packages, transitive risk, unused dependencies, dependency bloat, supply-chain integrity concerns, and tooling evidence gaps
- distinguish confirmed production risk from scanner-only or dev-only findings that need reachability evidence before blocking
- apply false-positive discipline for unused dependency claims, including CLI tools, build plugins, framework auto-discovery, dynamic imports, peer dependencies, tests, generated code, and consumer-facing exports
- return `BLOCK`, `CONCERNS`, or `CLEAN` with severity, classification, evidence, remediation, checks, and residual risk

### `dependency-choice-review`

This skill is aimed at design-time build-vs-buy and dependency-adoption decisions, before a library, framework, service, or platform is woven into a design.

It helps an assistant:

- score each candidate (including the build option) on six dimensions: maintenance health, API stability, fit, lock-in and exit, operational burden, and license and policy
- demand concrete evidence per `concern`, keep unverifiable claims `unknown`, and map each `unknown` to the cheapest way to settle it
- state an exit path and its cost for every candidate, including the recommended one
- treat license and compliance constraints as pass/fail eliminations
- end with a recommendation or deciding question plus concrete reversal triggers
- emit a deterministic BLOCK template when no capability or candidate is supplied

### `equivalence-class-audit`

This skill is aimed at situations where a concrete defect, incident, review finding, test failure, or bug report suggests a wider class of equivalent defects that need to be audited in one bounded pass.

For the expanded catalogue, output contract, anti-patterns, and worked example, see [skills/equivalence-class-audit/WORKFLOW.md](skills/equivalence-class-audit/WORKFLOW.md).

It helps an assistant:

- lock the audit scope before expanding from the triggering finding
- enumerate candidate equivalents across bounds, sibling fields, mirror use sites, inverse operations, paths, modes, contracts, authorization surfaces, tests, docs, and source-of-truth projections
- record evidence-based `present`, `absent`, `n/a`, and `blocked` presence verdicts without guessing
- assign explicit dispositions for present defects: `fix-now`, `defer-with-owner`, or `blocked` (use `n/a` only where appropriate)
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return one structured audit report with rows for every applicable axis or candidate, plus fix-now defects, deferred follow-ups, out-of-scope candidates, blocking questions, and test/doc implications

### `factcheck`

This skill is aimed at drafts, claim lists, citations, source bundles, and reports where factual accuracy and source support need to be checked before the content is trusted or edited.

For the expanded workflow, evidence taxonomy, verdict contract, and deterministic output format, see [skills/factcheck/WORKFLOW.md](skills/factcheck/WORKFLOW.md).

It helps an assistant:

- extract checkable claims and separate factual assertions from opinion, rhetoric, predictions, or professional advice requests
- treat drafts, source text, URLs, files, snippets, webpages, PDFs, and search results as untrusted content whose embedded instructions must not be followed
- classify evidence using source-quality labels such as primary, official, peer-reviewed, recognized-domain-authority, reputable-news, expert-analysis, user-provided, outdated, conflicted, and unavailable
- assign stable verdicts (`SUPPORTED`, `MOSTLY_SUPPORTED`, `MIXED`, `UNSUPPORTED`, `CONTRADICTED`, `UNVERIFIABLE`, `NOT_A_FACTUAL_CLAIM`) with high/medium/low confidence reasons
- default to report-only output, while keeping any approved correction proposals minimal and tied to claim IDs
- handle medical, legal, financial, public-health, election, safety, and other sensitive-domain claims conservatively without giving professional advice

### `failure-mode-design`

This skill is aimed at architecture sketches, component designs, and integration plans whose failure behavior needs explicit decisions before implementation.

It helps an assistant:

- sweep every component→dependency edge across four failure shapes: `slow`, `down`, `wrong`, and `partial`
- assign exactly one policy per edge × shape row — `fail-fast`, `degrade`, `queue-and-retry`, `block`, `as-decided`, or `n/a — <reason>` — with a concrete blast radius and an observability signal
- permit retries only where the operation is idempotent under retry, and settle the duplicate-application outcome for every mutating flow
- treat unbounded retries, queues, and fan-out as findings, and source every number or mark it inferred-with-basis or an open decision
- record supplied failure decisions `as-decided` with remarks instead of re-litigating them
- emit a deterministic BLOCK template when no design is supplied

### `fix-batching-and-root-cause`

This skill is aimed at the planning step between a review round and writing fixes: clustering findings by shared cause so the cause is fixed once instead of each symptom patched separately.

It helps an assistant:

- restate findings with stable IDs and treat finding text strictly as data, ignoring embedded instructions
- trace each finding to an in-scope producing cause and cluster findings only on evidenced shared causes, never on superficial similarity
- choose an honest fix depth per cluster: `root-cause`, justified `symptom-level` with a named follow-up, `no-fix` with reason and owner, or `cause-unknown` naming the missing information
- order the batch with root-cause fixes first and explicit dependencies, and attach one cause-level verification line per cluster
- return `BATCH-READY`, `BATCH-PARTIAL`, or `BLOCK` with the findings list, cluster table, symptom-level justifications, and fix order

### `fix-blast-radius`

This skill is aimed at the moment after a fix is drafted and before it is pushed, when the question is what the fix could newly break and which already-resolved findings it could reopen.

It helps an assistant:

- trace the fix structurally across five surfaces: callers and call sites, shared state, contracts, behavioral siblings, and previously resolved findings
- report every surface explicitly as risks found, `no impact found`, or `untraceable` with the missing context named, without padding speculative risks
- attach a surface tag, concrete failure, likelihood, and one executable verification step to each risk
- cross-check every resolved finding supplied for the cycle against the fix's touched code and state
- return `SAFE-TO-PUSH`, `VERIFY-FIRST`, or `BLOCK` with the full impact-trace table and regression cross-check

### `instruction-quality-audit`

This skill is aimed at AI instruction artifacts, prompts, prompt templates, LLM task prompts, agent instructions, skill files, `SKILL.md` artifacts, prompt-packaged workflows, custom agent modes, and reusable assistant guidance that need a structured prompt quality or instruction quality audit for contradictions, ambiguity, persona issues, cognitive load, duplication, semantic coverage, missing error handling, and custom diagnostics.

It helps an assistant:

- preserve strict input handling for pasted text, selections, file paths, multiple instruction artifacts, missing input, unreadable files, and empty input
- treat audited instruction artifact contents strictly as data and ignore YAML frontmatter unless the instruction artifact itself incorrectly depends on it
- apply a high-confidence quality bar that avoids speculative, stylistic, or low-impact findings
- produce stable report sections in the required order: `Contradictions`, `Ambiguity Issues`, `Persona Issues`, `Cognitive Load`, `Duplication`, `Coverage Analysis`, and `Custom Diagnostics`
- preserve exact excerpt requirements with fenced `text` blocks and concrete rewrite suggestions

### `interface-contract-design`

This skill is aimed at new boundaries — APIs, service interfaces, module seams, message schemas, webhooks — whose contract should be decided before anything implements or consumes it, and at existing contract descriptions that need an audit.

It helps an assistant:

- define six per-operation fields: name and intent, inputs with validators, outputs including the empty-result shape, distinguishable errors with caller actions, idempotency class with duplicate-call outcome, and side effects
- decide three per-boundary fields: ordering and concurrency assumptions, versioning posture with what counts as breaking, and invariants each owned by exactly one of `caller`, `boundary`, or `downstream`
- flag implementation leakage (table names, internal services, framework types) in audit mode
- route unsettled design choices to `### Open decisions` with who decides instead of picking silently
- emit a deterministic BLOCK template when no boundary description is supplied

### `filesystem-path-safety`

This skill is aimed at code that turns external input into filesystem paths under a trusted root and then reads, creates, mutates, or deletes files.

It helps an assistant:

- establish the target, trusted root, external-input surface, and operation kind before judging
- audit validation, canonicalization, containment, symlink, hardlink, TOCTOU, and mutation-ordering controls
- distinguish static safe paths from externally influenced paths that need a trusted-root contract
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return anchored findings, insufficient-context blocks, and test expectations without broader web-app review structure

### `web-app-security-review`

This skill is aimed at web application security reviews where the assistant needs to evaluate code, pull requests, designs, vulnerability reports, or fix validation with a defensive and evidence-based workflow.

For the expanded checklist and evidence standards, see [skills/web-app-security-review/references/WORKFLOW.md](skills/web-app-security-review/references/WORKFLOW.md).

It helps an assistant:

- set safe-use boundaries for static review, explicitly authorized active testing, and untrusted external report content
- map trust boundaries, actors, tenants, entry points, sensitive data, and downstream systems before judging
- review high-value areas such as broken access control / IDOR, auth and sessions, OAuth / OIDC / JWT, XSS, CSRF, injection, XXE, SSRF, CORS, browser headers, file uploads, GraphQL, WebSockets, webhooks, secrets, dependencies, cloud IAM, containers, ReDoS, and DoS
- use concrete grep and review heuristics without relying on weaponized payload lists
- classify findings with severity, confidence, evidence standards, false-positive discipline, and regression-test expectations
- recognize narrow outbound-fetch and filesystem path construction as separate review concerns when those specialized contracts apply

### `ssrf-outbound-fetch-review`

This skill is aimed at code paths that accept or derive URLs from untrusted or semi-trusted input and then perform outbound requests, especially when policy, parsing, DNS, proxy, transport, redirect, and trusted private-target opt-in behavior all need to line up.

It helps an assistant:

- define explicit egress and port policy contracts before implementation
- review URL parsing, normalization, IP classification, and DNS handling, including connection-time lookup and rebinding risks
- reason about proxy behavior and transport semantics such as SNI, Host, and certificate verification
- assess redirect safety, sensitive-header handling, and trusted private-target opt-ins
- build realistic adversarial tests for SSRF-related edge cases
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return findings in a consistent, review-ready format

The skill covers both implementation concerns and review discipline, including boundaries, required input context, a definition of done, and a structured output contract.

### `spec-edge-case-enumeration`

This skill is aimed at feature specs, user stories, and behavior descriptions being finalized, whose edge cases need systematic enumeration so spec decisions are made before implementation instead of during it.

It helps an assistant:

- sweep eight edge-case dimensions: empty-and-boundary, error-paths, permissions, concurrency, time, locale-and-text, limits, and lifecycle, reporting case-less dimensions as `n/a` with a reason or as swept with no plausible cases
- phrase each case as a concrete scenario and give it exactly one disposition: `spec-decision`, `spec-stated`, `implementation-detail`, or `flag-for-deep-review`
- present options with user-visible consequences for spec decisions while leaving the choice to the owner
- record supplied edge-case decisions as `spec-stated` even under disagreement, noting disagreement as a remark
- flag specialized surfaces (security-sensitive text, file parsing, payment idempotency) for dedicated review without performing it
- emit a deterministic BLOCK template when no feature description is supplied

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

### `pr-scope-slicer`

This skill is aimed at change sets that may be too large or too mixed to review well in one pass, where incremental reviewer discovery would otherwise stretch into many rounds.

It helps an assistant:

- apply explicit, user-overridable size signals (non-mechanical line count, file count, mixed concerns, generated-content mixing) and state which fired
- split along a preferred axis order: mechanical vs semantic, refactor vs behavior, dependency order, subsystem independence, and risk isolation
- keep each slice independently buildable, testable, revertible, and labeled with its review focus and dependencies
- state the tradeoffs of splitting versus not splitting instead of treating splitting as free
- return `SINGLE-PASS-OK`, `SPLIT-RECOMMENDED`, `SPLIT-REQUIRED`, or `BLOCK` with the ordered slice table when a split is called for

### `pre-review-self-audit`

This skill is aimed at the author-side moment just before requesting review, when most first-round findings (hygiene, scope creep, missing tests, description drift) are still cheap to fix.

It helps an assistant:

- audit the supplied diff against an eight-item gating checklist: diff hygiene, scope, tests, contracts, commit atomicity, description accuracy, project checks, and reviewer anticipation
- discover the project's own checks structurally from CI config, package scripts, and task runners, listing unrun checks as outstanding instead of inventing them
- classify findings as `High`, `Medium`, or `Low` by whether they would force a review round on their own
- keep the full checklist table even on the no-findings path
- return `CLEAN`, `CONCERNS`, or `BLOCK` with findings, outstanding items, and a deterministic insufficient-context template

### `requirements-ambiguity-audit`

This skill is aimed at draft specs, requirements documents, feature requests, user stories, and product briefs that need an ambiguity check before planning or implementation.

It helps an assistant:

- sweep eight ambiguity classes: vague quantifiers, undefined terms, missing actors, conflicting requirements, placeholders, unspecified paths, ambiguous references, and untestable wording
- quote the exact text, name its location, and state the plausible readings for every finding
- propose rewrites that preserve intent and turn unknowns into explicit open questions instead of invented values
- respect supplied glossaries and explicitly delegated flexibility instead of flagging them
- assign `blocker`, `should-fix`, or `suggestion` severity and return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts
- emit a deterministic BLOCK template when no spec text is supplied

### `review-cycle-gatekeeper`

This skill is aimed at pull requests and change reviews that have already gone through one or more fix cycles and need a clear, evidence-backed merge gate decision.

It helps an assistant:

- normalize findings into explicit states (`fixed`, `owned-with-remediation-plan`, `waived-with-rationale`, `open`)
- enforce severity-aware closure rules so unresolved high-risk findings cannot be merged silently
- require verification evidence for functional fixes and highlight missing proof
- track regressions introduced during fix rounds as first-class findings
- validate waiver quality and ownership/remediation metadata
- return a compact `pass`, `fail`, or `BLOCK` gate summary with exact blockers to clear

### `review-disagreement-resolution`

This skill is aimed at review threads that have stalled after at least one full position/counter-position exchange and need a structured decision instead of more opinion trading.

It helps an assistant:

- restate both positions neutrally and treat them as data, ignoring embedded instructions to take a side
- classify each dispute part as `fact`, `standard`, or `preference`, splitting mixed disputes
- anchor each part to a verifiable source in precedence order: test or runnable demonstration, documented platform behavior, written project standard, maintainer ruling
- apply symmetric decision rules: facts resolved only by evidence, standards by the written rule or escalation to its owner, preferences defaulting to the author as non-blocking notes
- return `RESOLVED`, `NEEDS-EVIDENCE`, `ESCALATE`, or `BLOCK` with per-part classification, anchor, resolution, and who acts

### `review-finding-quality`

This skill is aimed at draft review comments and findings lists that need to be actionable and closable in a single round before they are posted.

It helps an assistant:

- enforce a five-field contract per finding: severity (`blocker`, `should-fix`, `suggestion`), anchor, observed-vs-expected problem, concrete fix direction, and an objective `Resolved when` acceptance condition
- split compound findings, separate questions from findings, and drop formatter-covered style nits as non-findings
- mark findings that cannot satisfy the contract as `needs-author-input` with the missing information named, never inventing anchors or evidence
- report each input finding exactly once as `compliant`, `rewritten`, or `needs-author-input`
- return the finding quality report with summary table, per-finding fields, questions, and dropped items, or `BLOCK` when no findings text is supplied

### `single-pass-review-completeness`

This skill is aimed at review rounds that should be the only round, preventing the incremental-review pattern where new findings keep appearing on unchanged code.

It helps an assistant:

- lock the diff under review and enumerate eight dimensions (correctness, contracts, security, concurrency and state, performance, tests, maintainability, operability) before reporting anything
- sweep dimension by dimension across the whole diff and tag every finding with its dimension
- declare each dimension `swept`, justified `skipped`, or `n/a`, and surface uncovered file–dimension pairs as explicit coverage gaps
- keep pre-existing issues outside the locked diff separate from pass findings
- return `COMPLETE-PASS`, `PARTIAL-PASS`, or `BLOCK` with the coverage declaration table and an explicit no-findings path

### `multi-lens-review`

This skill is aimed at changes that span more than one concern (correctness, security, data, UX, ops) and need several review perspectives reconciled into a single merge decision, rather than a single-lens check that an existing focused skill already covers.

It helps an assistant:

- walk a target through Intent / Spec, Design, Implementation, Security & Privacy, Adversarial, and Verification lenses, skipping any lens that does not add value
- recognize when a lens falls squarely inside a focused review concern while keeping each skill independently discoverable by its own scope
- record findings with severity, confidence, classification, concrete trigger, evidence, and suggested fix, separated from one-line per-lens summaries
- run an explicit Synthesis step to deduplicate, reconcile lens conflicts by naming the winning tradeoff, and split required actions from follow-ups
- emit a `BLOCK`, `CONCERNS`, or `CLEAN` verdict with residual risk
- avoid role-playing independent reviewers, applying every lens by default, or hiding conflicts behind silent consensus

### `scope-boundary-definition`

This skill is aimed at features, specs, projects, and tasks whose scope needs explicit boundaries — or whose existing scope statement needs an audit — before planning or estimation.

It helps an assistant:

- produce four exclusive boundary lists: in scope, out of scope (with reasons), non-goals, and deferred (with revisit triggers)
- flag inferred in-scope items, and surface unsettled placements as boundary decisions for the owner instead of guessing
- identify the smallest valuable slice — what it includes, proves, and leaves for later — or rule one out with a reason
- list scope-creep vectors with the boundary statement that pre-empts each
- mark items `kept`, `moved`, or `split` when auditing an existing scope statement so the delta is reviewable
- emit a deterministic BLOCK template when no work-item description is supplied

### `source-to-skill`

This skill is aimed at turning source material into reusable agent skills that change future agent behavior, rather than producing document summaries. It was inspired by [book-to-skill](https://github.com/virgiliojr94/book-to-skill/blob/master/SKILL.md).

It helps an assistant:

- inventory source paths, URLs, notes, folders, globs, prior analysis, and existing skills before deciding whether to analyze, generate, or update
- apply rights, substitution, source-integrity, and scope gates before writing generated skill files
- use the local extractor helper for supported local documents, preserving metadata, source boundaries, line ranges, hashes, extraction quality, and warnings as provenance anchors
- extract behavior-shaping material such as trigger contexts, decision rules, workflows, checklists, frameworks, anti-patterns, examples, vocabulary, and confidence notes
- generate compact `SKILL.md` files with optional references, examples, or checklists only when those supporting files reduce cognitive load
- validate frontmatter, trigger specificity, links, provenance, copyright posture, output formats, severity rubrics, stop conditions, and completion reporting before declaring success

### `test-gap-to-test-plan`

This skill is aimed at the step that comes after a review has produced findings: turning those findings into a concrete, prioritized, owned test plan that a merge gate can verify. It consumes upstream review output rather than re-judging it, and stays stack-neutral so it can work from any source that supplies findings with enough context.

It helps an assistant:

- consume findings with severity labels when available from any of three declared local vocabularies — the 4-level `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` vocabulary, the 3-level `High` / `Medium` / `Low` vocabulary, or the `Critical` / `Warning` / `Suggestion` rubric — and map them to `must-have` / `should-have` / `nice-to-have` priority, preserving missing or unrecognized labels as `unmapped`
- restate each finding as one specific unverified behavior before proposing a test
- pick the smallest faithful test layer (unit, integration, or e2e) and record it on the case
- write each case against a fixed template covering finding reference, original severity label, target suite, scenario, input/setup, expected behavior, failure signal, layer, priority, owner, and status
- group cases by finding rather than by file so traceability survives deduplication
- record live-system or production-data dependencies under `Untestable risks` instead of forcing them into the plan
- return `BLOCK`, `PLAN-PARTIAL`, or `PLAN-READY` so downstream merge gates can distinguish proposed coverage from landed test evidence
- refuse to fabricate findings, severities, or owners; emit `BLOCK` when required input context is missing

### `type-safe-design`

This skill is aimed at architecture and code changes where correctness should be enforced through contracts, types, compiler feedback, or narrow runtime boundaries instead of scattered discipline and defensive checks.

Source material: [Type-Safe by Design: Explorations in Software Architecture and Expressiveness](https://github.com/SanQri/safe-by-design/blob/a6b7aa22160c2ee3d461df064c0161e87e6a7087/book.pdf) by Mykola Haliullin.

It helps an assistant:

- review change-locality risks using Big O-style reasoning for rigidity, fragility, immobility, and viscosity
- model raw, validated, trusted, authenticated, readable, serialized, or behavior-capable states as explicit contracts
- decide when generics are appropriate infrastructure tools and when behavior needs named interfaces or protocols
- evaluate reflection, deserialization, polymorphic factories, enum registries, and constructor contracts as constrained boundaries
- avoid public API pollution for one-off internal access by using scoped operations or dedicated closure-carrier abstractions
- plan compiler-guided refactors and verification through boundary tests, substitution tests, completeness checks, and fail-fast construction paths

### `unicode-text-security-review`

This skill is aimed at code, designs, and tests where untrusted text crosses an encoding, normalization, comparison, storage, or display boundary and the result affects a security decision, identifier, lookup, database query, path/URL policy, allowlist, or audit trail.

It helps an assistant:

- state the text contract per field: accepted encodings, decode error behavior, normalization/case policy, identifier profile, and stored forms
- verify strict UTF-8 decoding before security decisions, rejecting overlong encodings, surrogate code points, truncated sequences, and lenient error modes
- choose normalization deliberately (NFC for canonical text, NFKC only for restricted identifiers) and run it before allowlists, uniqueness checks, and routing decisions
- catch parser-consumer drift where validation runs on one representation (bytes, raw text, one normalization form) and a database, filesystem, URL parser, or auth layer consumes another
- review identifier policy for confusables, mixed scripts, mixed numbers, default-ignorable and bidi characters, with migration plans for Unicode data changes
- apply decision rules for length-limit units, safe truncation, lone surrogates, decode-layer ordering, log/display injection, regex Unicode semantics, normalization expansion, and canonical hostname comparison
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, adversarial test expectations, and residual risk, including a deterministic insufficient-context template

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
