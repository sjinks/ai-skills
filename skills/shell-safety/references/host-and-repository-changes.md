# Host and Repository Changes
Read this when a command changes Git state, local files, processes, privileges, signing keys, services, or archive contents.
Every record combines the dangerous pattern with its risk, decision gate, and complete safe replacement or inspection sequence.
## Git destructive operations
### GD1 - Hard reset
Example: `git reset --hard HEAD~3`
Risk: Discards staged and unstaged work.
Decision gate: Confirm the exact target and preserve local changes first.
Safe replacement: Run `git status --porcelain`; if changes exist, stop and decide what to preserve. After a separately approved and verified backup and target confirmation, run `git reset --hard HEAD~3`.
### GD2 - Force push
Example: `git push --force origin feature`
Risk: Overwrites shared remote history.
Decision gate: Prohibited for any discovered protected, default, release, production, or shared branch. When metadata is unavailable, treat `main`, `master`, `release/*`, `production`, and `prod` as protected fallbacks and block if status remains unknown; otherwise confirm a reviewed explicit lease.
Safe replacement:
```sh
git fetch origin
git rev-parse refs/remotes/origin/feature
```
Inspect repository hosting metadata or the authoritative branch policy, upstream/default-branch configuration, and collaborator use. After proving the branch is non-protected, non-default, and non-shared and reviewing the exact tip:
```sh
git push --force-with-lease=refs/heads/feature:<expected-sha> origin feature
```
Never use bare `--force-with-lease`.
### GD3 - Branch deletion
Example: `git branch -D feature-x`
Risk: Unmerged commits become unreachable.
Decision gate: Confirmable.
Safe replacement:
```sh
candidate_ref=feature-x
base_ref="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD)" || exit 1
git log --oneline "$base_ref..$candidate_ref"
```
Bind `candidate_ref`, `base_ref`, the candidate tip, and the reviewed commit set. Refresh them immediately before execution; after reviewing every unmerged commit and confirming that exact binding, run `git branch -D -- "$candidate_ref"`.
The `|| exit 1` sequence is for non-interactive use. In an interactive shell, wrap the inspection in a subshell so failure does not terminate the user's session.
### GD4 - Clean untracked files
Example: `git clean -fdx`
Risk: Removes ignored configuration, artifacts, and notes.
Decision gate: Confirmable after review.
Safe replacement: Run `git clean -ndx`; after reviewing every listed path and confirming exact targets, run `git clean -fdx`.
### GD5 - Detached checkout
Example: `git checkout 4a8c2f1`
Risk: New commits may be lost when switching away.
Decision gate: Rewrite.
Safe replacement: Use `git checkout -b new-branch 4a8c2f1` when a branch is intended, or `git switch --detach 4a8c2f1` for read-only inspection.
### GD6 - Rewrite pushed history
Example: `git rebase -i origin/main` then `git push --force`
Risk: Breaks collaborators' histories.
Decision gate: Block without explicit approval and remote-tip review; confirm the exact explicit-lease push separately.
Safe replacement: Run `git fetch origin` and `git log --oneline origin/main..HEAD`; after confirming no collaborator depends on the commits, record `refs/remotes/origin/feature`, run `git rebase -i origin/main`, review the result, then use GD2's exact explicit-lease push. Re-fetching requires a new review.
### GD7 - Forced submodule deinit
Example: `git submodule deinit --force <module>`
Risk: Discards local submodule work.
Decision gate: Confirmable only after no state must be preserved.
Safe replacement:
```sh
(
	cd -- <submodule> || exit 1
	git status --short --untracked-files=all --ignored=matching
)
```
Proceed only when the subshell exits successfully and its output is empty, meaning no tracked changes, untracked files, or ignored files need preservation. Re-run the same guarded check immediately before confirmation, then run `git submodule deinit -- <submodule>`. Never use `--force` in the replacement.
Before treating the inspection as complete, determine whether the target contains any initialized nested submodule. If it does, return `BLOCKED`; a non-recursive outer status can hide nested state through submodule ignore policy. Do not deinitialize the outer submodule until every nested submodule has first been deliberately preserved or separately deinitialized under the same policy.
### GD8 - Remote tag deletion
Example: `git push --delete origin v1.2.3`
Risk: Releases and consumers can lose a referenced tag.
Decision gate: Confirmable.
Safe replacement: Check release and package references, then after confirmation run `git push --delete origin v1.2.3`.
## Filesystem and processes
### FS1 - Recursive force delete
Example: `rm -rf ./build`
Risk: A typo can delete the parent.
Decision gate: Require an explicit, non-glob path.
Safe replacement: Resolve the explicit target with a platform-appropriate trusted canonicalization facility, compare both canonical path and filesystem identity against `/`, `$HOME`, and every verified account home, preview the bound target, then reverify the same identity immediately before deletion. Return `BLOCKED` when resolution, protected-path discovery, or identity binding is unavailable.
### FS2 - Variable recursive delete
Example: `rm -rf "$BUILD_DIR"`
Risk: An unset, empty, or root-like value is unsafe.
Decision gate: Block unresolved values.
Safe replacement: In a non-interactive script, first require a non-empty value with `: "${BUILD_DIR:?BUILD_DIR is unset}"`; the expansion error exits that shell before later mutations. In an interactive shell, inspect and resolve the value separately and keep deletion `BLOCKED` while it is unset or empty. Parameter expansion does not re-run tilde expansion, so literal `~` is relative to the current directory. Resolve that concrete target and apply FS1's canonical-path, filesystem-identity, preview, and immediate-reverification gates before deletion; reject alternate spellings or aliases of root and every verified home path.
### FS3 - Unbounded glob delete
Example: `rm -rf *`
Risk: Deletes the current directory's contents.
Decision gate: Prohibited.
Safe replacement: Enumerate explicit paths: `rm -rf -- build/ dist/ .cache/`.
### FS4 - Recursive delete below `/` or `~`
Example: `rm -rf /something`, `rm -rf ~/Downloads/old`
Risk: A spacing or expansion error can affect root or home.
Decision gate: Confirmable when the canonical resolved target is any absolute path or lies within a verified account home, after FS1/FS2 prove it is not `/` or a home directory itself.
Safe replacement: Apply FS1/FS2 canonical-path and filesystem-identity checks, bind and preview the exact target, reverify it immediately before execution, and require confirmation of that exact recursive deletion. Root and verified home directories themselves remain blocked.
### FS5 - `find` deletion
Example: `find . -name '*.log' -delete`
Risk: A broad expression deletes unexpected paths.
Decision gate: Block until one exact deletion snapshot is bound through execution.
Safe replacement: Use a trusted runtime/helper to capture one NUL-delimited result from the resolved root and expression into a protected structured snapshot, render every path with reversible unambiguous escaping and stable identity for review, then delete only those same identity-revalidated entries without rerunning `find`. A newline preview followed by `find ... -delete` or `-exec rm` remains `BLOCKED`.
### FS6 - Truncating a log
Example: `truncate -s 0 /var/log/app.log`
Risk: A glob or wrong path clears multiple files.
Decision gate: Confirm exact path.
Safe replacement: `[ -f /var/log/app.log ] && truncate -s 0 /var/log/app.log`.
### FS7 - `dd` to a device
Example: `dd if=image.iso of=/dev/sdb`
Risk: A wrong device destroys its data.
Decision gate: Confirmable.
Safe replacement: Run `lsblk /dev/sdb`; after exact device identity verification and confirmation, run `sudo dd if=image.iso of=/dev/sdb bs=4M status=progress conv=fdatasync`.
### FS8 - `mkfs.*`
Example: `mkfs.ext4 /dev/sdb1`
Risk: Formats the wrong partition.
Decision gate: Confirmable.
Safe replacement: Apply FS7's exact-device inspection and confirmation before formatting.
### FS9 - `chmod -R 777`
Example: `chmod -R 777 /var/www`
Risk: Makes all content world-writable and executable.
Decision gate: Prohibited.
Safe replacement: `chmod -R u=rwX,g=rX,o=rX /var/www`.
### FS10 - `chown -R` outside project root
Example: `sudo chown -R user:user /var`
Risk: Breaks system ownership.
Decision gate: Prohibited; confirmation cannot authorize recursive ownership changes outside the project root.
Safe replacement: Restrict ownership changes to the project root.
### PC1 - Immediate `SIGKILL`
Example: `kill -9 1234`
Risk: Skips cleanup and can hit a reused PID.
Decision gate: Last-resort confirmation.
Safe replacement: Resolve PID and full identity, send `kill <pid>`, wait through terminal or supervisor completion without `sleep`, re-resolve identity, then use `SIGKILL` only when still exact and justified.
### PC2 - Broad `pkill`
Example: `pkill node`
Risk: Matches unrelated processes.
Decision gate: Rewrite.
Safe replacement: Inspect all candidate PIDs and complete identities, select one, re-read it immediately before signaling, then run `kill <pid>` and follow PC1.
### PC3 - Background agent-terminal job
Example: `node server.js &`
Risk: Completion and cleanup cannot be reliably observed.
Decision gate: Block without a supervised async capability.
Safe replacement: Use the runtime's supervised async/background mechanism.
### PC4 - `sleep` as a wait primitive
Example: `sleep 5; check_status`
Risk: Polling is brittle and wastes time.
Decision gate: Prohibited.
Safe replacement: Rely on terminal or supervisor completion; request a supervised runtime when unavailable.
## Privilege, signing, services, and archives
### PE1 - `sudo`
Example: `sudo make install`
Risk: Privilege is silently escalated and pipelines may elevate the wrong process.
Decision gate: Confirm intent.
Safe replacement: State why it is required, avoid silent pipes, then use `sudo -- <command>`; optionally check `sudo -n true 2>/dev/null || { echo "sudo unavailable"; exit 1; }`.
### PE2 - Interactive root shell
Example: `sudo -i`, `sudo su -`
Risk: Subsequent actions remain root and exit is unreliable.
Decision gate: Prohibited.
Safe replacement: Use `sudo -- <command>` for a one-shot action.
### PE3 - Setuid
Example: `chmod u+s /usr/local/bin/myscript`
Risk: Users can run with owner privileges.
Decision gate: Prohibited.
Safe replacement: Use sudoers rules or a specific `setcap` capability.
### GP1 - Delete secret keys
Example: `gpg --delete-secret-keys ABCD1234`
Risk: Encrypted data may become unrecoverable.
Decision gate: Confirmable.
Safe replacement: Run `gpg --list-secret-keys ABCD1234`; after fingerprint verification and exact-key confirmation, delete it.
### GP2 - Export secret keys to stdout
Example: `gpg --export-secret-keys ABCD1234`
Risk: Key material enters output and logs.
Decision gate: Rewrite then confirm protected destination.
Safe replacement: Confirm fingerprint, recipient, and cleanup. Have the runtime create a unique owner-only destination outside `/tmp`, repositories, and synchronized paths through a no-follow exclusive-open API, retain that open handle, and direct GPG stdout to the inherited descriptor, for example `gpg --export-secret-keys --armor ABCD1234 1>&3` when descriptor 3 is the validated handle. Never reopen a validated pathname. If an already-open exclusive handle cannot be carried through export, return `BLOCKED`.
### GP3 - Batch destructive GPG
Example: `gpg --batch --yes --delete-keys ABCD1234`
Risk: Suppresses the prompt for a typo.
Decision gate: Confirm fingerprint.
Safe replacement: If batch is required, confirm that exact fingerprint first.
### GP4 - `--no-verify` on signed Git actions
Example: `git commit -S --no-verify`
Risk: Bypasses policy hooks.
Decision gate: Prohibited.
Safe replacement: Fix the hook failure; never pass `--no-verify`.
### GP5 - Untrusted GPG import
Example: `gpg --import < untrusted.asc`
Risk: Pollutes trust with attacker-controlled keys.
Decision gate: Inspect then import.
Safe replacement: Run `gpg --show-keys received.asc`; after authenticated out-of-band fingerprint verification, run `gpg --import received.asc`.
### GP6 - Passphrase in argv
Example: `gpg --passphrase "secret" --decrypt file.gpg`
Risk: Exposes the passphrase in process lists and history.
Decision gate: Rewrite.
Safe replacement: Prefer normal pinentry; noninteractive use requires a runtime-protected file descriptor or credential helper with explicit lifetime.
### SS1 - Stop critical service
Example: `systemctl stop sshd`
Risk: A remote operator can lock themselves out.
Decision gate: Confirm with recovery plan.
Safe replacement: State the lockout risk and ensure console recovery before the exact stop.
### SS2 - Disable critical service now
Example: `systemctl disable --now sshd`
Risk: Stops service and persists lockout through reboot.
Decision gate: Confirm with recovery plan.
Safe replacement: Apply SS1 checks before the exact operation.
### SS3 - Unit edit without reload
Example: Edit a unit then `systemctl restart foo`.
Risk: systemd uses its cached unit.
Decision gate: Rewrite.
Safe replacement: `sudo systemctl daemon-reload` then `sudo systemctl restart foo`.
### SS4 - Host shutdown or reboot
Example: `shutdown now`
Risk: Host downtime and remote disconnection.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Preserve the requested power action and timing. After confirming an immediate shutdown/power-off, run `sudo shutdown now`; use `sudo shutdown -r now` only when an immediate reboot was explicitly requested. Any delay or message must likewise come from the caller rather than being introduced by the rewrite.
### SS5 - Vacuum journal to zero
Example: `journalctl --vacuum-size=0`
Risk: Destroys forensic logs.
Decision gate: Confirm.
Safe replacement: Preserve the requested size-based policy. After privilege, journal scope, and exact size confirmation, run `sudo journalctl --vacuum-size=0`; use `--vacuum-time=<duration>` only when the caller explicitly requests a time-based retention policy.
### AR1 - Extract untrusted tar
Example: `tar -xf received.tar`
Risk: Entries can overwrite or escape the destination.
Decision gate: Block without an extractor-owned validation/write path.
Safe replacement: Run `tar -tf received.tar` only as preliminary inspection. Extraction must operate on a secured immutable copy and use one parser and decoded-name model for validation and writes. The extractor must:

