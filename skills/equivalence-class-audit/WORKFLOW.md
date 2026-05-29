# Equivalence-Class Audit Workflow

This supporting workflow expands the standalone `SKILL.md` entry point for language-agnostic equivalence-class audits. A single confirmed defect often marks a class of equivalent defects. This workflow turns one concrete trigger into a bounded, evidence-based audit of sibling fields, mirrored use sites, inverse operations, boundary checks, contracts, paths, modes, tests, docs, and source-of-truth projections.

The deliverable is one audit report. This skill package is standalone and does not require any other skill. If the audit finds defects, each present defect is explicitly marked for immediate fixing, deferred with a named owner or owning team and reason, or blocked on clarification.

## Boundaries

- The triggering finding and locked audit scope are required before candidate enumeration. If either is missing, stop before enumeration.
- Do not invent scope or candidates. Use the user's stated scope, supplied artifacts, current project files, tests, specs, and observable behavior as the source of truth.
- The audit scope is locked before candidate enumeration. Do not silently expand it. If an equivalent candidate is discovered outside the locked scope, record it under **Out-of-scope candidates discovered** with provenance.
- If no disposition boundary is provided, default in-scope present defects to `fix-now`.
- `defer-with-owner` requires a named owner or owning team and a reason. A ticket, issue, or reference alone is not enough.
- Every catalogue axis should be represented at least once in the table when the table is included (i.e., only after both the triggering finding and locked audit scope are available), except in explicit `quick` mode. If an axis has no candidates or is structurally inapplicable, include one explicit `n/a` row with evidence or a reason.

## When to Use

Use this workflow when there is a concrete triggering finding, such as:

- a review finding from a human or automated reviewer
- a production incident, alert, or customer bug report
- a security, authorization, privacy, or data-integrity finding
- a failing test that exposes a defect class rather than a single typo
- a confirmed mismatch between implementation, schema, migration, configuration, documentation, or tests

The audit can apply to any programming language, API, configuration, schema, migration, documentation/specification, or test artifact.

## When Not to Use

Do not use this workflow for:

- greenfield design or general advice with no triggering defect
- a broad initial code review before any specific finding exists
- formatting-only changes or isolated prose typos that have no equivalent behavioral class
- deliberately read-only generated/vendor artifacts where the operator has explicitly scoped out follow-up action

## Required Inputs

Before auditing, state the required inputs. The triggering finding and locked audit scope are the minimum inputs needed before candidate enumeration. If either is missing, do not enumerate candidates, do not invent scope, and do not add table rows. Return the report header and sections, and use **Blocking questions** to name the smallest missing input needed to proceed. Use table rows only when enough scope exists to identify at least one axis or candidate safely. This rule applies across languages, frameworks, configuration, schemas, documentation, tests, and other artifacts.

If another critical fact is missing after the triggering finding and locked audit scope are known, record the affected row as `blocked — clarification needed` with `blocked` disposition instead of guessing.

- **Triggering finding:** the concrete defect, incident, failing assertion, review comment, or bug report.
- **Locked audit scope:** exact files, modules, API surfaces, resources, specs, tests, schemas, migrations, configuration artifacts, or documentation sections to inspect.
- **Severity or criticality:** especially whether the defect class affects security, authorization, data integrity, public contracts, or user-visible behavior.
- **Allowed disposition boundary:** optional. If omitted, default in-scope present defects to `fix-now`. Use `defer-with-owner` only when an explicit named owner or owning team and a reason are available. Use `blocked` only when clarification is needed before deciding safely.

## Output Depth

Default to `standard` unless the user asks for another depth.

- `quick`: include only missing required context, blockers, high-risk concerns, and target-specific applicable axes. Do not enumerate the full catalogue. Add a short omitted-axis summary naming why the remaining axes were not expanded, such as no candidate in locked scope, structurally inapplicable, or not material to the triggering finding.
- `standard`: represent every catalogue axis at least once when the table is included. Add candidate rows where evidence exists and explicit `n/a` rows for axes with no candidates or structural inapplicability.
- `exhaustive`: represent every catalogue axis at least once and expand all reasonably discoverable candidates inside the locked scope.

If the user asks for `quick` or `exhaustive`, name the selected depth in the report. If quick mode omits an axis that has a target-specific blocker or high-risk concern, the quick report is incomplete.

## Procedure

