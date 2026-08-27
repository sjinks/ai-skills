# Quoting & Expansion Rules

Read this when a shell command's quoting, expansion, globbing, heredoc, or zsh/bash mode behavior needs deeper analysis than the short checklist provides.

## 1. Quoting characters

### Single quotes `'...'`

- No expansion of any kind. Every character is literal.
- May span literal newline and tab characters; the two-character strings `\n` and `\t` remain backslash plus letter.
- Cannot contain a single quote — not even with a backslash.
- To include a single quote, end the single-quoted string, add an escaped quote, restart: `'it'\''s'`.

### Double quotes `"..."`

- Preserve literal value of everything **except** `$`, `` ` ``, `\`, and (when history expansion is on) `!`.
- Variable expansion, command substitution, and arithmetic expansion still happen.
- A backslash inside double quotes only escapes `$`, `` ` ``, `"`, `\`, and newline.
- In interactive Bash, `!` inside double quotes may still trigger history expansion. Prefer single quotes for literal `!`, or run `set +H` before using double quotes that contain literal `!`.

### Backslash `\`

- Outside quotes, escapes the next character (loses any special meaning).
- Inside double quotes, only meaningful before `$`, `` ` ``, `"`, `\`, newline.
- Inside single quotes, literal.

### ANSI-C quoting `$'...'` (bash/zsh)

- Like single quotes, but supports C-style escapes: `\n`, `\t`, `\xHH`, `\uHHHH`.
- Use when the shell source should encode characters through escape notation rather than contain literal newlines or tabs.

```bash
printf '%s\n' $'first\nsecond'
```

## 2. Expansions and their order

Bash performs expansions in this order on each token:

1. Brace expansion: unquoted brace syntax such as `{a,b}c` expands to `ac bc` before other expansions; quoting any part of the brace operators prevents that part from being recognized as brace syntax.
2. Tilde expansion: `~` → `$HOME`, `~user` → user's home when an unquoted tilde starts a word. Bash also checks after an unquoted `=` in assignment words and after each unquoted `:` in an assignment value. Text produced later by parameter expansion is not rescanned for tilde expansion.
3. Parameter expansion (`$var`), command substitution (`$(cmd)`), and arithmetic expansion (`$((expr))`) are performed in one phase, left-to-right; process substitution participates where the shell supports it.
4. Word splitting: splits unquoted expansion results on `IFS`.
5. Pathname expansion (globbing): `*`, `?`, `[abc]`.
6. Quote removal: removes the quote characters that survived.

Key point: **word splitting** and **pathname expansion** happen on **unquoted** expansions. Quoting suppresses both.

## 3. `$@` vs `$*` vs `"$@"` vs `"$*"`

| Form | Behavior |
|------|----------|
| `$*` | All positional arguments joined by the first character of `IFS` (default: space). Word-splits and globbed. |
| `$@` | All positional arguments as separate words. Word-splits and globbed. |
| `"$*"` | All arguments as a single string, joined by `IFS[0]`. |
| `"$@"` | Each argument as a separate quoted word. Preserves spaces in arguments. **Always prefer this.** |

```sh
fn() { for a in "$@"; do echo "[$a]"; done; }
fn 'a b' c
# Output:
# [a b]
# [c]
```

## 4. Variable defaults and assertions

| Form | Behavior |
|------|----------|
| `${var:-default}` | Use `default` if `var` is unset or empty. |
| `${var-default}` | Use `default` if `var` is unset (empty is OK). |
| `${var:=default}` | Assign `default` if unset/empty, then expand. |
| `${var:?error}` | Raise an expansion error if unset/empty. A non-interactive shell exits; an interactive shell need not exit, so do not rely on it alone to stop later user-entered mutations. |
| `${var:+alt}` | Use `alt` if `var` is set and non-empty. |

```sh
: "${BUILD_DIR:?must be set}"
rm -rf -- "$BUILD_DIR"
```
Use this sequential form only in a non-interactive script with the required exit behavior. In an interactive shell, inspect and resolve the value separately and do not issue the mutation while it remains unset or empty.

## 5. Argument separator `--`

Most utilities accept `--` to mark the end of options. Everything after is treated as a positional argument, even if it begins with `-`.

```sh
rm -- -file        # delete a file literally named "-file"
grep -- -pattern file
```

## 6. Heredoc variants

| Form | Expansion in body | Indentation handling |
|------|-------------------|----------------------|
| `<<EOF` | Yes (variables, substitutions) | Terminator must be at column 0. |
| `<<'EOF'` | No (literal body) | Terminator must be at column 0. |
| `<<-EOF` | Yes | Strips leading **tabs** (not spaces) from each line and the terminator. |
| `<<-'EOF'` | No | Strips leading tabs. |

```sh
# Literal body, indented for readability
cat <<-'EOF'
	$literal stays as $literal
	`backticks` stay literal
