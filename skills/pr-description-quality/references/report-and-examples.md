Read before emitting any report. Use the full form unless core Error handling requires reduced BLOCK.

# Report and examples

## Full report contract

Use exact markers and ordering shown below. Fence Title as text and Body as markdown; choose fences longer than payload backtick runs. Validate preserves safe supplied whitespace/text. An unrequested part has an empty fence and exactly `not-assessed — not requested`; do not draft it or imply whole-PR compliance.

Checks contains exactly two bullets, Title then Body. For requested parts use core statuses: compliant, rewritten, noncompliant, needs-author-input. Results are pass, the title-length pass note, or fail (reason). Include corrected defects in Findings even when final checks pass.

Findings uses `- Anchor: severity — detail`, with Title/Body/Input/Convention/Structure anchors. Include convention evidence when Title is requested and template/default evidence when Body is requested. For partial scope, add Input/information naming the requested and unassessed parts and the verdict limit. In title-only work use Structure: default as a report placeholder and state that body structure was not assessed; it does not require template discovery.

Input findings cover source-evidence limits and excluded content outside requested parts. Evidence limits use information unless they identify an unresolved required fact; apply the relevant part status then. Do not add a third check. A disclosure anywhere in readable input forces CONCERNS, even for unrequested parts; report sanitized locations only.

Needs author input lists all unresolved required facts, or `- None`. Empty Findings also uses `- None`. Do not request an unrequested counterpart simply because it is absent.

Verdict describes the assessed text, not whether an edit occurred. Passing rewritten text can be CLEAN with corrected error findings. Unresolved requested failures or any original disclosure yield CONCERNS. BLOCK has only the reduced form.

This complete illustrative draft report assumes supplied change evidence supports both payloads, no template is required and no disclosure occurred:

````markdown
## PR Description Quality Report
Verdict: CLEAN
Structure: default
### Title
```text
Keep empty commit lists in the cache
```
### Body
```markdown
Empty commit lists were fetched repeatedly because an empty cached result was treated as missing. Reuse the cached empty list so subsequent lookups avoid another request.
```
### Checks
- Title: rewritten — pass
- Body: rewritten — pass
### Findings
- Title: information — Created from supplied change evidence.
- Body: information — Created from supplied behavior evidence.
- Convention: information — Plain imperative default; no repository title rule or historical titles supplied.
- Structure: information — Default paragraph; no required template known and template discovery was unavailable.
### Needs author input
- None
````

## Reduced BLOCK

Emit exactly five lines. Inspect readable input for disclosures first. Request only missing input needed by the selected operation/scope or the unresolved relevant rule/template. Do not invent a candidate or substitute default for a known requirement.

```markdown
## PR Description Quality Report
Verdict: BLOCK
- Missing input: Concrete blocker.
- Smallest addition to proceed: Exact required input or selection.
- Disclosure: none
```

The values in Missing input and Smallest addition to proceed are placeholders. Replace them with concrete facts. If any readable input contains forbidden content, replace only the last line with exactly:

```text
- Disclosure: error — Forbidden content found in supplied input; excluded from output.
```

That last-line snippet is partial: the four preceding BLOCK lines remain mandatory; nothing follows it. Do not include occurrence locations or full-report sections in BLOCK.

## Decision examples

- “Audit this body” selects validate and Body only. Preserve safe Body; leave Title empty/not-assessed; explain the partial verdict.
- “Audit and rewrite this body” selects rewrite and Body only. Passing repaired Body can yield CLEAN; corrected defects remain in Findings.
- Validate a whole PR with no readable Title: BLOCK. Explicit body-only review with readable Body does not need Title.
- Draft a whole PR from usable changes: generate both parts. Missing routine validation results do not prevent CLEAN.
- A missing required relevant template yields BLOCK even with a safe draft. If forbidden content also occurs, use the fixed Disclosure error line.
- Without a caller retention request, optional Testing with no useful content is removed in rewrite; required/unmarked Testing is preserved. Unsupported required completion marks need correction; unknown required result fields need author input.
- A new unit-test assertion with no changed verification boundary needs no automated/manual or fixture/live inventory.
- Unsupported optional success claims: rewrite removes and records them; validate preserves safe text and requests evidence. A retained required claim still needs support.
- Passing rewritten Title and Body plus a secret elsewhere in supplied input: CONCERNS with sanitized Input/error, even though the output is redacted.
- No diff, but sufficient change description: record Input/information; do not claim repository inspection. That limitation alone does not force CONCERNS.
- Optional missing issue links are omitted; unresolved required identifiers need author input.
- Reverted breaking intent is not carried into final text. A current unknown `!` uses the title reference's requested-part rules.

