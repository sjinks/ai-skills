---
name: assumption-surfacing
description: "Use when: surfacing implicit assumptions in a spec, plan, design, or estimate before work starts: data shapes, ordering, scale, auth context, environment, compatibility, dependency behavior, and people-process expectations, classifying each as verify-before-build or accept-with-risk."
argument-hint: "The spec, plan, design, or estimate text to sweep for implicit assumptions, plus any context about the system it targets."
user-invocable: true
---

# Assumption Surfacing

Enumerate the implicit assumptions a spec, plan, design, or estimate silently depends on, and decide for each whether it must be verified before building or can be consciously accepted with a named risk. Unsurfaced assumptions become mid-build surprises; surfaced ones become a checklist.

## When to Use

Use before implementation starts, when a spec, plan, design doc, or estimate is about to be committed to. Out of scope: verifying the assumptions themselves (this skill produces the verification worklist, not its results), reviewing finished code, challenging whether the work should happen at all, and general red-team critique of the design's decisions — this skill only extracts unverified premises the plan depends on.

## Required Inputs

- The spec, plan, design, or estimate text.
- Optional: system context (architecture notes, known constraints, prior incidents); used to ground assumptions, never required.

If no text is provided, emit the BLOCK template; do not invent a plan to analyze.

## Assumption Categories

Sweep the text once per category. For each, ask: what must be true for this plan to work that the text does not state or verify?

1. `data`: shapes, formats, encodings, nullability, uniqueness, volume, quality of existing data.
2. `ordering`: event order, idempotency, exactly-once vs at-least-once, race windows the plan ignores.
3. `scale`: load, growth, payload sizes, concurrency the design implicitly fits.
4. `auth-context`: who is authenticated, what tenant/role context is available where the code runs.
5. `environment`: runtime versions, infra availability, network topology, config presence.
6. `compatibility`: API consumers, stored-data formats, migration coexistence, rollback paths.
7. `dependency-behavior`: what third-party services, libraries, or sibling teams' components actually do under error, latency, or limit conditions.
8. `people-process`: review availability, deploy windows, on-call coverage, stakeholder sign-off the timeline presumes.

## Classification

Each assumption gets exactly one disposition:

- `verify-before-build`: a wrong guess would invalidate the design or cause rework larger than the verification cost. Carries a one-line verification step (who checks what, against which source).
- `accept-with-risk`: verification costs more than the plausible damage, or the assumption is overwhelmingly likely and a wrong guess would not cause rework larger than the verification cost. Carries the named risk if wrong and the earliest signal that would reveal it.

Tie-breaks, in order: when damage-if-wrong is structural (schema, contract, security, data loss), classify `verify-before-build` regardless of likelihood; when both definitions still apply, classify `verify-before-build`.

## Rules

- Every assumption quotes or paraphrases the plan text that depends on it, with location.
- State the assumption as a falsifiable claim ("the orders table has no rows with null customer_id"), not a topic ("data quality").
- Do not list universal background facts no plan could verify ("the compiler is correct"); an assumption is in scope when a realistic check exists or a realistic failure has been seen.
- Assign each `verify-before-build` item an owner only from names/roles in the input; otherwise write `Owner: none named in input`.
- Do not perform the verifications; produce the worklist.

## Output Format

```markdown
## Assumption Surfacing Report

- Target: <one sentence: what plan/spec was swept>

| # | Category | Assumption (falsifiable claim) | Disposition |
|---|----------|--------------------------------|-------------|

### Verify before build

For each, numbered as in the table:
- Depends on: <plan text and location>
- Verification: <who checks what, against which source>
- Owner: <name/role from input, or `none named in input`>

### Accepted with risk

For each, numbered as in the table:
- Depends on: <plan text and location>
- Risk if wrong: <consequence>
- Earliest signal: <what would reveal it>

### Categories with no findings

- <category>: <one line why nothing surfaced>
```

Empty sections are written with `None`. When a category genuinely yields nothing, list it under categories with no findings rather than padding it.

The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Assumption Surfacing Report

Verdict: BLOCK

- Missing input: <no plan or spec text provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Plan step: "Backfill script copies all files from /var/avatars to the bucket, keyed by user ID."

Table row: `| 1 | data | every file under /var/avatars maps to exactly one existing user ID, with no orphans or duplicates | verify-before-build |`

Under `### Verify before build`:
- Depends on: backfill step 1, which keys uploads by user ID.
- Verification: run a dry-run listing pass comparing filenames against the user table before the copy.
- Owner: none named in input

## Anti-Patterns

- Topic-shaped assumptions ("data quality") instead of falsifiable claims.
- Classifying by likelihood alone; the structural-damage tie-break overrides "it's almost certainly fine".
- Performing the verifications or reporting their results; this skill ends at the worklist.
- Padding every category with filler instead of using the no-findings line.
- Inventing owners for verification steps when the input names none.

## Definition of Done

All eight categories were swept and each is represented by findings or a no-findings line, every assumption is a falsifiable claim with a location anchor and exactly one disposition, every `verify-before-build` item has a verification step, and every `accept-with-risk` item has a risk and an earliest signal.