EOF
```

## 7. zsh-specific pitfalls

### Unmatched globs

By default, zsh raises `zsh: no matches found` when a glob has no matches. Quote the glob or use the `(N)` qualifier to make it expand to empty.

```zsh
ls *.foo(N)   # expands to empty if no matches
```

### Equals expansion

zsh expands a bare `=word` at the start of a token to the full path of `word` (like `which word`). Avoid bare `==` or `===`:

```zsh
echo '==='     # quote
[[ a == b ]]   # safe; inside [[ ]]
```

### `status` and other special parameters

`status` is read-only in zsh, so assigning captured output to it fails; choose a replacement name that describes the assigned value, such as `response`. Do not infer that every special parameter is read-only: assigning `argv` changes positional parameters, while `path` and `fpath` are assignable arrays tied to `PATH` and `FPATH`. Inspect a special parameter's documented semantics before rewriting an assignment to it.

### `setopt`/`unsetopt` shell options

- `nounset` — equivalent to `set -u`.
- `errexit` — equivalent to `set -e`.
- `pipefail` — equivalent to `set -o pipefail`.
- `extendedglob` — adds `^`, `~`, `(...)` glob operators.
- `globdots` — globs match dotfiles.

## 8. Process substitution

`<(cmd)` and `>(cmd)` (bash/zsh, not POSIX) provide a filename that streams from/to the command.

```bash
diff <(sort a.txt) <(sort b.txt)
tee >(grep foo > foo.log) >(grep bar > bar.log)
```

For a reviewed commit message, avoid filename-like process-substitution paths. Put the exact reviewed literal bytes in a quoted heredoc and feed them directly with `git commit -F -`.

## 9. Shell-mode safety idioms

Resolve the interpreter and review expected nonzero paths before enabling strict modes. The following form is Bash-specific:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e` — exit on error.
- `set -u` — error on unset variable.
- `set -o pipefail` — make the pipeline's status reflect a failing component; it does not exit the shell by itself. Exit behavior additionally depends on `errexit` and its contextual exceptions.

POSIX.1-2024 specifies `pipefail`, but older POSIX baselines and some `/bin/sh` implementations such as dash do not. Verify the target shell/version before using it; otherwise handle component status explicitly or select a supporting interpreter. `set -eu` still requires review of expected failures and does not substitute for pipeline-status handling.

For finer control, wrap risky blocks:

```bash
{ set +e; risky; rc=$?; set -e; }
if (( rc != 0 )); then echo "expected failure ($rc)" >&2; fi
```

## 10. Common ambiguous constructs

### `$(cat file)` vs `<file`

If a command accepts input from stdin or a file argument, prefer the file form:

```sh
# Less safe — embeds file content as argv
foo "$(cat msg)"

# Better — file as argument
foo --file msg
# Or stdin
foo < msg
```

### `set -x` and secrets

Trace prints the post-expansion command. If a secret is in scope, the trace leaks it.

```sh
{ set -x
  do_safe_thing
  set +x
}
# Then run the secret-bearing command outside the trace
auth_call --token-file=/tmp/token
```

### `$?` after a pipeline

Without `pipefail`, `$?` is the exit code of the **last** command in the pipeline.

```bash
set -o pipefail
cmd1 | cmd2
echo "$?"   # non-zero if either failed
```

### Brace expansion is not file expansion

Unquoted `{a,b}c` is brace expansion and expands to `ac bc` even if no such files exist; quoted `'{a,b}c'` stays literal. `*c` is pathname expansion and matches existing files. They are different mechanisms.

### `read` with default `IFS`

```sh
read -r line          # uses IFS; trims surrounding whitespace
IFS= read -r line     # preserves whitespace
while IFS= read -r line; do ...; done < file
```

For NUL-delimited input from `find -print0`:

```bash
while IFS= read -r -d '' file; do ...; done < <(find . -print0)
```

## 11. Reference

- bash manual: <https://www.gnu.org/software/bash/manual/bash.html>
- zsh manual: <https://zsh.sourceforge.io/Doc/Release/zsh_toc.html>
- POSIX shell command language: <https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html>
