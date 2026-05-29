---
name: filesystem-path-safety
description: "Use when: auditing code that builds filesystem paths from external input and then reads, creates, mutates, or deletes files under a trusted root. Detects traversal, symlink-follow, TOCTOU, file-type confusion, validator error-contract drift, and resource-ordering issues."
argument-hint: "Target file(s) or diff; trusted-root identifier; the external-input fields whose values flow into the path."
user-invocable: true
---

# Filesystem Path Safety

A read-only audit checklist for code that turns external identifiers into filesystem paths and then reads, creates, or mutates files under them. This is a high-yield bug class in systems that process tenant data, uploads, repositories, archives, or per-job scratch directories. Treat the checklist as a gate: every applicable item must be answered "yes, anchored at <file>:<line>" or "N/A because <reason>" before the path is considered safe.

A pathname is a lookup recipe, not a file. Every check on the path string is presumptive; the authoritative checks are descriptor-based (`fstat`, `fchmod`, `fchown`, `ftruncate`, `write`) on the fd you actually opened.

## When to Use

Run this skill against a target when its diff or current text matches any of:

- Path construction from a function parameter, request body, env var, header value, tenant-controlled identifier, filename, or external string.
- Use of a scratch or working directory shared across tenants, jobs, or requests (for example a system temp dir or shared volume).
- A symlink/realpath-aware validator that decides whether a path is "inside" a trusted root.
- Any mkdir, mkdtemp, open, write, rename, symlink, unlink, delete, or shell-out operation whose target argument is the constructed path.
- A design or implementation request for a component that will turn external input into filesystem paths under a trusted root; the checklist also doubles as the design contract.
- An auditor or reviewer is responding to a finding in this class and wants to verify the fix covers the rest of the surface, not just the reported site.

Do NOT use this skill for:

- A sweeping codebase audit unrelated to path handling.
- Code where the path is generated entirely by a known-safe hashing function with no user-controlled segment.
- Static or hardcoded paths with no external input.
- Broader concerns outside path handling (auth, secrets, SQL injection, deserialization).
- Archive-entry name validation (ZIP-slip / TAR-slip). That is a separate bug class — this skill audits the scratch-directory writer that hosts the extracted files, not the entry-name validation in the extractor itself.

## Boundaries

- Read-only against source, diff, and existing test files. No execution against live filesystems, no temp-dir probes, no calls into network or external services.
- Reasoning is rooted in the diff or the current file text plus narrowly cited supporting context (helper definitions, callers, related tests).
- Do not emit exploit recipes; describe the failure class and the missing guard, not how to weaponize it.
- Language-agnostic checklist. Do not treat any single language as canonical.
- The trusted-root containment check (B3) is a canonical-path policy, not a mount-identity check. A privileged actor in a separate mount namespace, or an unprivileged actor inside a user namespace with `CLONE_NEWNS`, can present an attacker-controlled filesystem at the configured path that satisfies every checklist item. Mount-namespace integrity is a deployment-layer concern (init-system unit options, seccomp filters denying namespace creation, MAC policy) and is out of scope for this code-review checklist; note it as residual risk when it applies.
- The checklist assumes a local POSIX filesystem (typically `tmpfs`, `ext4`, `xfs`, `apfs`, `ntfs`). On NFS, FUSE, or `overlayfs`, advisory-lock semantics (`F_OFD_SETLK` may degrade to `F_SETLK` or be unsupported), durability guarantees (`fsync`), and `O_NOFOLLOW` correctness on the final component may differ. Validate behavior on the target filesystem before relying on these guards.

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers applicable checklist areas with concise evidence. `exhaustive` enumerates the full checklist only when asked or when the risk surface warrants it. If the user asks for `quick` or `exhaustive`, name the selected depth in the report.

## Required Input Context

Before judging, the invoking agent must establish:

