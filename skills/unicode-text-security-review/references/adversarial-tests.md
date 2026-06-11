Read this file when designing or reviewing the regression test suite for a Unicode text security change; the class names are summarized in `SKILL.md`.

# Adversarial Test Matrix

Adapt each class to the runtime and product policy. In the test plan, mark each class as covered, not applicable, accepted tradeoff, or missing. When filling the skill report's `Checklist status`, collapse `not applicable` to `n/a` and record each `accepted tradeoff` as a finding with classification `Accepted tradeoff`.

## Invalid UTF-8

- Overlong NUL (`0xC0 0x80`) and overlong dot/slash (`0xC0 0xAE`, `0xC0 0xAF`).
- Surrogate code points encoded in UTF-8 (`0xED 0xA0 0x80` through `0xED 0xBF 0xBF`).
- 5- and 6-byte forms, truncated multibyte sequences, and lone continuation bytes.
- Replacement-character and ignore error-mode behavior before security decisions.

## Canonical Equivalence

- Precomposed vs decomposed accents (NFC vs NFD) for usernames, tenant names, object names, ACL entries, and signature inputs.
- Singleton equivalents such as U+212B ANGSTROM SIGN vs U+00C5.
- Combining-mark reordering cases that compare equal after normalization.

## Compatibility Characters

- Fullwidth dot/slash/backslash/colon (U+FF0E, U+FF0F, U+FF3C, U+FF1A) where syntax or identifiers are involved.
- Mathematical alphanumerics, circled digits, ligatures, Roman numerals, superscripts/subscripts, and nonbreaking spaces.
- Any character whose NFKC form introduces a syntax-significant ASCII character.

## Case And Locale

- Casefold collisions between distinct identifiers.
- Turkish dotted/dotless I and Greek final sigma where the locale applies.
- Application casefold vs database collation disagreement.

## Identifier Spoofing

- Mixed Latin/Cyrillic/Greek lookalikes and whole-script confusables.
- Mixed decimal number systems in one identifier.
- Default-ignorable characters, bidi controls, and ZWJ/ZWNJ in and out of permitted contexts.
- Confusable skeleton collisions between a new identifier and existing registrations.

## Storage Drift

- Application equality vs database unique index, search index, cache key, signature input, and display-name lookup.
- Reindex behavior after a normalization, collation, or Unicode data version change.

## Length And Truncation

- Limits measured in different units (bytes, code units, code points, graphemes) across layers.
- Truncation inside multibyte sequences, surrogate pairs, or combining clusters.
- Truncation that removes a blocked suffix or changes validation outcome.
- Normalization expansion (up to 3x) against length caps, in both limit-then-normalize and normalize-then-limit orders.

## Encoding Layers

- Double percent-decoding and validation before the final decode layer.
- Lone surrogates surviving serialization between UTF-16 runtimes and UTF-8 consumers.
- Mixed Unicode-form and punycode/ACE-form hostname or email comparison.

## Display Injection

- Bidi control characters (U+202A-U+202E, U+2066-U+2069) and zero-width characters in logged or displayed identifiers.
- U+2028/U+2029 in JSON-to-JS string contexts.
- Newline and control-character smuggling into log lines and audit trails.
