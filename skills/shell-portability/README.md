# shell-portability

> Use when: writing, reviewing, or fixing shell scripts that must run on more than one shell or OS — POSIX sh vs bash/ksh/zsh, dash/ash/busybox as /bin/sh, GNU vs BSD/macOS vs busybox coreutils, CI containers, Alpine, or unknown targets. Covers bashisms, non-portable utility flags (readlink -f, sed -i, grep -P, date -d), shebang and interpreter targeting, locale and word-splitting hazards, and portable replacements.

This skill is aimed at shell code that must run identically across multiple shells and operating systems, where the question is whether every construct and utility invocation is portable across the declared target set rather than whether it happens to work on the author's machine.

It helps an assistant:

- establish the portability target (declared shells/OSes, or a POSIX-sh + GNU/BSD/macOS/busybox default baseline) and check the shebang matches the language used
- catch bashisms in `#!/bin/sh` scripts (`[[ ]]`, arrays, `local`, `source`, `${var,,}`, process substitution, `pipefail`, …) and give POSIX replacements
- flag GNU-only utility usage on BSD/macOS/busybox targets (`readlink -f`, `sed -i`, `sed -r`, `grep -P`, `find -printf`, `date -d`, `seq`, `xargs -r`, `stat`) with portable forms
- catch behavioral hazards: `echo` escapes/flags, unquoted word-splitting, locale-dependent `sort`/`tr`, non-POSIX `trap`/`set` options
- return `BLOCK`, `CONCERNS`, or `CLEAN` with target, interpreter, findings, checklist status, verification path, and an insufficient-context template

It is **not** for shell command *safety* (destructive commands, secret leakage, data-loss-prevention quoting review), pure bash-only feature questions, or non-shell languages. Quoting is still in scope here for its word-splitting/globbing portability effects.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/portability-catalog.md`](references/portability-catalog.md) — bashism→POSIX table, GNU-vs-BSD utility flag matrix, behavioral hazards, and verification tooling.
- [`references/source-map.md`](references/source-map.md) — provenance and source-confidence notes.
