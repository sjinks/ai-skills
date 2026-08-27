---
name: shell-safety
description: "Use when: composing or running a nontrivial shell command in run_in_terminal, terminal, bash, zsh, or sh. Triggers: git commit, git push, git reset, git rebase, git clean, git checkout, rm, mv, cp, chmod, chown, kill, pkill, sudo, dd, mkfs, npm publish, pip install, docker, kubectl, helm, terraform, pulumi, aws, gcloud, az, psql, mysql, mongosh, redis-cli, ssh, scp, rsync, gpg, curl, wget, eval, find -delete, xargs, tar, unzip, systemctl, shutdown, reboot. Also use when drafting commit messages, handling paths with spaces or special characters, quoting variables, escaping arguments, using pipes, redirects, heredocs, command substitution, glob expansion, multi-line strings, the -m or -F flag, variable expansion, force-pushing, hard-resetting, or rewriting history."
argument-hint: "Paste the command you are about to run; the skill validates it."
user-invocable: true
---

# Shell Safety

## When to Use

Before composing or running any shell command that is not trivially safe. Trivially safe means: `git status`, `git log --oneline`, `ls`, `ls -la`, `pwd`, `whoami`, `which <cmd>`, `--version` / `--help` queries. File-content reads are not unconditionally trivial because they can disclose secrets.

**UTILITY SKILL.** INVOKES: terminal command composition and execution only after safety classification. FOR SINGLE OPERATIONS: use to classify one proposed command, rewrite a risky command, or decide what checks must pass before execution.

## DO NOT USE FOR:

- Portability-only shell reviews where the question is cross-shell or cross-OS compatibility rather than execution safety.
- Generic shell tutoring, syntax explanation, or command examples that the assistant is not about to run or recommend running.
- Non-shell languages or application-level security review where no shell command is being composed, validated, or executed.

Everything else needs validation. In particular:

- Any `git commit`, `git push`, `git reset`, `git rebase`, `git clean`, `git checkout`, `git branch -D`, `git tag`.
- Any `rm`, `mv`, `cp`, `chmod`, `chown`, `find -delete`, `dd`, `mkfs`, `truncate`.
- Any `sudo`, `kill -9`, `pkill`, `shutdown`, `reboot`, `systemctl stop/disable`.
- Any pipe (`|`), redirect (`>`, `>>`, `2>&1`), heredoc (`<<EOF`), command substitution (`$(...)`, backticks), glob (`*`, `?`), brace expansion (`{a,b}`).
- Any path with spaces, special characters, or that comes from a variable (`$VAR`, `"$VAR"`).
- Any `ssh`, `scp`, `rsync --delete`, `curl ... | sh`, `wget ... | bash`.
- Any cloud CLI mutation (`aws *-delete`, `aws s3 sync --delete`, `gcloud ... delete`, `az ... delete`).
- Any IaC mutation (`terraform destroy`, `terraform apply -auto-approve`, `pulumi destroy --yes`).
- Any container mass-mutation (`docker system prune`, `docker rm $(docker ps -aq)`, `kubectl delete namespace`).
- Any database mutation (`DROP`, `TRUNCATE`, `DELETE FROM ... ;` without `WHERE`, `FLUSHALL`, `dropDatabase()`).
- Any secret variable in echo, env dump, or command-line flag (`--password=`, `--token=`).

## Procedure

