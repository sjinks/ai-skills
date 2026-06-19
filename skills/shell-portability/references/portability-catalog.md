Read this when you need the full replacement matrix for a specific bashism or utility flag, or the source confidence behind a portability claim in `SKILL.md`.

# Portability Catalog

Targets referenced below:

- **POSIX sh** — POSIX.1-2017 (IEEE Std 1003.1-2017) Shell Command Language and Utilities. The portable floor.
- **dash** — Debian/Ubuntu default `/bin/sh`. Near-POSIX, few extensions.
- **busybox ash** — Alpine/embedded default `/bin/sh`. Mostly POSIX with some bash-like extras (`local`, `pipefail`).
- **bash** — GNU bash; note macOS ships bash 3.2 (no `mapfile`, no `${var^^}`, no associative arrays).
- **GNU coreutils** — Linux default utilities. Many flags here are GNU-only.
- **BSD/macOS** — FreeBSD/macOS userland; many GNU flags absent or spelled differently.

## Bashisms → POSIX replacements

| Bashism | POSIX replacement | Notes |
|---|---|---|
| `[[ cond ]]` | `[ cond ]` / `test` / `case` | `[[ ]]` is bash/ksh/zsh; not in dash/POSIX. Use `case` for pattern match. |
| `==` inside `[ ]` | `=` | `==` works in bash `[ ]` but is non-POSIX. |
| `for ((i=0;i<n;i++))` | `i=0; while [ "$i" -lt "$n" ]; do ...; i=$((i+1)); done` | C-style for is bash/ksh. |
| `arr=(a b c)` / `${arr[i]}` | positional params `set -- a b c` / `"$@"` / whitespace list | No arrays in POSIX sh. |
| `declare -A` associative arrays | separate vars or external tool | bash 4+ only (not macOS bash 3.2). |
| `local x` | (document assumption) | Not POSIX, but dash/ash/busybox/bash support it. Acceptable on those targets; note it. |
| `function name { }` | `name() { }` | `function` keyword is bash/ksh. |
| `source file` | `. file` | `source` is bash/zsh alias for `.`. |
| `${var,,}` / `${var^^}` | `printf '%s' "$var" \| tr '[:upper:]' '[:lower:]'` | Case modification is bash 4+. |
| `${var:offset:len}` | `cut` / `awk` / `expr substr` | Substring slicing is bash/ksh. |
| `var+=x` | `var="$var"x` | `+=` is bash/ksh. |
| `<(cmd)` / `>(cmd)` process subst | temp file or pipe | bash/zsh/ksh only; needs `/dev/fd`. |
| `cmd &>file` | `cmd >file 2>&1` | `&>` is bash. |
| `cmd1 \|& cmd2` | `cmd1 2>&1 \| cmd2` | `\|&` is bash. |
| `{1..10}` brace range | `seq 1 10` (note seq portability) or `while` loop | Brace ranges are bash/zsh. |
| `$'\t'` ANSI-C quoting | `printf` or literal tab via `"$(printf '\t')"` | `$'...'` is bash/ksh/zsh. |
| `read -a arr` | `read line; IFS=... set -- $line` | `-a` is bash. |
| `mapfile` / `readarray` | `while read` loop | bash 4+. |
| `$RANDOM` | `awk 'BEGIN{srand();print int(rand()*32768)}'` or `/dev/urandom` | bash/ksh/zsh. |
| `$SECONDS` | track via `date +%s` diff | bash/ksh/zsh. |
| `select` menu | manual `while`/`read`/`case` loop | bash/ksh. |
| `trap ... ERR` / `RETURN` / `DEBUG` | `EXIT`/`INT`/`TERM` + explicit checks | Only signal + `EXIT` traps are POSIX. |
| `set -o pipefail` | guard or drop for dash | bash/ksh/zsh/busybox-ash have it; **dash does not**. |
| `echo -n` / `echo -e` | `printf` | `echo` flag/escape behavior is unspecified by POSIX. |

## Utility flag differences