1. Restate the triggering finding and locked audit scope.
2. If the triggering finding or locked audit scope is missing, stop before candidate enumeration and ask the smallest blocking question in the report sections.
3. Select output depth. In `quick` mode, identify target-specific blockers, high-risk concerns, and applicable axes, then summarize omitted axes instead of walking the full catalogue in the table. In `standard` and `exhaustive`, walk every axis in the catalogue below.
4. For each axis, enumerate candidates inside the locked scope.
5. When the table is included after the triggering finding and locked audit scope are available, represent every catalogue axis at least once unless the selected depth is `quick`.
6. If an axis has candidates, add one row per candidate.
7. If an axis has no candidates or is structurally inapplicable, add one explicit `n/a` row with evidence or a reason.
8. For each candidate, decide **Presence** from evidence, not probability.
9. For every `present` defect, assign a **Disposition**: `fix-now`, `defer-with-owner`, or `blocked`.
10. Put candidates found outside the locked scope in the out-of-scope section rather than adding them to the table.
11. Capture test and documentation implications even when production code is already safe.

Do not use `unknown`, `maybe`, or speculative wording as a verdict. If a candidate cannot be evaluated from the available evidence, use `blocked — clarification needed` and ask the smallest blocking question.

## Strict Table Values

The report table must use only these values.

**Presence:**

- `present` - the same defect class exists for this candidate.
- `absent` - the candidate was checked and evidence shows the class does not manifest.
- `n/a — structurally inapplicable` - the axis cannot apply to this artifact or code shape.
- `n/a — no candidates in scope` - the axis could apply in principle, but no candidates exist in the locked scope.
- `blocked — clarification needed` - a critical fact is missing and the row cannot be judged safely.

**Disposition:**

- `fix-now` - the present defect should be fixed in the current change.
- `defer-with-owner` - the present defect is intentionally deferred with a named owner or owning team and a reason. A ticket, issue, or reference alone is not enough.
- `n/a` - used for `absent` and `n/a` presence rows.
- `blocked` - used when clarification is required before deciding or fixing, including when a present defect would be deferred but no named owner or owning team is available.

**Evidence** must cite a file, section, test, spec, schema, migration, configuration artifact, log, incident note, or state the reason for an `n/a` row. A row without evidence is incomplete.

## Catalogue

For `standard` and `exhaustive`, walk every axis. If an axis has no candidate or cannot apply, record the explicit `n/a` row. For `quick`, include only the target-specific applicable axes and summarize omitted axes instead of adding full-catalogue `n/a` rows.

### Opposite Bound

If the finding concerns one bound, audit the opposite bound and the boundary value itself.

Candidates include numeric ranges, string lengths, collection sizes, indexes, timestamps, versions, percentages, quotas, currency amounts, and retry limits.

### Sibling Parameter/Field

If the finding targets one parameter or field in a logical group, audit the other parameters or fields in that same signature, message, record, schema, config block, request, response, or form.

Candidates include pagination fields, date ranges, sort fields, resource IDs, auth token metadata, pricing fields, feature flags, configuration keys, schema columns, and migration fields.

### Mirror Call Site/Use Site

If the finding targets one invocation, reference, include, route, rule, query, template, or configuration use, audit other uses of the same API, helper, policy, schema, component, or artifact inside the locked scope.

### Inverse Operation

If the finding concerns one direction of a paired operation, audit the inverse.

Candidates include encode/decode, serialize/deserialize, marshal/unmarshal, compress/decompress, encrypt/decrypt, sign/verify, open/close, lock/unlock, subscribe/unsubscribe, create/delete, read/write, migrate/rollback, import/export, grant/revoke, and enable/disable.

### Type/Schema Narrowing

If the finding narrows a type, schema, enum, union, allowed value set, or contract at one boundary, audit all other producers and consumers that may still accept or rely on the wider shape.

Candidates include API validators, database schemas, JSON/XML schemas, protobuf/IDL definitions, config schemas, generated clients, static types, migration constraints, and downstream consumers.

### Validation vs Normalization/Sanitization

If one side was applied, audit whether the other is needed and present. Validation rejects bad input; normalization or sanitization transforms input before storage, comparison, logging, rendering, path construction, or execution.

Candidates include user strings, URLs, paths, identifiers, Unicode text, case-folded names, numeric coercion, structured logs, rendered HTML, shell or query sinks, and policy matching keys.

### Happy/Error/Retry/Cancel Path Twin

If one execution path was fixed, audit the corresponding happy, error, timeout, retry, cancellation, rollback, and partial-failure paths.

Candidates include response construction, transaction handling, state transitions, event emission, metrics, retries, compensating actions, and user notifications.

### Race/Shared-State Twin

If the finding involves consistency, ordering, idempotency, or concurrency at one site, audit other readers and writers of the same shared state.

Candidates include memory state, files, locks, queues, database rows, caches, leases, sessions, counters, idempotency keys, generated artifacts, and distributed coordination records.

### Permission/Authorization Class

If an authorization or permission check was missing or wrong for one surface, audit equivalent surfaces for the same resource, tenant, capability, role, ownership model, or administrative action.