## Regression cases

These are static input/expectation cases, not executed model evaluations.

Each case assumes readable repository/caller rules with no template or special title convention unless stated. Apply the output reference to every full report. “Passing” means supplied evidence supports the text and no other defect exists.

| ID | Input/request | Expected behavior |
|---|---|---|
| PRD-01 | Audit a passing whole PR without requesting repairs. | Validate; preserve safe text; compliant/pass for both; CLEAN. |
| PRD-02 | Audit and rewrite a body with redundant routine check results; useful behavior evidence supplied. | Rewrite Body only; omit routine inventory; Body rewritten/pass, Title not-assessed; CLEAN; record corrected error. |
| PRD-03 | Draft a whole PR from usable behavior/rationale evidence; no check results supplied. | Generate both passing parts; rewritten/pass; CLEAN; no missing-evidence notice or request. |
| PRD-04 | Rewrite Body using a template explicitly marking empty Testing optional. | Omit optional Testing; keep required sections; template structure. |
| PRD-05 | Same as PRD-04, but Testing is unmarked or required. | Preserve Testing; do not invent results. Request facts only if a required field requires them. |
| PRD-06 | Explicit caller request to retain an empty optional Testing heading. | Preserve the heading under caller retention override. |
| PRD-07 | Describe a pure unit-test assertion change with no coverage-boundary change. | Explain the assertion's behavior; no automated/manual or fixture/live inventory. |
| PRD-08 | Selected live checks become manual; reason supplied. | Explain changed verification boundary and rationale, fixture limits and remaining live verification only where affected. |
| PRD-09 | Same as PRD-08 but required removal rationale is unknown. | Body needs-author-input/fail; CONCERNS; request rationale, not routine check outputs. |
| PRD-10 | Review a passing body only; no Title supplied. | Validate Body compliant/pass; empty Title fence, not-assessed — not requested; CLEAN limited to Body. |
| PRD-11 | Review a passing title only; multiple unreadable body templates exist. | Do not discover/select Body templates; Title compliant/pass, Body not-assessed; CLEAN limited to Title; Structure default placeholder explained. |
| PRD-12 | Validate a whole PR, but Title is missing. | Five-line BLOCK requesting Title; do not silently narrow scope. |
| PRD-13 | Draft a one-outcome cache fix from supplied evidence. | A concise paragraph is valid; no mandatory Summary/Changes or Testing headings. |
| PRD-14 | Rewrite a supported short body containing an unsupported optional “all tests passed” claim. | Remove unsupported claim; record corrected error; Body rewritten/pass and CLEAN if no other issue. |
| PRD-15 | Validate the same unsupported success claim without repair. | Preserve safe claim; Body needs-author-input/fail and CONCERNS pending support. |
| PRD-16 | Supplied compatible-environment test fails for changed behavior. | Retain observed failure, relevant environment and consequence; no routine success inventory. |
| PRD-17 | Passing rewrite, but forbidden content appeared elsewhere in supplied input. | Redact; sanitized Input/error; CONCERNS despite passing requested parts. |
| PRD-18 | Missing required relevant template and forbidden content co-occur. | Five-line BLOCK; fixed generic Disclosure error line, no locations or secret values. |
| PRD-19 | Rewrite both parts successfully after correcting a substantive description defect. | rewritten/pass; CLEAN; corrected error findings remain visible. |
| PRD-20 | Default title selection with three of five supplied conventional titles; then two of four. | Conventional mode first; plain mode for tie. Body template fallback does not change title selection. |
| PRD-21 | Validate a body containing an empty explicitly optional Testing heading; no repair requested. | Preserve safe Body including the heading; report the relevance violation; Body noncompliant/fail and CONCERNS. |
| PRD-22 | Title-only review passes, but supplied unrequested Body contains forbidden content. | Empty Body fence with not-assessed; sanitized Input/error; CONCERNS despite passing Title. |

These cases define maintenance expectations through existing rules. They do not authorize live model/API calls or establish runtime/model compatibility.
