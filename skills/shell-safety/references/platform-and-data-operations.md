# Platform and Data Operations

Read this when a command can mutate cloud resources, infrastructure state, containers, orchestration resources, or databases.

Each record combines its dangerous form, risk, decision gate, and safe replacement or inspection sequence.

## Cloud CLIs

### CL1 - Recursive S3 removal
Example: `aws s3 rm s3://bucket/path --recursive`
Risk: Mass deletion is not recoverable without versioning.
Decision gate: Confirmable after dry run.
Safe replacement: Run `AWS_PROFILE=<profile> AWS_REGION=<region> aws s3 rm s3://bucket/path --recursive --dryrun`; review targets and confirm the same explicit profile, region, bucket, and prefix before the command without `--dryrun`.

### CL2 - S3 sync delete
Example: `aws s3 sync ./local s3://bucket --delete`
Risk: An empty or wrong source deletes destination objects.
Decision gate: Confirmable after dry run.
Safe replacement: Run `AWS_PROFILE=<profile> AWS_REGION=<region> aws s3 sync ./local s3://bucket --delete --dryrun`; review changes and confirm the same explicit profile, region, bucket, and prefix before mutation.

### CL3 - IAM deletion
Example: `aws iam delete-role --role-name X`
Risk: Can lock out infrastructure identities.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Run `AWS_PROFILE=<profile> AWS_REGION=<region> aws iam list-attached-role-policies --role-name X`; verify the account, review dependencies, and confirm the same explicit profile, region, and role before deletion.

### CL4 - EC2 termination
Example: `aws ec2 terminate-instances --instance-ids i-0abc`
Risk: A wrong ID terminates production.
Decision gate: Confirmable.
Safe replacement: Run ``AWS_PROFILE=<profile> AWS_REGION=<region> aws ec2 describe-instances --instance-ids i-0abc --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0]]' --output text``; verify the account and instance identity, then confirm the same explicit context before termination.

### CL5 - RDS deletion
Example: `aws rds delete-db-instance --db-instance-identifier prod`
Risk: A final-snapshot decision controls recoverability.
Decision gate: Confirmable after the final-snapshot decision is resolved.
Safe replacement: Preserve the caller's recovery choice and bind the same account, profile, region, and DB instance in either branch. For a final snapshot, require a collision-free snapshot ID and confirm `AWS_PROFILE=<profile> AWS_REGION=<region> aws rds delete-db-instance --db-instance-identifier prod --final-db-snapshot-identifier <snapshot-id>`. For an explicit skip choice, require acknowledgement that no final recovery snapshot will be created, then confirm the exact command with `--skip-final-snapshot`. Return `BLOCKED` while the recovery choice, snapshot identity, acknowledgement, or target binding is unresolved.

### CL6 - GCP project deletion
Example: `gcloud projects delete my-project`
Risk: Deletes project resources.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Verify the authenticated account and inspect `gcloud --project=<project> projects describe <project>`; confirm that same explicit project separately before deletion.

### CL7 - GCP VM deletion
Example: `gcloud compute instances delete my-vm`
Risk: A wrong name deletes the wrong machine.
Decision gate: Confirmable.
Safe replacement: Run `gcloud --project=<project> compute instances describe my-vm --zone=<zone>`; verify account, project, zone, and identity, then confirm the same explicit context before deletion.

### CL8 - Azure resource-group deletion
Example: `az group delete --name prod`
Risk: Deletes every resource in the group.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Verify the signed-in tenant and inspect `az --subscription=<subscription> resource list --resource-group prod -o table`; confirm the same explicit subscription and group before deletion.

### CL9 - Implicit cloud context
Example: `aws s3 rm s3://bucket --recursive` using defaults.
Risk: Defaults can target production.
Decision gate: Rewrite.
Safe replacement: First determine the caller-selected account/profile, region, project, subscription, cluster context, and namespace that apply; never invent or hard-code `dev`. Use read-only `ls`/`list`/`get` commands with those explicit selectors only as inspection prerequisites. Then add the same verified selector to the original mutation, preserve its action and target, and reclassify the complete explicit-context command under every applicable mutation rule.

