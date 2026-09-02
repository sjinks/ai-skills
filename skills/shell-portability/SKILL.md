---
name: shell-portability
description: "Use when: writing, reviewing, or fixing shell code against a declared shell/OS target or across multiple targets — POSIX sh vs bash/ksh/zsh, dash/ash/busybox as /bin/sh, GNU vs BSD/macOS vs busybox coreutils, CI containers, Alpine, or unknown targets. Covers bashisms, non-portable utility flags, shebang/interpreter targeting, locale and word-splitting hazards, and portable replacements. Do not use for generic shell feature tutoring or a raw mixed construction-and-portability request before a separate construction result is supplied."
argument-hint: "Paste the script or the commands, and name the target shells/OSes if known."
user-invocable: true
---

# Shell Portability

Use this skill when shell code (a script, snippet, `Makefile`/CI recipe, or command) must be assessed against a declared shell/OS target or across multiple targets, and the question is whether every construct and utility invocation is portable for that target set.

The goal is shell code that runs identically on its declared targets: no bashisms in a `#!/bin/sh` script, no GNU-only utility flags on a BSD/macOS/busybox box, and every behavioral assumption (word-splitting, locale, `echo`, glob) made explicit and safe.

**UTILITY SKILL.** INVOKES: read-only access to the supplied script/commands; no other tools or skills. FOR SINGLE OPERATIONS: use to audit a script for portability, pick a portable replacement for one command, or write a new script against a stated target.

## Scope

- Use this skill for: bashisms in POSIX `sh` scripts; GNU-vs-BSD/macOS-vs-busybox utility differences (`readlink`, `sed`, `grep`, `find`, `date`, `stat`, `mktemp`, `xargs`, `cp`, `sort`, `head`, `tr`, `awk`, `getopt`); shebang and interpreter selection; `echo`/`printf` behavior; quoting, word-splitting, and glob behavior across shells; locale-dependent behavior (`LC_ALL=C`); and declaring the portability target.
- Apply it to script reviews, new-script authoring, "is this command portable?" questions, and CI failures that differ between Linux and macOS or between bash and dash/ash.
- Treat a `#!/bin/sh` script that depends on bash-only features as a finding even if it happens to work on the author's machine (where `/bin/sh` may be bash) — `/bin/sh` is `dash` on Debian/Ubuntu and `busybox ash` on Alpine.

## DO NOT USE FOR:

- Shell command construction correctness when portability is not the requested outcome — concrete literal-data, argv-boundary, heredoc, redirection, and transport preservation is outside this skill. (Quoting is in scope here only for its word-splitting/globbing portability effects, not as data-loss-prevention review.)
- Pure bash feature questions where bash is the only declared target and portability is not required.
- Performance tuning, general scripting style, or non-shell languages (Python, Perl, PowerShell) where shell portability does not apply.

For a raw request that combines construction correctness and portability, do not activate this skill. If shell construction is in scope for construction review, that review owns the first response. If correctness instead depends on excluded domain-specific interface semantics such as GitHub CLI field or stdin behavior, the dedicated interface workflow owns the first response and must supply an exact corrected command; subsequent portability review treats that command as direct code and does not require an SCC result. If no concrete target exists, ask for a command, executable, fragment, or payload interface before either review. Direct portability-only requests that supply code also follow the normal review path without a construction result. Only for a mixed-request handoff after SCC review, require one complete ordered five-field result: `Construction result`, nonblank `Construction assessment`, `Candidate`, exact `Execution authority: NOT ASSESSED BY THIS SKILL`, then nonblank `Next step`. The result value must be exactly `BLOCKED`, `VALID`, or `REWRITE`; absent, unknown, missing, reordered, or duplicated fields use the reduced insufficient-context `BLOCK` template. Then validate disposition/candidate consistency: `BLOCKED` requires exact `Candidate: Not provided`; `VALID` and `REWRITE` forbid that reserved placeholder (including trailing-whitespace variants) and require either a nonblank one-line candidate or exact `Candidate: |` with correctly prefixed payload lines and at least one non-whitespace payload character. A one-line candidate whose first non-whitespace character is `|` requires a later non-whitespace character on that same line. Only bare `Candidate: |` with no trailing whitespace is the multiline marker; trailing whitespace after that pipe is malformed whether or not payload lines follow. Route every malformed or inconsistent SCC handoff to reduced `BLOCK` and request a corrected construction result. For a consistent `BLOCKED` result, state that no exact constructed candidate is available and require construction to be completed or resolved first. Otherwise review the exact construction candidate and make no construction claim.

