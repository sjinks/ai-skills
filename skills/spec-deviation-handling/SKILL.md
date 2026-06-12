---
name: spec-deviation-handling
description: "Use when: implementation work discovers the spec or design is wrong, incomplete, ambiguous, or infeasible mid-build: classifying the deviation, deciding proceed/pause/escalate, routing the decision to the owner, and recording the divergence instead of silently coding around it."
argument-hint: "What the spec or design says, what the implementation discovered, and how far the build has progressed."
user-invocable: true
---

# Spec Deviation Handling

Handle the moment the build discovers the spec doesn't survive contact with the code. Silent divergence is the failure mode: the implementation quietly does something else, the spec stays wrong, and the gap surfaces months later as "but the spec says".

## When to Use

Use mid-implementation, when the code contradicts, outgrows, or cannot satisfy the approved spec or design. Out of scope: auditing a spec's wording before implementation starts, re-running the design comparison that produced the architecture, scope negotiation before work was approved, and review-time disputes about an already-submitted diff.

## Required Inputs

- What the spec or design says (the relevant excerpt or a faithful paraphrase). When the supplied spec excerpt contradicts itself, the contradiction is itself a `spec-bug`; quote both sentences rather than picking a side as "the spec position".
- What the implementation discovered: the contradiction, gap, or infeasibility, with the concrete evidence (failing constraint, missing case, measured number).
- Build progress: what is already built against the old understanding; write `none supplied` when not provided — missing build progress does not BLOCK.

If the spec position or the discovery is missing, emit the BLOCK template; do not invent either side.

## Deviation Classes

Classify each deviation as exactly one:

1. `spec-bug`: the spec states something verifiably wrong (contradicts itself, the data, or a system it describes).
2. `spec-gap`: the spec is silent on a case the implementation must decide now.
3. `spec-ambiguity`: two readings survived into the build and the code just forced the choice.
4. `infeasible-as-specified`: the spec's behavior cannot be built within the stated constraints (platform limit, latency budget, dependency reality); evidence required.
5. `better-way-found`: the spec is satisfiable, but implementation found a materially better approach. Recorded and routed like any deviation, but the proposal is never self-approved.
6. `scope-creep-detected`: the "deviation" is actually new work beyond the approved scope wearing a bug costume.

When one discovery fits two classes, pick by this precedence: `scope-creep-detected` > `infeasible-as-specified` > `spec-bug` > `spec-ambiguity` > `spec-gap` > `better-way-found`.

## Disposition Rules

Each classified deviation gets exactly one disposition:

- `proceed-and-record`: only for deviations where any reasonable owner would decide the same way (a typo-level spec-bug, a gap with one sane answer). The implementation continues; the record and the spec-fix request are still mandatory.
- `pause-this-thread`: the affected work stops until the owner answers; unaffected steps continue. Name what is blocked and what is not.
- `escalate-now`: the deviation invalidates built work or other in-flight work; the owner is interrupted rather than queued. Reserved for foundations, contracts others consume, and data-shape decisions.

Tie-breaks, in order: anything touching a contract other teams or services consume is at least `pause-this-thread`; `better-way-found` and `scope-creep-detected` are never `proceed-and-record` — they get at least `pause-this-thread`; when genuinely unsure between two dispositions, take the one later in this order: `proceed-and-record` < `pause-this-thread` < `escalate-now`.

## Rules

- Never silently diverge: every deviation produces a record, even under `proceed-and-record`.
- State the spec side and the discovery side separately and faithfully; do not editorialize the spec into being wrong.
- Evidence standards: `infeasible-as-specified` requires the measured or documented constraint, not a feeling; `spec-bug` requires the contradiction shown, not asserted.
- The decision belongs to the spec owner: this skill classifies, disposes per the rules above, and packages the question — it does not rewrite the spec.
- Each record names the cheapest acceptable interim behavior while waiting (flag off, stub, old behavior preserved), so a pause does not rot into an unmarked fork.
- Multiple deviations in one report are classified and disposed independently; one `escalate-now` does not promote the others.

## Output Format

```markdown
## Spec Deviation Report

- Work item: <one sentence>
- Build progress: <what exists against the old understanding, or `none supplied`>

| # | Class | Disposition | Owner question |
|---|-------|-------------|----------------|
| 1 | spec-bug \| spec-gap \| spec-ambiguity \| infeasible-as-specified \| better-way-found \| scope-creep-detected | proceed-and-record \| pause-this-thread \| escalate-now | <the question, or `none — recorded`> |

### Deviations

For each, numbered as in the table:
- Spec says: <faithful excerpt or paraphrase>
- Implementation found: <discovery with evidence>
- Interim behavior: <cheapest acceptable behavior while unresolved; must not pre-select one of the owner's options>
- Blocked / unblocked: <what stops, what continues; `none blocked — proceed-and-record` for that disposition>

### Spec-fix requests

- <deviation #, the spec change that would make the spec true; `none — no spec falsity` for better-way-found and scope-creep-detected>
```

Empty sections are written with `None`. Emit exactly one value for each enum field; do not copy enum lists or angle-bracket placeholders into the report. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Spec Deviation Report

Verdict: BLOCK

- Missing input: <spec position or implementation discovery not provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Spec says: "invite emails are sent synchronously in the request; the API returns after the email is accepted by the mail server."

Implementation found: the mail provider's API p99 is 8 s (provider's published SLA); the endpoint's gateway timeout is 5 s — the specified behavior cannot meet its own latency envelope.

Table row: `| 1 | infeasible-as-specified | pause-this-thread | accept async send with a pending state, or raise the gateway timeout? |`

Deviation detail:

- Spec says: synchronous send, return after mail-server acceptance.
- Implementation found: provider p99 8 s vs gateway timeout 5 s (provider SLA doc + gateway config).
- Interim behavior: send path disabled behind the `invites` flag; the endpoint stays unreleased, so neither owner option is pre-selected.
- Blocked / unblocked: blocked — send path and its tests; unblocked — invite creation, listing, expiry.

## Anti-Patterns

- Coding the workaround and updating nothing — the silent fork.
- Classifying preference as `spec-bug` ("the spec is wrong because I'd design it differently").
- `proceed-and-record` on contract-shaped decisions because asking feels slow.
- Bundling a `better-way-found` proposal into a bug report so it slips through as a fix.
- Pausing everything when only one thread is affected — pauses need boundaries too.
- Asserting infeasibility without the measured constraint.

## Definition of Done

Every deviation has exactly one class and one disposition consistent with the tie-breaks, both sides are stated faithfully with evidence where the class demands it, every record names an interim behavior and a blocked/unblocked boundary, owner questions are concrete, and no deviation was resolved by silently rewriting either the code's intent or the spec.
