---
name: architecture-tradeoff-analysis
description: "Use when: comparing two or more candidate architectures, designs, or technical approaches against weighted quality attributes: performance, consistency and correctness, operability, cost, evolvability, team fit — making what each option worsens explicit before the choice is made."
argument-hint: "The candidate options, the quality attributes that matter with any known weights, and the constraints the choice must respect."
user-invocable: true
---

# Architecture Tradeoff Analysis

Compare candidate architectures against the quality attributes that actually matter, with every option's costs stated as plainly as its benefits. A comparison where one option has no downsides is advocacy; the downsides exist whether or not they are written down.

## When to Use

Use when two or more candidate architectures, designs, or technical approaches need a structured comparison before a decision. Out of scope: recording the decision after it is made (a decision-record activity, not a comparison), single build-vs-adopt dependency decisions judged on maintenance, license, and exit dimensions, inventing candidate options the input does not name beyond the explicit `do-nothing` baseline rule below, running benchmarks or spikes to produce evidence, and product prioritization between features.

## Required Inputs

- Two or more candidate options, named in the input. When only one option is supplied, add `do-nothing` (keep the current state) as the baseline second option and say so; if the input explicitly rules the baseline out, emit the BLOCK template asking for a second real option.
- The quality attributes that matter for this choice, with weights when supplied.
- Constraints the choice must respect (budget, deadline, compliance, existing stack), when supplied.

If no options are provided at all, emit the BLOCK template; do not invent candidates.

## Attribute Set

Score against the attributes the input names. When the input names none, use this default set: `performance`, `consistency-and-correctness`, `operability`, `cost`, `evolvability`, `team-fit`. The `Attribute set:` header line discloses whether the set was supplied or defaulted and names any dropped default with its one-line reason; add input-specific attributes freely.

Weights: use supplied weights verbatim. When none are supplied, mark every attribute `weight: unstated` and do not invent a ranking between attributes. Without weights, recommend only when one option is at least as good on every attribute and better on at least one; otherwise report the per-attribute split and the deciding question.

## Scoring

Per option per attribute, assign exactly one of:

- `strong`: clearly better than the other options here, with the evidence or reasoning stated.
- `adequate`: meets the need; neither differentiator nor risk.
- `weak`: materially worse here; the concrete cost is stated.
- `unknown`: the input gives no basis to judge; name what evidence would settle it.

Every `unknown` cell gets a `### Score rationale` line naming the missing basis and a matching `### Evidence needed` entry naming the cheapest way to settle it.

Every option must have at least one `weak` or `unknown` cell, including a `do-nothing` baseline. When every named attribute genuinely scores strong/adequate on evidence, do not corrupt a cell: add the input-specific attribute that carries the option's real cost (every option has one — migration effort, opportunity cost, complexity) and score it there.

## Rules

- Score only on evidence or reasoning the input supports; `unknown` is the honest cell, not a failure.
- The "what this option makes worse" line per option is mandatory and concrete.
- Constraints are pass/fail, not scores: an option that violates a hard constraint is excluded from the recommendation but keeps its normally scored cells in the table; the `eliminated: <constraint>` mark lives on its `### Per-option costs` line.
- Recommend only when the scores and weights support a recommendation; with unstated weights and split per-attribute outcomes, report the split and the deciding question instead of forcing a winner.
- The decision itself belongs to the owner: the output ends with a recommendation or a deciding question, never with "decided".
- Evidence gaps that block a responsible choice go under `### Evidence needed`, each with the cheapest way to get the evidence (spike, load test, reference check).

## Output Format

```markdown
## Architecture Tradeoff Analysis

- Choice: <one sentence: what is being decided>
- Constraints: <pass/fail constraints, or `none supplied`>
- Attribute set: <supplied | default (input named none); dropped: <attribute — reason>, or `none dropped`>
- Attributes and weights: <attribute: weight | unstated>
- Options: <list; note when `do-nothing` was added as baseline>

| Attribute | <option A> | <option B> |
|-----------|------------|------------|
| <attribute> | strong \| adequate \| weak \| unknown | strong \| adequate \| weak \| unknown |

### Per-option costs

- <option>: makes worse — <concrete cost>; eliminated: <constraint, when applicable>

### Score rationale

- <attribute> / <option>: <evidence or reasoning for non-adequate cells>

### Evidence needed

- <unknown cell>: <cheapest way to settle it>

### Recommendation

<recommended option with the reason grounded in the decisive attribute scores and weights — or the deciding question and what answer picks which option>
```

Empty sections are written with `None`. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input, or a single supplied option with the `do-nothing` baseline explicitly ruled out.

```markdown
## Architecture Tradeoff Analysis

Verdict: BLOCK

- Missing input: <no options provided / single option with baseline ruled out / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Choice: order-history storage — keep rows in the orders table vs. event-sourced history. Attributes supplied: query flexibility (high), write throughput (medium), operability (high).

Sample table column outcomes: event sourcing scores `strong` on write throughput, `weak` on operability ("projection rebuild tooling does not exist here yet — must be built and operated"), `unknown` on query flexibility ("depends on projection design; a one-day projection spike settles it").

Under `### Per-option costs`:

- table rows: makes worse — write throughput stays bounded by the single table's measured ceiling.
- event sourcing: makes worse — operability; projection rebuild tooling must be built and operated.

Under `### Recommendation`:

The deciding question is operability cost versus write-throughput need: if peak write load stays under the current table's measured ceiling, keep table rows; if the supplied growth forecast is firm, event sourcing wins on throughput and the projection spike under `### Evidence needed` should run before committing.

## Anti-Patterns

- An option column with no `weak` or `unknown` cell — advocacy, not analysis.
- Inventing weights or evidence to force a single winner.
- Down-ranking an option that violates a hard constraint instead of marking it `eliminated` on its costs line.
- Strawman options included only to lose.
- Burying the recommendation's deciding factor instead of naming it in one line.
- Declaring the decision made instead of leaving it with the owner.

## Definition of Done

Every option is scored on every attribute with exactly one score value, every option has at least one `weak` or `unknown` cell and a concrete makes-worse line, non-adequate cells have rationale, constraint violations eliminate rather than down-score, `unknown` cells map to `### Evidence needed` entries, and the report ends with a recommendation or deciding question — not a decision.
