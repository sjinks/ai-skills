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
Safe replacement: Run `cd <submodule>; git status; cd -`; after confirming nothing to preserve, run `git submodule deinit -- <submodule>`. Avoid `--force`.
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
Safe replacement: `target='./build'; [ -n "$target" ] && [ "$target" != "/" ] && [ "$target" != "$HOME" ] && [ -d "$target" ] && rm -rf -- "$target"`.
### FS2 - Variable recursive delete
Example: `rm -rf "$BUILD_DIR"`
Risk: An unset, empty, or root-like value is unsafe.
Decision gate: Block unresolved values.
Safe replacement: `: "${BUILD_DIR:?BUILD_DIR is unset}"; [ -n "$BUILD_DIR" ] && [ "$BUILD_DIR" != "/" ] && [ "$BUILD_DIR" != "$HOME" ] && [ -d "$BUILD_DIR" ] && rm -rf -- "$BUILD_DIR"`.
### FS3 - Unbounded glob delete
Example: `rm -rf *`
Risk: Deletes the current directory's contents.
Decision gate: Prohibited.
Safe replacement: Enumerate explicit paths: `rm -rf -- build/ dist/ .cache/`.
### FS4 - Recursive delete below `/` or `~`
Example: `rm -rf /something`, `rm -rf ~/Downloads/old`
Risk: A spacing or expansion error can affect root or home.
Decision gate: Block absent strong justification; otherwise preview and confirm exact path.
Safe replacement: Name an exact subdirectory and apply FS2 guards.
### FS5 - `find` deletion
Example: `find . -name '*.log' -delete`
Risk: A broad expression deletes unexpected paths.
Decision gate: Confirmable after dry run.
Safe replacement: Run `find . -name '*.log' -print`; after complete-list review and confirmation of the same root and expression, run `find . -name '*.log' -delete`.
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
Decision gate: Refuse without explicit confirmation.
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
Safe replacement: Confirm fingerprint, recipient, and cleanup. Create a unique owner-only destination outside `/tmp`, repositories, and synchronized paths through a no-follow exclusive-open facility, then write with `gpg --output <validated-open-destination> --export-secret-keys --armor ABCD1234`. If the destination cannot be bound against links and replacement races, return `BLOCKED`.
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
Safe replacement: After confirmation, `sudo shutdown -r +1 'reboot for kernel upgrade'`.
### SS5 - Vacuum journal to zero
Example: `journalctl --vacuum-size=0`
Risk: Destroys forensic logs.
Decision gate: Confirm.
Safe replacement: `sudo journalctl --vacuum-time=7d`.
### AR1 - Extract untrusted tar
Example: `tar -xf received.tar`
Risk: Entries can overwrite or escape the destination.
Decision gate: Block without an extractor-owned validation/write path.
Safe replacement: Run `tar -tf received.tar` only as preliminary inspection. Extraction must operate on a secured immutable copy and use one parser for validation and writes, normalize every destination under a fresh root, reject absolute, drive/UNC, traversal, unsafe backslash, symlink, hardlink, special-file, device, pre-existing-link-following, duplicate, normalized-name-collision, and disallowed-overwrite entries, enforce compressed/decompressed byte, entry-count, per-entry, depth, and ratio limits, and clean up partial output on failure. Bind the validated digest to the bytes opened for extraction and fail closed if immutability or parser identity cannot be guaranteed.
### AR2 - Absolute or traversal archive entries
Example: members `/etc/passwd` or `../escape`.
Risk: Writes outside the destination.
Decision gate: Block untrusted extraction absent AR1 validation.
Safe replacement: `tar -tf received.tar | awk '/^\//{abs=1} /(^|\/)\.\.($|\/)/{rel=1} END {exit (abs||rel)}'` catches only a narrow subset; use AR1's extractor-owned path on the exact immutable archive.
### AR3 - Unzip into existing directory
Example: `unzip received.zip`
Risk: Overwrites and path traversal.
Decision gate: Block untrusted archives absent AR1 validation.
Safe replacement: For a trusted archive and fresh destination only: `mkdir -p /tmp/extract; unzip -n received.zip -d /tmp/extract`.
### AR4 - Network tar without verified checksum
Example: `curl https://.../archive.tar.gz | tar -xzf -`
Risk: Partial or substituted content extracts without adequate verification.
Decision gate: Rewrite and block absent authenticated digest and validator.
Safe replacement: Follow the network-to-execution workflow in `remote-delivery.md`, then pass the secured immutable copy and authenticated digest to AR1's single-parser validation/write path. Separate validator and extractor implementations are insufficient; any digest, parser, limit, destination, or archive-identity mismatch returns `BLOCKED`.
### AR5 - Delete after partial extraction
Example: `tar -xf foo.tar || rm -rf foo`
Risk: Hides partial state and extraction failure.
Decision gate: Inspect before mutation.
Safe replacement: Run `find /tmp/extract -mindepth 1 -maxdepth 2 -print` and `tar -tf foo.tar`; compare partial state with the full list before resuming or removing any named path.