---
name: dependency-choice-review
description: "Use when: deciding at design time whether to build, buy, or adopt a library, framework, service, or platform dependency: maintenance signals, API stability, lock-in and exit cost, operational burden, license fit, and the conditions under which the choice should be reversed."
argument-hint: "The capability needed, the candidate dependencies or the build option, and project constraints (license policy, stack, team capacity)."
user-invocable: true
---

# Dependency Choice Review

Decide whether to take on a dependency before it is woven into the design. A dependency is a long-term operational and social commitment priced as a one-line install command; the real costs are maintenance risk, lock-in, and the exit nobody planned.

## When to Use

Use at design time, when a capability could be met by adopting a library, framework, service, or platform — or by building it — and the choice needs structured review. "Buy" is the adopt path with a commercial service or platform as the candidate. Out of scope: auditing an existing dependency tree for vulnerabilities or license violations in a release context, version-upgrade decisions for dependencies already adopted, runtime vendor incident response, negotiating commercial terms, and multi-attribute comparison of whole candidate architectures.

## Required Inputs

- The capability needed, in one or two sentences.
- The candidate or candidates: named dependencies, services, or the build option. A single named candidate is valid input: add `build` as the second table column and say so on the Candidates line; the review then judges adopt-vs-build rather than ranking candidates.
- Project constraints when supplied: license policy, existing stack, team capacity, compliance needs.

If no capability or no candidate is provided, emit the BLOCK template; do not invent candidates.

## Review Dimensions

Assess each candidate on six dimensions. Score each dimension `ok`, `concern`, or `unknown`; every `concern` and `unknown` carries a one-line note (evidence, or the missing evidence named) under `### Dimension notes` — `ok` cells need no note.

1. `maintenance-health`: release cadence, responsiveness to issues, bus factor, governance. For services: vendor viability signals in the input.
2. `api-stability`: breaking-change history and policy, deprecation discipline, version maturity.
3. `fit`: how much of the need it covers, and how much of it you would actually use; both 10% coverage and 10x oversize are findings.
4. `lock-in-and-exit`: what adopting couples you to (data formats, proprietary APIs, ecosystem), and what leaving would cost; name the concrete exit path or its absence.
5. `operational-burden`: what running it demands — hosting, upgrades, monitoring, expertise the team does or does not have.
6. `license-and-policy`: license compatibility with the project's stated policy; flag copyleft/source-available/commercial terms against supplied constraints. When no policy is supplied, name the license and mark policy fit `unknown`.

The build option, when in scope, is assessed on the same dimensions (its `maintenance-health` and `operational-burden` are your team's). The build option's exit path is the cost of replacing the built component with an adopted dependency later, plus decommissioning what was built.

## Rules

- Use only evidence in the input or facts you can state with confidence and attribute; mark internet-era facts that may have changed with exactly `(as of input/knowledge — verify)`, optionally followed by the concrete verification step. Unverifiable claims are `unknown`, not guesses.
- Every `concern` is concrete: "last release 26 months ago", not "seems unmaintained".
- Exit cost is stated even for the recommended candidate; recommending without an exit path is a finding against the recommendation, to be stated in it.
- Constraints are pass/fail: a candidate violating a hard constraint (license policy, compliance) is excluded from the recommendation but keeps its normally scored cells in the table; the `eliminated: <constraint>` mark lives on its `### Dimension notes` line for the violated dimension.
- The choice belongs to the owner: end with a recommendation or the deciding question. With a recommendation, write reversal triggers for the recommended candidate; with a deciding question, write reversal triggers per candidate-if-chosen.
- The recommendation's reason is grounded in the decisive dimension scores.
- Evidence gaps that block a responsible choice go under `### Evidence needed` with the cheapest way to settle each (changelog read, spike, vendor question).

## Output Format

```markdown
## Dependency Choice Review

- Capability: <one sentence>
- Candidates: <list, including `build` when in scope>
- Constraints: <pass/fail constraints, or `none supplied`>

| Dimension | <candidate A> | <candidate B> |
|-----------|---------------|---------------|
| maintenance-health | ok \| concern \| unknown | ok \| concern \| unknown |
| api-stability | ok \| concern \| unknown | ok \| concern \| unknown |
| fit | ok \| concern \| unknown | ok \| concern \| unknown |
| lock-in-and-exit | ok \| concern \| unknown | ok \| concern \| unknown |
| operational-burden | ok \| concern \| unknown | ok \| concern \| unknown |
| license-and-policy | ok \| concern \| unknown | ok \| concern \| unknown |

### Dimension notes

- <dimension> / <candidate>: <one-line evidence for every concern and unknown; eliminated: <constraint> when applicable>

### Exit paths

- <candidate>: <concrete exit path and its cost, or `no credible exit path`>

### Evidence needed

- <unknown>: <cheapest way to settle it>

### Recommendation

<recommended candidate with the reason grounded in the decisive dimension scores and its stated exit cost — or the deciding question>

### Reversal triggers

- <concrete condition that should reopen this choice>
```

Empty sections are written with `None`. The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Dependency Choice Review

Verdict: BLOCK

- Missing input: <no capability or candidates provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Capability: PDF invoice rendering. Candidates: library `pdfkit-like` (input says: active releases, MIT) vs. SaaS render API (input says: per-document pricing, proprietary template format).

Sample dimension notes:

- lock-in-and-exit / SaaS render API: concern — templates are written in the vendor's proprietary format; exit means rewriting every template.
- operational-burden / pdfkit-like: concern — rendering moves in-process; memory spikes on large invoices become your pager's problem `(as of input/knowledge — verify)` with a load spike.

Under `### Reversal triggers`:

- Library: release cadence stops for 12+ months, or invoice volume outgrows in-process rendering.
- SaaS: per-document cost crosses the supplied budget line, or the vendor deprecates the template format.

## Anti-Patterns

- Hype-based scoring ("popular, should be fine") instead of evidence per dimension.
- Recommending a candidate without stating its exit cost.
- Treating license policy as a soft score instead of pass/fail elimination.
- Ignoring the build option's own maintenance and operational dimensions.
- Guessing maintenance facts instead of marking them `unknown` with a verification step.
- A recommendation with no reversal triggers — the choice that can never be revisited.

## Definition of Done

Every candidate is scored on all six dimensions with exactly one score value, every `concern` and `unknown` has a one-line note, every candidate has an exit-path line, constraint violations eliminate rather than down-score, every `unknown` maps to an `### Evidence needed` entry, and the report ends with a recommendation or deciding question plus concrete reversal triggers.