1. **Target.** File path(s) or diff hunk(s) under review.
2. **Trusted root.** The directory the target claims to confine paths within (for example a temp root, configured work directory, or mounted volume). If the target does not declare one, this triggers insufficient-context mode; use the label `trusted-root-undeclared` as the Trigger value of the single Open question finding.
3. **External-input surface.** Which fields flow into the path (for example tenant id, branch name, filename, request parameter). If the surface is unclear from the diff and immediate callers, this triggers insufficient-context mode; use the label `external-input-surface-undeclared` as the Trigger value.
4. **Operation kind.** Read, create, mutate, delete, or several. Each has different required guards (see Checklist sections C–D).

If any of these four are missing and cannot be inferred from the target with confidence, emit a single Open question finding naming what is missing and stop. Do not guess. A guessed trusted root or input surface produces guessed findings.

Insufficient-context mode: when required context is missing, emit `Verdict: BLOCK` with exactly one `Open question` finding using the insufficient-context template in Output Format and stop; do not emit checklist evidence, checklist coverage counts (A-F), cross-cutting recommendations, or residual risk in this mode.

## The Checklist

Every applicable item must be answered "yes, anchored at <file>:<line>" or "N/A because <reason>". An unanswered item is a finding.

### A. Input validation at the trust boundary

