# Command Construction

Read this when a command review involves commit-message construction, quoting, substitutions, heredocs, redirection, shell modes, secrets, or encoding.

Each record keeps the unsafe form, its risk, decision gate, and safe replacement together; retain separate inspection and mutation phases.

When a replacement names a tool not guaranteed by the target baseline, provide a baseline-compatible alternative or list tool availability under `Required checks:` before emitting the command.

## Git commit messages

### GC1 - Multi-line `-m`
Example: `git commit -m "Subject\n\nBody"`

Risk: The literal `\n` is recorded instead of newlines.

Decision gate: Rewrite.

Safe replacement:
```sh
git commit -F - <<'EOF'
Subject

Body paragraph.
EOF
```
Review the exact literal heredoc before execution. Git consumes those bytes directly from stdin, so no replaceable temporary pathname exists between review and use.

### GC2 - Repeated `-m`
Example: `git commit -m "Subject" -m "Body line 1" -m "Body line 2"`

Risk: Each `-m` becomes a paragraph and bodies with lists or code are error-prone.

Decision gate: Rewrite.

Safe replacement: Prefer GC1's reviewed stdin sequence for any body beyond a subject.

### GC3 - Substitution in `-m`
Example: `git commit -m "Fix: $(cat issue.txt)"`

Risk: Embedded newlines and shell-special text can produce malformed messages.

Decision gate: Rewrite.

Safe replacement: Resolve and review the message content, then place those exact literal bytes in GC1's quoted heredoc. Do not review one pathname and let Git reopen it later.

### GC4 - Variable in `-m`
Example: `git commit -m "Fix: $TITLE"`

Risk: Newlines and shell-special content make the message ambiguous.

Decision gate: Rewrite.

Safe replacement: Resolve and restate `TITLE` without losing its line boundaries, review the exact result, then place those literal bytes in GC1's quoted heredoc.

### GC5 - Backtick substitution
Example: ``git commit -m "ship at `date"``

Risk: Backticks are difficult to nest and escape.

Decision gate: Rewrite.

Safe replacement: Resolve the date first, review the exact result, then place it as literal text in GC1's quoted heredoc.

### GC6 - Backtick or quote in `-m`
Example: ``git commit -m "use `foo()` here"``

Risk: The backtick triggers a failing command substitution.

Decision gate: Rewrite.

Safe replacement: Use GC1's quoted heredoc with the literal subject ``use `foo()` here``.

### GC7 - Apostrophe in single-quoted `-m`
Example: `git commit -m 'it\'s broken'`

Risk: Single quotes do not permit backslash escaping.

Decision gate: Rewrite.

