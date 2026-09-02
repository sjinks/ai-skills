# shell-portability

> Use when: writing, reviewing, or fixing shell code against a declared shell/OS target or across multiple targets — POSIX sh vs bash/ksh/zsh, dash/ash/busybox as /bin/sh, GNU vs BSD/macOS vs busybox coreutils, CI containers, Alpine, or unknown targets. Covers bashisms, non-portable utility flags, shebang/interpreter targeting, locale and word-splitting hazards, and portable replacements.

This skill is aimed at shell code assessed against an explicit shell/OS target or across multiple targets, where the question is whether every construct and utility invocation is portable for the declared target rather than whether it happens to work on the author's machine.

It helps an assistant:

- establish the portability target (declared shells/OSes, or a POSIX-sh + GNU/BSD/macOS/busybox default baseline) and check the shebang matches the language used
- catch bashisms in `#!/bin/sh` scripts (`[[ ]]`, arrays, `local`, `source`, `${var,,}`, process substitution, `pipefail`, …) and give POSIX replacements
- flag non-portable utility flags and non-POSIX utilities on BSD/macOS/busybox targets (`readlink -f`, `sed -i`, `sed -r`, `grep -P`, `find -printf`, `date -d`, `seq`, `xargs -r`, `stat`) with portable forms
- catch behavioral hazards: `echo` escapes/flags, unquoted word-splitting, locale-dependent `sort`/`tr`, non-POSIX `trap`/`set` options
- return `BLOCK`, `CONCERNS`, or `CLEAN` with target, interpreter, findings, checklist status, verification path, and an insufficient-context template

It is **not** for concrete shell command construction correctness where literal data, argv boundaries, heredocs, redirection, or transport preservation are the primary concern; it is also not for pure bash-only feature questions or non-shell languages. Quoting is still in scope here for its word-splitting/globbing portability effects. A raw mixed request does not activate this skill: shell construction review owns in-scope construction, while excluded domain-specific interface work (for example GitHub CLI field/stdin semantics) owns its correction first and must supply an exact command; that command can then use the direct portability path without an SCC result. Generic requests need a concrete target. Direct portability-only code also uses the normal path. Only a mixed handoff after SCC review requires the complete ordered five fields, exact unassessed authority, and result `BLOCKED`, `VALID`, or `REWRITE`; malformed fields or unknown disposition use reduced `BLOCK`. `BLOCKED` requires exact `Candidate: Not provided`; `VALID`/`REWRITE` forbid that placeholder and require a nonblank one-line candidate or exact `Candidate: |` with correctly prefixed nonblank payload. A leading one-line `|` requires later text; whitespace after a bare pipe is malformed. For multiline SCC candidates, remove exactly the two-space prefix and preserve remaining data; only exact unprefixed `Execution authority: NOT ASSESSED BY THIS SKILL` terminates payload. Any earlier unprefixed SCC field or missing payload prefix uses reduced `BLOCK` and requests a corrected result.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/portability-catalog.md`](references/portability-catalog.md) — bashism→POSIX table, GNU-vs-BSD utility flag matrix, behavioral hazards, and verification tooling.
- [`references/source-map.md`](references/source-map.md) — provenance and source-confidence notes.
