---
name: requirement-sharpening
description: "Use when: sharpening a software requirement or a requirement set so it is buildable and decidable rather than merely well-formed - replacing vague quality words and quantifiers with a measured threshold plus a named measurement method, eliminating requirements that defer their own observable behavior to a later decision, decoupling a requirement from named implementation files or symbols so it survives refactors, making MUST/SHOULD/MAY rankings actually discriminate instead of everything being mandatory, adding a completeness matrix against a standard or dependency the spec leans on, and asserting a bidirectional traceability invariant as a mechanical gate."
argument-hint: "The requirement, requirements section, or SRS to sharpen, plus any sibling architecture/test-plan docs and the measurement tooling (benchmarks, profilers) available."
user-invocable: true
---

# Requirement Sharpening

Use this skill to make requirements **buildable and decidable**, not merely well-formed. A requirement can be singular, ranked, and traceable — passing a structural audit — and still be impossible for a builder to implement unambiguously or for a tester to assert a definite outcome. This skill closes that gap: it converts "looks rigorous" into "a builder and a tester cannot misread it."

The governing rule: **every requirement must name a definite, observable outcome and a way to decide whether that outcome was met.** A requirement that hedges its own behavior, uses an unmeasurable quality word, or pins itself to today's file names fails this rule even when it is grammatically a single sentence.

This skill judges the **content decidability** of requirements — what each requirement actually commits to — not the document's outline or the standard's structural characteristics.

## Scope

- Apply to: an individual requirement, a functional/non-functional requirement set, or a whole SRS that already has stable IDs and a structure — when the concern is "can someone build and verify this without guessing," not "is the document shaped to a standard."
- Use the six checks below in order; each has a detection cue, a pass/fail test, and the concrete rewrite.
- Preserve every stable ID and trace link exactly: sharpening edits the *wording and thresholds* of a requirement, never its ID.

## DO NOT USE FOR:

- Document structure, clause outline, singular decomposition, or honest conformance statements — that is a structural-conformance concern, handled separately.
- Word-level ambiguity (passive voice, undefined pronouns, vague verbs in isolation) — that is a prose-ambiguity concern; this skill sharpens only the *measurability and decidability* of the obligation, not general prose.
- Whether an acceptance criterion is itself testable/observable/single — that is an acceptance-criteria-quality concern.
- Test-code quality (can the test fail) — that is a test-quality concern.
- Deciding *what* the product should require (product decisions) or inventing missing requirements — flag the gap, do not fabricate the requirement.

## The Six Sharpening Checks

### 1. Measured threshold + named method (kill the unmeasurable quality word)

- **Cue:** a quality/performance/reliability requirement using *fast, efficient, gratuitous, minimal, reasonable, scalable, robust, low, bounded, quickly, as needed*.
- **Test:** is there (a) a number or a definite boundary, and (b) a named method that produces that number (a benchmark, profiler, counter, measurement harness, or a specific inspection)? If either is missing, it fails — the requirement is review-only, not verifiable.
- **Fix:** state the threshold and the instrument. Reuse measurement tooling the repo already has rather than inventing a metric.
  - Before: "MUST avoid gratuitous per-message heap allocations."
  - After: "MUST perform ≤ N heap allocations per steady-state message, measured by the allocation-counting harness over a fixed-count loop (differencing two run sizes)."
  - Before: "timeouts MUST be enforceable to defend against stalls."
  - After: "MUST enforce a handshake timeout (default 10 s), idle timeout (default 60 s), and close timeout (default 5 s); on expiry the connection is torn down with a cancellation-classified error." (`0` = disabled, documented.)
- A bound with no default value is not yet sharp: give the default the implementation will ship.

### 2. No requirement defers its own observable behavior

