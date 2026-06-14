# unicode-text-security-review

> Use when: reviewing, designing, implementing, or testing security-sensitive Unicode text handling, UTF-8 decoding, invalid byte sequences, overlong encodings, surrogate handling, NFC/NFKC normalization, canonical equivalence, compatibility characters, fullwidth or halfwidth bypasses, byte-vs-character validation drift, database charset mismatch, case folding, Unicode identifiers, confusables, mixed scripts, or text parser-consumer mismatch.

This skill is aimed at code, designs, and tests where untrusted text crosses an encoding, normalization, comparison, storage, or display boundary and the result affects a security decision, identifier, lookup, database query, path/URL policy, allowlist, or audit trail.

It helps an assistant:

- state the text contract per field: accepted encodings, decode error behavior, normalization/case policy, identifier profile, and stored forms
- verify strict UTF-8 decoding before security decisions, rejecting overlong encodings, surrogate code points, truncated sequences, and lenient error modes
- choose normalization deliberately (NFC for canonical text, NFKC only for restricted identifiers) and run it before allowlists, uniqueness checks, and routing decisions
- catch parser-consumer drift where validation runs on one representation (bytes, raw text, one normalization form) and a database, filesystem, URL parser, or auth layer consumes another
- review identifier policy for confusables, mixed scripts, mixed numbers, default-ignorable and bidi characters, with migration plans for Unicode data changes
- apply decision rules for length-limit units, safe truncation, lone surrogates, decode-layer ordering, log/display injection, regex Unicode semantics, normalization expansion, and canonical hostname comparison
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, adversarial test expectations, and residual risk, including a deterministic insufficient-context template

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
