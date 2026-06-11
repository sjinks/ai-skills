---
name: scope-boundary-definition
description: "Use when: defining or auditing the scope of a feature, project, spec, or task: explicit in-scope and out-of-scope lists, non-goals, deferred items, smallest valuable slice, and scope-creep risks, before work is planned or estimated."
argument-hint: "The feature description, spec, or task text whose scope needs boundaries, plus any constraints, deadlines, or stakeholder asks already known."
user-invocable: true
---

# Scope Boundary Definition

Make a piece of work's boundaries explicit before it is planned: what is in, what is out, what is deliberately not a goal, what is deferred, and what the smallest valuable slice is. Undeclared boundaries become scope creep during the build and "I assumed that was included" disputes at delivery.

## When to Use

Use when a feature, spec, project, or task needs its scope made explicit or an existing scope statement audited, before planning or estimation. Out of scope: splitting an already-written code change into reviewable pieces, prioritizing a backlog across multiple features, and making the product call on what should be in scope (the skill surfaces the decisions; the owner makes them).

## Required Inputs

- The feature description, spec, or task text.
- In audit mode, the existing scope statement to audit.
- Known constraints (deadline, team size, dependencies, compliance) when supplied.
- Stakeholder asks or adjacent requests already floating around the work, when supplied.

If no description is provided, emit the BLOCK template; do not invent the work item.

## Boundary Lists

Produce four lists. Every item is one line and names a capability, behavior, or artifact — not a vague theme.

1. In scope: what this work delivers. Each item should be traceable to the supplied description; flag any item you inferred rather than read.
2. Out of scope: adjacent things a reasonable stakeholder might assume are included but are not. Each carries a one-line reason (different owner, later phase, separate decision).
3. Non-goals: things this work deliberately does not optimize for, even where it touches them ("not optimizing for >10k concurrent users", "not redesigning the settings UI it links from").
4. Deferred: in-principle in scope but consciously pushed to a later iteration, each with the trigger or milestone that revisits it.

An item appears in exactly one list. When the supplied text does not settle which list an item belongs to, it becomes a boundary decision (below), not a silent placement.

## Smallest Valuable Slice

Identify the smallest subset of the in-scope list that delivers observable user or system value on its own. Name what it includes, what it proves, and which in-scope items it leaves for later slices. If no subset smaller than the whole is valuable, say so and why.

## Creep Risks

List the 3–5 most likely scope-creep vectors: stakeholder asks already hovering, "while we're in there" temptations adjacent to the touched surface, and out-of-scope items most likely to be mistaken for in-scope. One line each, with the boundary statement that pre-empts it.

## Output Format

```markdown
## Scope Boundary Report

- Work item: <one sentence>
- Constraints considered: <list or none supplied>

### In scope

- <item>

### Out of scope

- <item> — <reason>

### Non-goals

- <item>

### Deferred

- <item> — revisit when <trigger>

### Smallest valuable slice

- Includes: <items>
- Proves: <value delivered>
- Leaves for later: <items>

### Boundary decisions needed

- <item, the two lists it could belong to, who decides>

### Creep risks

- <vector> — pre-empted by: <boundary statement>
```

Empty sections are written with `None`. When no smaller subset is valuable, replace the three `### Smallest valuable slice` bullets with the single line `- No smaller valuable slice: <reason>`. Append exactly ` (inferred)` to any in-scope item not read directly from the description; items read directly carry no `(inferred)` suffix.

Audit mode (an existing scope statement was supplied): append a delta mark to each existing item inside its list — ` [kept]`, ` [moved from <list>]`, or ` [split: → items <n>, <m>]`; `<list>` is one of the exact heading labels `in scope`, `out of scope`, `non-goals`, `deferred`. Items produced by a split are listed as normal items with ` [from split of <original item>]`. New items you add carry no delta mark. When an item earns both suffixes, `(inferred)` comes first, then the delta mark: `- <item> (inferred) [moved from in scope]`.

The report has no verdict line; `Verdict: BLOCK` appears only in the insufficient-input template below.

## Error Handling (BLOCK Template)

Use this reduced template only for missing or unreadable input.

```markdown
## Scope Boundary Report

Verdict: BLOCK

- Missing input: <no work-item description provided / text unreadable>
- Smallest addition to proceed: <concrete ask>
```

## Example

Work item: in-app notifications for @-mentions. Marketing has asked for email digests "since we're doing notifications anyway".

- In scope: bell-menu notification on @-mention; unread count on the bell.
- Out of scope: email digests — different delivery channel, marketing owns the ask.
- Deferred: notification preferences — revisit when more than one notification type exists.
- Creep risk: email digests — pre-empted by: "this work delivers in-app delivery only; email is a separate decision."

Audit-mode line: `- CSV export of contacts [kept]` / `- Export scheduling [moved from in scope] — sales ask, owner undecided`.

## Anti-Patterns

- Silently placing an item the supplied text does not settle, instead of raising a boundary decision.
- Vague list items ("improve performance") instead of named capabilities or artifacts.
- An out-of-scope list of strawmen nobody would assume included, while real adjacent asks go unmentioned.
- Making the product call on a contested item instead of naming who decides.
- Treating the smallest valuable slice as a delivery commitment rather than a scoping observation.

## Definition of Done

All four lists are populated or explicitly `None`, every item sits in exactly one list, inferred items are flagged, a smallest valuable slice is named or ruled out with a reason, creep risks and boundary decisions are populated or explicitly `None`, and unresolved placements appear under boundary decisions rather than being guessed.
