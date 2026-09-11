Read this reference when portability review begins from a mixed request or a prior construction handoff instead of direct shell code.

# Construction Handoff Validation

## Routing

1. If shell construction is within the catalogued construction scope, construction review owns the first response.
2. If correction depends on excluded domain-specific interface semantics, that interface workflow owns the first response. Review portability only after it supplies an exact corrected command; treat that command as direct code without requiring a prior construction result.
3. If no concrete command, executable, fragment, or payload interface exists, request one before portability review.
4. For a supplied construction result, extract and validate the contiguous handoff block below before any portability analysis.

## Envelope validation

Require exactly one complete result with these top-level fields in order:

1. `Construction result: VALID | REWRITE | BLOCKED`
2. `Construction assessment: <nonblank one-line value>`
3. `Candidate: <value>`
4. `Execution authority: NOT ASSESSED BY THIS SKILL`
5. `Next step: <nonblank one-line value>`

When the caller embeds a construction result inside surrounding prose, the handoff is the contiguous nonblank block that starts at the `Construction result:` line and ends immediately after the `Next step:` line, with zero or one terminal newline inside that block. Nonblank prose may appear before that start marker without a blank separator. A nonblank line immediately after `Next step:` is adjacent handoff content, not surrounding prose. Inside or adjacent to the block, code fences, blank or free-form lines between top-level fields, trailing prose after `Next step:`, and any other extra unprefixed line make it malformed. Multiline candidate payload is the only allowed intervening block and follows the rules below.

Missing, unknown, reordered, duplicated, or blank fields make the handoff malformed.

## Candidate consistency

- `BLOCKED` requires exact `Candidate: Not provided`.
- `VALID` and `REWRITE` forbid that inline placeholder, including trailing-whitespace variants.
- If the exact one-line candidate text is `Not provided` for `VALID` or `REWRITE`, canonical serialization is block form:
  ```text
  Candidate: |
    Not provided
  ```
- A one-line candidate must be nonblank. If its first non-whitespace character is `|`, later non-whitespace text must occur on the same line.
- Only exact `Candidate: |` with no trailing whitespace opens multiline form. Every payload line must have the two-space serialization prefix, and at least one decoded payload line must contain non-whitespace text.

## Multiline decoding

Remove exactly the first two spaces from each payload line. Preserve additional indentation and serialized empty lines. Only unprefixed `Execution authority: NOT ASSESSED BY THIS SKILL` validly terminates payload. If another result field appears unprefixed first, or a payload line lacks its prefix, the handoff is malformed; do not truncate or analyze altered text.

## Outcome

- For any malformed or inconsistent handoff, use the reduced insufficient-context `BLOCK` template and request a corrected construction result.
- For a consistent `BLOCKED` result, use reduced `BLOCK` and request completion of construction.
- For a consistent `VALID` or `REWRITE` result, review only the exact decoded candidate and make no construction claim.