Candidates include REST routes, GraphQL fields, RPC methods, CLI commands, background jobs, webhooks, admin variants, bulk actions, export paths, import paths, and read-only projections.

### Observability Twin

If logging, metrics, tracing, audit events, alerts, or diagnostics were missing or fixed on one branch, audit the matching branch and equivalent resources.

Candidates include success/failure metrics, span start/end, correlation IDs, audit logs, redaction rules, sampled traces, retry counters, and alert thresholds.

### Resource Cleanup

If cleanup was missing or fixed on one path, audit every path that allocates, reserves, opens, subscribes, locks, schedules, or materializes the same kind of resource.

Candidates include files, sockets, database connections, cursors, transactions, locks, timers, listeners, subscriptions, child processes, temp files, buffers, leases, and cloud resources.

### Contract Symmetry

If one side of a machine-checkable or externally consumed contract changed, audit the matching side.

Candidates include request/response shapes, schema/runtime validators, serializer/deserializer pairs, migration up/down, API spec/runtime behavior, generated client/server definitions, producer/consumer event schemas, and seed data/schema constraints.

### Equivalence by Naming

If names imply parallel responsibilities, audit the parallel symbols, sections, routes, resources, tests, or documents.

Candidates include `findBy...` families, `before...`/`after...` hooks, `on...` handlers, role-prefixed permissions, resource-prefixed routes, similarly named configuration keys, migration pairs, and repeated documentation sections.

### Test Mirror

If a test was added, changed, or revealed a bug for one case, audit the neighboring tests that should exist for sibling candidates, boundaries, paths, modes, contracts, and sentinels.

Candidates include parameterized cases, boundary tests, negative tests, contract tests, migration rollback tests, permission matrix tests, retry/cancel tests, and documentation examples that function as executable tests.

### Empty/Sentinel Equivalence

If the finding concerns one absent-like or sentinel value, audit the other sentinel values that callers or artifacts can supply for the same logical slot.

Candidates include missing key, explicit null, empty string, whitespace-only string, zero, negative one, false, NaN, empty list, empty object/map, empty file, default enum value, omitted config key, and sentinel timestamps.

### Async/Sync or Mode Twin

If the finding targets one variant or mode, audit equivalent variants.

Candidates include async/sync APIs, streaming/buffered modes, dry-run/apply modes, strict/lenient parsing, batch/single item operations, online/offline modes, admin/user modes, preview/publish modes, and read-only/mutating modes.

### Documentation/Spec Prose Twin

If behavior, constraints, errors, or guarantees changed, audit human-readable prose that describes the old behavior.

Candidates include README sections, API reference prose, comments, runbooks, migration guides, changelog notes, tutorials, generated docs, error messages, UI copy, and incident remediation notes.

### Cache/Projection/Source-of-Truth Twin

If a defect involves stale data, invalidation, consistency, or duplicated representation, audit every cache, projection, index, export, denormalized field, materialized view, read replica, or generated artifact of the same source of truth.

## Output Format

Return one report with this header and these sections.
Only include the table after both the triggering finding and locked audit scope are available. For insufficient input, keep the report header and section headings, omit table rows, and put the missing input under **Blocking questions**.

```markdown
## Equivalence-Class Audit Report

Triggering finding: <one concrete defect or finding>
Locked audit scope: <files/modules/API surfaces/specs/tests/artifacts>

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | <candidate or -> | <strict Presence value> | <strict Disposition value> | <file/section/test/spec or n/a reason> |

### Defects to fix now
- <present candidate with disposition fix-now, or `None`>

### Deferred follow-ups
- <present candidate with disposition defer-with-owner, named owner or owning team, optional ticket/reference, and reason, or `None`>

### Out-of-scope candidates discovered
- <candidate, why it is outside locked scope, and provenance, or `None`>

### Blocking questions
- <candidate/axis and the exact clarification needed, or `None`>

### Test/doc implications
- <test, documentation, spec, migration, or contract implications, or `None`>

### Omitted axes (quick mode only)
- <summary of omitted catalogue axes and why they were not expanded, or `None` when depth is not quick>
```

When the table is included after both the triggering finding and locked audit scope are available, every catalogue axis must be represented in the table at least once for `standard` and `exhaustive` depth. If an axis has candidates, add one row per candidate. If an axis has no candidates or is structurally inapplicable, add one explicit `n/a` row with evidence explaining why. In explicit `quick` mode, include only target-specific applicable axes and add an omitted-axis summary instead of full-axis enumeration.

## Anti-Patterns