- **A1. Whitelist regex per component.** Each segment that comes from external input passes a positive-match pattern, not a blocklist. Multi-segment inputs are split on every path separator valid on the target platform (`/` on POSIX; `/` and `\` on Windows-cross-compatible inputs) and each subsegment validated. Apply the regex after Unicode NFC normalization.
- **A2. Length bound.** Each segment has a maximum length (`255` (UTF-8 byte length, matching the typical POSIX `NAME_MAX`; specify the unit explicitly when documenting your validator) is a sensible filesystem-derived ceiling).
- **A3. No leading `-`.** No segment starts with `-` or `+`, and no segment contains NUL, newline, or tab. Mark N/A when the code performs no shell-out and the path is consumed only by syscalls. CLI-argument-injection defense additionally requires spawn-array invocation (not a shell string) and `--` end-of-options separator before user input.
- **A4. No `.` or `..` segments.** Reject after splitting, not before; a value like `feature/../escape` must fail at the subsegment check.
- **A5. Type and emptiness check.** External input is a string, non-empty, and not coerced from `null`/`undefined`/a number that stringifies into a path.
- **A6. Validation runs before any cache key, lock key, hash, or shared-resource computation derived from the same input.** If a derived key computed from untrusted input precedes validation, a malformed input can churn shared state before being rejected.

### B. Trusted-root handling

- **B1. realpath once, store once.** The trusted root is canonicalized at the boundary (see appendix for language equivalents) and the canonical value is what every subsequent check compares against. Avoid unnecessary re-canonicalization; if canonicalization is repeated per operation, ensure consistent semantics and document why.
- **B2. The root is a real directory.** `lstat(root)` rejects symlinks and non-directories. The root being a symlink is a deployment misconfiguration that should fail loud, not silently follow.
- **B3. Containment uses platform-aware canonical path semantics.** Compare canonical target and canonical root using the platform's path model (separator rules, case sensitivity, volume/device boundaries, normalization behavior) so containment cannot be bypassed by representation differences. In environments where string-prefix checks are known-safe with canonicalized inputs and explicit separator handling, an example is `resolved_target === resolved_root || resolved_target.startsWith(resolved_root + sep)` (pseudo-code; see the Language Appendix Node/TS row for the exact JS idiom). On case-insensitive filesystems (APFS default, NTFS), compare case-folded canonical forms. On macOS, normalize both target and root to a single Unicode form (NFC or NFD) before string compare. The `===`/`startsWith` form above is correct only on Linux ext4/xfs. Comparing unresolved and resolved forms is rejected. A parent of `/tmp/repos/Acme/repo` must not match `/tmp/repos/Acme/repo-EVIL`.

### C. Walk and gate

- **C1. Per-component walk.** Containment is enforced not just on the final path, but on every component from root → target. Each component is `lstat`ed at least once per validation pass. Re-validation passes required by D4/E2 are expected to repeat these checks immediately before mutation.
- **C2. Reject links at path components regardless of target reachability.** A link-type component is rejected without resolving its target (for example, a symlink/reparse-point check in environments that expose it). Dangling links must be rejected, not skipped via an existence-check guard.
- **C3. Reject non-regular components.** At every intermediate segment, regular files, devices, sockets, and FIFOs must be rejected — the next iteration's `lstat` on a joined child otherwise throws raw `ENOTDIR` and breaks the error contract. At the leaf, sensitive control files (PID files, lock files, configs the daemon writes through) must additionally pass `S_ISREG` on `fstat(fd)` after open: a pre-existing FIFO/socket/device at the destination passes a symlink check but is still a hazard.
- **C4. Map filesystem failure classes to the public contract.** Missing-component errors are treated as "not yet existing, continue." Non-directory-intermediate errors are mapped to the validator's documented invalid-path error class. Permission-denied and link-resolution-loop failures are mapped explicitly. Raw OS-specific error details must not leak out of the validator.
- **C5. Hardlink at the leaf.** `lstat` cannot distinguish a hardlink to an outside-root inode from a regular file under the trusted root. For **create**, use `O_CREAT | O_EXCL` (or the platform equivalent) so a planted leaf fails the create. For **mutate or delete** on an existing leaf, open the leaf via anchor-relative ops (`openat` / `dir_fd=fd`) against a fd opened on the canonical parent directory — do not re-traverse the leaf by name. Where the operation reads or exposes file contents, optionally compare `(st_dev, st_ino)` against an explicit deny-list. Where the trusted root resides on a filesystem the runtime user cannot create hardlinks into (e.g. tmpfs-per-tenant, dedicated mount), this item may be marked N/A with the mount/policy as the compensating control.

### D. Open and mutation guards (apply per operation kind)

- **D1. No recursive parent creation on user-derived paths.** Recursive create can follow links at intermediate segments. Use per-segment directory creation (without recursive mode) plus per-segment no-follow metadata checks instead. Tolerate "already exists" only when the existing segment is verified as a real directory, not a link.
- **D2. No-follow open flag (or equivalent) where supported.** When opening an existing or new file under the trusted root, use a symlink-refusing flag. On Linux, `O_NOFOLLOW` only refuses the final pathname component — intermediate-component protection still relies on C1's per-component walk (or `openat` from a fd opened on an already-validated directory). On platforms lacking this guard, document the platform limitation and compensating controls. When opening an attacker-influenced filename for validation, use a non-blocking open variant where available (`O_NONBLOCK` on POSIX) so the open cannot hang on a hostile FIFO before `fstat` rejects non-regular files; clear the non-blocking flag after the file type is verified for a regular file. D2 applies to both read and write opens — opening an existing file for read can follow a symlink just as easily as opening for write.
- **D3. Atomic-rename pattern for writes.** If a new file is being written, write to a sibling temp name under the same realpathed parent and `rename` into place. Do not write through a path that crosses an intermediate component an attacker could swap. Use an unguessable temp name (e.g. random suffix or `mkstemp`-family) created with `O_CREAT | O_EXCL | O_NOFOLLOW`, not a fixed `.tmp` suffix.
- **D4. No chmod/chown/unlink/delete via a path that has not been re-validated immediately before the call.** For especially sensitive deletes, prefer anchor-relative operations (openat/unlinkat family) where the language exposes them.
- **D5. Mutate via the validated fd, not by re-opening the path.** Once a file has been opened and validated, subsequent operations on that file must go through the descriptor: `fstat` not `stat`, `fchmod` not `chmod`, `fchown` not `chown`, `ftruncate` not `truncate`, `write(fd)` not reopen-by-path. Path-based operations re-traverse the filesystem from the root and reintroduce TOCTOU. Where the language exposes anchor-relative `*at` (`openat`, `unlinkat`, `mkdirat`) operations, prefer those for any operation that takes a name relative to an already-validated directory fd.

### E. Resource ordering

- **E1. Validate before acquiring shared resources.** Locks, DB connections, semaphores, file handles must be acquired only after validation throws would have fired. A throw inside a constructor or validator must not leak a held lock or other resource. Construct/validate first, lock second.
- **E2. Re-validate on every entry to a mutating method.** A constructor that validated at instantiation does not absolve a later mutating method from re-validating. Symlinks can be planted between construction and the next call.
- **E3. Same gate on every branch.** If a method has multiple branches (e.g. clone-if-missing vs reset-if-exists), every branch must run the gate before any filesystem mutation. Asymmetric branch coverage is the most common regression after a partial fix.

### F. Tests

- **F1. Per-test isolated temp dir.** Use a per-test isolated temp directory, not a shared fixed-name temp path. Parallel test runners make shared paths race-prone.
- **F2. Time-dependent path segments use a frozen clock.** If the constructed path includes date-based segments, tests freeze time so production code and assertions compute the same value.
- **F3. Coverage for each applicable gate.** At minimum one regression test per applicable A–E gate, including: traversal attempt via `..` segment (A4), root configured as a symlink (B2), symlink at path component (C2), dangling symlink (C2), regular-file intermediate component (C3), leaf-hardlink-to-outside-root (C5), planted symlink between validation and mutation (D1+E2), asymmetric branch gating (E3), and lock-not-held-on-throw (E1). Tests that only cover happy paths or simple ".." traversal do not satisfy this item.

## Procedure

1. Identify the trusted root, external-input surface, and operation kind from the target. If unclear, switch to insufficient-context mode (Output Format) and stop.
2. Walk the checklist top to bottom (A -> F). For each item, find an anchor in the target or mark it as a finding.
3. For each finding, classify using this local vocabulary:
  - Confirmed issue: evidence in code or diff directly shows the guard is missing or broken.
  - Likely risk: strong signal exists, but one dependency or caller context is not fully visible.
  - Open question: required context is missing; no safe conclusion yet.
  - Accepted tradeoff: the gap is real but the project has documented a deviation with an explicit owner and rationale; record the gap, do not re-litigate it.
  - Test gap: control may exist, but tests do not cover a required failure mode.
4. Map severity using this local rubric:
  - CRITICAL: externally reachable path operation can lead to traversal, symlink-follow, destructive mutation, or persistent cross-tenant impact.
  - HIGH: strong security risk exists but exploitability depends on additional constraints or partial mitigations.
  - MEDIUM: meaningful robustness or safety weakness, usually around incomplete hardening or missing regression coverage.
  - LOW: clarity, maintainability, or defensive-hardening gap with limited direct impact.
  Default mapping:
  - C2, C3, C5, D1, D2, E1, E3 -> CRITICAL when externally reachable with no compensating control; otherwise HIGH.
  - A1-A6, B1-B3, C1, C4, D3, D4, D5, E2 -> HIGH unless a compensating control is documented and verifiable.
  - F1-F3 -> MEDIUM (test-gap class).
  - Severity may be adjusted up or down by one level based on external reachability, privilege boundary crossing, operation destructiveness, and verifiable compensating controls.
5. Map findings to the overall verdict:
  - BLOCK: any Confirmed-issue CRITICAL finding, any HIGH finding without a documented compensating control or owner-accepted tradeoff, OR insufficient-context mode (required context cannot be established).
  - CONCERNS: HIGH or MEDIUM findings remain but each is either non-externally-reachable, has a documented compensating control, or is owner-accepted.
  - CLEAN: every applicable item is anchored AND F3 regression coverage exists per applicable A-E gate. (See also the existing CLEAN constraint at the end of Output Format.)
6. Deduplicate findings — if the same missing helper triggers multiple checklist items, file one finding with the full list of failing item IDs.
7. Emit findings in the Output Format below.

Insufficient-context mode output rule: when step 1 cannot establish required context with confidence, emit `Verdict: BLOCK` with exactly one `Open question` finding using the insufficient-context template and stop; skip checklist evidence, the A-F coverage summary, cross-cutting recommendations, and residual risk.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <file or diff>
Trusted root: <declared canonical root or "undeclared">
External-input surface: <fields or "undeclared">
Operation kind: <read | create | mutate | delete | mixed>

Findings:
1. <checklist item IDs and short title>
  Anchor: <file:line> or "no anchor; missing from target"
  Category: Input validation | Trusted-root handling | Walk and gate | Mutating operation | Resource ordering | Tests
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff | Test gap
  Trigger: <one-sentence concrete scenario>
  Risk: <what an attacker, a planted symlink, or a race wins>
  Required guard: <the specific check or pattern the checklist names>
  Suggested anchor: <minimal language-appropriate snippet pointing at the missing guard>

Checklist evidence (non-findings):
  <item ID>: YES @ <file:line>
  <item ID>: N/A because <reason>

Coverage summary:
  A: <count answered yes> / <count applicable>
  B: <...>
  C: <...>
  D: <...>
  E: <...>
  F: <...>

Cross-cutting recommendations: <e.g. extract a shared safeMkdirP helper used at every site; promote validation to the constructor and re-check at each mutating method entry; share the per-test mkdtemp + fake-timers setup as a test helper>
Residual risk: <e.g. filesystem-level TOCTOU between consecutive lstat checks remains bounded but not eliminated; trusted-root compromise is out of scope; etc.>
```

Insufficient-context mode template (deterministic):

```text
Verdict: BLOCK
Target: <file or diff>

Findings:
1. <missing-context short title>
  Anchor: "no anchor; missing from target"
  Category: Input validation | Trusted-root handling | Walk and gate | Mutating operation | Resource ordering | Tests
  Severity: LOW
  Classification: Open question
  Trigger: <which required context is missing>
  Risk: <why safe conclusion is blocked>
  Required guard: <what context must be supplied>
  Suggested anchor: <where to look or what to provide>
```

In insufficient-context mode, do not emit checklist evidence, coverage summary, cross-cutting recommendations, or residual risk.

`CLEAN` is permitted when every applicable item has an anchor and at least one regression test per applicable A-E gate exists.

## Language Appendix

The checklist is language-agnostic. The table below presents common equivalents across languages as peers.

| Concern | Node / TypeScript | Python | Go | Rust | C | C++ | Windows (Win32 / .NET) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canonicalize root | `fs.realpathSync` / `fs.promises.realpath` | `os.path.realpath` | `filepath.EvalSymlinks` | `std::fs::canonicalize` | `realpath(3)` | `std::filesystem::canonical` | `GetFinalPathNameByHandle` / `Path.GetFullPath` |
| `lstat` (no follow) | `fs.lstatSync` / `fs.promises.lstat` | `os.lstat` | `os.Lstat` | `std::fs::symlink_metadata` | `lstat(2)` | `::lstat` (POSIX) / `std::filesystem::symlink_status` | `GetFileAttributesExW` (check `FILE_ATTRIBUTE_REPARSE_POINT`) / `File.GetAttributes` |
| Symlink check | `stats.isSymbolicLink()` | `stat.S_ISLNK(st_mode)` | `mode & fs.ModeSymlink != 0` | `metadata.file_type().is_symlink()` | `S_ISLNK(st.st_mode)` | `std::filesystem::is_symlink(std::filesystem::symlink_status(p))` | `attr & FILE_ATTRIBUTE_REPARSE_POINT != 0` |
| Directory check | `stats.isDirectory()` | `stat.S_ISDIR(st_mode)` | `info.IsDir()` | `metadata.is_dir()` | `S_ISDIR(st.st_mode)` | `std::filesystem::is_directory(std::filesystem::symlink_status(p))` | `attr & FILE_ATTRIBUTE_DIRECTORY != 0` |
| Open without follow | `fs.openSync(p, fs.constants.O_RDWR \| fs.constants.O_NOFOLLOW)` | `os.open(..., os.O_NOFOLLOW)` | `unix.O_NOFOLLOW` | `OpenOptions::custom_flags(libc::O_NOFOLLOW)` | `open(path, flags \| O_NOFOLLOW, mode)` | `::open(path.c_str(), flags \| O_NOFOLLOW, mode)` | `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT` |
| Non-recursive mkdir | `fs.mkdirSync(p)` (no `recursive`) | `os.mkdir(p)` | `os.Mkdir(p, mode)` | `std::fs::create_dir(p)` | `mkdir(path, mode)` | `std::filesystem::create_directory` | `CreateDirectoryW` |
| Per-job temp dir | `fs.mkdtempSync(prefix)` | `tempfile.mkdtemp(prefix=)` | `os.MkdirTemp(dir, prefix)` | `tempfile::TempDir::new_in` | `mkdtemp(template)` | `mkdtemp` via wrapper / `std::filesystem::temp_directory_path` + unique suffix | `GetTempPathW` + `CreateDirectoryW` with unique suffix |
| Anchor-relative ops | n/a (no `*at` in stdlib) | `os.open(..., dir_fd=fd)`, `os.mkdir(..., dir_fd=fd)`, `os.unlink(..., dir_fd=fd)` (see `os.supports_dir_fd`) | `unix.Openat`, `unix.Mkdirat`, `unix.Unlinkat` | `openat` crate | `openat`, `mkdirat`, `unlinkat` | `::openat`, `::mkdirat`, `::unlinkat` | n/a (no `*at` family on Win32) |

## Anti-Patterns

- **Do not flag "use a hashed directory name" unconditionally.** Hashed names eliminate the input-validation problem but lose human-debuggable layout; this is a tradeoff, not a universal fix.
- **Do not require `O_NOFOLLOW` on platforms that lack it.** Mark D2 as N/A on Windows-only code paths; the equivalent guard is `FILE_FLAG_OPEN_REPARSE_POINT`.
- **Do not restate the diff as a finding.** "The code calls `mkdirSync`" is not a finding; "the code calls `mkdirSync({ recursive: true })` on a user-derived path with no per-segment `lstat`" is.
- **Do not widen scope beyond path safety.** If the target also has auth, secrets, or business-logic concerns, capture them separately; this skill is only for filesystem path safety.
- **Do not produce a `CLEAN` verdict when only happy-path tests exist.** F3 specifically requires regression tests anchored to each applicable gate.
- **Do not open with `O_TRUNC` before validation.** Truncate-on-open clobbers the file before `fstat` and the lock acquisition can decide it's the wrong file. Open without `O_TRUNC`, validate (`S_ISREG`, ownership, mode, `st_nlink == 1`), acquire any required lock, then `ftruncate(fd, 0)` through the validated descriptor.
- **Do not gate an open on `access()`.** `access(2)` uses the real UID/GID rather than the effective UID/GID, and the file the kernel checks may not be the file you later open. Open with the minimum-privilege flags, then validate via `fstat(fd)`. The same applies to `stat(path)` before `open(path)`: any check on the pathname before the open is presumptive — only `fstat` on the resulting descriptor is authoritative.
- **Do not `chmod`/`chown` by path after open.** `chmod(path, ...)` and `chown(path, ...)` re-traverse the filesystem from the root and can land on a different inode than the one your fd refers to. Use `fchmod(fd, ...)` and `fchown(fd, ...)` (see D5).