When an SCC handoff serializes a multiline candidate as `Candidate: |`, remove exactly the first two spaces from every following candidate payload line before portability analysis. Preserve any additional leading spaces and serialized empty lines as candidate data. Only unprefixed `Execution authority: NOT ASSESSED BY THIS SKILL` validly terminates the payload. If `Construction result:`, `Construction assessment:`, `Candidate:`, or `Next step:` appears unprefixed before that terminator, or any payload line lacks the two-space prefix, use reduced `BLOCK` and request a corrected SCC result rather than truncating or analyzing altered command text.

## Required Context

Establish or infer before judging:

- The code: the script, snippet, or command under review (or the behavior to author).
- The portability target: which shells (`POSIX sh`, `bash`, `ksh`, `zsh`, `dash`/`ash`/`busybox`), which OSes/coreutils (GNU/Linux, BSD/macOS, busybox/Alpine), and any version floors (e.g. bash 3.2 for macOS).
- The interpreter: the shebang line, or how the script is invoked (`sh script`, `bash script`, sourced).

If no code is supplied, return `Verdict: BLOCK` with one open question; do not invent a script. If code is supplied but the target is unstated, **default to the broadest baseline** — `POSIX sh` (POSIX.1-2017 Shell & Utilities) running under `dash`/`busybox ash`, with utilities that may be GNU **or** BSD/macOS **or** busybox — state that assumption on a `Target:` line, and judge against it. Only narrow the baseline when the user names specific targets.

## Workflow

1. Establish the target (declared or default baseline) and read the shebang to learn the intended interpreter.
2. Scan for **interpreter/shebang mismatch**: bash features under `#!/bin/sh`, a missing shebang on a directly-executed script, a hardcoded interpreter path that does not match the declared target (e.g. `#!/bin/bash` where bash is needed but not at that path — prefer `#!/usr/bin/env bash`), or reliance on the login shell.
3. Scan for **bashisms** (constructs absent from POSIX sh): see the catalog. Flag each with its POSIX replacement.
4. Scan for **non-portable utility usage**: GNU-only flags and utilities that differ or are absent on BSD/macOS/busybox. Flag each with a portable form.
5. Scan for **behavioral hazards**: unquoted expansions (word-splitting/globbing), `echo` with flags or escapes, locale-dependent `sort`/`sed`/`tr`, `$RANDOM`/`$SECONDS`/arrays/associative arrays, non-portable `trap`/`set` options (`pipefail`).
6. For each finding, give the portable replacement and the condition under which the original is acceptable (e.g. "fine if the target is bash-only").
7. Classify by severity, map to a verdict, and state how to verify (run under `dash`, `shellcheck`, `checkbashisms`, or a BSD/macOS box).

## Decision Rules

The Checklist below is the gating source of truth when these rules overlap; the rules explain rationale.