- **Cue:** "or, if the design chooses, …", "the implementation MAY instead …", "one of the following", or an obligation whose outcome is parked in an open question (`OQ-*`) the architecture has since resolved.
- **Test:** can a tester write an assertion with a single expected outcome from the requirement text alone? If the requirement offers a choice of observable behaviors, no.
- **Fix:** pick the decided behavior and state it; demote the alternatives to a resolved-decision log. A requirement is the contract, not the menu.
  - Before: "a second concurrent write MUST be rejected with an error (or, if the architecture chooses, serialized)."
  - After: "a second write started while one is in flight MUST be rejected with a single-flight error; writes are never serialized internally in v1." (Note the rejected alternative once, in a decisions/rationale section.)
- When an `OQ-*` is settled elsewhere (architecture, a decision record), fold the answer into the requirement and mark the OQ resolved; do not leave the spec hedging a question that is closed.

### 3. Decouple the requirement from named implementation

- **Cue:** a requirement that names a source file, a private symbol, a helper, or an internal class (`reuses src/foo_utils.*`, `via the close_lowest_layer path`, `mirroring the X member`).
- **Test:** would the requirement still be true and checkable after an internal refactor that renames those files/symbols? If a rename would falsify the *requirement* (not just the design), it is over-coupled.
- **Fix:** state the externally observable obligation; move the file/symbol names to the architecture as the *how*.
  - Before: "for wss the client MUST verify the host using `src/https_openssl_utils.*` and the `host_name_verification` helper."
  - After: "for wss the client MUST verify the server certificate chain and hostname, failing closed by default." (Implementation reuse belongs in the architecture doc.)
- Exception: a requirement that an interface/ID/enum value is *stable* (append-only, never renumbered) legitimately names the artifact — that naming *is* the contract.

### 4. Make the ranking discriminate

- **Cue:** every requirement is MUST.
- **Test:** does the keyword carry information — i.e., are there genuinely-optional or recommended items marked SHOULD/MAY? If everything is mandatory, the ranking is decoration and cannot guide a scope cut under pressure.
- **Fix:** re-rank honestly. Reserve MUST for what the feature is incorrect without; mark tuning knobs, example-only policies, and convenience toggles SHOULD/MAY. Do not down-rank a security/correctness/safety default to make the list look balanced — those stay MUST.
  - Typical SHOULD/MAY candidates: optional tuning parameters, an example's stylistic policy, a disable-toggle for a non-default behavior.
  - Always-MUST: fail-closed security defaults, lifetime/teardown correctness, data-integrity, the core capability the user asked for.

### 5. Completeness matrix against a leaned-on standard or dependency

- **Cue:** the spec says "the library/dependency handles it" for a protocol or standard (an RFC, a wire format, a spec the dependency implements) instead of enumerating which cases it must handle.
- **Test:** is there a short matrix mapping the externally-required cases (status codes, frame types, edge encodings, error categories) to a requirement or an explicit "covered by dependency D"? If the spec assumes the dependency covers every case without listing them, the requirement *set* is not demonstrably complete.
- **Fix:** add a compact conformance matrix: one row per externally-mandated case, each pointing at the requirement/edge-case that covers it or naming the dependency that does. This turns "we assume it's complete" into "here is the coverage." It also surfaces the cases the dependency does *not* handle (those become your requirements).

### 6. Bidirectional traceability as a mechanical gate

- **Cue:** traceability exists as prose ("see coverage matrix") but no invariant is asserted, and IDs drift between the spec, architecture, and test plan (a reused ID, a dangling citation).
- **Test:** is there a stated invariant — *every acceptance criterion traces to ≥1 requirement and ≥1 test case; every requirement traces to ≥1 acceptance criterion* — that can be checked mechanically (e.g. a grep/script over the trio)? If the only check is human reading, drift is inevitable.
- **Fix:** assert the invariant in the spec and make it greppable: consistent ID tokens across the three documents, and a note that a citation to a non-existent or duplicate ID is a defect. A duplicate/reused ID is the symptom this gate catches early; fix the ID collision at its source and gate against recurrence here.

## Procedure