### CL10 - Echoing cloud secret
Example: `echo $AWS_SECRET_ACCESS_KEY`
Risk: Leaks credentials.
Decision gate: Prohibited.
Safe replacement: Do not print resolved secret environment variables.

## Infrastructure as code

Before any IC1–IC8 mutation, bind one complete identity-bound IaC mutation snapshot containing the command source actor, credential-backed authenticated execution principal/account, credentials, executable/configuration inputs and content bindings, backend authority, selected workspace or fully qualified stack, state generation/serial and relevant lock identity, exact targets, rollback/recovery evidence, concurrency/other-operator state, endpoint policy, and isolation controls. Keep source actor and execution principal distinct from each other and from credentials, authorities, and targets. Retain the unchanged snapshot through the operation and immediately revalidate it before every mutation phase; return `BLOCKED` if any field is missing, changes, or cannot be held stable.

Terraform planning is executable, not an inert preview. Before any `terraform plan` sequence, bind and trust the exact Terraform binary and CLI configuration, root configuration and complete module graph, dependency lockfile and provider binaries, backend and workspace, variable/configuration inputs, external data-source programs and provisioner-like local execution paths, environment, credentials, the resolved authenticated principal/account, and allowed network endpoints. Treat actor identity as distinct from credentials, backend/workspace context, and target identifiers. For every Terraform, provider, runtime, loader/interpreter, data-source, provisioner, or other executable input, bind its canonical path and retained filesystem identity plus content digest, or retain an equivalently immutable reviewed object; name/version alone is insufficient. Keep those executable bytes non-replaceable through invocation using retained immutable objects, trusted non-writable storage/read-only mounts, descriptor-bound execution, or an equivalent guarantee; return `BLOCKED` when execution must reopen mutable pathnames. Run planning in a fresh isolated least-privilege environment that allows only snapshot-bound executable transitions/subprocesses and snapshot-bound endpoints, denies every other subprocess and network destination, and prevents unreviewed host writes. Capture all of those inputs, content bindings, the authenticated actor, other authorities, endpoint rules, and isolation controls in one identity-bound trust snapshot retained through the sequence; immediately revalidate executable content, actor identity, and the complete snapshot before plan and again before apply. Return `BLOCKED` if any executable input, plugin, external program, configuration layer, actor, authority, endpoint, isolation control, content binding, or snapshot binding is unresolved or changes.

### IC1 - Terraform destroy
Example: `terraform destroy -auto-approve`
Risk: Tears down all managed resources.
Decision gate: Refuse without explicit confirmation and reviewed workspace.
Safe replacement: First satisfy the common IaC mutation and Terraform planning preconditions above. Then run the trusted `terraform workspace show` and `terraform providers`, and create the saved destroy plan in a fresh private owner-only directory outside the repository and synchronized/shared paths, with trusted non-writable parents. Treat the plan as sensitive and permit only its bounded private persistence from creation through the retained `apply`; clean it on success, failure, timeout, or cancellation. Review the plan through a controlled non-recording private channel. Do not print, log, upload, or retain unredacted machine-readable renderings; keep any transient derived review artifact under the same private controls and remove it immediately after review. Bind the plan's filesystem identity and digest to the retained trust snapshot, including the Terraform binary, trusted configuration/module graph, lockfile/provider set, CLI and variable/configuration inputs, external/provisioner-like program set, environment, credentials, source actor, authenticated execution principal, endpoint policy, isolation controls, workspace, backend, state generation/lock, targets, and reviewed changes. Prevent replacement while Terraform opens it for `apply`, and revalidate the complete trust snapshot plus both actor identities, plan identity, and digest immediately before execution. If controlled review cannot avoid disclosure, planning inputs are untrusted, or any binding cannot remain stable through pathname reopening, return `BLOCKED`.

