When to read: when checking report construction or illustrating evidence and disposition choices.

# Equivalence-Class Audit Examples

Examples are non-normative; `SKILL.md` defines the report contract. The following scenario uses supplied hypothetical evidence rather than facts about a real system.

## Standard report


Triggering finding: a review found that `maxRetries` in `config/service.yml` accepts `0`, causing permanent failure without retry.

Locked audit scope: `config/service.yml`, `docs/retry-policy.md`, and `tests/retry_policy_spec.rb`.

Allowed disposition boundary: defer documentation corrections to owner Platform Docs because that team owns `docs/retry-policy.md` outside the current code change.

```markdown
## Equivalence-Class Audit Report

Triggering finding: `maxRetries` accepts `0`, disabling retry behavior unexpectedly.
Locked audit scope: config/service.yml, docs/retry-policy.md, tests/retry_policy_spec.rb
Output depth: standard
Verdict: CONCERNS
Severity: MEDIUM

| Axis | Candidate | Presence | Disposition | Evidence |
|------|-----------|----------|-------------|----------|
| Opposite Bound | `maxRetries` upper bound | present | fix-now | `config/service.yml` defines no maximum; incident note says very large values can stall workers |
| Sibling Parameter/Field | `retryDelaySeconds` lower bound | present | fix-now | `config/service.yml` allows `0`, same retry policy group |
| Mirror Call Site/Use Site | Batch worker retry config | absent | n/a | `config/service.yml` uses one shared retry block for API and batch workers |
| Inverse Operation | Disable retry mode | n/a — structurally inapplicable | n/a | retry policy has no inverse operation in scope |
| Type/Schema Narrowing | Retry configuration schema | n/a — no candidates in scope | n/a | no schema artifacts are included in the locked scope |
| Validation vs Normalization/Sanitization | - | n/a — no candidates in scope | n/a | no candidates in locked scope |
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
| Cache/Projection/Source-of-Truth Twin | - | n/a — no candidates in scope | n/a | no candidates in locked scope |

### Defects to fix now
- `maxRetries` upper bound: add an upper-bound constraint in `config/service.yml`.
- `retryDelaySeconds` lower bound: reject `0` in `config/service.yml`.
- `retryDelaySeconds` and `maxRetries` policy names: align their bound rules.
- Lower-bound test for `retryDelaySeconds`: add coverage in `tests/retry_policy_spec.rb`.

### Deferred follow-ups
- Retry docs versus config behavior: update `docs/retry-policy.md`; owner: Platform Docs; reason: it documents the old `0` behavior.
- Retry policy minimum value prose: correct the documented minimum; owner: Platform Docs; reason: docs are owned outside this change.

### Out-of-scope candidates discovered
- Generated deployment schema may mirror the retry constraints, but it is outside the locked scope; provenance: schema reference in deployment README.
- String value `"0"` from environment override may need equivalent validation, but overrides are outside the locked scope; provenance: retry configuration input model.

### Blocking questions
- None

### Test/doc implications
- Lower-bound test for `retryDelaySeconds`: add tests for `retryDelaySeconds=0`.
- Retry docs versus config behavior: update `docs/retry-policy.md` with the config constraint.
- Retry policy minimum value prose: correct the documented minimum when the deferred docs follow-up lands.
```

The example intentionally includes present, absent, `n/a`, and deferred rows while representing every catalogue axis at least once.
