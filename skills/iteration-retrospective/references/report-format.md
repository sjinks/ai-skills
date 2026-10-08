Read this reference before classifying attempts, selecting a skill candidate, or formatting the report.

# Decision and Report Rules

## Workflow

1. State the goal, success condition, scope, and evidence available.
2. Build the attempt timeline in chronological order. For every supplied attempt, record action, result, and evidence. Use `unknown` for an unavailable action or result and `unavailable` for missing evidence.
3. Classify each attempt using Attempt Status. Preserve a known outcome even when a later attempt replaces the approach.
4. In non-`BLOCK` reports, failed or partly-worked attempts require learning rows recording cause confidence as `confirmed`, `likely`, or `unknown`. Use `confirmed` for a cause established by evidence, `likely` for an evidence-supported hypothesis, and `unknown` when evidence cannot support a cause. If no causal lesson is supported, record the observed failure pattern with `Cause: unknown`. Do not turn correlation into cause.
5. Group failures that evidence attributes to the same cause. If the cause is unknown, record the repeated failure pattern without assigning a shared cause. Prefer correcting an established cause over treating its symptoms.
6. If the `BLOCK` condition in Verdict Selection holds, use the blocked report without selecting prevention. Otherwise, for each distinct failure pattern, consider only mechanisms that address the evidenced failure. For environment-related patterns, apply the Environment Prevention reference before comparing mechanisms; its lenses do not change the cost ordering or eligibility below. Choose the mechanism with the fewest new dependencies. If dependency counts tie, choose the mechanism with the fewest new workflow steps. If both counts tie, choose the first applicable mechanism in this list:
   - deterministic check for mechanically detectable recurrence;
   - shared helper for repeated mechanical implementation;
   - repository guidance for local workflow recurrence;
   - refactor for duplication or drift, including a source-of-truth change;
   - reusable skill only when every New Skill Eligibility condition holds.
   Use only evidenced costs in these comparisons. A sole applicable mechanism requires no comparison. With several applicable mechanisms, if missing dependency or step counts prevent establishing a unique choice, leave that pattern unselected, record the needed cost evidence under `Retrospective Next Checks`, and use `CONCERNS`. Do not invent counts or apply the list order before establishing both ties. Preserve selections for other patterns. If no mechanism is selected for any pattern, use `None.` under `Retrospective Prevention`. Otherwise, report only selected mechanisms. Record any pattern without supported prevention under `Retrospective Next Checks`.
7. List concrete next checks and any unresolved uncertainty. Finish after the Completion Checklist passes; do not perform the proposed follow-up work without an explicit caller request.

## Verdict Selection

Select the verdict using the first applicable rule:

1. If the goal is unavailable, no attempt can be reconstructed, or no outcome can be established, use `BLOCK`.
2. If an unresolved cause, prevention decision, or validation gap could change the lesson or next action, use `CONCERNS`.
3. Otherwise, use `CLEAN`.

Missing evidence for one attempt does not require `BLOCK` when another attempt supports analysis. Preserve the missing values and assess their effect using Verdict Selection.

## Attempt Status

Apply the following rules in order against each attempt's stated or evidence-supported success condition:

- If evidence establishes that the attempt met its success condition, use `worked`.
- If evidence establishes that the attempt met only part of its success condition, use `partly-worked`.
- If evidence establishes that the attempt failed its success condition without partial success, use `failed`.
- If no outcome can be established and evidence shows that another approach replaced the attempt before evaluation, use `superseded`.
- Otherwise, use `inconclusive`. Missing action, result, evidence, or success criteria must not be inferred.

## New Skill Eligibility

Apply eligibility to the failure pattern addressed by the proposed skill. Consider a reusable skill only when every condition holds:

- The lesson is neither unique to the incident nor speculative.
- At least two independent, evidence-backed instances show the same decision failure. Successive attempts within one incident count as one instance.
- The decision procedure is stable and requires judgment that a deterministic check cannot replace.
- The inputs and outputs are portable across repositories.
- Evidence supports recurrence across repositories and identifies a concrete consequence of recurrence.
- No deterministic check, shared helper, repository guidance, or refactor resolves the failure.

## Skill Candidate Selection

Select the candidate after selecting prevention mechanisms and finalizing the verdict. For `BLOCK`, use `not assessed` without selecting a prevention mechanism.