### IC2 - Auto-approved or saved-plan Terraform apply
Example: `terraform apply -auto-approve`, `terraform apply apply.plan`
Risk: Bypasses interactive approval or reopens a saved plan whose review, identity, or sensitive-data lifecycle may be unbound.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: First satisfy the common IaC mutation and Terraform planning preconditions above. Create the saved plan in a fresh private owner-only directory outside the repository and synchronized/shared paths, with trusted non-writable parents. Treat the plan as sensitive and permit only its bounded private persistence from creation through the retained `apply`; clean it on every outcome. Review through a controlled non-recording private channel. Do not print, log, upload, or retain unredacted machine-readable renderings; keep any transient derived review artifact under the same private controls and remove it immediately after review. Bind the plan's filesystem identity and digest to the retained trust snapshot, including the Terraform binary, trusted configuration/module graph, lockfile/provider set, CLI and variable/configuration inputs, external/provisioner-like program set, environment, credentials, source actor, authenticated execution principal, endpoint policy, isolation controls, workspace, backend, state generation/lock, targets, and changes. Prevent replacement while Terraform opens it for `apply`, revalidate the complete trust snapshot plus both actor identities, plan identity, and digest immediately before execution, and confirm only that retained plan. If controlled review cannot avoid disclosure, planning inputs are untrusted, or any binding cannot remain stable through pathname reopening, return `BLOCKED`.

### IC3 - Terraform apply without plan
Example: `terraform apply`
Risk: No reviewed change set.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: Satisfy the common IaC mutation and Terraform planning preconditions, then use IC2's plan-first sequence. Planning remains `BLOCKED` until every executable input, actor, authority, state/lock, and isolation control is trusted.

### IC4 - Terraform state mutation
Example: `terraform state rm aws_instance.web`
Risk: Creates drift and can recreate resources.
Decision gate: Confirmable after the common IaC mutation precondition, exact state-generation/lock, target, drift consequence, and recovery plan are reviewed.
Safe replacement: From the unchanged bound backend/workspace snapshot, inspect the exact state serial/generation and lock, run the trusted read-only state inspection for `aws_instance.web`, document the reason and recreation/import consequences, bind recovery evidence, then confirm only `terraform state rm aws_instance.web`. Revalidate the complete snapshot immediately before execution; any actor, principal, backend, workspace, state, lock, or target change returns `BLOCKED`.

### IC5 - Terraform workspace delete
Example: `terraform workspace delete prod`
Risk: Removes state metadata.
Decision gate: Confirmable only after the common IaC mutation precondition and proof that the exact workspace state/resources are empty or deliberately preserved.
Safe replacement: Bind the backend authority, workspace identity, state serial/generation and lock, inspect every resource and pending operation, preserve required state/recovery evidence, and confirm only the exact non-current workspace deletion. Revalidate the complete snapshot immediately before execution; return `BLOCKED` for the current workspace, non-empty/unreviewed state, concurrency, or any changed identity.

### IC6 - Pulumi destroy with approval bypass
Example: `pulumi destroy --yes`
Risk: Deletes the stack without review.
Decision gate: Rewrite then confirm.
Safe replacement: First satisfy the common IaC mutation precondition. `pulumi preview` executes the stack program and provider plugins; it is not a safe first inspection step. Before preview, bind and trust the exact Pulumi CLI and CLI configuration, project/stack program, language runtime and complete dependency lock/closure, provider plugins, caller-selected backend authority and fully qualified stack identity, configuration/secrets inputs, external programs, environment, credentials, the source actor, authenticated execution principal/account, and allowed network endpoints. Treat both actors as distinct from each other, credentials, backend authority, organization/project context, and stack identity. For every CLI, runtime, loader/interpreter, program, plugin, or external executable, bind its canonical path and retained filesystem identity plus content digest, or retain an equivalently immutable reviewed object. Keep those executable bytes non-replaceable through invocation using retained immutable objects, trusted non-writable storage/read-only mounts, descriptor-bound execution, or an equivalent guarantee; return `BLOCKED` when execution must reopen mutable pathnames. Run the preview in a fresh isolated least-privilege environment that allows only snapshot-bound executable transitions/subprocesses and snapshot-bound endpoints, denies every other subprocess and network destination, and prevents unreviewed host writes. Retain the common snapshot through the sequence; immediately revalidate both actor identities and the complete snapshot before preview and again immediately before destroy. Return `BLOCKED` while any input, actor, principal, authority, endpoint, isolation control, content binding, or snapshot binding is unresolved or changes. After those checks pass, use the same explicit stack selector for `pulumi preview --diff --stack <fully-qualified-stack>` and the corresponding `pulumi destroy --stack <fully-qualified-stack>` without `--yes`; review and confirm the exact bound effects against the unchanged trust snapshot.