- When a script's shebang is `#!/bin/sh`, every construct must be POSIX sh; bash-only syntax is a finding even if it runs on the author's machine. If bash features are genuinely needed, the fix is either to rewrite them in POSIX form or to change the shebang to `#!/usr/bin/env bash` and accept the bash dependency. Do not rely on `/bin/sh` being bash.
- When choosing a shebang for a bash-targeted script, prefer `#!/usr/bin/env bash` over `#!/bin/bash`: the bash you want is not always at `/bin/bash` (macOS ships an old bash 3.2 there; a newer Homebrew/MacPorts bash lives at `/usr/local/bin/bash` or `/opt/homebrew/bin/bash`; some BSDs put it under `/usr/local/bin` or have no `/bin/bash` at all). `env` resolves the first `bash` on `PATH`; the tradeoff is you get whichever that is.
- When the target is POSIX sh, replace bashisms with POSIX equivalents: `[[ ]]`→`[ ]`/`test`, `==`→`=` in `[ ]`, arrays→positional params or whitespace-separated lists, `local`→note it is not POSIX (widely supported by dash/ash/busybox but not guaranteed; document the assumption), `function name()`→`name()`, `source`→`.`, `${var,,}`/`${var^^}`→`tr`, `+=`→`var="$var$add"`, `<()`/`>()` process substitution→temp files or pipes, `&>file`→`>file 2>&1`, `cmd1 |& cmd2`→`cmd1 2>&1 | cmd2`, `{1..10}`→a `while`-loop counter (`seq` is not POSIX), `$'...'`→`printf`, `read -a`→`read` + `IFS`/`set --`.
- When portable output is needed, use `printf` instead of `echo`: `echo` is not portable for flags (`-n`, `-e`) or backslash escapes — escape interpretation and `-n` handling vary by implementation and by options (`xpg_echo`, `-e`/`-E`), and `echo -n` is unspecified by POSIX. `printf '%s\n' "$x"` and `printf '%s' "$x"` are the portable forms. Never pass user data as the `printf` format string; put it in a `%s` argument.
- When `set -o pipefail` is used, note it is not POSIX (bash/ksh/zsh/busybox-ash have it; dash does not). For `#!/bin/sh` targeting dash, either drop it or guard it; do not assume it exists.
- When a non-portable utility flag or a non-POSIX utility is used, replace it with a portable form (see the catalog): exact `readlink -f` canonicalization requires a confirmed available `realpath` implementation whose final-component, existence, and error semantics match the requirement; GNU `realpath`/`grealpath` are examples, not the only implementations. A `cd`/`pwd -P` plus basename fallback has reduced semantics and is valid only when that reduction is accepted; `sed -i`→write to a temp file and `mv`, or split `-i ''` (BSD) vs `-i` (GNU) by target; `grep -P`→`grep -E` (ERE is POSIX) and avoid PCRE; `sed -r`/`sed -E`→rewrite to POSIX BRE (POSIX `sed` specifies neither `-r` nor `-E`; BSD/macOS and modern GNU accept `-E`, busybox often only `-r`); `find -printf`/`find -regex`→portable `-exec`/`-name`; `date -d`/`date +%s -d`→`date -v` (BSD) differs, prefer no relative-date math or a dedicated tool; `xargs -r`→GNU/busybox and macOS (older BSD) `xargs` run the utility once even on empty input; `-r` suppresses that but is GNU/busybox-only (FreeBSD accepts `-r` but already skips empty input; macOS lacks `-r`), so guard empty input explicitly (`[ -s file ]`) rather than relying on `-r`; `mktemp`→`mktemp` template forms differ, use `mktemp 2>/dev/null || mktemp -t tmp`; `stat`/`cp --parents`/`sort -h`/`tac`/`seq` similarly.
- When word-splitting or globbing matters, quote every expansion (`"$var"`, `"$@"`) unless splitting is the explicit intent, in which case set `IFS` deliberately; unquoted `$var` behaves differently with different `IFS` and filenames across shells.
- When byte-exact text processing matters, set `LC_ALL=C` for `sort`, `sed`, `tr`, `grep` ranges; locale changes collation and character-class behavior across systems.
- When the script uses `awk`, stick to POSIX awk features: GNU awk extensions (`gensub`, `asort`, `--`, `length(array)`, third arg of `match`) are absent in BSD/`mawk`/busybox awk.

## Checklist

### Interpreter And Shebang