| Non-portable | Portable approach | Notes |
|---|---|---|
| `readlink -f` / `-m` | shell `cd`+`pwd -P` function, or require GNU `realpath`/`grealpath` | BSD/macOS `readlink` has no `-f`. macOS `realpath` exists (10.11+) but predates that on older systems. |
| `sed -i 's/.../.../' f` | `t=$(mktemp); sed '...' f >"$t" && mv "$t" f` | GNU `-i` (no arg), BSD/macOS `-i ''` (empty backup suffix). In-place is non-portable. |
| `sed -r` / `sed -E` | rewrite to POSIX BRE, or branch by target | POSIX `sed` specifies neither `-r` nor `-E` (BRE only). BSD/macOS and modern GNU accept `-E`; `-r` is GNU/busybox. For strict portability rewrite to BRE. |
| `grep -P` (PCRE) | `grep -E` (ERE) or `awk` | PCRE is GNU-only; `grep -E` (ERE) is POSIX. Rewrite the pattern in ERE. |
| `grep -o` | mostly portable now (GNU+BSD+busybox) | OK on modern targets; avoid on ancient ones. |
| `find -printf` | `find ... -exec printf ...` or `-print` + processing | `-printf` is GNU-only. |
| `find -regex` / `-iregex` | `-name`/`-path` globs or `-exec ... grep` | `-regex` semantics differ GNU vs BSD. |
| `find -maxdepth`/`-mindepth` | mostly portable (GNU+BSD+busybox) | Not POSIX but widely available; note if strict POSIX. |
| `date -d "..."` / `date --date` | BSD uses `date -v`; avoid relative-date math or use a dedicated tool | GNU `-d` vs BSD `-v` are incompatible. `date +%s` (epoch) is portable. |
| `date +%s` | portable on GNU/BSD/busybox | Reading epoch is fine; computing from a date is not. |
| `cp --parents` | `mkdir -p` the target dir, then `cp` | GNU-only. |
| `cp -a` | `cp -pR` | `-a` is GNU/BSD-ish; `-pR` is POSIX. |
| `sort -h` (human sizes) | numeric pre-format then `sort -n` | GNU-only. |
| `sort` collation | prefix `LC_ALL=C sort` | Locale changes order across systems. |
| `tac` | `sed '1!G;h;$!d'` or `tail -r` (BSD) | `tac` is GNU-only; `tail -r` is BSD-only. |
| `seq` | `i=1; while [ "$i" -le "$n" ]; do ...; i=$((i+1)); done` | `seq` is not POSIX (GNU/BSD/busybox have it, with flag differences). |
| `xargs -r` | guard empty input (e.g. `[ -s file ]`) instead of relying on `-r` | GNU/busybox `xargs` run the utility once on empty input unless `-r` is given; BSD/macOS `xargs` already skip on empty input (FreeBSD accepts `-r` as a no-op for compatibility; older macOS lacks `-r`). |
| `xargs -0` / `-d` | `-0` widely available; `-d` is GNU-only | Prefer `-0` with `find -print0` (GNU/BSD) over `-d`. |
| `mktemp` | `mktemp 2>/dev/null \|\| mktemp -t prefix` | Template/`-t` semantics differ GNU vs BSD. |
| `stat -c` (GNU) / `stat -f` (BSD) | avoid, or branch by `uname`; use `find -printf`-free alternatives, `wc -c`, `ls` parsing as last resort | Format strings are entirely different. |
| `head -c N` | `dd bs=1 count=N 2>/dev/null` for strict POSIX | `head -c` is widely available but not POSIX; busybox quirks exist. |
| `realpath` | shell function or GNU coreutils | Not POSIX; availability varies. |
| `getopt` (GNU enhanced) | POSIX `getopts` builtin | GNU `getopt` long-options are non-portable; `getopts` is the portable builtin (short opts only). |
| `awk` GNU extensions (`gensub`, `asort`, `length(arr)`, `match` 3rd arg, `--`) | POSIX awk only | BSD `awk`/`mawk`/busybox `awk` lack them. |
| `ls --color`, `grep --color` | omit or branch | GNU-only long flags. |

## Behavioral hazards

- **Word-splitting / globbing**: unquoted `$var` and `$@` split on `IFS` and glob. Always `"$var"` / `"$@"` unless splitting is intended; use `set -f` to disable globbing when iterating untrusted values.
- **`echo`**: backslash-escape interpretation and `-n` handling vary by implementation and by options (`xpg_echo`, `-e`/`-E`); `echo -n` is unspecified by POSIX. Use `printf '%s\n'`. Never put data in the format string: `printf '%s\n' "$user"`, not `printf "$user"`.
- **Locale**: `sort`, `tr` ranges (`[a-z]`), `sed`/`grep` character classes, and `printf` numeric formatting depend on `LC_ALL`/`LC_COLLATE`. Pin `LC_ALL=C` for byte-stable behavior.
- **`set -e` (`errexit`)**: subtle and shell-divergent (behavior inside `&&`, command substitution, functions, and `if` differs across shells and versions). Don't rely on it for correctness; check critical commands explicitly.
- **`$(...)` vs backticks**: both are POSIX; prefer `$(...)` for nesting and clarity. Backticks mangle backslashes.
- **Arithmetic**: `$((expr))` is POSIX; `let` and `(( ))` are bash/ksh.
- **`type`/`command -v`**: use `command -v cmd` to test for a command (POSIX); `which` is not POSIX and varies.
- **`test`/`[`**: `-a`/`-o` (binary AND/OR inside `[ ]`) are deprecated and ambiguous; chain with `&&`/`||` between separate `[ ]` calls.
- **Signals in `trap`**: use names without `SIG` prefix (`trap ... INT TERM`) and only `EXIT` plus real signals; `ERR`/`DEBUG`/`RETURN` are non-POSIX.

## Verification tooling

- `shellcheck -s sh script` (POSIX mode) flags most bashisms; `-s bash` for bash scripts. ShellCheck code `SC2039`/`SC3xxx` family marks non-POSIX features.
- `checkbashisms script` (from Debian `devscripts`) specifically targets `/bin/sh` scripts.
- Run the script under `dash script` and `busybox ash script` to catch dash/busybox-specific failures.
- Run on a BSD/macOS box (or in a FreeBSD/macOS CI runner) to catch coreutils-flag differences that Linux hides.

## Source confidence

- **High**: presence/absence of constructs in POSIX.1-2017 (authoritative spec text); GNU vs BSD flag differences for the common utilities above (verifiable in each project's man pages). bash version-feature gates (macOS bash 3.2) are documented in the bash manual `CHANGES`.
- **Medium**: busybox feature coverage varies by build configuration (a stripped busybox may omit applets or flags); treat busybox claims as "default build" and verify on the actual image.
- **Lower**: exact behavior of `set -e` and `echo` across every historical shell version; the catalog gives the safe portable form rather than enumerating every divergence.
