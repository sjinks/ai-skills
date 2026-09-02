# Construction Handoff Validation

Use this reference only when portability follows a mixed request or a completed construction workflow. Direct portability-only code reviews do not require an SCC result.

## Routing

1. If shell construction is within the construction skill's catalogued scope, construction review owns the first response.
2. If correction depends on excluded domain-specific interface semantics, that interface workflow owns the first response. Review portability only after it supplies an exact corrected command; treat that command as direct code without requiring an SCC result.
3. If no concrete command, executable, fragment, or payload interface exists, request one before portability review.
4. For a supplied SCC result, validate the envelope and candidate below before any portability analysis.

## Envelope validation

Require exactly one complete result with these top-level fields in order:

1. `Construction result: BLOCKED | VALID | REWRITE`
2. `Construction assessment: <nonblank one-line value>`
3. `Candidate: <value>`
4. `Execution authority: NOT ASSESSED BY THIS SKILL`
5. `Next step: <nonblank one-line value>`

Missing, unknown, reordered, duplicated, or blank fields make the handoff malformed.

## Candidate consistency

- `BLOCKED` requires exact `Candidate: Not provided`.
- `VALID` and `REWRITE` forbid that placeholder, including trailing-whitespace variants.
- A one-line candidate must be nonblank. If its first non-whitespace character is `|`, later non-whitespace text must occur on the same line.
- Only exact `Candidate: |` with no trailing whitespace opens multiline form. Every payload line must have the two-space serialization prefix, and at least one decoded payload line must contain non-whitespace text.

## Multiline decoding

Remove exactly the first two spaces from each payload line. Preserve additional indentation and serialized empty lines. Only unprefixed `Execution authority: NOT ASSESSED BY THIS SKILL` validly terminates payload. If another SCC field appears unprefixed first, or a payload line lacks its prefix, the handoff is malformed; do not truncate or analyze altered text.

## Outcome

- For any malformed or inconsistent handoff, use the reduced insufficient-context `BLOCK` template and request a corrected SCC result.
- For a consistent `BLOCKED` result, use reduced `BLOCK` and request completion of construction.
- For a consistent `VALID` or `REWRITE` result, review only the exact decoded candidate and make no construction claim.