Safe replacement: Use GC1's quoted heredoc with the literal subject `it's broken`.

### GC8 - Unicode in a non-UTF-8 terminal
Example: `git commit -m "🎉 ship"`

Risk: A legacy terminal or locale can mangle multi-byte characters.

Decision gate: Rewrite.

Safe replacement: In a verified UTF-8 terminal, use GC1's quoted heredoc with the reviewed literal UTF-8 text.

## Quoting and expansion

### Q1 - Unquoted variable in an argument
Example: `rm $file`

Risk: Word splitting and pathname expansion change the argument list.

Decision gate: Block until the intended argv boundary is known, then rewrite.

Safe replacement: Use `rm -- "$file"` only when `$file` is confirmed to represent one argument. When it intentionally represents multiple arguments, require a structured argv source such as an array or positional parameters, preserve each reviewed element, and invoke the command with that structure's boundary-preserving expansion. Never collapse an intended list into one quoted scalar.

### Q2 - Unquoted variable in a path
Example: `cd $dir`

Risk: Word splitting and pathname expansion change the path.

Decision gate: Rewrite.

Safe replacement: `cd -- "$dir"`.

### Q3 - `for` over `$(ls)`
Example: `for f in $(ls); do ...; done`

Risk: Whitespace in names becomes separate iterations.

Decision gate: Rewrite.

Safe replacement: First define whether the intended set is immediate non-hidden entries, regular files only, recursive entries, or another scope. To preserve plain `ls`'s default immediate non-hidden entry set in Bash or POSIX-style shells:
```sh
for f in ./*; do
	[ -e "$f" ] || [ -L "$f" ] || continue
	...
done
```
The existence/link guard prevents a literal `./*` no-match iteration while retaining files, directories, and symlinks. This record also covers a bare glob used directly as an in-shell `for` list, such as `for f in *.log`; an unguarded glob list matches Q3, and the guarded form above is the compliant result. zsh's default `NOMATCH` aborts before the loop on an empty directory; use a deliberately scoped zsh null-glob form such as `./*(N)` only for a zsh target. Use `find` only when the caller explicitly requests its recursive/type-filtered scope, and consume names through a NUL-safe structured path.

### Q4 - Unquoted glob in a command's argument list
Example: `mv *.log /tmp`

Risk: No-match behavior differs by shell and a literal glob is ambiguous.

Decision gate: Block until one structured expansion is captured and bound through execution.

Safe replacement: Use a runtime or helper that resolves the glob once into a structured argv list, records path identity when replacement matters, renders every path with unambiguous escaping for review, and invokes `mv --` with that same stored list. Do not expand `*.log` again after review; if the exact structured list cannot survive through execution, return `BLOCKED`. This record applies to a glob expanded into an external command's argument list. A glob used as an in-shell `for` list with Q3's existence/link guard is classified under Q3 and does not additionally match Q4.

### Q5 - Unquoted `$@` or `$*`
Example: `cmd $@`, `cmd $*`

Risk: Each positional parameter can split and glob further; unquoted `$*` does not perform the single-string `IFS[0]` join of quoted `"$*"`.

Decision gate: Rewrite.

Safe replacement: Use `cmd "$@"` when preserving argument boundaries. Use `cmd "$*"` only when the caller explicitly intends one argument joined by the first character of `IFS` and that separator is resolved.

### Q6 - Path with spaces
Example: `cat /tmp/my file.txt`

Risk: This supplies two paths even when one path containing a space was intended.

Decision gate: Rewrite when the caller confirms single-path intent.

Safe replacement: For confirmed single-path intent, use `cat "/tmp/my file.txt"`. Otherwise preserve the two original arguments, `/tmp/my` and `file.txt`, and reclassify the unchanged command without Q6.

### Q7 - Variable in single quotes
Example: `echo '$HOME'`

Risk: Single quotes prevent the intended expansion.

Decision gate: Rewrite when expansion is wanted.

Safe replacement: `printf '%s\n' "$HOME"`.

### Q8 - Mixed quotes
Example: `echo "it's $name`

Risk: The unbalanced double quote can consume the rest of a script or fail parsing.

Decision gate: Block until the intended quote boundary and text are known, then rewrite.

Safe replacement: After confirming the intended text, use `printf '%s\n' "it's $name"`. A balanced command such as `echo "it's $name"` does not match Q8 merely for mixing a double-quoted string with an apostrophe.

### Q9 - Backslash escapes in single quotes
Example: `echo 'a\nb'`

Risk: Single quotes pass `\n` literally through shell parsing, but `echo` handling of a backslash-containing operand is implementation-defined and may emit literal characters or interpret an escape; `echo -e` is also non-portable.

Decision gate: Block until escape intent is known, then rewrite.

Safe replacement: When the caller intends two lines, use `printf '%s\n%s\n' a b`. When the caller intends the literal characters `a\nb`, preserve them with `printf '%s\n' 'a\nb'`. Do not infer escape interpretation from the original `echo` form.

### Q10 - Filename beginning with `-`
Example: `rm -file`

Risk: The name is parsed as options.

Decision gate: Rewrite.

Safe replacement: `rm -- -file`.

### Q11/SE8 - Bash history expansion in double quotes
Example: `echo "deploy!"`

Risk: Interactive history expansion can substitute history or fail.

Decision gate: Rewrite.

Safe replacement: Use single quotes for a literal `!`:
```sh
echo 'deploy!'
```
Or disable history expansion before the double-quoted command in Bash:
```bash
set +H
echo "deploy!"
```

### Q12 - Backslash-escaped downstream literals inside shell single quotes
Example: `aws ... --query 'Tags[?Key==\`Name\`]'`

Risk: Shell single quotes preserve the backslashes, so a downstream language such as JMESPath receives different or invalid literal delimiters.

Decision gate: Rewrite.

Safe replacement: Verify the downstream grammar, remove only backslashes that were incorrectly added before its literal delimiters, and preserve the exact shell quoting, command, selector, target, and expression structure. For JMESPath backtick literals inside shell single quotes, use raw backticks such as `--query 'Tags[?Key==`Name`]'`.

## Command substitution and pipes

### CS1 - Backtick substitution
Example: ``echo "today is `date"``

Risk: Backticks do not nest and are hard to escape.

Decision gate: Rewrite.

Safe replacement: `printf 'today is %s\n' "$(date)"`.

### CS2 - Unquoted nested substitution
Example: `echo $(echo $(date))`

Risk: Output word-splits at each level.

Decision gate: Rewrite.

Safe replacement: `printf '%s\n' "$(date)"`.

### CS4 - `eval` on text
Example: `eval "$cmd"`

Risk: Text executes with the shell's privileges and cannot be safely sanitized.

Decision gate: Prohibited.

Safe replacement for POSIX `sh`, Bash, or zsh:
```sh
(
	set -- rsync -av --delete src/ dst/
	"$@"
)
```
Construct the arguments directly rather than parsing a command string. The subshell preserves the caller's positional parameters; omit it only when replacing the caller's `$@` is explicitly intended. This removes `eval` injection risk but does not authorize the reconstructed command: reclassify it from the beginning, including RX5 dry-run and confirmation requirements for `rsync --delete`.

### CS5 - `xargs` without NUL delimiters
Example: `find . -name '*.log' | xargs rm`

Risk: Spaces, quotes, and newlines split filenames.

Decision gate: Block until the exact deletion set is captured and bound.

Safe replacement: Use a trusted runtime/helper to capture one NUL-delimited result from the exact `find` root and expression into a protected structured snapshot. Render every entry with reversible, unambiguous escaping and stable identity for review. After confirmation, delete only the entries from that same snapshot without rerunning `find` or reparsing newline-delimited names; revalidate identities immediately before deletion. If the snapshot cannot remain bound through execution, return `BLOCKED`.

### CS6 - Pipeline without `pipefail`
Example: `set -e; cmd1 | cmd2`

Risk: Failure in an earlier pipeline command is lost.

Decision gate: Inspect the selected interpreter, then rewrite.

Safe replacement for Bash or another verified `pipefail`-capable shell:
```bash
set -o pipefail
cmd1 | cmd2 | cmd3
```
`pipefail` is specified by POSIX.1-2024, but older POSIX targets and shells such as dash may not support it. For a POSIX.1-2024-conforming shell or another verified supporting interpreter, the replacement above is valid. For older or unknown targets, verify the capability first; otherwise capture component status through an explicitly designed non-pipeline flow or select a supporting interpreter.

## Heredocs and multi-line text

### HD1 - Indented heredoc terminator
Example: `cat <<EOF` with an indented closing `EOF`.

Risk: `<<EOF` requires a column-zero terminator and keeps reading input.

Decision gate: Rewrite.

Safe replacement:
```sh
cat <<-EOF
	line
	EOF
```
`<<-EOF` strips tabs, not spaces.

### HD2 - Unwanted heredoc expansion
Example: `cat <<EOF` when `$var` must be literal.

Risk: An unquoted terminator expands variables and substitutions.

Decision gate: Rewrite.

Safe replacement:
```sh
cat <<'EOF'
literal $var and $(cmd)
EOF
```

### HD3 - Heredoc redirected to a root-owned file
Example: `cat <<EOF > /etc/foo.conf`

Risk: The unprivileged shell performs the redirection.

Decision gate: Confirm both privilege use and overwrite of the exact destination.

Safe replacement:
```sh
sudo tee /etc/foo.conf >/dev/null <<'EOF'
content
EOF
```
`tee` without `-a` truncates the destination. Use `tee -a` only when the caller explicitly requests append behavior; never change overwrite to append or append to overwrite implicitly.

### HD4 - `echo -e`
Example: `echo -e "a\nb"`

Risk: `-e` is non-portable.

Decision gate: Rewrite.

Safe replacement: `printf 'a\nb\n'`.

## Output and shell modes

### OR1 - Overwrite redirection
Example: `cmd > important.log`

Risk: Existing contents are replaced.

Decision gate: Confirm overwrite unless the file is verified disposable.

Safe replacement: Preserve the requested write semantics. Use `cmd >> log.txt` only when the caller explicitly intends append behavior. For overwrite behavior, inspect and confirm the exact existing destination before `cmd > log.txt`, or choose a new exclusively created destination; never silently replace overwrite with append.

### OR2 - Wrong stderr-redirection order
Example: `cmd 2>&1 > log`

Risk: stderr remains on the original stdout, which differs from sending both streams to `log`.

Decision gate: Rewrite when the caller confirms that both streams should go to `log`; otherwise this pattern does not apply and the original routing is preserved for reclassification.

Safe replacement: `cmd > log 2>&1`.

### OR3 - Only stdout suppressed
Example: `cmd > /dev/null`

Risk: stderr remains visible, which may surprise the caller.

Decision gate: Rewrite when the caller confirms both streams should be silenced; otherwise this pattern does not apply and the segment is reclassified without it.

Safe replacement: `cmd > /dev/null 2>&1` only when both streams should be silenced.

### OR4 - `sudo` with a redirect
Example: `sudo echo 'content' > /etc/foo.conf`

Risk: The current shell, not `sudo`, opens the file.

Decision gate: Confirm both privilege use and overwrite of the exact destination.

Safe replacement: After those confirmations, run `printf '%s\n' 'content' | sudo tee /etc/foo.conf > /dev/null`. The replacement preserves the requested content and overwrite behavior while moving the privileged open into `tee`.

### SM1 - Script without strict mode
Example: A multi-step script without `set -euo pipefail`.

Risk: Later mutations can run after earlier failure, while blindly enabling strict mode can also change intended control flow or fail under an incompatible shell.

Decision gate: Inspect the selected interpreter and expected nonzero paths, then rewrite.

Safe replacement for a reviewed Bash script:
```bash
#!/usr/bin/env bash
set -euo pipefail
```

For POSIX `sh`, use `set -eu` only after reviewing expected failures and handle pipeline component status explicitly; if `pipefail` is required, select a shell that supports it and update the shebang.

### SM2 - Unguarded `cd`
Example: `cd /tmp/build; rm -rf -- ./cache`

Risk: A failed directory change can leave a destructive operation in the wrong directory.

Decision gate: Rewrite.

Safe replacement:
```sh
cd -- /tmp/build || exit 1
rm -rf -- ./cache
```
This preserves the intended `/tmp/build/cache` target while guarding the directory change. Reclassify the deletion itself under FS1 before execution.
The `|| exit 1` form is for non-interactive scripts. In an interactive shell, wrap the dependent sequence in a subshell so a failed `cd` does not terminate the user's session.

### SM3 - Bash constructs under `/bin/sh`
Example: `#!/bin/sh` with `[[ ... ]]`.

Risk: `/bin/sh` can be a shell without Bash extensions.

Decision gate: Rewrite.

Safe replacement:
```sh
#!/bin/sh
if [ -f "$file" ]; then ...; fi
```

### SM4 - `status` variable in zsh
Example: `status=$(curl ...)`.

Risk: `status` is read-only in zsh.

Decision gate: Rewrite.

Safe replacement: `response=$(curl ...)`. This preserves the original stdout capture while avoiding zsh's read-only name. If the exit status is also needed, capture it separately immediately afterward with `curl_status=$?`.

### SM5 - Bare `==` in zsh
Example: `echo ===`.

Risk: equals expansion changes bare `==` or `===`.

Decision gate: Rewrite.

Safe replacement:
```zsh
echo '==='
[[ "$a" == "$b" ]]
```

### SM6 - Persisted `IFS` mutation
Example: `IFS=,` followed by unrelated commands.

Risk: A sourced script or interactive shell retains the altered splitter.

Decision gate: Rewrite.

Safe replacement:
```bash
IFS=, read -r a b c <<< "$line"
```
The assignment is scoped to `read`, so a nonzero result under `set -e` cannot leave a modified `IFS` behind. For POSIX `sh`, here-strings are unavailable; use a command-scoped assignment with a heredoc:
```sh
IFS=, read -r a b c <<EOF
$line
EOF
```
For multi-command parsing, use a subshell instead of manual save/restore.

## Secret and environment hygiene

### SE1 - Echoing a secret variable
Example: `echo $TOKEN`

Risk: The expanded value is exposed through terminal output and any transcript or log capture. Interactive shell history records the source text `echo $TOKEN`, not the expanded value.

Decision gate: Prohibited.

Safe replacement:
```sh
if [ "${TOKEN+x}" = x ]; then printf 'TOKEN is set\n'; else printf 'TOKEN is not set\n'; fi
```

### SE2 - Environment dump to a file
Example: `env > env.txt`

Risk: Credentials may be persisted.

Decision gate: Rewrite; block while any allowlisted variable's current value has unresolved sensitivity or persistence acceptability.

Safe replacement: Never authorize the broad form, even after all current values are classified. Define an explicit allowlist and establish from each variable's name, trusted producer, documented purpose, and data contract that its current value is non-secret and acceptable to persist; never print a value to determine its sensitivity. For each concrete variable, verify presence only with a `[ "${PATH+x}" = x ]`-style check. Emit only allowlisted names with `printf`, using a fixed format string and passing every name and value through quoted `%s` arguments. Do not dump first and filter afterward. If classification would require reading a value, any allowlisted variable is unresolved, or the destination cannot be protected and lifecycle-managed, return `BLOCKED`.

### SE3 - Secret in argv
Example: `curl --header "Authorization: Bearer abc123"`

Risk: Values are visible in history and process listings.

Decision gate: Rewrite.

Safe replacement: Use a credential helper or pre-provisioned protected file descriptor; when a file is necessary, keep it outside the repository, owner-readable only, and lifecycle-managed.

### SE4 - Authorization header in an interactive command
Example: `curl -H "Authorization: Bearer $TOKEN" https://api/...`

Risk: The command context and trace output can leak authentication.

Decision gate: Rewrite.

Safe replacement: Use the protected credential-file or helper pattern in SE3 without interpolating the secret into a displayed command.

### SE5 - Secret written into `.env`
Example: `echo "API_KEY=abc" >> .env`

Risk: Shell redirection can follow a link or race a checked path, and an already tracked file remains tracked despite `.gitignore`.

Decision gate: Block direct shell redirection of secret material.

Safe replacement: Use a credential helper or runtime secret store. When a file is unavoidable, create it outside repositories and synchronized paths through a platform API that atomically enforces no-follow, exclusive creation, owner-only permissions, and descriptor-bound writes; if that facility is unavailable, return `BLOCKED`. Never interpolate the secret into a displayed command.

### SM7/SE6 - Tracing around secret use
Example: `set -x; do_thing --token=$TOKEN`

Risk: Trace output prints the token.

Decision gate: Rewrite; block when argv is the only available interface.

Safe replacement: Disable tracing before the secret enters scope; use a credential helper, protected file, stdin, or file descriptor. Redirecting output does not hide argv.

### SE7 - Echoing secret-search results
Example: `grep -r PASSWORD . > findings.txt`

Risk: Raw matches persist secret values.

Decision gate: Rewrite.

Safe replacement: Report locations only. On POSIX.1-2024 or a target whose `grep` supports recursive search, use `grep -rlE 'PASSWORD|TOKEN|SECRET|PRIVATE[ _-]?KEY' .`; on POSIX.1-2017 use `find . -type f -exec grep -lE 'PASSWORD|TOKEN|SECRET|PRIVATE[ _-]?KEY' {} +`. `rg -l` is an optional accelerator only after verifying ripgrep is installed.

### SE9 - Reading a likely secret file to output
Example: `cat credentials`

Risk: Terminal, transcript, and log output can persist credentials even when the path itself is syntactically simple.

Decision gate: Inspect path identity and sensitivity without reading file contents; block when the file is sensitive or classification is uncertain.

Safe replacement: Report only non-secret metadata such as existence, owner, permissions, or an approved schema. Use an application-specific verifier when content validation is required; never display the secret value.

## Encoding and locale

### EN1 - CRLF shell script
Example: A script saved with CRLF.

Risk: `\r` corrupts commands and can break the shebang.

Decision gate: Rewrite.

Safe replacement: First verify the file is CRLF text with no intentional carriage returns. Use a runtime-created private temporary file and a baseline text transform such as `tr -d '\r' < script.sh > "$temporary_file"`, review the result, then atomically replace the original under the filesystem policy. `dos2unix` is only an optional convenience after verifying it is installed; do not assume compatible `mktemp` or `sed -i` forms across targets.

### EN2 - UTF-8 BOM in a shell script
Example: An editor writes a BOM before `#!`.

Risk: Shebang parsing fails.

Decision gate: Rewrite.

Safe replacement: use a byte-aware editor or tool after resolving the platform; do not assume GNU/BSD `sed -i` or `\xHH` compatibility.

### EN3 - Byte-sensitive tools under an unspecified locale
Example: `sort file.txt`.

Risk: Locale collation changes cross-host output.

Decision gate: Rewrite when the caller requires bytewise, cross-host-stable semantics; otherwise this pattern does not apply and the selected locale is preserved for reclassification.

Safe replacement:
```sh
LC_ALL=C sort file.txt
LC_ALL=C grep pattern file.txt
LC_ALL=C tr 'a-z' 'A-Z' < file.txt
```

### EN4 - `grep -P` portability
Example: `grep -P 'foo' file`.

Risk: BSD `grep` lacks PCRE support.

Decision gate: Rewrite.

Safe replacement: First determine whether the pattern uses PCRE-only semantics. Translate it only to POSIX ERE constructs, without GNU-only escapes, and only when semantic equivalence has been tested against representative positive and negative inputs on every actual target `grep -E` implementation under the intended locale and encoding; default `rg` is not a PCRE-preserving substitute. Otherwise use a verified available PCRE-capable implementation, such as `rg -P` after checking PCRE2 support or `pcre2grep`, and preserve the original flags, input scope, locale, encoding, and match/output behavior. Return `BLOCKED` when a target implementation is unknown or no semantics-preserving translation or verified PCRE implementation is available.

### EN5 - Locale-dependent date
Example: `date +'%B %d'`.

Risk: Localized output changes scripts across hosts.

Decision gate: Rewrite when the caller requires stable English local-time output or UTC ISO output; block while the intended format, language, or timezone is unresolved. When localized local-time output is intentional, this pattern does not apply and the original is preserved.

Safe replacement: For stable English month names while preserving the original local-time format, use `LC_ALL=C date '+%B %d'`. Use `date -u '+%Y-%m-%dT%H:%M:%SZ'` only when the caller explicitly selects UTC ISO output. Preserve `date +'%B %d'` when localized local-time output is intended.