- create or receive a private, canonicalized, extractor-controlled fresh root that did not previously exist; shared roots require locking and explicit pre-existing-entry policy;
- normalize Unicode and platform path syntax before containment and duplicate checks; reject empty names, NUL/control characters, `.`, `..`, absolute, drive-relative, drive/UNC/namespace/device, alternate-data-stream, reserved-device, trailing-dot/space, unsafe-separator, overlong, case-folding, Unicode, duplicate, and normalized-name-collision paths;
- reject symlinks, unsafe hardlinks, devices, FIFOs, sockets, and other special files by default;
- enforce entry/directory count, path length/depth, per-file and total decompressed bytes, sparse apparent size, metadata/header size, compression ratio, CPU, time, memory, and nested-archive recursion limits before and during extraction;
- perform root-confined no-follow writes with containment and file-type revalidation at write time, reject disallowed overwrites and pre-existing links, and prevent path swaps;
- restore executable bits, permissions, timestamps, and ownership only under an explicit policy, never archive uid/gid by default; and
- clean partial output after rejection, limit failure, timeout, cancellation, or parser error so no consumer sees it as complete.

Bind the validated digest to the exact bytes opened by that extractor and fail closed if destination trust, parser identity, immutability, limits, or race-resistant writes cannot be guaranteed.
### AR2 - Absolute or traversal archive entries
Example: members `/etc/passwd` or `../escape`.
Risk: Writes outside the destination.
Decision gate: Block untrusted extraction absent AR1 validation.
Safe replacement: `tar -tf received.tar | awk '/^\//{abs=1} /(^|\/)\.\.($|\/)/{rel=1} END {exit (abs||rel)}'` catches only a narrow subset; use AR1's extractor-owned path on the exact immutable archive.
### AR3 - Unzip into existing directory
Example: `unzip received.zip`
Risk: Overwrites and path traversal.
Decision gate: Block untrusted archives absent AR1 validation.
Safe replacement: Even for a trusted archive, require a runtime-created private destination that did not previously exist and root-confined no-follow writes with an explicit overwrite policy. Do not use a predictable path or `mkdir -p` as proof of freshness. For untrusted archives, apply the complete AR1 contract.
### AR4 - Network tar without verified checksum
Example: `curl https://.../archive.tar.gz | tar -xzf -`
Risk: Partial or substituted content extracts without adequate verification.
Decision gate: Rewrite and block absent authenticated digest and validator.
Safe replacement: Follow the network-to-execution workflow in `remote-delivery.md`, then pass the secured immutable copy and authenticated digest to AR1's single-parser validation/write path. Separate validator and extractor implementations are insufficient; any digest, parser, limit, destination, or archive-identity mismatch returns `BLOCKED`.
### AR5 - Delete after partial extraction
Example: `tar -xf foo.tar || rm -rf foo`
Risk: Hides partial state and extraction failure.
Decision gate: Prohibited for resumption; cleanup is blocked unless bound to the extractor-owned root.
Safe replacement: The extractor must clean its exact identity-bound private root on rejection, limit failure, timeout, cancellation, or parser error. Never resume a failed extraction. If in-process cleanup did not complete, quarantine that exact root so no consumer can observe it as complete, then remove it only through independently revalidated filesystem controls bound to the same root identity. Do not substitute a hard-coded path or shallow listing as cleanup authorization.