### IC7 - Forced Pulumi stack removal
Example: `pulumi stack rm --force prod`
Risk: Loses rollback history.
Decision gate: Refuse without explicit confirmation after the common IaC mutation precondition, exact backend/fully qualified stack identity, state generation/lock, and recovery consequences are reviewed.
Safe replacement: No automatic replacement. Revalidate the complete snapshot immediately before a caller-confirmed exact `pulumi stack rm --force <fully-qualified-stack>`; return `BLOCKED` if the stack is not already deliberately destroyed/preserved, recovery evidence is absent, or any actor, principal, backend, stack, state, lock, or concurrency binding changes.

### IC8 - Backend reconfiguration
Example: `terraform init -migrate-state` while another operator holds the lock.
Risk: Can corrupt state.
Decision gate: Block until lock ownership and the common IaC mutation precondition are verified; force-unlock and backend migration are separate confirmable mutations.
Safe replacement: Phase 1: prove the exact lock is stale, bind lock ID/owner, state serial/generation, backend/workspace, all active clients/operators, and recovery evidence, then revalidate the common snapshot and confirm only `terraform force-unlock <lock-id>`. Lock-owner verification never authorizes migration. Phase 2: after a successful unlock and fresh snapshot/state revalidation, bind source and destination backend authorities, migration inputs, state backup/digest, rollback plan, and concurrency controls; preview the migration where the trusted tool supports it, then separately confirm `terraform init -migrate-state`. Return `BLOCKED` on a live/ambiguous lock, missing recovery, changed state/backend/actor/principal, or any unclassified acquisition/executable path.

## Containers and orchestration

### OK1 - Docker system prune
Example: `docker system prune -af --volumes`
Risk: Deletes detached volumes and broad local state.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Inspect images, containers, networks, build cache, and volumes separately. If the caller still intends the original broad scope, confirm and preserve the exact `docker system prune -af --volumes` effect; offer narrower per-resource prune commands only when the caller explicitly chooses narrower scope.

### OK2 - Mass container removal
Example: `docker rm -f $(docker ps -aq)`
Risk: Stops and removes all containers.
Decision gate: Confirm selected IDs.
Safe replacement: Capture the complete `docker ps -aq` ID set once and review each captured ID with its name, image, and state. If the caller still intends force-removing all containers, confirm that exact captured set and pass those same IDs to `docker rm -f`; if the caller chooses a subset, preserve only that explicit subset and its requested force behavior. Do not silently narrow all containers to exited containers, and do not recalculate the ID set inside the removal command. Return `BLOCKED` when the captured set is empty, incomplete, changed, or cannot be reviewed.

### OK3 - Privileged container
Example: `docker run --privileged ...`
Risk: Near-full host access.
Decision gate: Refuse without explicit need.
Safe replacement: Add only required capabilities, such as `--cap-add=NET_ADMIN`.

### OK4 - Host-root mount
Example: `docker run -v /:/host ubuntu sh`
Risk: Container writes affect the host root.
Decision gate: Prohibited.
Safe replacement: Mount only a needed path, for example `-v /tmp/work:/work`.

### OK5 - Namespace deletion
Example: `kubectl delete namespace staging`
Risk: Cascade-deletes namespaced resources.
Decision gate: Confirm dynamic namespace-wide scope, or require server-side stability for an exact reviewed set.
Safe replacement: Discover and inventory every listable namespaced API resource under the exact context:
```sh
resources="$(kubectl --context=<context> api-resources --namespaced=true --verbs=list -o name)" || exit 1
[ -n "$resources" ] || exit 1
while IFS= read -r resource; do
	[ -n "$resource" ] || continue
	objects="$(kubectl --context=<context> --namespace=<namespace> get "$resource" -o name)" || exit 1
	count="$(printf '%s\n' "$objects" | awk 'NF { count++ } END { print count+0 }')" || exit 1
	printf '%s\t%s\n' "$resource" "$count"
	[ -z "$objects" ] || printf '%s\n' "$objects"
done <<EOF
$resources
EOF
```
Any discovery or list failure blocks deletion. The client-side inventory is an inspection prerequisite only; refreshing it cannot bind the resource set through the delete request. Before deletion, either (a) explicitly confirm dynamic namespace-wide scope, including resources created or changed before the server processes deletion, while binding the namespace UID and exact context, or (b) use a server-side admission, freeze, or equivalent control that keeps the reviewed set stable and submit the namespace deletion with server-enforced UID/resourceVersion preconditions. If the caller requires only the exact reviewed object set and no server-side stability mechanism is available, return `BLOCKED`.

