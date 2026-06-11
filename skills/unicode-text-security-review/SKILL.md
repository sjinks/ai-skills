---
name: unicode-text-security-review
description: "Use when: reviewing, designing, implementing, or testing security-sensitive Unicode text handling, UTF-8 decoding, invalid byte sequences, overlong encodings, surrogate handling, NFC/NFKC normalization, canonical equivalence, compatibility characters, fullwidth or halfwidth bypasses, byte-vs-character validation drift, database charset mismatch, case folding, Unicode identifiers, confusables, mixed scripts, or text parser-consumer mismatch."
argument-hint: "Describe the text input boundary, encoding/normalization policy, security decision, downstream consumer, and tests."
user-invocable: true
---
# Unicode Text Security Review

Use this skill when untrusted text crosses an encoding, normalization, comparison, storage, or display boundary and the result affects a security decision, identifier, lookup, routing decision, database query, path/URL policy, allowlist, denylist, or audit trail.

The goal is not to make every string ASCII-only. The goal is to make the text contract explicit so every layer sees the same characters, equivalence rules, and identifier policy before security-sensitive behavior depends on them.

**UTILITY SKILL.** INVOKES: read-only file access for supplied targets; no other tools or skills. FOR SINGLE OPERATIONS: use for focused Unicode text-security review, design, implementation guidance, or test planning.

## Scope

- Use this skill for Unicode-specific security review of text boundaries, strict UTF-8 decoding, normalization order, canonical or compatibility equivalence, identifier spoofing, confusable names, mixed-script identifiers, byte/character mismatch, charset mismatch, and parser-consumer drift.
- Apply this skill directly when Unicode text affects paths, archive entry names, URLs, hostnames, database queries, tenants, accounts, roles, claims, permissions, package names, or any other security-sensitive identifier.
- Keep the review centered on text representation: decoding, normalization, comparison, storage/index semantics, downstream parser agreement, and display ambiguity. Mention non-text risks only as residual context.

## DO NOT USE FOR:

- Routine display bugs, localization copy, font rendering, emoji layout, ordinary UnicodeDecodeError troubleshooting, or broad web security reviews where Unicode text handling is not central.
- General Unicode explanations with no security decision, identifier policy, parser-consumer boundary, or persistent identity risk.

## Required Context

Collect or infer the narrowest useful context before judging:

- Input boundary: bytes, declared charset, transport, file, request field, database value, user identifier, URL/path segment, or source code token.
- Decoder and error mode: strict reject, replacement, ignore, surrogate pass, legacy charset fallback, or unknown.
- Normalization and case policy: none, NFC, NFD, NFKC, NFKD, casefold, locale-specific casing, IDNA, or custom mapping.
- Security decision: validation, allowlist, denylist, routing, access control, uniqueness, signing, logging, display warning, database query, path/URL containment, or parser selection.
- Downstream consumer: filesystem, URL parser, database, template engine, shell, auth layer, browser, search index, cache key, display UI, or another service.
- Persistence: whether raw, normalized, casefolded, skeleton, or display forms are stored and indexed.
- Tests and target Unicode/library versions when the behavior depends on them.

If the input boundary, security decision, or downstream consumer is missing and cannot be inferred, return `Verdict: BLOCK` with one open question. Do not guess a Unicode policy.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable checklist with concise evidence. `exhaustive` enumerates the full checklist and adversarial matrix only when asked or when the risk surface warrants it. If the user asks for `quick` or `exhaustive`, name the selected depth in the report.

## Workflow

1. State the text contract: accepted encodings, decode error behavior, normalization/case policy, allowed identifier profile, and stored forms.
2. Trace representation changes in order: raw bytes -> decoded text -> normalized or casefolded form -> validation -> storage/indexing -> downstream parser/consumer -> display.
3. Verify strict decoding before security decisions. Invalid UTF-8, overlong byte sequences, surrogate code points in UTF-8, truncated sequences, and unexpected BOM handling must fail closed or be explicitly policy-covered before validation runs.
4. Verify validation and consumption use the same representation. A check on bytes, raw text, NFC text, NFKC text, casefolded text, IDNA/punycode text, or database-connection text is only valid for consumers that use the same representation and equivalence rules.
5. Choose normalization deliberately. Prefer NFC for canonical text interoperability. Use NFKC or NFKC plus casefold only for restricted identifiers or matching keys where compatibility distinctions are intentionally erased. Do not blindly apply NFKC to arbitrary user-visible text.
6. Review identifier policy separately from prose text. Identifiers that grant access, reserve names, select tenants, address packages, or appear in URLs need an explicit allowed-character profile, normalization form, case policy, mixed-script/confusable policy, collision handling, and migration plan.
7. Check storage and index drift. The database collation, unique index, search index, cache key, signature input, and application-level comparison must agree or the code must document which source of truth wins.
8. Review tests for adversarial equivalence classes, not just examples. Include invalid bytes, canonical equivalents, compatibility characters, separator-like characters, mixed scripts, confusables, casefolding edge cases, and database/parser mismatch fixtures.

