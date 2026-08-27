# Remote Delivery
Read this when a command downloads executable content, installs software, or sends shell work to a remote host.
Each record combines its dangerous form, risk, decision gate, and safe replacement with inspection and mutation phases separated.
### CS3 / NS1 - Network content piped to an interpreter
Example: `curl https://example.com/install.sh | sh` or `wget ... | bash`
Risk: A compromised or substituted server supplies uninspected code.
Decision gate: Rewrite; block without authenticated expected digest, review, or verification.
Safe replacement: Obtain the expected SHA-256 through an authenticated publisher channel. Have the runtime download into a private, exclusively created object and make it immutable to other writers while retaining a stable handle/identity. Verify the digest with a mismatch-failing API over that object, review those exact bytes, and execute through the same immutable object or inherited descriptor without reopening a replaceable pathname. Immediately before execution, revalidate object identity, immutability, and digest. If the runtime cannot preserve one object identity through download, verification, review, and execution, return `BLOCKED`. Clean up through the runtime's protected object lifecycle.
### NS2 - Global npm install
Example: `npm install -g some-tool`
Risk: Pollutes and can privilege-escalate the host.
Decision gate: Rewrite, then reclassify package installation or execution after provenance and lifecycle-script review.
Safe replacement: Pin an exact reviewed version and prefer a project-local dependency, for example `npm install --save-dev --ignore-scripts some-tool@<reviewed-version>`. If lifecycle scripts are required, review them before a separately classified install. Do not use unpinned `npx` as a safety rewrite because it can fetch and execute code.
### NS3 - npm publish
Example: `npm publish`
Risk: Registry publication is supply-chain affecting and may be irreversible.
Decision gate: Refuse without explicit confirmation.
Safe replacement: After confirmation, run `npm publish --dry-run`; review complete package contents and confirm package, version, registry, and access before `npm publish --access public`.
### NS4 - pip install outside a virtual environment
Example: `pip install requests`
Risk: Pollutes or breaks system Python.
Decision gate: Rewrite.
Safe replacement:
```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
### NS5 - Privileged package manager
Example: `sudo apt install foo`
Risk: Privileged install can violate host policy.
Decision gate: Confirm intent.
Safe replacement: Prefer supported dry-run first, then use the explicit approved action.
### NS6 / RX1 - Long remote shell pipeline
Example: `ssh prod "find / -name '*.log' | xargs rm"`
Risk: Nested local and remote parsing makes quoting and targets ambiguous.
Decision gate: Rewrite.
Safe replacement:
```sh
ssh host bash -s < local-script.sh
```
This form is for a reviewed script with no dynamic arguments. SSH does not provide a portable argv-preserving boundary for appended arguments; when dynamic input is required, block until a transport-specific structured encoding and remote decoder are defined and reviewed.
### RX2 - Disabled SSH host-key checking
Example: `ssh -o StrictHostKeyChecking=no user@host`
Risk: Defeats host authentication; unauthenticated `ssh-keyscan` does not restore it.
Decision gate: Prohibited unless the target is verified as an ephemeral CI host whose lifecycle and threat model permit the exception. Return `BLOCKED` for normal or unresolved hosts; for the verified exception, reclassify the complete replacement and return `SAFE` only when no other pattern applies.
Safe replacement: Obtain expected `SHA256:` fingerprint through an authenticated channel; bind it to hostname, port, and algorithm; write `ssh-keyscan -t ed25519 host` to a secure temporary file; inspect each candidate with `ssh-keygen -lf <candidate-record> -E sha256`; require exactly one matching record, append only it to `known_hosts`, then connect with strict checking enabled.
### RX3 - Remove known-host entry
Example: `ssh-keygen -R host`
Risk: Hides a host-key-change warning.
Decision gate: Confirm intent.
Safe replacement: State why the record is removed and expect a verified key rotation.
### RX4 - Remote glob via scp
Example: `scp host:/var/log/*.log .`
Risk: Remote expansion and whitespace make escaping unreliable.
Decision gate: Block until the exact remote source set is captured and bound.
Safe replacement: Use an authenticated remote API or helper to resolve the glob once into a structured path list, render every remote path unambiguously for review, and transfer each explicit retained path without another remote glob expansion. Do not replace `*.log` with recursive transfer of `/var/log/`, which broadens scope to unrelated entries. If exact path boundaries cannot survive through transfer, return `BLOCKED`.
### RX5 - rsync delete
Example: `rsync -a --delete src/ dst/`
Risk: A source typo can delete destination contents.
Decision gate: Confirmable after dry run.
Safe replacement: Run `rsync -av --delete -n src/ dst/`; after reviewing every deletion and confirming source and destination, run `rsync -av --delete src/ dst/`.
### RX6 - SSH agent forwarding to untrusted host
Example: `ssh -A user@untrusted`
Risk: The host can use the local agent to access trusted hosts.
Decision gate: Prohibited.
Safe replacement: Use `ProxyJump` or `ssh -o ProxyCommand=...`.
### RX7 - sshpass
Example: `sshpass -p "$PASS" ssh user@host`
Risk: Password appears in process listings.
Decision gate: Prohibited.
Safe replacement: Use key authentication and remove `sshpass`.