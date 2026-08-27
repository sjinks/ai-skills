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
Decision gate: Require final snapshot decision and confirmation.
Safe replacement: After verifying the account and choosing a collision-free snapshot ID, confirm `AWS_PROFILE=<profile> AWS_REGION=<region> aws rds delete-db-instance --db-instance-identifier prod --final-db-snapshot-identifier <snapshot-id>`.

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
Safe replacement: Specify environment explicitly: `AWS_PROFILE=dev AWS_REGION=us-east-1 aws s3 ls`, `gcloud --project=dev compute instances list`, `az --subscription=dev resource list`, and `kubectl --context=dev get pods`.

### CL10 - Echoing cloud secret
Example: `echo $AWS_SECRET_ACCESS_KEY`
Risk: Leaks credentials.
Decision gate: Prohibited.
Safe replacement: Do not print resolved secret environment variables.

## Infrastructure as code

### IC1 - Terraform destroy
Example: `terraform destroy -auto-approve`
Risk: Tears down all managed resources.
Decision gate: Refuse without explicit confirmation and reviewed workspace.
Safe replacement: Run `terraform workspace show`, `terraform providers`, and `terraform plan -destroy -out=destroy.plan`; record workspace, backend, targets, plan digest, and complete set. After exact plan review and confirmation, recheck its digest then run `terraform apply destroy.plan`; changed plan, backend, workspace, or target blocks execution.

### IC2 - Auto-approved Terraform apply
Example: `terraform apply -auto-approve`
Risk: Bypasses plan review.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: Run `terraform plan -out=apply.plan`; review exact workspace, backend, targets, and digest, then confirm before `terraform apply apply.plan`.

### IC3 - Terraform apply without plan
Example: `terraform apply`
Risk: No reviewed change set.
Decision gate: Rewrite then confirm the reviewed replacement.
Safe replacement: Use IC2's plan-first sequence.

### IC4 - Terraform state mutation
Example: `terraform state rm aws_instance.web`
Risk: Creates drift and can recreate resources.
Decision gate: Confirm and document intent.
Safe replacement: Run `terraform state list` and `terraform state show aws_instance.web`; document reason and confirm exact address before `terraform state rm aws_instance.web`.

### IC5 - Terraform workspace delete
Example: `terraform workspace delete prod`
Risk: Removes state metadata.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Inspect resources first.

### IC6 - Pulumi destroy with approval bypass
Example: `pulumi destroy --yes`
Risk: Deletes the stack without review.
Decision gate: Rewrite then confirm.
Safe replacement: Run `pulumi preview --diff`; review exact stack and effects, then confirm before `pulumi destroy`.

### IC7 - Forced Pulumi stack removal
Example: `pulumi stack rm --force prod`
Risk: Loses rollback history.
Decision gate: Refuse without explicit confirmation.
Safe replacement: No automatic replacement.

### IC8 - Backend reconfiguration
Example: `terraform init -migrate-state` while another operator holds the lock.
Risk: Can corrupt state.
Decision gate: Verify lock ownership.
Safe replacement: Use `terraform force-unlock <lock-id>` only when stuck and owner-confirmed, then `terraform init -migrate-state`.

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
Safe replacement: Run `docker ps -aq --filter status=exited`; review and pass only selected IDs in `docker rm <container-id> <container-id>`.

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
Decision gate: Confirmable.
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
Any discovery or list failure blocks deletion. Review and bind every resource name, object name, and count; refresh the complete inventory immediately before confirming the exact context and namespace deletion.

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
Decision gate: Refuse without explicit confirmation.
Safe replacement: Read and bind the PVC UID, resource version, and current PV name with `kubectl --context=<context> --namespace=<namespace> get pvc data-0 -o jsonpath='{.metadata.uid}{" "}{.metadata.resourceVersion}{" "}{.spec.volumeName}{"\n"}'`. Require a non-empty `spec.volumeName`, then inspect that bound PV with `kubectl --context=<context> get pv <pv-name> -o jsonpath='{.metadata.uid}{" "}{.metadata.resourceVersion}{" "}{.spec.persistentVolumeReclaimPolicy}{"\n"}'`. After confirmation, re-read both objects immediately before execution; any binding, identity, version, or PV reclaim-policy change invalidates authorization and blocks deletion.

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
Safe replacement: Run `SELECT COUNT(*) FROM orders WHERE created_at < '2020-01-01';`; review target/count and recovery, then confirm `BEGIN; DELETE FROM orders WHERE created_at < '2020-01-01'; COMMIT;`.

### DB3 - Unqualified UPDATE
Example: `UPDATE users SET status='inactive';`
Risk: Mutates all rows.
Decision gate: Refuse without explicit confirmation.
Safe replacement: Run `SELECT COUNT(*) FROM users WHERE last_login < '2020-01-01';`; review target/count and recovery, then confirm `BEGIN; UPDATE users SET status='inactive' WHERE last_login < '2020-01-01'; COMMIT;`.

### DB4 - psql URI password
Example: `psql postgres://user:secret@host/db`
Risk: Password leaks through history and process listings.
Decision gate: Rewrite.
Safe replacement: Use a protected `~/.pgpass` with mode `0600` or credential helper; verify ownership and permission without reading it, then `psql 'host=host dbname=db user=user'`.

### DB5 - MySQL argv password
Example: `mysql -uuser -psecret`
Risk: Password leaks in argv.
Decision gate: Rewrite.
Safe replacement: `mysql_config_editor set --login-path=prod --host=host --user=user --password`, then `mysql --login-path=prod`.

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