1. **Classify.** Identify every applicable pattern ID and category for every segment of the command, including hazards created by interactions between segments.
2. **Match.** Walk the Danger Checklist and matching domain references for all matched categories. A command is not safe until every matched pattern is addressed.
3. **Resolve conflicts.** Apply decision gates in this order: prohibited > rewrite-only > confirmable > safe. If two applicable rules cannot be satisfied together, return `BLOCKED`; do not choose one silently.
4. **Rewrite.** Apply the matching entry in the appropriate domain reference and reassess the complete rewritten command, not only the segment that triggered the first match.
5. **Resolve.** Determine non-secret variable values, substitutions, globs, working directory, and external targets without executing unsafe fragments. For a secret-bearing variable, verify only its source and presence; keep its name in the restatement and never expose its value. If a material non-secret value cannot be resolved, do not run the command.
6. **Apply the decision gate.** Use the [Decision Gates](#decision-gates) to distinguish prohibited forms, mandatory rewrites, and confirmable effects. Confirmation applies only to the exact restated command and targets.
7. **Restate.** Before sending a command, show the exact resolved form with quoting visible, except that secret values remain represented by their variable names or `<redacted>`.

For deep quoting questions, consult [quoting-rules.md](./references/quoting-rules.md).

## Danger Checklist

One-line summaries grouped by category. Use [command construction](./references/command-construction.md) for commit messages, quoting, shell composition, secrets, and encoding; [host and repository changes](./references/host-and-repository-changes.md) for Git, local files, processes, privilege, signing, services, and archives; [remote delivery](./references/remote-delivery.md) for network-to-shell and SSH; [platform and data operations](./references/platform-and-data-operations.md) for cloud, IaC, containers, and databases.

### Git commit messages

- `GC1` Multi-line message via `-m "...\n..."` → review exact literal bytes, then use `git commit -F -` with a quoted heredoc.
- `GC2` Repeated `-m` for paragraphs → prefer the reviewed stdin form for multi-paragraph bodies.
- `GC3` `-m "... $(cmd) ..."` → resolve and review the substitution, then use the reviewed stdin form.
- `GC4` `-m "... $VAR ..."` with whitespace-sensitive content → resolve and review the value, then use the reviewed stdin form.
- `GC5` Backtick substitution in `-m` → resolve and review the value, then use the reviewed stdin form.
- `GC6` Backtick or quote character inside `-m` → use `git commit -F -` with a quoted heredoc.
- `GC7` Apostrophe in single-quoted `-m` → use the reviewed stdin form.
- `GC8` Emoji/unicode + non-UTF-8 terminal → provide reviewed UTF-8 bytes through stdin.

### Git destructive operations

- `GD1` `git reset --hard` → confirm the exact reset target and preserve local changes first; any ref-moving reset is a confirmable effect even when the tree is clean.
- `GD2` `git push --force` / `-f` → require `--force-with-lease=<ref>:<expected-sha>` and block any discovered protected, default, release, production, or shared branch; treat `main|master|release/*|production|prod` as protected fallbacks.
- `GD3` `git branch -D` → confirm unmerged commits are intentional and then treat deletion as a confirmable effect.
- `GD4` `git clean -fdx` → dry-run first: `git clean -ndx`; reviewed deletion is still a confirmable effect.
- `GD5` `git checkout <sha>` (detached) → if you want a branch, add `-b <name>`.
- `GD6` Rebase on shared/pushed branch → require explicit user approval plus remote-tip review; without both, return `BLOCKED`; with both, treat the exact rewrite as a confirmable effect.
- `GD7` `git submodule deinit --force` → confirm no unstaged content and then treat deinit as a confirmable effect.
- `GD8` `git push --delete origin <tag>` → confirm tag not referenced by releases and then treat remote deletion as a confirmable effect.

### Filesystem destruction

- `FS1` `rm -rf <path>` → path must be explicit, not a glob, not a bare variable.
- `FS2` `rm -rf "$DIR"` → verify `$DIR` is set, non-empty, and not `/` or `~`.
- `FS3` `rm -rf *` or any unbounded glob → refuse; require explicit paths.
- `FS4` `rm -rf /...` or `rm -rf ~/...` → return `BLOCKED` unless the user gives strong justification; after exact-path preview, treat it as a confirmable effect.
- `FS5` `find ... -delete` or `-exec rm` → dry-run with `-print` first; reviewed deletion is still a confirmable effect.
- `FS6` `truncate -s 0 <log>` → confirm file path explicitly.
- `FS7` `dd of=/dev/...` → refuse without explicit user confirmation.
- `FS8` `mkfs.*` → refuse without explicit user confirmation.
- `FS9` `chmod -R 777` → refuse; recommend explicit minimum permission set.
- `FS10` `chown -R` outside project root → refuse without explicit user confirmation.

### Quoting & expansion

- `Q1` Unquoted variable in argument (`rm $file`) → `rm -- "$file"`.
- `Q2` Unquoted variable in path (`cd $dir`) → `cd -- "$dir"`.
- `Q3` Word-splitting `for f in $(ls)` → `for f in *` or `while IFS= read -r f`.
- `Q4` Unquoted glob (`mv *.log /tmp`) → verify expansion; quote if literal.
- `Q5` `$@` vs `"$@"` → always `"$@"` to preserve arguments.
- `Q6` Path with spaces (`cat /tmp/my file`) → quote: `"/tmp/my file"`.
- `Q7` `'$HOME'` (single quotes, no expansion) → `"$HOME"` if expansion wanted.
- `Q8` Mixed quoting → verify intent.
- `Q9` `'a\nb'` (backslash literal in single quotes) → `printf '%s\n%s\n' a b`.
- `Q10` Filename starting with `-` (`rm -file`) → `rm -- -file`.
- `Q11` `!` inside Bash double quotes with history expansion enabled → use single quotes, disable history expansion, or avoid interactive history expansion context.

### Command substitution & pipes

- `CS1` Backticks `` `cmd` `` → `$(cmd)`.
- `CS2` Unquoted nested `$(...)` → quote: `"$(...)"`.
- `CS3` `curl ... | sh` / `wget ... | bash` → download to temp, inspect, then run.
- `CS4` `eval "$var"` → refuse; restructure.
- `CS5` `find ... | xargs rm` (no NUL) → preview the NUL-safe target set, then confirm the exact `find ... -print0 | xargs -0 rm --` replacement.
- `CS6` Pipelines whose earlier commands must succeed → identify the interpreter first; use `set -o pipefail` only where supported, otherwise capture component status explicitly or require a shell that supports it.

### Heredoc & multi-line

- `HD1` `EOF` indented but `<<EOF` not `<<-EOF` → use `<<-EOF` with tabs.
- `HD2` `cat <<EOF` with `$var` literal → use `cat <<'EOF'` (quoted terminator).
- `HD3` `cat <<EOF > /etc/...` (root-owned) → use `sudo tee`.
- `HD4` `echo -e` → use `printf` for portable escapes.

### Process control

- `PC1` `kill -9 <pid>` → send `SIGTERM`, wait through a terminal or process-supervisor completion primitive, then re-verify process identity before considering `SIGKILL`.
- `PC2` `pkill <pattern>` → inspect matching PIDs and complete command identities, select one intended PID, then signal that PID directly.
- `PC3` `cmd &` (background in agent terminal) → use a supervised async/background capability when available; if unavailable, do not launch it and return the needed runtime capability.
- `PC4` `sleep` to wait for a process → refuse; rely on terminal completion signal.

### Network & supply-chain

- `NS1` `curl ... | bash` / `wget ... | sh` → refuse; download, inspect, run.
- `NS2` `npm install -g <pkg>` → prefer project-local install.
- `NS3` `npm publish` → refuse without explicit user confirmation.
- `NS4` `pip install` without venv → use venv.
- `NS5` `sudo <package-manager>` → confirm intent.
- `NS6` `ssh host '<long pipeline>'` → use `ssh host bash -s < script.sh`.

### Permission escalation

- `PE1` `sudo <anything>` → confirm intent; do not chain into pipes silently.
- `PE2` `sudo -i` / `sudo su` → refuse.
- `PE3` `chmod u+s` (setuid) → refuse.

### Output capture & redirection

- `OR1` `> file` overwriting important file → use `>>` or confirm overwrite.
- `OR2` `cmd 2>&1 > log` (wrong order) → `cmd > log 2>&1`.
- `OR3` `cmd > /dev/null` swallowing only stdout → explicit; add `2>&1` only if intended.
- `OR4` `cmd | sudo > file` → `cmd | sudo tee file`.

### Shell mode safety

- `SM1` Script without failure guards → identify the interpreter and review expected nonzero paths first; use `set -euo pipefail` for compatible Bash scripts, or `set -eu` plus explicit pipeline-status handling for POSIX `sh`.
- `SM2` `cd && cmd` in script → `set -e` or `cd ... || exit 1`.
- `SM3` `[[ ]]` in `/bin/sh` → use `[ ]` for POSIX.
- `SM4` `status` variable in zsh → use `exit_code`.
- `SM5` Bare `==` in zsh → quote `'=='`.
- `SM6` Mutating `IFS` without restore → subshell or save/restore.
- `SM7` `set -x` left on with secrets in scope → scope tightly.

### SSH & remote

- `RX1` `ssh host '<long pipeline>'` → `ssh host bash -s < script.sh`.
- `RX2` `ssh -o StrictHostKeyChecking=no` → refuse unless ephemeral CI host.
- `RX3` `ssh-keygen -R <host>` → confirm intent.
- `RX4` `scp host:'/path/*.log'` (remote glob) → quote glob explicitly.
- `RX5` `rsync --delete` → dry-run `-n` first.
- `RX6` `ssh -A` to untrusted host → refuse.
- `RX7` `sshpass` in pipeline → refuse; use key auth.

### GPG & signing

- `GP1` `gpg --delete-secret-keys` → refuse without explicit user confirmation.
- `GP2` `gpg --export-secret-keys` to stdout → use a uniquely and exclusively created owner-only destination outside repositories and synchronized paths, then confirm its lifecycle.
- `GP3` `gpg --batch --yes` with destructive op → confirm intent.
- `GP4` `git commit -S --no-verify` / `git tag -s --no-verify` → refuse; address the hook.
- `GP5` `gpg --import` from untrusted source → verify first.
- `GP6` `--passphrase` on command line → use `--pinentry-mode loopback` with file/stdin.

### Cloud CLIs (AWS / gcloud / az)

- `CL1` `aws s3 rm --recursive` → require `--dryrun` first and confirmation.
- `CL2` `aws s3 sync --delete` → run `--dryrun` first.
- `CL3` `aws iam delete-*` → refuse without explicit user confirmation.
- `CL4` `aws ec2 terminate-instances` → confirm instance IDs explicitly.
- `CL5` `aws rds delete-db-instance` → require final snapshot decision.
- `CL6` `gcloud projects delete` → refuse without explicit user confirmation.
- `CL7` `gcloud compute instances delete` → confirm names explicitly.
- `CL8` `az group delete` → refuse without explicit user confirmation.
- `CL9` Default `--profile`/`--region`/context unset → always specify explicitly.
- `CL10` Echo of secret env var (`echo $AWS_SECRET_ACCESS_KEY`) → refuse.

### Infrastructure as Code

- `IC1` `terraform destroy` → refuse without explicit user confirmation and workspace.
- `IC2` `terraform apply -auto-approve` → require plan review in same session.
- `IC3` `terraform apply` without prior `plan` → run `plan` first.
- `IC4` `terraform state rm` / `state mv` → confirm intent; document.
- `IC5` `terraform workspace delete` → refuse without explicit user confirmation.
- `IC6` `pulumi destroy --yes` → refuse without explicit user confirmation.
- `IC7` `pulumi stack rm --force` → refuse without explicit user confirmation.
- `IC8` Backend reconfiguration → verify state lock.

### Containers & orchestration

- `OK1` `docker system prune -af --volumes` → refuse without explicit user confirmation.
- `OK2` `docker rm -f $(docker ps -aq)` → confirm intent; show resolved IDs.
- `OK3` `docker run --privileged` / `--cap-add=ALL` → refuse without explicit need.
- `OK4` `docker run -v /:/host` → refuse.
- `OK5` `kubectl delete namespace <ns>` → confirm namespace and show object counts.
- `OK6` `kubectl apply -f <url>` → download and inspect first.
- `OK7` `kubectl drain` → show plan; decide on `--ignore-daemonsets`.
- `OK8` `kubectl delete pvc` → refuse without explicit user confirmation.
- `OK9` Default `kubectl --context` unset → always specify explicitly.
- `OK10` `helm uninstall <release>` → confirm release and namespace.
- `OK11` `helm install` without `--atomic` → use `--atomic --timeout`.
- `OK12` `kubectl exec -it ... -- sh` for write ops → suggest manifest edit.

### Database CLIs

- `DB1` `DROP DATABASE`, `DROP TABLE` → refuse without explicit user confirmation.
- `DB2` `TRUNCATE` / `DELETE FROM ...;` without `WHERE` → refuse without explicit user confirmation.
- `DB3` `UPDATE ...;` without `WHERE` → refuse without explicit user confirmation.
- `DB4` `psql` connection string with embedded password → use `~/.pgpass` or env from file.
- `DB5` `mysql -p<pass>` → use an encrypted login path or another credential helper that keeps the password out of argv and environment variables.
- `DB6` `redis-cli FLUSHALL` / `FLUSHDB` → refuse without explicit user confirmation.
- `DB7` `redis-cli CONFIG SET` → confirm intent.
- `DB8` `mongosh --eval 'db.dropDatabase()'` → refuse without explicit user confirmation.
- `DB9` Connection defaulting to prod → verify target host explicitly.
- `DB10` `pg_restore --clean` to wrong target → refuse without explicit user confirmation.

### Systemd & service control

- `SS1` `systemctl stop <critical>` (sshd/network) → confirm; warn about lockout.
- `SS2` `systemctl disable --now <critical>` → confirm intent.
- `SS3` Unit file edit without `daemon-reload` → reminder.
- `SS4` `shutdown` / `reboot` / `halt` / `poweroff` → refuse without explicit user confirmation.
- `SS5` `journalctl --vacuum-size=0` → confirm intent.

### Secret & environment hygiene

- `SE1` `echo $SECRET` / `$TOKEN` / `$KEY` / `$PASSWORD` → refuse to echo.
- `SE2` `env` / `printenv` piped to file/log → refuse without explicit user confirmation.
- `SE3` `--password=...` / `--token=...` on command line → use file/stdin.
- `SE4` `curl -H "Authorization: Bearer $TOKEN"` in interactive shell → use config file.
- `SE5` Writing a secret through shell redirection → use a credential helper or a pre-opened no-follow, exclusive, owner-only descriptor outside repositories; otherwise block.
- `SE6` `set -x` with secret in scope → disable around block.
- `SE7` Result of secret-search echoed → pipe to 0600 file.
- `SE8` `!` history expansion in double quotes → `set +H` or single quotes.
- `SE9` Reading a likely secret file to terminal output → resolve the file without reading its contents; block output when sensitivity is known or uncertain.

### Archives

- `AR1` `tar -xf untrusted.tar` → block extraction until one extractor-owned validation/write path handles the same immutable bytes under a fresh destination with containment, entry/type, resource-limit, collision, overwrite, and cleanup enforcement; `tar -tf` is preliminary inspection only.
- `AR2` `tar -xf` with absolute paths or `../` entries → block extraction; a member-list grep is not a substitute for AR1 validation.
- `AR3` `unzip untrusted.zip` to existing dir → block absent AR1-equivalent ZIP validation; for a trusted archive, use a fresh destination and an explicit overwrite policy.
- `AR4` `tar` over network without checksum → download first, verify authenticated provenance and digest, then require AR1 validation before extraction.
- `AR5` `rm -rf <extract-dir>` after partial extract → inspect first.

### Encoding & locale

- `EN1` Shell script with CRLF → `dos2unix`.
- `EN2` UTF-8 BOM in shell script → strip BOM.
- `EN3` `sort` / `tr` / `grep` on bytes without `LC_ALL=C` → set `LC_ALL=C`.
- `EN4` `grep -P` portability → use `grep -E` or `rg`.
- `EN5` `date` with locale leakage → set `LC_ALL=C` or use `date -u +'%Y-%m-%dT%H:%M:%SZ'`.

## Decision Gates

Classify each exact command segment with the narrowest matching rule below. A compound command can match several gates; the most restrictive matching gate wins for the complete command.

Reference records use shorter gate phrases. Map `Prohibited` and unconditional `Block` to **Prohibited**; map `Rewrite` to **Rewrite-Only**; and map `Confirm`, `Confirmable`, or `Refuse without explicit confirmation` to **Confirmable Effects**. `Inspect`, `Verify`, and `Require` name prerequisites rather than outcomes: return `BLOCKED` while they are unresolved, then reclassify the complete command after they pass. For compound phrases, apply every named phase in order and keep the most restrictive result.

### Prohibited

Return `BLOCKED`. Confirmation never authorizes the original command.

- `rm -rf /`, `rm -rf ~`, or `rm -rf $VAR` when `$VAR` is empty or unresolved.
- Any force push to a branch discovered to be protected, default, release, production, or shared; when repository metadata is unavailable, treat `main|master|release/*|production|prod` as protected fallbacks and return `BLOCKED` if the branch's status cannot be established.
- `eval` on a variable or other untrusted text.
- `chmod -R 777`, `chmod u+s`, or `chown -R` outside the project root.
- `docker run -v /:/host` or equivalent host-root mounts.
- Printing, logging, hashing, or otherwise disclosing a credential, token, password, or other secret value or deterministic derivative, except a secret-key export handled by the rewrite-only and confirmable rules below.
- `ssh -A` to a host the user does not control.

### Rewrite-Only

Confirmation never authorizes the original form. Provide a concrete replacement that removes it, then classify the replacement from the beginning. Return `REWRITE` if the replacement is safe without confirmation, `NEEDS-CONFIRMATION` if the replacement has a confirmable effect, or `BLOCKED` if no deterministic replacement exists.

A replacement that installs or executes fetched code, applies infrastructure, mutates a cluster, or otherwise has a confirmable effect is not a `REWRITE` result merely because its syntax is safer. Verify provenance and target context, then return `NEEDS-CONFIRMATION` for the exact replacement; unresolved provenance or context returns `BLOCKED`.

- Bare `git push --force`, `-f`, or `--force-with-lease` without `<ref>:<expected-sha>`.
- `curl ... | sh`, `wget ... | bash`, or another network-to-interpreter pipe.
- `pip install` outside a virtual environment or an unreviewed `sudo <package-manager>` command.
- `terraform apply -auto-approve`, `pulumi destroy --yes`, or another approval-bypassing flag.
- `kubectl apply -f <url>` before the content and authenticated provenance are verified.
- `gpg --export-secret-keys` to stdout or `--no-verify` on commits and tags.
- Commands that persist or pass secret values through process arguments, without printing, logging, hashing, or otherwise disclosing them, when a credential helper, protected file, or stdin/file-descriptor interface can be used.

### Confirmable Effects

Return `NEEDS-CONFIRMATION` only after every required preview, identity, environment, and recovery check has passed. Bind that result to the normalized command, working directory, shell or interpreter, resolved non-secret expansions, authenticated identity and account, repository or platform context, target identifiers, reviewed preview or plan digest, and relevant branch tips or object versions. On a later turn, re-run cheap mutable checks immediately before execution. Return `AUTHORIZED` only when the user confirmed that exact binding and every check still matches; any changed or unverifiable binding invalidates authorization and requires full reclassification. `AUTHORIZED` means approved to execute, not harmless.

- `git reset --hard` with local changes, or a non-protected force push with an explicit lease.
- Git ref or history mutations that survived the prohibited and rewrite-only gates: clean-tree `git reset --hard`, `git branch -D`, `git clean -fdx`, forced submodule deinit, remote tag deletion, or pushed/shared-branch rebase after explicit approval and remote-tip review.
- Destructive filesystem operations that survived the prohibited gate: justified absolute/home recursive deletion after exact-path preview, `find ... -delete` or `-exec rm` after reviewed dry-run output, and `rsync --delete` after a reviewed dry run.
- Bulk deletion through a NUL-safe `find ... -print0 | xargs -0 rm --` replacement after previewing and binding the exact target set.
- Package installation or execution of fetched code after exact-version provenance and lifecycle-script review.
- `npm publish` or an already reviewed package-manager command requiring privilege.
- `dd of=/dev/...`, `mkfs.*`, or partition-table changes against an exact device.
- `terraform destroy`, applying a destroy plan, `terraform workspace delete`, `pulumi destroy` without approval-bypassing flags, or forced stack removal without approval-bypassing flags.
- `docker system prune`, justified `docker run --privileged`, Kubernetes namespace/PVC deletion, or node draining with data loss.
- `helm uninstall` after release and namespace verification.
- `kubectl apply`, `helm install`, `helm upgrade`, and other cluster mutations after manifest or chart review plus explicit context and namespace verification.
- `DROP`, `TRUNCATE`, unguarded `DELETE`/`UPDATE`, Redis flush, or database deletion.
- Shutdown, reboot, or disabling/stopping a critical service.
- Cloud IAM, project, resource-group, recursive object, instance, or database deletion.
- Secret-key deletion or export to a protected destination.

## Output

When the user directly asks to validate a command, return these fields in order:

- `Result:` one of `SAFE`, `REWRITE`, `NEEDS-CONFIRMATION`, `AUTHORIZED`, or `BLOCKED`.
- `Matched patterns:` every applicable pattern as `ID (category)`, or `None`.
- `Assessment:` the concrete risk and decision.
- `Command:` the exact safe or rewritten command, or `Not provided` when blocked; never include secret values.
- `Required checks:` checks that must pass before execution, or `None`.

If the user asks for command safety but supplies no command, still use the same fields: `Result: BLOCKED`, `Matched patterns: None`, `Assessment:` explaining that no exact command was provided, `Command: Not provided`, and `Required checks:` asking for the exact command plus relevant working directory, shell, target, and whether any variables or secrets are involved.

Use `SAFE` only when the original command can run as restated without confirmation. Use `REWRITE` when the original must not run but a replacement is safe without further confirmation. Use `NEEDS-CONFIRMATION` before approval of an exact confirmable command. Use `AUTHORIZED` only after that exact command was confirmed and all prerequisites still hold. Use `BLOCKED` when no deterministic safe rewrite exists, material values remain unresolved, applicable rules conflict, or the exact action is prohibited.

## Provenance

See [source-map.md](./references/source-map.md) for provenance, source-confidence notes, and the boundary between shell semantics and conservative assistant-side policy.

## Verification Before Execution

Before sending the command:

1. Restate the command with non-secret `$VAR` and `$(cmd)` expansions resolved and quoting visible. Keep secret values represented by the variable name or `<redacted>`.
2. If a material non-secret value is unknown, do not run; ask or inspect first. For secret variables, verify the source and presence without reading or echoing the value.
3. Apply the most restrictive matching Decision Gate. Do not treat confirmation as authorization for a prohibited or rewrite-only original form, and reclassify every replacement from the beginning.
4. For destructive operations, name the exact target (path, branch, instance, table, namespace) in your restatement.
5. Re-run classification over the complete restated command and confirm that every matched pattern is addressed. Immediately before an authorized command, refresh mutable identity, context, target, preview, digest, and branch-tip evidence; any mismatch invalidates authorization.

## References

- [Command construction](./references/command-construction.md) — commit messages, quoting, shell composition, secrets, and encoding.
- [Host and repository changes](./references/host-and-repository-changes.md) — Git, filesystem, processes, privilege, signing, services, and archives.
- [Remote delivery](./references/remote-delivery.md) — network-to-shell and SSH safety.
- [Platform and data operations](./references/platform-and-data-operations.md) — cloud, IaC, containers, and database changes.
- [Quoting rules](./references/quoting-rules.md) — bash/zsh quoting and expansion deep dive.
- [Source map](./references/source-map.md) — provenance and source-confidence notes.