For non-`BLOCK` reports, apply the first matching rule:

1. If any selected prevention mechanism is `reusable skill`, use `new skill`.
2. If any selected prevention mechanism is `repository guidance` and updates an established workflow's guidance, use `extend existing guidance`.
3. Otherwise, use `no new skill`. This includes new repository guidance and reports with no supported prevention.

An unselected guidance update does not change the candidate. For reports with several prevention rows, evaluate these rules across all selected rows.

## Missing Evidence

If an evidence source is unavailable, record the missing values. Apply Verdict Selection to choose between partial analysis and `BLOCK`. Do not invent a replacement source or result.

## Report Format

Emit one plain-text report or label clarification as selected below. Do not add a code fence, introduction, or trailing prose. Blank lines between response lines are permitted.

### Markers and labels

Use each top-level marker from the Output template exactly once, in the template order. Keep `Retrospective`, `Retrospective Assessment`, `Retrospective Skill Candidate`, and `Retrospective Verdict` values on their marker lines. Put section contents after their section markers.

Select the verdict before validating caller labels. For `BLOCK`, use all default labels regardless of caller replacements; do not request label clarification.

For a non-`BLOCK` report, the caller may replace any top-level label with a distinct, nonempty, single-line label (no C0/C1 control characters: U+0000–U+001F and U+007F–U+009F; no Unicode line separators U+2028/U+2029) with exactly one `:` at its end. Keep unreplaced labels unchanged. Preserve caller labels exactly. Replacement labels must not duplicate another active label or start with `- `, which denotes report rows. Labels do not change row fields, enum values, requiredness, or order.

If nonblocked caller labels violate these constraints, emit only `Retrospective Label Conflict:` with a nonempty explanation of the violated constraint, followed by `Retrospective Label Request:` with a nonempty request for valid replacement labels. Each marker occurs once, with its value on the same line; the request line terminates the response. Do not emit report markers, rows, candidate, or verdict. Stop pending valid labels. This clarification uses fixed labels; caller replacements do not apply to it.

### Rows and empty sections

Write each row on one line. Use ` | ` between fields. Do not put the literal `|` or a line break inside a field value; paraphrase or cite the source instead. Field values must be nonempty.

Number rows consecutively from 1 within each section, using `A`, `L`, `P`, or `N` as shown in the Output template. Emit one timeline row per supplied attempt in chronological order, except when the blocked-timeline rule applies. A report with no supplied attempts must use `BLOCK` and the blocked-timeline rule.

Choose one status per attempt from Attempt Status. Choose one cause confidence per learning from Workflow. The template values `worked` and `confirmed` are illustrations.

For non-`BLOCK` reports with any `failed` or `partly-worked` attempt, learning rows are required. Otherwise, use learning rows when supported or `None.`. Use prevention rows for selected mechanisms or `None.` when none is selected, including unresolved cost comparisons. `CONCERNS` requires next-check rows describing unresolved gaps. `CLEAN` permits next-check rows or `None.` when no further check remains. Do not use `Not assessed.` in these sections of a non-`BLOCK` report.

For `BLOCK`, retain supported timeline rows with the normal missing-value representation. If no supplied attempt can be reconstructed, use `Not assessed.` instead of timeline rows. Under `Retrospective Learnings`, write exactly one line beginning `Missing:` that identifies the smallest missing evidence needed. Use `Not assessed.` under `Retrospective Prevention`. Under `Retrospective Next Checks`, write one or more normal `N` rows naming how to obtain the missing evidence. If the goal is unavailable, use `Retrospective: Not assessed.`. Begin the assessment with `Not assessed.` and explain the blocker on that line.

### Domains and termination

Use one of these `Mechanism` values: `deterministic check`, `shared helper`, `repository guidance`, `refactor`, `reusable skill`. Classify a test as `deterministic check`. Classify an update to existing guidance as `repository guidance`. Classify a source-of-truth change as `refactor`.

Use `Retrospective Skill Candidate: not assessed` only for `BLOCK`. Otherwise, use `new skill`, `extend existing guidance`, or `no new skill` according to Skill Candidate Selection.

Use `CLEAN`, `CONCERNS`, or `BLOCK` for the verdict. The verdict line must be the final nonblank line.
