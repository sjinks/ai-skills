---
name: archive-extraction-safety
description: "Use when: reviewing, designing, implementing, or testing safe archive extraction for ZIP, TAR, tar.gz, tgz, package importers, backup restore, plugin/theme upload, artifact unpacking, decompression bomb controls, Zip Slip, Tar Slip, symlink and hardlink entries, absolute paths, Windows drive or UNC paths, Unicode path normalization, nested archives, parser mismatch, extraction destination containment, overwrite policy, and cleanup after partial extraction."
argument-hint: "Archive format(s), extraction code or design, destination root, allowed entry types, resource limits, overwrite policy, and tests."
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
- Extraction destination root and whether it is per-job, per-tenant, or shared.
- Entry sources and trust level.
- Allowed entry types: regular files, directories, symlinks, hardlinks, special files, device nodes, FIFOs, sockets.
- Resource limits: file count, per-file decompressed size, total decompressed size, compression ratio, recursion depth for nested archives.
- Overwrite policy for existing files and directories.
- Permission, executable-bit, timestamp, and ownership restoration policy.
- Cleanup behavior after rejected entries, partial extraction, errors, timeout, or cancellation.
- Existing tests and target platform path semantics, including POSIX and Windows compatibility.

If destination root, archive format/parser, or allowed entry types are missing and cannot be inferred, emit `Verdict: BLOCK` with the missing context. Do not guess.

## Procedure And Checklist

1. State the extraction contract: accepted formats, destination root, allowed entry types, overwrite behavior, and resource limits.
2. Confirm validation and extraction use the same parser, canonicalization rules, and decoded entry names. Parser mismatch is a finding when validation accepts one view and extraction writes another.
3. Normalize and reject unsafe entry names before touching the destination:
   - Reject empty names, NUL bytes, control characters, trailing separators that change file type, and ambiguous duplicate names after normalization.
   - Reject `.` and `..` path segments after splitting on all relevant separators.
   - Reject absolute POSIX paths, Windows drive paths such as `C:\...`, drive-relative paths, and UNC paths such as `\\server\share`.
   - Normalize Unicode consistently (for example NFC) before duplicate detection and containment checks.
4. Enforce destination containment for every entry by joining against the extraction root, canonicalizing parent paths, and checking the final write remains inside the destination. A string prefix check on raw entry names is insufficient.
5. Handle links and file types explicitly:
   - Reject symlink entries unless the product has a documented, contained, no-follow link policy.
   - Reject hardlink entries unless the target is validated as an already-extracted, contained regular file.
   - Reject device nodes, FIFOs, sockets, block/char devices, and other special files by default.
   - Do not follow archive-created links during later extraction steps.
6. Apply resource limits before and during extraction:
   - Bound archive entry count, directory count, per-file decompressed size, total decompressed size, and compression ratio.
   - Bound nested archive recursion and require the same policy at each level.
   - Stop extraction fail-closed when a limit is exceeded.
7. Apply safe write semantics:
   - Extract into a fresh per-job destination or staging directory when possible.
   - Define overwrite policy; reject overwrites by default for externally supplied archives unless explicitly required.
   - Use atomic writes where possible and avoid writing through paths that can be swapped between validation and write.
   - Preserve executable bits, permissions, timestamps, and ownership only when explicitly allowed; never restore archive-owned uid/gid by default.
8. Clean up partial extraction on failure. Rejected entries, timeout, cancellation, and mid-stream parser errors must not leave a partially trusted tree that later code consumes as complete.
9. Review tests for traversal, absolute paths, Windows drive/UNC paths, Unicode normalization collisions, symlinks, hardlinks, special files, duplicates, overwrite attempts, decompressed size, compression ratio, file count, nested archives, cleanup, and parser mismatch.

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
Allowed entry types: <regular files/directories/...>
Resource limits: <file count, total size, ratio, nested depth, or undeclared>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Evidence: <file:line, diff hunk, design sentence, or missing-from-target>
  Risk: <what unsafe extraction enables>
  Required guard: <specific control from the checklist>
  Test expectation: <regression test or N/A>

Checklist status:
- Parser consistency: covered | missing | n/a
- Entry path normalization: covered | missing | n/a
- Destination containment: covered | missing | n/a
- Links and special files: covered | missing | n/a
- Resource limits: covered | missing | n/a
- Overwrite and write semantics: covered | missing | n/a
- Permission/ownership restoration: covered | missing | n/a
- Partial extraction cleanup: covered | missing | n/a
- Tests: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

Use `Findings: None` only when the verdict is `CLEAN` or all remaining issues are explicitly recorded as accepted tradeoffs under residual risk.

## Anti-Patterns

- Validating with one archive parser and extracting with another.
- Checking only for `../` substrings instead of splitting, decoding, normalizing, and containing paths.
- Assuming ZIP and TAR entry semantics are interchangeable.
- Allowing symlinks or hardlinks because their textual target appears relative.
- Restoring archive-supplied uid/gid, broad mode bits, executable bits, or special files by default.
- Extracting into a shared long-lived directory with overwrite enabled and no cleanup plan.
- Trusting compressed size instead of enforcing decompressed byte and ratio limits while streaming.
- Treating nested archives as ordinary files when later code auto-extracts them without the same policy.
- Reporting only traversal while ignoring parser mismatch, links, limits, overwrite, permissions, and cleanup.