### OK6 - Apply manifest from URL
Example: `kubectl apply -f https://example.com/manifest.yaml`
Risk: Applies uninspected remote workload definitions.
Decision gate: Rewrite and confirm consequential effects.
Safe replacement: Obtain authenticated provenance and an expected digest. Have the runtime create a private temporary location and an exclusive no-follow handle, download through that handle, and bind the digest to the exact bytes reviewed. Keep the reviewed object immutable and inaccessible to other writers; immediately before apply, reverify its handle/inode and digest. Then confirm the explicit context/namespace and apply those same bytes. If `kubectl` must reopen a pathname, it must be inside the private directory with unchanged identity, permissions, ownership, and digest; otherwise return `BLOCKED`. Never use a predictable shared `/tmp` path.

### OK7 - kubectl drain
Example: `kubectl drain node-1`
Risk: Evictions and local-data behavior require explicit decisions.
Decision gate: Confirmable after plan.
Safe replacement: Run `kubectl --context=<context> drain node-1 --dry-run=client`; review context, node, eviction effects, and local-data loss before confirming the same explicit-context command with the required daemonset and local-data flags.

### OK8 - PVC deletion
Example: `kubectl delete pvc data-0`
Risk: Dynamic provisioner reclaim policy may delete storage.
Decision gate: Block without server-side preconditions and PV-policy coordination that preserve the reviewed state through deletion.
Safe replacement: Read and bind the PVC UID, resource version, and current non-empty `spec.volumeName`, then inspect that exact PV's UID, resource version, and `spec.persistentVolumeReclaimPolicy`. The PVC delete request must use server-side UID and resourceVersion preconditions so a recreated or modified claim cannot match. Because PV reclaim policy is independently mutable, keep deletion `BLOCKED` unless an admission policy, controller, lock, or equivalent server-side mechanism guarantees the reviewed PV identity and reclaim policy through the PVC deletion request. A final client-side re-read alone is insufficient.

### OK9 - Implicit kubectl context
Example: `kubectl apply -f svc.yaml`
Risk: Current context can be production.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: Review the manifest, pin context and namespace, then confirm `kubectl --context=<context> --namespace=<namespace> apply -f svc.yaml`.

### OK10 - Helm uninstall
Example: `helm uninstall my-release`
Risk: Deletes the release with chart-specific storage effects.
Decision gate: Confirmable.
Safe replacement: Run `helm list -n my-ns`; verify release and namespace, then confirm before `helm uninstall my-release -n my-ns`.

### OK11 - Non-atomic Helm install
Example: `helm install foo ./chart`
Risk: Failure leaves partial resources.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: Review the chart and rendered manifests, verify cluster context and namespace, then confirm `helm --kube-context=<context> install foo ./chart --namespace=<namespace> --atomic --timeout 5m`.

### OK12 - Write through kubectl exec
Example: `kubectl exec -it pod-0 -- sh -c "echo data > /etc/config"`
Risk: Bypasses audit and disappears on restart.
Decision gate: Rewrite.
Safe replacement: Edit the manifest in Git and reapply it.

## Database CLIs

### DB1 - DROP database or table
Example: `psql -c "DROP TABLE users;"`
Risk: Schema and data loss.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Take a backup or snapshot first, then confirm exact target.

### DB2 - Unqualified TRUNCATE or DELETE
Example: `DELETE FROM orders;`
Risk: Removes all rows.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Preserve the caller's requested scope. If all-row deletion is intentional, inspect `SELECT COUNT(*) FROM orders;`, bind the exact database/schema/table and recovery plan, then confirm the unchanged all-row transaction. If a subset is intended, require the caller to supply the exact predicate and validate its count; never invent a date or business criterion.