- Shebang matches the language actually used (POSIX sh script uses only POSIX features; bash script uses `#!/usr/bin/env bash`).
- No reliance on `/bin/sh` being bash, or on a hardcoded `/bin/bash` path.

### Bashisms (when target includes POSIX sh)

- No `[[ ]]`, `==` in test, `-nt`/`-ot`/`-ef` test operators (POSIX.1-2024 only), C-style `for ((;;))`, arrays/associative arrays, `local` without a documented assumption (ksh uses `typeset`), `function` keyword, `source`, `${var,,}`/`${var^^}`/`${var:offset:len}` slicing, `${var/pat/repl}` substitution, `+=`, process substitution, herestrings `<<<`, extended globs `+( )`/`@( )`/`!( )`, `$(<file)` slurp, `&>`/`|&`, brace ranges `{1..n}`, `$'...'`, `read -a`, `mapfile`, `$RANDOM`, `$SECONDS`, `select`, `shift N` past `$#` (aborts dash/posh/mksh/ksh93), `trap ... ERR`, `set -o pipefail` assumed present.

### Utilities And Flags

- No non-portable utility flags or non-POSIX utilities on a target that includes BSD/macOS/busybox (`readlink -f`, `sed -i`/`-r`, `grep -P`, `find -printf`/`-regex`, `date -d`, `cp --parents`, `sort -h`, `xargs -r` assumed, `head -c` on busybox quirks, `stat` format strings, `seq`, `tac`, `realpath`).
- Each utility invocation uses POSIX-specified options, or a target-conditional branch, or a portable shell replacement.

### Output And Behavior

- `printf` is used instead of `echo` for anything beyond a trailing-newline literal with no escapes/flags; user data never sits in the format string.
- Every expansion that could word-split or glob is quoted, or `IFS`/`set -f` is set deliberately.
- `read` loops that must process a no-trailing-newline final line use `while IFS= read -r line || [ -n "$line" ]`.
- Locale-sensitive text operations set `LC_ALL=C` where byte/collation behavior matters.
- No reliance on non-POSIX `set`/`trap` options (`pipefail`, `ERR`) when targeting POSIX sh.

### Verification

- Portability fixes have a verification path: `shellcheck` (with the right `-s sh`/`-s bash` shell), `checkbashisms` for `/bin/sh` scripts, or a run under `dash`/`posh`/`busybox ash` (and `ksh` for BSD/UNIX targets) and on a BSD/macOS box. If no code changes are in scope, this item is n/a.

## Severity And Verdicts

- `CRITICAL`: the code will fail or silently misbehave on a target the user explicitly named as required — e.g. a bashism under `#!/bin/sh` when Alpine/busybox is a stated target, or a GNU-only flag when macOS is a stated target.
- `HIGH`: non-portable construct that breaks on an in-scope target under the default baseline (no explicit target was named) while working in the author's environment — e.g. works on Linux, breaks under dash/macOS — or `echo`-with-escapes whose output silently differs by shell. Silent wrong output (not just an error) is at least `HIGH` regardless of which rule selects the target.
- `MEDIUM`: portability hazard that is currently latent — unquoted expansion that is safe for today's inputs, missing `LC_ALL=C` where collation could bite, `local`/`pipefail` used without documenting the relaxed-target assumption.
- `LOW`: style, hardening, or a portable-but-fragile idiom with no current incorrect behavior.

Verdicts:

- `BLOCK`: no code supplied (cannot judge), any `CRITICAL`, or any unmitigated `HIGH`.
- `CONCERNS`: any unmitigated `MEDIUM`, or remaining `HIGH`/`MEDIUM` findings that each have a stated relaxed target, compensating branch, or accepted tradeoff.
- `CLEAN`: every applicable checklist item holds for the target. `LOW`-only findings do not block `CLEAN` and are listed. If no code changes are in scope, Verification is n/a and does not block `CLEAN`.

## Output Format

