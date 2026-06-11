Read this file when maintaining or auditing provenance for the Unicode Text Security Review skill; it is not needed for normal skill invocation.

# Source Map

## Programming With Unicode

- Source identity: Programming with Unicode, Victor Stinner, "Unicode issues", https://unicodebook.readthedocs.io/issues.html.
- Retrieval date: 2026-06-11.
- Relevant locations: "Security vulnerabilities", "Special characters", "Non-strict UTF-8 decoder: overlong byte sequences and surrogates", and "Check byte strings before decoding them to character strings".
- Extracted concepts: fullwidth and halfwidth compatibility characters can bypass text checks; NFKC can turn fullwidth dot and slash into ASCII syntax characters; UTF-8 decoders must reject overlong encodings and surrogate code points; validating byte strings before character decoding can drift from downstream character semantics.
- Confidence: high for historical bypass classes and operational review prompts; medium for historical library-specific examples because the page is old.
- Use in skill: decode-boundary checks, compatibility-character tests, byte-vs-character drift checks, and parser-consumer mismatch wording.

## RFC 3629

- Source identity: RFC 3629, "UTF-8, a transformation format of ISO 10646", https://www.rfc-editor.org/rfc/rfc3629.
- Retrieval date: 2026-06-11.
- Relevant locations: sections 3, 4, and 10.
- Extracted concepts: valid UTF-8 is limited to 1-4 byte sequences for U+0000 through U+10FFFF; surrogate code points are excluded; overlong and other invalid sequences must not decode to characters; invalid decoding can bypass checks such as NUL and directory traversal filters; canonical-equivalent character sequences can affect matching, indexing, searching, regular expressions, credentials, and ACLs.
- Confidence: high.
- Use in skill: strict UTF-8 rejection rules, invalid byte adversarial tests, and security-decision ordering.

## Unicode Standard Annex #15

- Source identity: Unicode Standard Annex #15, "Unicode Normalization Forms", revision 57 / Unicode 17.0.0, https://unicode.org/reports/tr15/.
- Retrieval date: 2026-06-11.
- Relevant locations: sections 1, 9, 10, and 13.
- Extracted concepts: NFC and NFD preserve canonical equivalence; NFKC and NFKD erase compatibility distinctions; NFKC/NFKD must not be blindly applied to arbitrary text; normalized strings are not closed under concatenation; systems can either preserve canonical equivalence through each component or normalize/check at boundaries; normalization checks can be cheaper than conversion.
- Confidence: high.
- Use in skill: normalization policy, NFC vs NFKC guidance, concatenation caveat, storage/index consistency, and definition-of-done checks.

## Unicode Technical Standard #39

- Source identity: Unicode Technical Standard #39, "Unicode Security Mechanisms", revision 32 / Unicode 17.0.0, https://unicode.org/reports/tr39/.
- Retrieval date: 2026-06-11.
- Relevant locations: sections 3, 4, 5, 6, 7, and Migration.
- Extracted concepts: security-sensitive identifiers need explicit profiles; Identifier_Status and Identifier_Type data support allowed/restricted character decisions; default-ignorable, join-control, restricted, mixed-script, mixed-number, and confusable cases need policy; confusable skeletons are internal comparison artifacts and must not be used as display text or general normalization; Unicode security data changes require migration/backward-compatibility planning for persistent identifiers.
- Confidence: high.
- Use in skill: identifier profile checklist, confusable/mixed-script tests, migration requirement, and skeleton warning.