---
name: archive-extraction-safety
description: "Use when: reviewing, designing, implementing, or testing safe archive extraction for ZIP, TAR, tar.gz, tgz, package importers, backup restore, plugin/theme upload, artifact unpacking, decompression bomb controls, Zip Slip, Tar Slip, symlink and hardlink entries, absolute paths, Windows drive, UNC, namespace, device, ADS, or normalization hazards, Unicode path normalization, nested archives, parser mismatch, extraction destination-root trust and containment, race-resistant writes, overwrite policy, and cleanup after partial extraction."
argument-hint: "Archive format(s), extraction code or design, destination-root trust, allowed entry types, resource limits, overwrite policy, and tests."
user-invocable: true
---

# Archive Extraction Safety

Use this skill for static review or design of code that extracts archive entries into a destination directory. The goal is to make extraction safe before any archive-controlled path, metadata, file type, permission, ownership, or decompressed content reaches the filesystem.

## Trigger Conditions

- ZIP, TAR, tar.gz, tgz, package, backup, artifact, plugin, theme, or import flows that unpack files.
- Code or designs that validate archive entry names, then write them to disk.
- Reviews of Zip Slip / Tar Slip, symlink, hardlink, absolute-path, Windows path, Unicode normalization, decompression-bomb, nested-archive, overwrite, or partial-extraction cleanup risks.
- Tests for archive extraction policy, parser consistency, decompressed size limits, file count limits, compression-ratio limits, and destination containment.

Do NOT use this skill for:

- Pure archive download or outbound URL validation with no extraction.
- General filesystem path construction after extraction has already produced trusted, validated paths.
- Archive creation, compression tuning, or backup retention with no untrusted archive input.
- Live execution against untrusted archives. Prefer inert excerpts, fixture manifests, and static reasoning.

## Required Input Context

Collect or ask for:

- Archive format and parser/library used for both validation and extraction.
- Extraction destination root: how it is canonicalized/resolved, who controls it, whether it is attacker-writable, and whether it is fresh per job, staged, per-tenant, shared, or reused.
- Locking/isolation and pre-existing-entry policy for any shared or reused destination root.
- Entry sources and trust level.
- Allowed entry types: regular files, directories, symlinks, hardlinks, special files, device nodes, FIFOs, sockets.
- Resource limits: file count, directory count, path length/depth, per-file decompressed size, total decompressed size, sparse-file apparent size, metadata/header size, compression ratio, CPU/time/memory budgets, and recursion depth for nested archives.
- Overwrite policy for existing files and directories.
- Permission, executable-bit, timestamp, and ownership restoration policy.
- Cleanup behavior after rejected entries, partial extraction, errors, timeout, or cancellation.
- Existing tests and target platform path semantics, including POSIX and Windows compatibility, case sensitivity, device names, namespace paths, alternate data streams, and trailing dot/space normalization.

If destination root, archive format/parser, or allowed entry types are missing and cannot be inferred, emit `Verdict: BLOCK` with the missing context. Do not guess. Missing resource limits, overwrite policy, permission restoration, cleanup behavior, platform semantics, or tests are findings that prevent `CLEAN` unless explicitly accepted as tradeoffs.

## Procedure And Checklist

1. State the extraction contract: accepted formats, destination-root trust model, allowed entry types, overwrite behavior, and resource limits.
2. Confirm destination-root trust before extraction:
    - Canonicalize/resolve the root itself, not only entry paths.
    - Require an extractor-controlled root that is not attacker-writable.
    - Prefer a fresh per-job destination or staging root.
    - For shared or reused roots, require explicit locking/isolation and a policy for pre-existing entries.
3. Confirm validation and extraction use the same parser, canonicalization rules, and decoded entry names. Parser mismatch is a finding when validation accepts one view and extraction writes another.
4. Normalize and reject unsafe entry names before touching the destination:
    - Reject empty names, NUL bytes, control characters, trailing separators that change file type, and ambiguous duplicate names after normalization.
    - Reject `.` and `..` path segments after splitting on all relevant separators.
    - Reject absolute POSIX paths, drive paths such as `C:\...`, drive-relative paths, UNC paths such as `\\server\share`, namespace/device paths, reserved device names, alternate data streams, and names changed by trailing dot/space normalization where applicable.
    - Detect case-insensitive duplicate collisions where the target platform or later consumers are case-insensitive.
    - Normalize Unicode consistently (for example NFC) before duplicate detection and containment checks.
5. Enforce destination containment for every entry by joining against the extraction root, canonicalizing parent paths, and checking the final write remains inside the destination. A string prefix check on raw entry names is insufficient.
6. Handle links and file types explicitly:
    - Reject symlink entries unless the product has a documented, contained, no-follow link policy.
    - Reject hardlink entries unless the target is validated as an already-extracted, contained regular file.
    - Reject device nodes, FIFOs, sockets, block/char devices, and other special files by default.
    - Do not follow archive-created links during later extraction steps.