1. **Inventory the requirements and their current ranking, thresholds, and trace links.** This is the contract you sharpen without breaking IDs.
2. **Run checks 1–6 over each requirement (1–4) and the set (5–6).** Record each finding with the exact quote, the failing check, and the concrete rewrite.
3. **Confirm decided answers before folding them in.** For check 2, read the sibling architecture/decision docs to get the *actual* chosen behavior; do not invent it.
4. **Apply rewrites in place**, preserving every stable ID and updating any sibling-doc citation that a wording change touches (especially check 6).
5. **Re-state the ranking and the trace invariant**, and list any requirement you could only flag (a genuine product decision or a missing measurement tool) as an open item rather than fabricating its threshold.

## Output

```markdown
## Requirement Sharpening Report

Verdict: BLOCK | CONCERNS | SHARP | insufficient-context
Mode: audit | sharpen

### Findings
| # | ID | Check | Severity | Issue |
|---|----|-------|----------|-------|

For each finding:
- Quote: <exact requirement text>
- Problem: <which of the six checks fails and why a builder/tester cannot decide it>
- Fix: <the sharpened rewrite — threshold+method, decided behavior, decoupled wording, honest rank, matrix row, or trace invariant>

### Sharpened Requirements (sharpen mode only)
- <ID>: <the full rewritten requirement text, ready to paste back into the spec>

### Open items (flag, do not fabricate)
- <requirements needing a product decision or a measurement tool that does not exist yet>
```

`Mode` is determined by the request, not by run-to-run choice, and changes the output:

- `audit` — the caller wants findings only. Emit the Findings and Open items sections; **omit** the `### Sharpened Requirements` section. Use this mode when the caller asks to review/audit/flag, or when editing the source spec in place is out of scope.
- `sharpen` — the caller wants the rewritten requirements. Emit everything `audit` does **plus** the `### Sharpened Requirements` section, with one entry per requirement you rewrote (full replacement text). Use this mode when the caller asks to sharpen/rewrite/fix the requirements. Open items still list what you could only flag, not fabricate.

Default to `sharpen` when the caller's verb is sharpen/rewrite/fix and to `audit` when it is review/audit/check; if ambiguous, pick `audit` and say so.

Use these exact labels (`Verdict:`, `Mode:`, `Quote:`, `Problem:`, `Fix:`) unless the caller requests different ones, in which case follow the caller's labels exactly. Each finding's `Severity` column is `BLOCK` or `CONCERNS` (a finding is never `SHARP` — that is a whole-report verdict only).

Verdict mapping:

- `BLOCK` — a requirement defers its own observable behavior (check 2), an unmeasurable quality word has no threshold *and* no method (check 1), or a reused/dangling ID breaks traceability (check 6).
- `CONCERNS` — over-coupled to implementation (check 3), undifferentiated ranking (check 4), or a missing completeness matrix for a leaned-on standard (check 5).
- `SHARP` — every requirement names a definite outcome and a way to decide it; rankings discriminate; the set's completeness and traceability are demonstrable.
- `insufficient-context` — no requirement text is supplied, so there is nothing to sharpen. Return this verdict and name what is missing; do not invent requirements. When a requirement *is* supplied but the docs (check 2) or tooling (check 1) needed to resolve its threshold or decided behavior are absent, that is a normal `BLOCK`/`CONCERNS` finding plus an Open item — not this verdict.

## Anti-Patterns

- Adding a number with no instrument (check 1 needs *both* a threshold and a named method).
- Folding an open question's answer into a requirement without confirming the decided behavior in the architecture — guessing the resolution.
- Down-ranking a fail-closed security or lifetime-correctness default to SHOULD to make the ranking "look balanced."
- Deleting the rejected alternative entirely instead of recording it once in a decisions log (loses the rationale).
- Stripping a *legitimate* artifact name — an append-only enum or a stable interface ID whose naming is the contract — in the name of decoupling.
- Sharpening wording in a way that silently renumbers or drops a stable ID (preserve IDs).
- Inventing a requirement to fill a completeness-matrix row instead of flagging the gap as a product decision.
