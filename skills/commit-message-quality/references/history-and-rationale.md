Read when calibrating standalone usefulness, body necessity or final squash scope. All examples assume supplied evidence establishes their facts; they are illustrations, not executed tests or claims about a particular repository.

# Messages that survive the PR

Code blocks illustrate message text, not complete quality reports.

## Preserve consequences and decisions

An activity summary such as “align review scope and quality verdicts” does not preserve which outcomes changed. Given evidence of unwanted audit rewriting and edit-based failure verdicts, a more useful message is:

```text
fix(descriptions): separate edits from quality failures

Audits could rewrite supplied text, and repaired descriptions always
received CONCERNS even when no problem remained. Partial reviews also
required an unrelated title or body.

Preserve safe text during audits and assess the requested parts.
Passing repairs can return CLEAN while corrected defects remain in
Findings. Mark unrequested parts as not-assessed.
```

The body records motivation, before/after behavior and exact status names that help a human or LLM interpret the contract later. It does not require a PR link to explain the decision. If migration effects for report consumers matter and are established, include them too.

For a security fix, preserve the invariant that a future refactor must respect. Given the relevant evidence:

```text
fix(approval): scope file decisions to each pull request

Two PRs can share a head commit while using different bases. Approval of
a nonfunctional change in one PR could suppress findings for a functional
change to the same file in the other.

Key approval reasons by PR and filename so one PR cannot determine the
other PR's eligibility or remove its findings.
```

This explains why the extra key dimension matters. “Update every producer and consumer” alone would describe implementation work without preserving that reason.

## Explain the interception boundary

Given evidence that live service data, credentials and rate limits destabilize tests, and that retry logic must remain exercised:

```text
test(api): replay responses below the HTTP client

Live API data, credentials and rate limits made client tests depend on
external services. Replay responses at the cURL boundary so the existing
client parsing and retry paths still run.

Keep real transport available through explicit live mode for checking
service compatibility. Offline results do not establish that live service
schemas remain compatible.
```

The boundary and limitation explain a consequential design choice. “Add fixtures” or a passing-suite inventory would not preserve that distinction. Include rejected approaches only if their comparison is needed and supported; do not invent why an author rejected them.

## Scale the body to missing information

A supplied change only corrects the spelling of “configuration” in help text, without another consequential decision. This subject can stand alone:

```text
docs(cli): correct the spelling of configuration in help
```

Body uses `n/a (not needed)`, with compliant status for an already absent or intentionally omitted body. A filler body such as “No functional change.” adds no explanation. Conversely, a one-line change that raises a resource limit may need a body explaining the evidenced failure, reason for the limit and compatibility effect. Small diff size does not establish body sufficiency.

Routine “all tests passed” text is omitted by default. Preserve a regression scenario when it explains the defect: for example, two PRs sharing a head but differing in base must retain independent approval decisions. Describe what the scenario establishes without claiming that a test ran unless execution evidence is supplied.

## Describe the surviving squash

Suppose an earlier commit mocks high-level HTTP helpers, then a later commit switches to cURL replay to retain retry coverage. An individual message describes its own change. A squash message describes the final replay boundary and retains the supported reason for it. It does not claim both approaches remain active or concatenate the sequence of review fixes.

If the final combined diff is unavailable and supplied messages disagree about the surviving approach, request the final scope or author clarification. Do not choose the earliest or latest message as proof of final behavior.

## Static regression cases

These are maintenance expectations, not measured model results:

| Case | Supplied situation | Expected decision |
|---|---|---|
| CMH-01 | Motivation exists only behind an issue number. | Add supported problem/impact/decision context; request missing required facts instead of copying the link as the explanation. |
| CMH-02 | Subject says “align behavior”; evidence identifies changed verdicts. | Name the observable result and preserve relevant exact status names. |
| CMH-03 | Self-contained spelling-correction subject, no other context needed. | Permit absent Body with `n/a (not needed)` unless selected rules require a body. |
| CMH-04 | One-line size-limit change with consequential rationale missing. | Request required rationale; do not treat a small diff as sufficient context. |
| CMH-05 | A required body rule applies despite a self-contained subject. | Include the required body; absence fails rather than receiving an omission pass. |
| CMH-06 | Routine passing checks and counts accompany supported change facts. | Omit the routine inventory; no checks are requested merely to fill a body. |
| CMH-07 | A supplied regression scenario explains cross-PR approval isolation. | Retain its input conditions and intended invariant; distinguish coverage from executed results. |
| CMH-08 | Earlier messages describe an approach removed by the combined diff. | Describe surviving behavior and retain only still-relevant rationale. |
| CMH-09 | Source messages disagree and final combined evidence is unavailable. | Request scope/clarification; do not invent a surviving approach. |
| CMH-10 | Rejected alternatives are unknown and comparison is unnecessary. | Omit the comparison without inventing deliberation. |
| CMH-11 | Validate an otherwise well-formatted message missing evidenced consequential context. | Preserve safe text and report the content omission, rather than passing it on grammar alone. |
| CMH-12 | Repair a message containing unsupported optional runtime-success claims. | Omit the unsupported claims and record corrections; preserve required factual gaps. |
| CMH-13 | Draft a test-runner migration; supplied facts say a routine build passed but the replacement suite was not run. | Omit routine build success; retain the unverified runner migration and its consequence. Do not invent a prior failure or claim the suite ran. Passing drafted parts remain rewritten and the verdict remains CONCERNS. |
| CMH-14 | Supplied scope also changes license metadata and removes reports that supplied workflow evidence still requires. | Preserve these separate consequences without a file inventory or invented author rationale. A split recommendation does not silently narrow the returned message. |