### DB3 - Unqualified UPDATE
Example: `UPDATE users SET status='inactive';`
Risk: Mutates all rows.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Preserve the caller's requested scope. If the all-row update is intentional, inspect `SELECT COUNT(*) FROM users;`, bind the exact database/schema/table, new value, rollback/recovery plan, and transaction, then confirm the unchanged all-row update. If a subset is intended, require the caller to supply the exact predicate and validate its count; never invent a date or business criterion.

### DB4 - psql URI password
Example: `psql postgres://user:secret@host/db`
Risk: Password leaks through history and process listings.
Decision gate: Rewrite.
Subsumes: `SE3` for the password-in-argv hazard because DB4 preserves the one-time database connection while applying the same no-secret-argv requirement.
Safe replacement: For the original one-time connection, remove the password from the URI and force an interactive prompt without persisting it, for example `psql -W 'host=host dbname=db user=user'`; preserve the caller's host, port, database, user, TLS, and other options. Use an existing approved `.pgpass` or credential helper only after verifying it without reading the secret. Create or modify persistent credential state only when the caller explicitly requests storage, after separately classifying its destination, replacement behavior, ownership, permissions, and lifecycle.

### DB5 - MySQL argv password
Example: `mysql -uuser -psecret`
Risk: Password leaks in argv.
Decision gate: Rewrite.
Subsumes: `SE3` for the password-in-argv hazard because DB5 preserves the requested MySQL connection while applying the same no-secret-argv requirement.
Safe replacement: For the original one-time connection, remove the password value but keep `-p` so MySQL prompts without placing the secret in argv, for example `mysql -uuser -p`; preserve any caller-supplied host, port, database, and options. A login path stores host, user, password, port, and socket, not the default database, so pass any requested database explicitly as a positional argument such as `mysql --login-path=<name> <database>`. Create a persistent `mysql_config_editor` login path only when the caller explicitly requests credential storage, after separately classifying the exact login-path name, host, user, existing-entry replacement, credential-store destination, ownership, permissions, lifecycle, and confirmation. Never invent a `prod` login path.

### DB6 - Redis flush
Example: `redis-cli FLUSHALL`
Risk: Deletes every key.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Preserve the requested scope; never replace `FLUSHALL` with `FLUSHDB` or vice versa.

- Standalone `FLUSHDB`: bind server identity, host, port, and the zero-based logical database, then confirm `redis-cli -h <host> -p <port> -n <db> FLUSHDB`.
- Standalone `FLUSHALL`: bind server identity, host, and port, then confirm the unchanged `FLUSHALL` scope across every logical database on that server.
- Redis Cluster: only database 0 exists, so `FLUSHDB` and `FLUSHALL` have equivalent scope on the contacted node; one endpoint is not a cluster-wide plan. Bind cluster identity, current topology, contacted node ID and role, served slots, and replication group. For cluster-wide intent, enumerate every current primary and require an explicit per-primary command plan.

After confirmation, revalidate the same standalone target or complete cluster topology immediately before execution. Any identity, role, topology, slot, replication-group, or requested-scope change invalidates authorization.

### DB7 - Redis CONFIG SET
Example: `redis-cli CONFIG SET maxmemory 0`
Risk: Unpersisted runtime configuration drifts.
Decision gate: Confirm intent.
Safe replacement: Preserve runtime-only semantics with `redis-cli CONFIG SET maxmemory 0` after target and value confirmation. Run `redis-cli CONFIG REWRITE` only when the caller explicitly requests persistence and separately confirms the configuration-file mutation.

### DB8 - Mongo database drop
Example: `mongosh "$URI" --eval "db.dropDatabase()"`
Risk: Data and schema loss.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Take a backup first.

### DB9 - Default production target
Example: `psql $DATABASE_URL` where it points at production.
Risk: Silent cross-environment mutation.
Decision gate: Verify target.
Safe replacement: `psql 'host=host dbname=db user=user' -c 'SELECT current_database(), inet_server_addr();'`.

### DB10 - pg_restore clean on the wrong target
Example: `pg_restore --clean -d prod backup.dump`
Risk: Drops live objects before a possibly failing restore.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Restore the same dump to a temporary database first as validation, without treating that as a substitute target. If the requested target remains `prod`, bind its identity, backup/recovery plan, dump identity, and validation result, then separately confirm the original `--clean -d prod` scope. Change the destination only when the caller explicitly chooses a different target.