# shell-portability

> Use when: writing, reviewing, or fixing shell code against a declared shell/OS target or across multiple targets — POSIX sh vs bash/ksh/zsh, dash/ash/busybox as /bin/sh, GNU vs BSD/macOS vs busybox coreutils, CI containers, Alpine, or unknown targets. Covers bashisms, non-portable utility flags, shebang/interpreter targeting, locale and word-splitting hazards, and portable replacements.

This skill is aimed at shell code assessed against an explicit shell/OS target or across multiple targets, where the question is whether every construct and utility invocation is portable for the declared target rather than whether it happens to work on the author's machine.

It helps an assistant:

- establish the portability target (declared shells/OSes, or a POSIX-sh + GNU/BSD/macOS/busybox default baseline) and check the shebang matches the language used
- catch bashisms in `#!/bin/sh` scripts (`[[ ]]`, arrays, `local`, `source`, `${var,,}`, process substitution, `pipefail`, …) and give POSIX replacements
- flag non-portable utility flags and non-POSIX utilities on BSD/macOS/busybox targets (`readlink -f`, `sed -i`, `sed -r`, `grep -P`, `find -printf`, `date -d`, `seq`, `xargs -r`, `stat`) with portable forms
- catch behavioral hazards: `echo` escapes/flags, unquoted word-splitting, locale-dependent `sort`/`tr`, non-POSIX `trap`/`set` options
- return `BLOCK`, `CONCERNS`, or `CLEAN` with target, interpreter, findings, checklist status, verification path, and an insufficient-context template

It is **not** for concrete shell command construction correctness where literal data, argv boundaries, heredocs, redirection, or transport preservation are the primary concern; it is also not for pure bash-only feature questions or non-shell languages. Quoting is still in scope here for its word-splitting/globbing portability effects. A raw mixed request without a separate construction result does not activate this skill: construction review owns a concrete target first, while a generic request needs a concrete command, executable, fragment, or payload interface before either review. Before portability analysis, require `BLOCKED` with exact `Candidate: Not provided`; `VALID`/`REWRITE` forbid that placeholder (including trailing whitespace) and require a nonblank one-line candidate or a correctly prefixed multiline candidate with nonblank payload. Inconsistent combinations use reduced `BLOCK` and request a corrected result. A consistent blocked result also uses reduced `BLOCK`, while a complete candidate is reviewed without making a construction claim. For a serialized multiline candidate, remove exactly its two-space per-line serialization prefix before review while preserving additional indentation and empty lines; a missing prefix uses the reduced `BLOCK` form and requires a corrected construction result.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/portability-catalog.md`](references/portability-catalog.md) — bashism→POSIX table, GNU-vs-BSD utility flag matrix, behavioral hazards, and verification tooling.
- [`references/source-map.md`](references/source-map.md) — provenance and source-confidence notes.