- **Silent omission:** skipping an axis or candidate because it seems unlikely, or using quick mode to omit a target-specific blocker or high-risk concern instead of reporting it.
- **Speculative presence:** writing "probably", "maybe", or "looks similar" instead of citing evidence.
- **Scope drift:** adding outside-scope candidates to the main table instead of recording them separately.
- **Disposition blur:** marking a present defect as `n/a`, deferring it without a named owner or owning team and reason, or treating a ticket/reference alone as an owner.
- **One-row class smearing:** grouping multiple candidates into one row so individual evidence and disposition are unclear.
- **Fix-first audit:** using the report only to justify changes already chosen, instead of deciding the class explicitly.
- **Language lock-in:** assuming the catalogue applies only to one framework, language, or artifact type.

## Worked Example

Triggering finding: a review found that `maxRetries` in `config/service.yml` accepts `0`, causing permanent failure without retry.

Locked audit scope: `config/service.yml`, `docs/retry-policy.md`, and `tests/retry_policy_spec.rb`.

```markdown
## Equivalence-Class Audit Report

Triggering finding: `maxRetries` accepts `0`, disabling retry behavior unexpectedly.
Locked audit scope: config/service.yml, docs/retry-policy.md, tests/retry_policy_spec.rb

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | `maxRetries` upper bound | present | fix-now | `config/service.yml` defines no maximum; incident note says very large values can stall workers |
| Sibling Parameter/Field | `retryDelaySeconds` lower bound | present | fix-now | `config/service.yml` allows `0`, same retry policy group |
| Mirror Call Site/Use Site | Batch worker retry config | absent | n/a | `config/service.yml` uses one shared retry block for API and batch workers |
| Inverse Operation | Disable retry mode | n/a — structurally inapplicable | n/a | retry policy has no inverse operation in scope |
| Type/Schema Narrowing | Retry configuration schema | n/a — no candidates in scope | n/a | no schema artifacts are included in the locked scope |
| Validation vs Normalization/Sanitization | String value `"0"` from environment override | blocked — clarification needed | blocked | Need to know whether environment overrides are in scope for this audit |
| Happy/Error/Retry/Cancel Path Twin | Retry exhaustion error path | absent | n/a | `tests/retry_policy_spec.rb` covers exhaustion after allowed retries |
| Race/Shared-State Twin | Shared retry counter state | n/a — structurally inapplicable | n/a | locked scope contains static config/docs/tests, not shared mutable state |
| Permission/Authorization Class | Admin retry-policy edit surface | n/a — no candidates in scope | n/a | no authorization surface is included in the locked scope |
| Observability Twin | Metric for disabled retry behavior | n/a — no candidates in scope | n/a | no logging, metrics, or alert artifacts are included in the locked scope |
| Resource Cleanup | Retry timer cleanup | n/a — structurally inapplicable | n/a | no resource allocation or timer implementation is included in the locked scope |
| Contract Symmetry | Retry docs versus config behavior | present | defer-with-owner | `docs/retry-policy.md` says `0` means immediate retry; owner: Platform Docs; reason: docs are owned by the docs team |
| Equivalence by Naming | `retryDelaySeconds` and `maxRetries` policy names | present | fix-now | both keys are in the retry policy group in `config/service.yml` and lack lower-bound consistency |
| Test Mirror | Lower-bound test for `retryDelaySeconds` | present | fix-now | `tests/retry_policy_spec.rb` covers `maxRetries=0` only |
| Empty/Sentinel Equivalence | Omitted `maxRetries` config key | absent | n/a | `tests/retry_policy_spec.rb` covers omitted key defaulting to 3 retries |
| Async/Sync or Mode Twin | Dry-run retry mode | n/a — no candidates in scope | n/a | no mode variants are present in the locked scope |
| Documentation/Spec Prose Twin | Retry policy minimum value prose | present | defer-with-owner | `docs/retry-policy.md` documents `0` as valid; owner: Platform Docs; reason: docs follow-up is owned outside code change |
| Cache/Projection/Source-of-Truth Twin | Generated deployment schema projection | n/a — no candidates in scope | n/a | generated deployment schema is outside the locked scope and recorded below |

### Defects to fix now
- Add lower and upper bound validation for retry values in `config/service.yml`.
- Add missing lower-bound tests in `tests/retry_policy_spec.rb`.

### Deferred follow-ups
- `docs/retry-policy.md` must be updated by owner Platform Docs because it still documents the old `0` behavior.

### Out-of-scope candidates discovered
- Generated deployment schema may mirror the retry constraints, but it is outside the locked scope; provenance: schema reference in deployment README.

### Blocking questions
- Are environment overrides part of this audit scope, or should they be tracked separately?

### Test/doc implications
- Add tests for `maxRetries=0`, excessive `maxRetries`, and `retryDelaySeconds=0`.
- Update retry policy prose when the deferred docs follow-up lands.
```

The example intentionally includes present, absent, `n/a`, deferred, and blocked rows while representing every catalogue axis at least once.