```text
Verdict: BLOCK | CONCERNS | CLEAN
Target: <declared shells/OSes, or "default baseline: POSIX sh under dash/busybox ash + GNU/BSD/macOS/busybox utilities">
Interpreter: <shebang / how invoked, or undeclared>

Findings:
1. <short title>
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Classification: Confirmed issue | Likely risk | Open question | Accepted tradeoff
  Evidence: <line, snippet, or command>
  Rule: <interpreter-shebang | bashisms | utilities-flags | output-behavior | verification>
  Risk: <what breaks, on which target>
  Portable fix: <POSIX replacement or target-conditional branch>
  Verification: <shellcheck -s sh | checkbashisms | run under dash/busybox | BSD/macOS run | N/A>

Checklist status:
- Interpreter and shebang: covered | missing | n/a
- Bashisms: covered | missing | n/a
- Utilities and flags: covered | missing | n/a
- Output and behavior: covered | missing | n/a
- Verification: covered | missing | n/a

Residual risk: <remaining caveats or None>
```

`Rule:` values map to checklist sections: `interpreter-shebang` -> Interpreter And Shebang; `bashisms` -> Bashisms; `utilities-flags` -> Utilities And Flags; `output-behavior` -> Output And Behavior; `verification` -> Verification.

When no material issues exist, write exactly `Findings: None` (allowed only with `CLEAN`) and list assumptions under Residual risk.

Insufficient-context mode: when no reviewable code or exact construction candidate is available because no code was supplied, construction was `BLOCKED` without a candidate, or multiline construction serialization is malformed, emit exactly this reduced template and stop; do not emit interpreter or checklist status with guessed values. The `BLOCK` verdict here is triggered by unavailable reviewable command text, not by the finding's severity:

```text
Verdict: BLOCK
Target: <declared or default baseline>

Findings:
1. <missing-context short title>
  Severity: LOW
  Classification: Open question
  Evidence: <why no reviewable command text is available>
  Rule: <interpreter-shebang | bashisms | utilities-flags | output-behavior | verification>
  Risk: <why no safe conclusion is possible>
  Portable fix: <the code, completed construction, or corrected serialization that must be supplied>
  Verification: N/A
```

## Examples

- `readlink -f "$path"` under a macOS/BSD target fails: BSD `readlink` has no `-f`. For exact canonicalization, require a confirmed available `realpath` implementation with matching final-component, existence, and error semantics; GNU `realpath`/`grealpath` are examples. A `cd`/`pwd -P` plus basename fallback does not resolve a final-component symlink and is only a documented reduced-semantics alternative.
- `#!/bin/sh` script using `if [[ "$x" == y* ]]; then`: under dash/busybox this is a syntax error. Portable fix: `case "$x" in y*) ... ;; esac`, or `[ "$x" = "y" ]` for exact match.
- `sed -i 's/a/b/' f` differs: GNU takes `-i`, BSD/macOS needs `-i ''`. Portable fix: `tmp=$(mktemp 2>/dev/null || mktemp -t tmp) || exit; sed 's/a/b/' f > "$tmp" && mv "$tmp" f`, or use an explicit GNU/BSD branch.
- `echo -n "$msg"` is unspecified: whether `-n` is treated as a flag or printed, and whether escapes are interpreted, varies by shell/implementation and options (`xpg_echo`, `-e`/`-E`). Portable fix: `printf '%s' "$msg"`.

## Provenance

Source confidence and key references live in [references/source-map.md](references/source-map.md); the full replacement matrix lives in [references/portability-catalog.md](references/portability-catalog.md).

## Definition Of Done

A shell portability review or rewrite is ready only when:

- The target is stated (declared or default baseline) and the shebang matches the language used (per Interpreter And Shebang).
- No bashisms remain for a POSIX-sh target, or each is justified by a stated relaxed target (per Bashisms).
- Every utility invocation is POSIX-portable, target-conditional, or replaced (per Utilities And Flags).
- Output uses `printf`, expansions are quoted, and locale-sensitive ops are pinned (per Output And Behavior).
- A verification path is recorded for the changes (per Verification).
