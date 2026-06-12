---
name: architecture-decision-record
description: "Use when: writing, rewriting, or auditing an architecture decision record (ADR), design decision log entry, or technical decision write-up: context, decision drivers, options considered with costs, chosen option, positive and negative consequences, and revisit triggers."
argument-hint: "The decision context, options considered, and constraints — or an existing ADR to audit, plus any project decision-log conventions."
user-invocable: true
---

# Architecture Decision Record

Turn a technical decision into a durable, complete decision record. An ADR that lists one option and no negative consequences is a press release, not a record; the cost lands on the next engineer who cannot reconstruct why alternatives were rejected.

## When to Use

Use when a technical decision needs to be recorded, an existing ADR needs an audit, or a decision write-up needs rewriting into ADR form. Out of scope: running the weighted comparison that produces the choice (this skill records a decision and the already-considered options; it does not score candidates or compare options before a choice exists), making the decision on the owner's behalf, documenting an as-built system with no decision in it, and incident retrospectives.

Input modes:

- Draft mode: decision context supplied (problem, options considered, constraints, chosen or leaning option). Produce the ADR. A decision write-up not yet in ADR form is draft mode.
- Audit mode: input already structured as an ADR. Reproduce it restructured into the contract fields and list every contract gap under `### Contract gaps`.

In both modes, material the contract requires but the input lacks is named under `### Contract gaps` instead of being invented; an audited ADR that defers a choice routes that choice to `### Open decisions`.

## Required Inputs

- The decision context (problem, constraints, options considered, who decides), or the existing ADR text to audit.
- Project decision-log conventions (numbering, status vocabulary), when supplied.

If neither decision context nor an ADR is provided, emit the BLOCK template; do not invent a decision.

## ADR Contract

A complete record carries all eight fields:

1. Title: imperative summary of the decision ("Use event sourcing for order history"), not a topic.
2. Status: one of `proposed`, `accepted`, `superseded` (or the project's supplied status vocabulary); default `proposed` unless the input states the decision is made. A `superseded` record names its successor on the Status line (`superseded by <record>`).
3. Context: the forces that make this decision necessary now — constraints, scale, deadlines, prior decisions. Facts, not justification.
4. Decision drivers: the 2–5 criteria that actually discriminate between options.
5. Options: at least two real options, each with its main benefit and main cost. "Do nothing" counts when it is genuinely viable. A single-option record is a contract gap, not an ADR.
6. Decision: the chosen option and the driver-based rationale; one paragraph.
7. Consequences: what becomes easier and what becomes harder or is given up. At least one negative consequence; a decision with no downsides was not a decision.
8. Revisit triggers: the concrete conditions under which this decision should be reconsidered (scale threshold, dependency EOL, constraint disappearing).

## Rules

- Record only options, drivers, and consequences supported by the supplied input; mark anything you inferred with `(inferred)`, including inferred option benefits and costs.
- Do not pick the option in draft mode when the input names no choice and no leaning: list the options, write `pending — see Open decisions` under `### Decision`, and put the choice under `### Open decisions`. A Decision routed this way counts as present for the Definition of Done.
- Negative consequences are stated concretely ("every schema change now requires a projection rebuild"), not as hedges ("may have some complexity").
- Strawman options (options no one would choose, listed to make the winner look good) are flagged as a contract gap in both modes.
- Preserve the project's status vocabulary when supplied; when the project numbers its records, carry the number in the Title line (`ADR-014: <title>`). Otherwise use the defaults above.
- Empty-value conventions: header fields use their stated inline fallback (for example `none named in input`); `###` sections use `None`.

## Output Format

```markdown
## Architecture Decision Record

- Title: <imperative decision summary; prefixed with the project's record number when supplied>
- Status: <proposed | accepted | superseded by <record> | the project's supplied status vocabulary>
- Deciders: <from input, or `none named in input`>

### Context

<forces and constraints, 2–6 sentences>

### Decision drivers

- <driver>

### Options

- <option> — benefit: <main benefit>; cost: <main cost>

### Decision

<chosen option and driver-based rationale; `pending — see Open decisions` when no choice was named>

### Consequences

- Easier: <what improves>
- Harder: <what degrades or is given up>

### Revisit triggers

- <concrete condition>

### Contract gaps

- <field>: <what is missing or weak>

### Open decisions

- <decision left to the owner, who decides>
```

Empty sections are written with `None`. In draft mode `### Contract gaps` is `None` unless the input is missing material the contract requires (then name it instead of inventing it). The `Deciders:` header line is a template field outside the eight audited contract fields. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input, or input that contains no decision at all (an as-built description or a retrospective); in that case write `Missing input: no decision found in input`.

```markdown
## Architecture Decision Record

Verdict: BLOCK

- Missing input: <no decision context or ADR provided / no decision found in input / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Input: "We picked Redis for session storage over Postgres and JWT-only sessions; main constraints were p99 < 5 ms and ops already runs Redis."

Selected output lines:

- Title: Use Redis for session storage
- Status: accepted

Under `### Options`:
- Redis — benefit: existing ops experience; cost: one more stateful service in the session path `(inferred)`
- Postgres sessions table — benefit: no new infrastructure `(inferred)`; cost: p99 < 5 ms budget at risk under load `(inferred)`
- JWT-only stateless sessions — benefit: no session store at all `(inferred)`; cost: revocation requires extra machinery `(inferred)`

Under `### Consequences`:
- Easier: meeting the p99 < 5 ms budget.
- Harder: session data is now bounded by Redis memory `(inferred)`; Redis outage logs everyone out `(inferred)`.

## Anti-Patterns

- One option, zero negative consequences, no revisit triggers — a justification document, not a record.
- Inventing options, drivers, or consequences the input does not support instead of marking gaps.
- Making the choice for the owner when the input names no decision and no leaning.
- Vague revisit triggers ("revisit if needed") instead of concrete conditions.
- Restating the decision as its own rationale ("we chose Redis because Redis fits best").

## Definition of Done

All eight contract fields are present, routed per the no-choice rule, or explicitly gapped under `### Contract gaps`; at least two options each carry a benefit and a cost, or the single-option gap is listed under `### Contract gaps`; at least one negative consequence is concrete; revisit triggers are concrete conditions; inferred content is marked `(inferred)`; and no decision was invented on the owner's behalf.