7. Apply resource limits before and during extraction:
    - Bound archive entry count, directory count, path length/depth, per-file decompressed size, total decompressed size, sparse-file apparent size, metadata/header size, compression ratio, and CPU/time/memory use.
    - Bound nested archive recursion and require the same policy at each level.
    - Stop extraction fail-closed when a limit is exceeded.
8. Apply race-resistant write semantics:
    - Treat validate-then-write-by-path as insufficient by itself.
    - Define overwrite policy; reject overwrites by default for externally supplied archives unless explicitly required.
    - Use no-follow, root-confined, race-resistant writes or an equivalent design.
    - Revalidate containment and file type at write time, not only during earlier path validation.
    - Reject pre-existing links in destination paths unless a documented contained link policy permits them.
    - Use atomic writes where possible and prevent path swaps between validation and write.
    - Preserve executable bits, permissions, timestamps, and ownership only when explicitly allowed; never restore archive-owned uid/gid by default.
9. Clean up partial extraction on failure. Rejected entries, timeout, cancellation, and mid-stream parser errors must not leave a partially trusted tree that later code consumes as complete.
10. Review tests for traversal, absolute paths, drive/UNC/namespace/device paths, reserved device names, alternate data streams, trailing dot/space normalization, case-insensitive duplicate collisions, Unicode normalization collisions, symlinks, hardlinks, special files, duplicates, overwrite attempts, decompressed size, sparse-file apparent size, metadata/header size, compression ratio, path length/depth, CPU/time/memory limits, file count, nested archives, cleanup, and parser mismatch.

## Severity And Verdict Mapping

- `CRITICAL`: archive-controlled extraction can write outside the destination, overwrite sensitive paths, plant followed links, create special files, or cause severe resource exhaustion in normal use.
- `HIGH`: a strong extraction safety risk exists but exploitability depends on format, platform, privileges, or partial compensating controls.
- `MEDIUM`: bounded robustness or defense-in-depth gap, usually missing limits, cleanup, duplicate handling, or test coverage.
- `LOW`: documentation, clarity, or maintainability issue with limited direct impact.

Verdict mapping:

- `BLOCK`: any `CRITICAL`, any unmitigated `HIGH`, or missing required input context that prevents judging extraction safety.
- `CONCERNS`: actionable `HIGH` or `MEDIUM` gaps remain but each has a documented compensating control, accepted tradeoff, or bounded impact.
- `CLEAN`: the contract, implementation, and tests cover every applicable checklist item with no material gaps.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <files, diff, design, or archive flow>
Archive format/parser: <format and parser/library>
Destination root: <root or undeclared>
Destination-root trust: <canonicalized/controlled/fresh/locked/pre-existing policy or undeclared>
Allowed entry types: <regular files/directories/...>
Resource limits: <file count, path depth, total size, ratio, CPU/time/memory, nested depth, or undeclared>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, design sentence, or missing-from-target>
  Risk: <what unsafe extraction enables>
  Required guard: <specific control from the checklist>
  Test expectation: <regression test or N/A>

Checklist status:
- Destination-root trust: covered | missing | n/a
- Parser consistency: covered | missing | n/a
- Entry path normalization: covered | missing | n/a
- Platform path hazards: covered | missing | n/a
- Destination containment: covered | missing | n/a
- Links and special files: covered | missing | n/a
- Resource limits: covered | missing | n/a
- Race-resistant writes: covered | missing | n/a
- Overwrite policy: covered | missing | n/a
- Permission/ownership restoration: covered | missing | n/a
- Partial extraction cleanup: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

Use `Findings: None` only when the verdict is `CLEAN` or all remaining issues are explicitly recorded as accepted tradeoffs under residual risk.

## Anti-Patterns

- Validating with one archive parser and extracting with another.
- Checking only for `../` substrings instead of splitting, decoding, normalizing, and containing paths.
- Trusting an extraction root that has not itself been resolved, isolated, or protected from attacker writes.
- Assuming ZIP and TAR entry semantics are interchangeable.
- Treating drive, UNC, namespace, device, alternate-data-stream, case-folding, or trailing-dot/space behavior as platform trivia.
- Allowing symlinks or hardlinks because their textual target appears relative.
- Restoring archive-supplied uid/gid, broad mode bits, executable bits, or special files by default.
- Extracting into a shared long-lived directory with overwrite enabled and no cleanup plan.
- Validating a final path and later writing through that path without no-follow, root-confined, write-time revalidation or equivalent race resistance.
- Trusting compressed size instead of enforcing decompressed byte and ratio limits while streaming.
- Treating nested archives as ordinary files when later code auto-extracts them without the same policy.
- Reporting only traversal while ignoring parser mismatch, links, limits, overwrite, permissions, and cleanup.