## Decision Rules

These rules explain rationale; the Checklist below is the gating source of truth when they overlap, so edit the checklist first and keep these rules aligned with it.

- When a length limit exists, state its unit explicitly (bytes, code units, code points, or grapheme clusters) and enforce the same unit at every layer; mismatched units let one layer accept what another truncates.
- When truncating text, never cut inside a UTF-8 multibyte sequence, a UTF-16 surrogate pair, or a combining-mark cluster; truncate at a safe boundary and re-validate the result, because truncation can create new characters or strip a security-relevant suffix.
- When the runtime allows lone surrogates in strings (JavaScript, Java, C# UTF-16 strings), reject or replace unpaired surrogates before serialization, signing, or cross-system transfer; downstream UTF-8 encoders disagree on how to handle them.
- When text is percent-encoded, base64-encoded, HTML-entity-encoded, or escaped, fix the decode order and validate after the final decode; validating before the last decode step is a bypass, and double decoding is a finding.
- When text reaches logs, terminals, diffs, code review, or other plain-text surfaces, treat bidirectional controls (U+202A-U+202E, U+2066-U+2069), zero-width characters, and U+2028/U+2029 line separators as injection-capable: they can reorder display, hide content, forge log lines, or break JS/JSON string contexts.
- When regexes enforce security policy, verify the engine's Unicode semantics for `\w`, `\d`, `\s`, `.`, anchors, and case-insensitive mode; the same pattern can pass in tests and fail in production on another engine.
- When regexes run on astral characters (above U+FFFF), verify whether the engine matches them as one code point or two surrogate halves; quantifiers and character classes behave differently in each mode.
- When normalizing or casefolding untrusted text, bound the input first: NFC/NFD can expand up to 3x in code units and casefolding can grow strings, so normalize-after-limit and limit-after-normalize give different costs and results - pick one ordering and test it.
- When comparing secrets, passwords, or tokens, decide normalization explicitly (for example a SASLprep-like profile or exact bytes); silent normalization differences between enrollment and verification cause both false accepts and lockouts.
- When hostnames or emails are compared, compare a single canonical form (IDNA/punycode plus lowercase) on both sides; mixing Unicode-form and ACE-form comparisons defeats allowlists.

## Checklist

### Decode Boundary

- The declared charset is explicit and trusted only if the surrounding protocol makes it trustworthy.
- UTF-8 decoding rejects invalid sequences, overlong encodings, 5- or 6-byte forms, surrogate code points, truncated sequences, and illegal continuation bytes.
- Replacement or ignore error modes are not used before security decisions unless the policy explicitly treats data loss as rejection.
- UTF-8-like encodings such as CESU-8 or modified UTF-8 are not accepted as UTF-8 unless the downstream consumer uses the same variant by contract.
- BOM handling is specified per field or stream. Stripping, preserving, or ignoring U+FEFF cannot differ between validator, signature, storage, and consumer.

### Normalization And Matching

- The code normalizes or rejects at the trust boundary before allowlists, denylist checks, cache keys, uniqueness checks, signatures, or routing decisions.
- Canonically equivalent strings cannot create distinct security identities unless the product explicitly supports that behavior.
- Compatibility normalization is limited to contexts where losing distinctions is intentional, such as restricted identifiers or lookup keys.
- The same normalization and casefolding policy is used for validation, storage, lookup, authorization, and display warnings.
- Concatenating normalized strings is followed by a normalization check when the concatenation result is security-sensitive.

### Parser And Consumer Drift

- The validator and downstream parser agree on code points for syntax-significant characters such as NUL, quotes, slash, backslash, dot, colon, at-sign, percent, control characters, and whitespace.
- Checks do not run on bytes and then feed decoded characters to a database, template engine, URL parser, filesystem, shell, or auth layer with different charset semantics.
- Database escaping, collation, connection charset, and unique indexes use the same character semantics as application validation.
- Logs and audit trails preserve enough canonical identity to investigate collisions without exposing secrets.

### Identifiers And Spoofing

- Security-sensitive identifiers have an explicit allowed-character profile, usually based on ASCII-only, UAX #31 identifiers, UTS #39 General Security Profile, IDNA, or a product-specific subset.
- Mixed-script, mixed-number, default-ignorable, bidirectional-control, join-control, private-use, unassigned, deprecated, and restricted characters are rejected, warned, or allowed only by documented exception.
- Confusable detection is used for collision warning or registration policy when humans must distinguish identifiers. Confusable skeletons are internal comparison artifacts, not display strings or general normalization.
- Existing identifiers have a migration and grandfathering policy before tightening the profile or changing Unicode/security data versions.

### Storage And Indexes

- The stored form (raw, NFC, casefolded, or skeleton) is named per field, and the unique index, search index, and cache key are built from that same form.
- Application equality, database collation, and index uniqueness agree, or the documented source of truth wins and the others defer to it.
- Changing the stored form, collation, or Unicode data version comes with a reindex/migration step for existing rows.

### Limits, Layers, And Display

- Length limits name their unit and are enforced in the same unit at every layer; truncation happens only at safe boundaries and is re-validated.
- Validation runs after the final decode layer (percent, base64, entity, escape); no double decode after validation.
- Identifiers rendered into logs, terminals, JSON-to-JS, or review surfaces strip or escape bidi controls, zero-width characters, U+2028/U+2029, and newlines.

### Tests

- Existing regression tests cover each applicable class from the Adversarial Tests section; a written test plan alone does not satisfy this item.

## Severity And Verdicts

- `CRITICAL`: externally controlled text can bypass access control, write or read outside policy, select a different tenant/account/resource, inject into a command/query/template, or create persistent identity collision with direct security impact.
- `HIGH`: strong bypass or spoofing risk exists, but exploitability depends on downstream parser, database collation, deployment charset, or user interaction.
- `MEDIUM`: meaningful robustness, auditability, migration, or test gap that could become security-relevant in realistic extensions.
- `LOW`: documentation, clarity, or defensive-hardening issue with limited immediate impact.

Verdicts:

- `BLOCK`: missing required context, any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: actionable `HIGH` or `MEDIUM` gaps remain with compensating controls, accepted tradeoffs, or bounded reachability.
- `CLEAN`: the contract, implementation, storage/index behavior, downstream consumers, and existing regression tests cover every applicable checklist item. For design-stage targets with no code or tests yet, the best achievable verdict is `CONCERNS` with test expectations recorded per finding.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, design, or flow>
Text contract: <encoding, decode errors, normalization, case, identifier profile>
Security decision: <what depends on the text>
Downstream consumer: <parser, database, filesystem, URL, auth, display, etc.>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap | Defense-in-depth
  Evidence: <file:line, diff hunk, design sentence, or missing-from-target>
  Rule: <decode | normalize | compare | identifier | parser-consumer | storage/index | encoding-layers | length/truncation | display-injection rule>
  Risk: <what bypass, collision, spoof, or drift becomes possible>
  Required guard: <specific change or policy decision>
  Test expectation: <regression test or N/A>

Checklist status:
- Decode boundary: covered | missing | n/a
- Normalization and matching: covered | missing | n/a
- Parser and consumer drift: covered | missing | n/a
- Identifiers and spoofing: covered | missing | n/a
- Storage and indexes: covered | missing | n/a
- Limits, layers, and display: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

The `Rule:` values `length/truncation`, `encoding-layers`, and `display-injection` map to the `Limits, Layers, And Display` checklist section; the other values map to the same-named checklist sections.

Use `Findings: None` only with `CLEAN` or when all remaining issues are explicitly accepted tradeoffs. If there are no material issues, say `No material findings` and list assumptions and residual risk instead of inventing findings.

Insufficient-context mode: when required context (input boundary, security decision, or downstream consumer) is missing and cannot be inferred, emit exactly this reduced template and stop; do not emit the text contract, checklist status, or residual risk with guessed values:

```text
Verdict: BLOCK
Target: <files, diff, design, or flow>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <which required context is missing>
  Rule: <decode | normalize | compare | identifier | parser-consumer | storage/index | encoding-layers | length/truncation | display-injection rule>
  Risk: <why no safe conclusion is possible>
  Required guard: <what context must be supplied>
  Test expectation: N/A
```

## Adversarial Tests

Cover each applicable class: invalid UTF-8 (overlong, surrogate, truncated forms), canonical equivalence (NFC vs NFD), compatibility characters (fullwidth separators, NFKC-changing characters), case and locale folding, identifier spoofing (confusables, mixed scripts, default-ignorables), storage drift, length and truncation, encoding layers (double decode, lone surrogates, Unicode vs punycode), and display injection (bidi/zero-width/newline in logs). Use the detailed per-class matrix in [references/adversarial-tests.md](references/adversarial-tests.md) when writing the actual test plan.

## Examples

- Normalize-after-validate bypass: code rejects `/` then applies NFKC, so fullwidth solidus U+FF0F becomes `/` after the check. Fix: normalize first, then validate the normalized form.
- Uniqueness drift: registration compares NFC strings in the app, but the unique index is on the raw column, so `café` (NFC) and `café` (NFD) become two accounts that one login can match. Fix: store and index one named form.
- Lenient decode bypass: a byte-level filter rejects `0x00` and `../`, then a lenient decoder accepts overlong `0xC0 0xAE` as `.`. Fix: strict-decode first, fail closed on invalid sequences, validate the decoded text.

## Definition Of Done

A Unicode text security change is ready only when:

- Strict decode behavior is explicit and tested before security decisions.
- Normalization, casefolding, and identifier profile are defined per field, not globally guessed.
- Validation, storage, lookup, authorization, parser behavior, and display warnings agree on the representation they use.
- Compatibility normalization and confusable skeletons are limited to security-sensitive matching or registration policy, not used as display text.
- Versioned Unicode data, database collations, and migration of existing identifiers are documented when persistent identities are affected.
- Regression tests cover the applicable adversarial classes above.

## Provenance

Source map and confidence notes live in [references/source-map.md](references/source-map.md).
